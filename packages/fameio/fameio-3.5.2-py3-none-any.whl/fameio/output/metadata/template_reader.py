# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Reading of metadata templates in YAML or JSON format."""

from __future__ import annotations

from pathlib import Path

from fameio.input import YamlLoaderError
from fameio.input.loader import ALLOWED_SUFFIXES as YAML_SUFFIXES, load_yaml
from fameio.logs import log_error
from fameio.output.metadata import MetadataCompilationError

JSON_SUFFIX: str = ".json"
ENCODING = "UTF-8"

_ERR_UNKNOWN_ENDING = "Template file ending '{}' corresponds neither to a JSON or YAML file."
_ERR_READING_FILE = "Could not read template file: '{}'"


def read_template_file(file: Path) -> dict:
    """Reads and returns metadata template `file` encoded in UTF-8.

    Args:
        file: to be read

    Returns:
        dictionary content of the file

    Raises:
        MetadataCompilationError: if template file has unknown type, could not be opened/read, logged with level "ERROR"
    """
    file_ending = file.suffix.lower()
    if _has_yaml_ending(file_ending) or _has_json_ending(file_ending):
        return _read_yaml(file)
    raise log_error(MetadataCompilationError(_ERR_UNKNOWN_ENDING.format(file_ending)))


def _has_yaml_ending(file_ending: str) -> bool:
    """Returns True if `file_ending` corresponds to a YAML file."""
    return file_ending in YAML_SUFFIXES


def _has_json_ending(file_ending: str) -> bool:
    """Returns True if `file_ending` corresponds to a JSON file."""
    return file_ending == JSON_SUFFIX


def _read_yaml(file: Path) -> dict:
    """Returns content of the provided yaml file

    Args:
        file: to be opened and read

    Returns:
        file content as dict

    Raises:
        MetadataCompilationError: if file could not be opened or read, logged with level "ERROR"
    """
    try:
        return load_yaml(file, encoding=ENCODING)
    except YamlLoaderError as e:
        raise log_error(MetadataCompilationError(_ERR_READING_FILE.format(file))) from e
