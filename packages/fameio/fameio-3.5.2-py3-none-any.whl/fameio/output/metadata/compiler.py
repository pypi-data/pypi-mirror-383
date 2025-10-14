# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Compiling metadata files accompanying the output CSV files."""

from __future__ import annotations

import ast
from typing import Final, Any

from fameprotobuf.input_file_pb2 import InputData

from fameio.input.metadata import Metadata
from fameio.logs import log_error, log
from fameio.output.metadata import MetadataCompilationError
from fameio.output.metadata.locator import Locator
from fameio.tools import keys_to_lower


class MetadataCompiler(Locator):
    """Compiles metadata for output files based on ExecutionData and InputData."""

    ENTRY_SCHEMA: Final[str] = "Schema".lower()
    ENTRY_SCENARIO: Final[str] = "Scenario".lower()
    ENTRY_EXECUTION: Final[str] = "Execution".lower()
    SEPARATOR: Final[str] = ":"

    _ERR_MALFORMED_DICT_STRING = "Input data reading failed: Malformed string representation of metadata dictionaries."
    _INFO_NOT_FOUND = "Could not find element at '{}' in input section of provided file."

    def __init__(
        self, execution_data: dict[str, Any], input_data: InputData, agent_columns: dict[str, list[str]]
    ) -> None:
        """Initialises a new MetadataCompiler.

        Args:
            execution_data: to read execution metadata from
            input_data: to read schema and scenario metadata from
            agent_columns: agents and their output columns
        """
        super().__init__(agent_columns)
        try:
            self._data: dict[str, dict] = {
                self.ENTRY_SCHEMA: ast.literal_eval(input_data.schema),
                self.ENTRY_SCENARIO: {
                    Metadata.KEY_METADATA: ast.literal_eval(input_data.metadata) if input_data.metadata else {}
                },
                self.ENTRY_EXECUTION: execution_data,
            }
        except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError) as e:
            raise log_error(MetadataCompilationError(self._ERR_MALFORMED_DICT_STRING)) from e

    def _replace(self, data_identifier: str) -> Any | None:
        identifier = data_identifier[1:-1]
        address = identifier.split(self.SEPARATOR)
        data_source = address[0].lower()
        try:
            if data_source in self._data:
                return self._get_from(self._data[data_source], address[1:])
        except KeyError:
            log().info(self._INFO_NOT_FOUND.format(self.SEPARATOR.join(address)))
            return None
        return None

    @staticmethod
    def _get_from(base: dict, address: list[str]) -> Any:
        """Returns element in `base` at given `address`.

        Raises:
            KeyError: if element cannot be found; error not logged
        """
        element = base
        for entry in address:
            element = keys_to_lower(element)[entry.lower()]
        return element
