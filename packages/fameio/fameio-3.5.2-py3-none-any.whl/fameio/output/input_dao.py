# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Accessing input content of protobuf messages."""

import ast
from typing import Any, Optional

from fameprotobuf.data_storage_pb2 import DataStorage
from fameprotobuf.field_pb2 import NestedField
from fameprotobuf.input_file_pb2 import InputData

from fameio.input.scenario import GeneralProperties, Agent, Contract, Scenario, StringSet, Attribute
from fameio.input.schema import Schema, AttributeSpecs, AttributeType
from fameio.logs import log_error, log
from fameio.output import OutputError
from fameio.series import TimeSeriesManager, TimeSeriesError


class InputConversionError(OutputError):
    """Indicates an error during reconstruction of input from its protobuf representation."""


class InputDao:
    """Data access object for inputs saved in protobuf."""

    _ERR_NO_INPUTS = "No input data found on file."
    _ERR_MULTIPLE_INPUTS = "File corrupt. More than one input section found on file."
    _ERR_NO_SCHEMA = "No schema found on file - cannot recover inputs."
    _ERR_SERIES_MISSING = "References time series '{}' was not registered on file."
    _ERR_SCENARIO_METADATA = "Proceeding without metadata for scenario - could not be extracted due to: {}"
    _ERR_STRING_SET_METADATA = "Proceeding without metadata for string set '{}' - could not be extracted due to: {}"

    _FIELD_NAME_MAP: dict = {
        AttributeType.STRING: "string_values",
        AttributeType.STRING_SET: "string_values",
        AttributeType.ENUM: "string_values",
        AttributeType.INTEGER: "int_values",
        AttributeType.DOUBLE: "double_values",
        AttributeType.LONG: "long_values",
        AttributeType.TIME_STAMP: "long_values",
        AttributeType.TIME_SERIES: "series_id",
        AttributeType.BLOCK: "fields",
    }

    def __init__(self) -> None:
        self._inputs: list[InputData] = []
        self._timeseries_manager: TimeSeriesManager = TimeSeriesManager()

    def store_inputs(self, data_storages: list[DataStorage]) -> None:
        """Extracts and stores Inputs in given DataStorages - if such are present.

        Args:
            data_storages: to be scanned for InputData
        """
        self._inputs.extend([data_storage.input for data_storage in data_storages if data_storage.HasField("input")])

    def recover_inputs(self) -> tuple[TimeSeriesManager, Scenario]:
        """Recovers inputs to GeneralProperties, Schema, Agents, Contracts, Timeseries.

        Return:
            recovered timeseries and scenario

        Raises:
            InputConversionError: if inputs could not be recovered, logged with level "ERROR"
            InputError: if scenario in file is incompatible with this version of fameio, logged with level "ERROR"
        """
        input_data = self.get_input_data()
        schema = self._get_schema(input_data)
        metadata = self._metadata_to_dict(input_data.metadata)
        scenario = Scenario(schema, self._get_general_properties(input_data), metadata)
        for contract in self._get_contracts(input_data):
            scenario.add_contract(contract)

        self._init_timeseries(input_data)
        for agent in self._get_agents(input_data, schema):
            scenario.add_agent(agent)

        for name, string_set in self._get_string_sets(input_data).items():
            scenario.add_string_set(name, string_set)

        return self._timeseries_manager, scenario

    def get_input_data(self) -> InputData:
        """Check that exactly one previously extracted input data exist and returns them; otherwise raises an exception.

        Returns:
            the previously extracted input data

        Raises:
            InputConversionException: if no input, or more than one input is present, logged with level "ERROR"
        """
        if not self._inputs:
            raise log_error(InputConversionError(self._ERR_NO_INPUTS))
        if len(self._inputs) > 1:
            raise log_error(InputConversionError(self._ERR_MULTIPLE_INPUTS))
        return self._inputs[0]

    @staticmethod
    def _get_schema(input_data: InputData) -> Schema:
        """Read and return Schema from given `input_data`."""
        return Schema.from_string(input_data.schema)

    @staticmethod
    def _metadata_to_dict(metadata: Optional[str] = None) -> dict:
        """Convert given metadata `metadata to dict`, proceeds on error but logs given `message`"""
        if metadata:
            try:
                return ast.literal_eval(metadata)
            except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError) as e:
                log().error(InputDao._ERR_SCENARIO_METADATA.format(e))
        return {}

    @staticmethod
    def _get_general_properties(input_data: InputData) -> GeneralProperties:
        """Read and return GeneralProperties from given `input_data`."""
        return GeneralProperties(
            run_id=input_data.run_id,
            simulation_start_time=input_data.simulation.start_time,
            simulation_stop_time=input_data.simulation.stop_time,
            simulation_random_seed=input_data.simulation.random_seed,
        )

    @staticmethod
    def _get_contracts(input_data: InputData) -> list[Contract]:
        """Read and return Contracts from given `input_data`."""
        return [
            Contract(
                sender_id=contract.sender_id,
                receiver_id=contract.receiver_id,
                product_name=contract.product_name,
                delivery_interval=contract.delivery_interval_in_steps,
                first_delivery_time=contract.first_delivery_time,
                expiration_time=contract.expiration_time,
                metadata=ast.literal_eval(contract.metadata) if contract.metadata else None,
            )
            for contract in input_data.contracts
        ]

    @staticmethod
    def _get_string_sets(input_data: InputData) -> dict[str, StringSet]:
        """Read and return StringSets from given `input_data`."""
        string_sets = {}
        for dao in input_data.string_sets:
            values = {
                entry.name: {StringSet.KEY_METADATA: InputDao._metadata_to_dict(entry.metadata)} for entry in dao.values
            }
            metadata = InputDao._metadata_to_dict(dao.metadata)
            string_sets[dao.name] = StringSet.from_dict(
                {StringSet.KEY_VALUES: values, StringSet.KEY_METADATA: metadata}
            )
        return string_sets

    def _init_timeseries(self, input_data: InputData) -> None:
        """Read timeseries from given `input_data` and initialise TimeSeriesManager."""
        self._timeseries_manager.reconstruct_time_series(list(input_data.time_series))

    def _get_agents(self, input_data: InputData, schema: Schema) -> list[Agent]:
        """Read and return Agents from given `input_data`.

        Args:
            input_data: to read agents from
            schema: corresponding to the agent definitions

        Returns:
            all extracted agents

        Raises:
            InputError: if agents cannot be reconstructed, logged with level "ERROR"
            InputConversionError: if attributes could not be reconstructed, logged with level "ERROR"
        """
        agents = []
        for agent_dao in input_data.agents:
            agent = Agent(
                agent_id=agent_dao.id,
                type_name=agent_dao.class_name,
                metadata=ast.literal_eval(agent_dao.metadata) if agent_dao.metadata else None,
            )
            attributes_dict = self._get_attributes_dict(
                list(agent_dao.fields), schema.agent_types[agent_dao.class_name].attributes
            )
            agent.init_attributes_from_dict(attributes_dict)
            agents.append(agent)
        return agents

    def _get_attributes_dict(self, fields: list[NestedField], schematics: dict[str, AttributeSpecs]) -> dict[str, dict]:
        """Read and return all Attributes as Dictionary from given list of fields.

        Args:
            fields: data fields representing attributes
            schematics: description of the attributes associated by name

        Returns:
            all recovered attributes and their associated values as dictionary

        Raises:
            InputConversionError: if attributes could not be reconstructed, logged with level "ERROR"
        """
        attributes: dict[str, dict[str, Any]] = {}
        for field in fields:
            value = self._get_field_value(field, schematics[field.field_name])
            attributes[field.field_name] = value if not field.metadata else self._get_field_dict(value, field.metadata)
        return attributes

    def _get_field_value(self, field: NestedField, schematic: AttributeSpecs) -> Any:
        """Extracts and returns value(s) of given `field`.

        Args:
            field: to extract the value(s) from
            schematic: describing the data type of this field

        Returns:
            value(s) of provided field

        Raises:
            InputConversionError: if TimeSeries could not be found, logged with level "ERROR"
        """
        attribute_type: AttributeType = schematic.attr_type
        if attribute_type is AttributeType.TIME_SERIES:
            try:
                return self._timeseries_manager.get_reconstructed_series_by_id(field.series_id)
            except TimeSeriesError as e:
                raise log_error(InputConversionError(self._ERR_SERIES_MISSING.format(field.series_id))) from e
        if attribute_type is AttributeType.BLOCK:
            if schematic.is_list:
                return [
                    self._get_attributes_dict(list(entry.fields), schematic.nested_attributes) for entry in field.fields
                ]
            return self._get_attributes_dict(list(field.fields), schematic.nested_attributes)
        value = getattr(field, self._FIELD_NAME_MAP[attribute_type])
        if schematic.is_list:
            return list(value)
        return list(value)[0]

    def _get_field_dict(self, field_value: Any, metadata: str) -> dict[str, Any]:
        """Returns dict with metadata and `field_value` associated with either singular or plural key, if is list."""
        result: dict[str, Any] = {Attribute.KEY_METADATA: self._metadata_to_dict(metadata)}
        if isinstance(field_value, list):
            result[Attribute.KEY_VALUES] = field_value
        else:
            result[Attribute.KEY_VALUE] = field_value
        return result
