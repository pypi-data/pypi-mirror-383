# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Writing of dataframes to CSV files."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

from fameio.cli.options import TimeOptions
from fameio.logs import log_error
from fameio.output import OutputError
from fameio.output.conversion import apply_time_option
from fameio.output.data_transformer import INDEX
from fameio.series import TimeSeriesManager
from fameio.tools import ensure_path_exists


class CsvWriterError(OutputError):
    """An error occurred during writing a CSV file."""


class CsvWriter:
    """Writes dataframes to different csv files."""

    _ERR_FILE_OPEN = "Could not open file for writing: '{}'"
    _ERR_FILE_WRITE = "Could not write to file '{}' due to: {}"

    CSV_FILE_SUFFIX = ".csv"

    def __init__(self, output_folder: Path, single_export: bool) -> None:
        """Constructs a new CsvWriter.

        Args:
            output_folder: to write the output files to
            single_export: if true, one output file per unique agent is created
        """
        self._single_export = single_export
        self._output_folder = output_folder
        self._files: dict[str, Path] = {}

    def write_to_files(self, agent_name: str, data: dict[None | str, pd.DataFrame]) -> None:
        """Writes `data` for given `agent_name` to .csv file(s).

        Args:
            agent_name: name of agent whose data are to be written to file(s)
            data: previously extracted data for that agent that are to be written

        Raises:
            CsvWriterError: when file could not be written, logged on level "ERROR"
        """
        for column_name, column_data in data.items():
            column_data.sort_index(inplace=True)
            if self._single_export:
                for agent_id, agent_data in column_data.groupby(INDEX[0]):
                    identifier = self._get_identifier(agent_name, column_name, str(agent_id))
                    self._write_data_frame(agent_data, identifier)
            else:
                identifier = self._get_identifier(agent_name, column_name)
                self._write_data_frame(column_data, identifier)

    def write_all_time_series_to_disk(
        self, timeseries_manager: TimeSeriesManager, time_mode: TimeOptions | None = None
    ) -> None:
        """Writes time_series of given `timeseries_manager` to disk.

        Args:
            timeseries_manager: to provide the time series that are to be written
            time_mode: mode of representing time in series that are to be written

        Raises:
            CsvWriterError: if data could not be written to disk, logged on level "ERROR"
        """
        for _, name, data in timeseries_manager.get_all_series():
            if data is not None:
                target_path = Path(self._output_folder, name)
                ensure_path_exists(target_path.parent)
                if time_mode:
                    apply_time_option(data={name: data}, mode=time_mode)
                self.write_single_time_series_to_disk(data, target_path)

    @staticmethod
    def write_single_time_series_to_disk(data: pd.DataFrame, file: Path) -> None:
        """Writes given timeseries the provided file path.

        Args:
            data: to be written
            file: target path of csv file

        Raises:
            CsvWriterError: if data could not be written to disk, logged on level "ERROR"
        """
        CsvWriter._dataframe_to_csv(data, file, header=False, index=True, mode="w")

    @staticmethod
    def _dataframe_to_csv(data: pd.DataFrame, file: Path, header: bool, index: bool, mode: Literal["a", "w"]) -> None:
        """Write given data to specified CSV file in UTF8 encoding with specified parameters using semicolon separators.

        Args:
            data: to be written
            file: target path of csv file
            header: write column headers
            index: write index column(s)
            mode: append to or overwrite file

        Raises:
            CsvWriterError: if data could not be written to disk, logged on level "ERROR"
        """
        try:
            data.to_csv(path_or_buf=file, sep=";", header=header, index=index, mode=mode, encoding="UTF-8")
        except OSError as e:
            raise log_error(CsvWriterError(CsvWriter._ERR_FILE_OPEN.format(file))) from e
        except UnicodeError as e:
            raise log_error(CsvWriterError(CsvWriter._ERR_FILE_WRITE.format(file, str(e)))) from e

    @staticmethod
    def _get_identifier(agent_name: str, column_name: str | None = None, agent_id: str | None = None) -> str:
        """Returns unique identifier for given `agent_name` and (optional) `agent_id` and `column_name`"""
        identifier = str(agent_name)
        if column_name:
            identifier += f"_{column_name}"
        if agent_id:
            identifier += f"_{agent_id}"
        return identifier

    def _write_data_frame(self, data: pd.DataFrame, identifier: str) -> None:
        """Writes `data` to csv file derived from `identifier`.

        Appends data if csv file exists, else writes new file with headers instead.

        Args:
            data: to be written to file
            identifier: to derive the file name from

        Raises:
            CsvWriterError: when file could not be written, logged on level "ERROR"
        """
        if self._has_file(identifier):
            outfile_name = self._get_outfile_name(identifier)
            mode: Literal["a", "w"] = "a"
            header = False
        else:
            outfile_name = self._create_outfile_name(identifier)
            self._save_outfile_name(outfile_name, identifier)
            mode = "w"
            header = True
        self._dataframe_to_csv(data, outfile_name, header=header, index=True, mode=mode)

    def _has_file(self, identifier: str) -> bool:
        """Returns True if a file for given `identifier` was already written."""
        return identifier in self._files

    def pop_all_file_paths(self) -> dict[str, Path]:
        """Clears all stored file paths and returns their previous identifiers and their paths."""
        current_files = self._files
        self._files = {}
        return current_files

    def _get_outfile_name(self, identifier: str) -> Path:
        """Returns file path for given `agent_name` and (optional) `agent_id`."""
        return self._files[identifier]

    def _create_outfile_name(self, identifier: str) -> Path:
        """Returns fully qualified file path based on given `agent_name` and (optional) `agent_id`."""
        return Path(self._output_folder, f"{identifier}{self.CSV_FILE_SUFFIX}")

    def _save_outfile_name(self, outfile_name: Path, identifier: str) -> None:
        """Stores given name for given `agent_name` and (optional) `agent_id`."""
        self._files[identifier] = outfile_name
