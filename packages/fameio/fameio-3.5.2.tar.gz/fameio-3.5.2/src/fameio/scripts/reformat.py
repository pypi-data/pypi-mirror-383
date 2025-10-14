#!/usr/bin/env python
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fameio.cli import update_default_config
from fameio.cli.options import Options
from fameio.cli.reformat import handle_args, CLI_DEFAULTS as DEFAULT_CONFIG
from fameio.logs import fameio_logger, log_error, log_and_print
from fameio.output.csv_writer import CsvWriter, CsvWriterError
from fameio.scripts.exception import ScriptError
from fameio.series import TimeSeriesManager, TimeSeriesError
from fameio.tools import get_csv_files_with_pattern, extend_file_name

FILE_NAME_APPENDIX = "_reformatted"

_ERR_FAIL = "Timeseries reformatting script failed."
_ERR_NO_FILES = "No file found matching this pattern: '{}'"
_ERR_FILE_CONVERSION = "Could not reformat file: '{}'"
_ERR_FILES_FAILED = "Could not reformat these files: '{}'"


def reformat_file(file: Path, replace: bool) -> None:
    """Transforms content of specified CSV file to FAME format.

    Args:
        file: whose content is to be reformatted
        replace: if true, original file will be replaced; otherwise, a new file will be created instead

    Raises:
        ScriptError: if file could not be read, file reformatting failed, or result file could not be written;
            logged with level "ERROR"
    """
    try:
        data = TimeSeriesManager.read_timeseries_file(file)
        data = TimeSeriesManager.check_and_convert_series(data, str(file), warn=False)
        target_path = file if replace else extend_file_name(file, FILE_NAME_APPENDIX)
        CsvWriter.write_single_time_series_to_disk(data, target_path)
    except (TimeSeriesError, CsvWriterError) as ex:
        raise log_error(ScriptError(_ERR_FILE_CONVERSION.format(file))) from ex


def run(config: dict[Options, Any] | None = None) -> None:
    """Executes the workflow of transforming time series file(s).

    Args:
        config: configuration options

    Raises:
        ScriptError: if no file could be found, or if any file could not be transformed, logged with level "ERROR"
    """
    config = update_default_config(config, DEFAULT_CONFIG)
    fameio_logger(log_level_name=config[Options.LOG_LEVEL], file_name=config[Options.LOG_FILE])
    try:
        files = get_csv_files_with_pattern(Path("."), config[Options.FILE_PATTERN])
    except ValueError as ex:
        raise log_error(ScriptError(_ERR_NO_FILES.format(config[Options.FILE_PATTERN]))) from ex
    if not files:
        raise log_error(ScriptError(_ERR_NO_FILES.format(config[Options.FILE_PATTERN])))

    erroneous_files = reformat_files(files, config[Options.REPLACE])
    if len(erroneous_files) > 0:
        log_error(ScriptError(_ERR_FILES_FAILED.format(erroneous_files)))
    else:
        log_and_print("All files reformatted.")


def reformat_files(files: list[Path], replace: bool) -> list[str]:
    """Reformats given files and potentially replaces them.

    Args:
        files: list of files to be reformatted
        replace: if true, original files are replaced

    Returns:
        list of files that could not be reformatted
    """
    erroneous_files: list[str] = []
    for file in files:
        log_and_print(f"Reformatting file: {file}")
        try:
            reformat_file(file, replace)
        except ScriptError:
            erroneous_files.append(file.as_posix())
    return erroneous_files


if __name__ == "__main__":
    cli_config = handle_args(sys.argv[1:])
    try:
        run(cli_config)
    except ScriptError as e:
        raise SystemExit(1) from e
