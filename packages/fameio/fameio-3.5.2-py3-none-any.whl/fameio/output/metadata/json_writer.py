# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Writing of data to JSON files."""

import json
from pathlib import Path

from fameio.logs import log, log_error
from fameio.output import OutputError
from fameio.output.files import METADATA_FILE_NAME

_ERR_OPEN_FILE = "Could not open file for writing: '{}'"
_INFO_DESTINATION = "Saving JSON to file to {}"


class JsonWriterError(OutputError):
    """An error occurred during writing a JSON file."""


def data_to_json_file(data: dict, base_path: Path) -> None:
    """Save the given data to a JSON file at given path.

    Args:
        data: to be saved to JSON file
        base_path: at which the JSON file will be created

    Raises:
        JsonWriterError: if file could not be opened or written, logged with level "ERROR"
    """
    log().info(_INFO_DESTINATION.format(base_path))
    try:
        with open(Path(base_path, METADATA_FILE_NAME), "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError as e:
        raise log_error(JsonWriterError(_ERR_OPEN_FILE.format(base_path))) from e
