# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Finding output folders and files, creating the output folder."""

from __future__ import annotations

from pathlib import Path
from typing import Final, Optional

from fameio.logs import log, log_error
from fameio.output import OutputError

_ERR_DIR_CREATE = "Could not create directory for output files: '{}'"

_INFO_USING_PATH = "Using specified output path: '{}'"
_INFO_USING_DERIVED_PATH = "No output path specified - writing to new local folder: '{}'"

_DEBUG_NEW_FOLDER = "Output folder '{}' not present, trying to create it..."
_DEBUG_EXISTING_FOLDER = "Output folder '{}' already exists..."

RECOVERED_INPUT_PATH: Final[str] = "./recovered"
RECOVERED_SCENARIO_PATH: Final[str] = "./recovered/scenario.yaml"
METADATA_FILE_NAME: Final[str] = "metadata.json"


class OutputPathError(OutputError):
    """An error that occurred during creation of the output path."""


def get_output_folder_name(config_output: Optional[Path | str], input_file_path: Path) -> Path:
    """Returns name of the output folder derived either from the specified `config_output` or `input_file_path`."""
    if config_output:
        output_folder_name = config_output
        log().info(_INFO_USING_PATH.format(config_output))
    else:
        output_folder_name = input_file_path.stem
        log().info(_INFO_USING_DERIVED_PATH.format(output_folder_name))
    return Path(output_folder_name)


def create_output_folder(output_path: Path) -> None:
    """Creates output folder if not yet present.

    Raises:
        OutputPathError: if output folder could not be created, logged with level "ERROR"
    """
    if not output_path.is_dir():
        log().debug(_DEBUG_NEW_FOLDER.format(output_path))
        try:
            output_path.mkdir(parents=True)
        except OSError as e:
            raise log_error(OutputPathError(_ERR_DIR_CREATE.format(output_path))) from e
    else:
        log().debug(_DEBUG_EXISTING_FOLDER.format(output_path))
