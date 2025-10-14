# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Locating replacement strings in complex template dictionaries."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, Final

from fameio.logs import log_error
from fameio.output.metadata import MetadataCompilationError
from fameio.tools import keys_to_lower


class Locator(ABC):
    """Locates replacement strings within a given template and organises their replacement."""

    KEY_BASE: Final[str] = "base".lower()
    KEY_PER_AGENT: Final[str] = "perAgent".lower()
    KEY_PER_COLUMN: Final[str] = "perColumn".lower()

    PLACEHOLDER_START: Final[str] = "<"
    PLACEHOLDER_END: Final[str] = ">"
    _PLACEHOLDER_PATTERN: Final[re.Pattern] = re.compile(PLACEHOLDER_START + ".*?" + PLACEHOLDER_END)

    KEY_AGENT: Final[str] = "Agent".lower()
    KEY_COLUMN: Final[str] = "Column".lower()

    ITERATION_START: Final[str] = "{{"
    ITERATION_END: Final[str] = "}}"
    _PER_AGENT_PATTERN: Final[str] = ITERATION_START + KEY_PER_AGENT + ITERATION_END
    _PER_COLUMN_PATTERN: Final[str] = ITERATION_START + KEY_PER_COLUMN + ITERATION_END

    _ESC = "\\"
    ITERABLE_START: Final[str] = "("
    ITERABLE_END: Final[str] = ")"
    _AGENT_PATTERN: Final[re.Pattern] = re.compile(
        f"{_ESC}{ITERABLE_START}{KEY_AGENT}{_ESC}{ITERABLE_END}", re.IGNORECASE
    )
    _COLUMN_PATTERN: Final[re.Pattern] = re.compile(
        f"{_ESC}{ITERABLE_START}{KEY_COLUMN}{_ESC}{ITERABLE_END}", re.IGNORECASE
    )

    _ERR_MUST_BE_DICT = "Element '{}' in metadata template must be a dictionary."

    def __init__(self, agent_columns: dict[str, list[str]]) -> None:
        """Initialise a new Locator.

        Args:
            agent_columns: agents and their output columns
        """
        self._agent_columns: dict = agent_columns
        self._per_agent_template: dict = {}
        self._per_column_template: dict = {}
        self._current_agent: str = ""
        self._current_column: str = ""

    def locate_and_replace(self, template: dict) -> dict:
        """Returns copy of given `template` with filled-in metadata to each placeholder - if available.

        Args:
            template: dict with placeholders to be filled

        Returns:
            template with filled in placeholders (if any)

        Raises:
            MetadataCompilationError: if template is ill-formatted, logged with level "ERROR"
        """
        template = keys_to_lower(template)
        per_agent_template = template.get(self.KEY_PER_AGENT, {})
        self._ensure_is_dict(per_agent_template, self.KEY_PER_AGENT)
        self._per_agent_template = per_agent_template

        per_column_template = template.get(self.KEY_PER_COLUMN, {})
        self._ensure_is_dict(per_column_template, self.KEY_PER_COLUMN)
        self._per_column_template = per_column_template

        self._current_column = ""
        self._current_agent = ""

        return self._fill_dict(template.get(self.KEY_BASE, {}))

    def _ensure_is_dict(self, item: Any, key: str) -> None:
        """Raises an error if given `item` is not a dictionary.

        Args:
            item: to be tested if it is a dictionary
            key: to be specified in error message

        Raises:
            MetadataCompilationError: if given `item` is not a dictionary, logged with level "ERROR"
        """
        if not isinstance(item, dict):
            raise log_error(MetadataCompilationError(self._ERR_MUST_BE_DICT.format(key)))

    def _fill_dict(self, template: dict) -> dict:
        """Fills in metadata to each value of the given dictionary `template`.

        Args:
            template: dict with placeholders to be filled

        Returns:
            template with filled in placeholders (if any)
        """
        result: dict = {}
        for key, value in template.items():
            if isinstance(value, dict):
                result[key] = self._fill_dict(value)
            elif isinstance(value, list):
                result[key] = self._fill_list(value)
            else:
                result[key] = self._fill_value(value)
        return result

    def _fill_list(self, values: list) -> list:
        """Fills in metadata to each value of the given `values` list.

        Args:
            values: list of elements with potential placeholders to be filled

        Returns:
            values, potentially with filled-in placeholders
        """
        result: list = []
        for value in values:
            if isinstance(value, dict):
                result.append(self._fill_dict(value))
            elif isinstance(value, list):
                result.append(self._fill_list(value))
            else:
                filled_value = self._fill_value(value)
                if isinstance(filled_value, list):
                    result.extend(filled_value)
                else:
                    result.append(filled_value)
        return result

    def _fill_value(self, value: str | int | float) -> Any:
        """Checks for placeholders, iterables, or iteration template markers to replace.

        Returns replacement or original value if replacement cannot be found.

        Args:
            value: to replace or return if no replacement is needed / available

        Returns:
            replacement or original value if replacement is not needed / available
        """
        if isinstance(value, (int, float)):
            return value
        if self._is_agent_replacement(value):
            value = self._replace_agent(value)
        if self._is_column_replacement(value):
            value = self._replace_column(value)
        if self._has_basic_placeholder(value):
            return self._replace_all(value)
        if self._is_per_column(value):
            return self._per_column()
        if self._is_per_agent(value):
            return self._per_agent()
        return value

    def _has_basic_placeholder(self, value: str) -> bool:
        """Returns true if given value contains placeholder symbols."""
        return self.PLACEHOLDER_START in value and self.PLACEHOLDER_END in value

    def _replace_all(self, value: str) -> str | Any:
        """Replaces all placeholders in given `value` and returns the string with all replacements.

        If the whole string is a single placeholder, replace it completely with the replacement content - of any type.
        Otherwise, replace the placeholders within the string with the replacement content.
        """
        matches = re.findall(self._PLACEHOLDER_PATTERN, value)
        if len(matches) == 1:
            if re.fullmatch(self._PLACEHOLDER_PATTERN, value):
                return self._replace(value)
        return re.sub(self._PLACEHOLDER_PATTERN, self._callback_wrapper, value)

    @abstractmethod
    def _replace(self, data_identifier: str) -> Any | None:
        """Returns replacement for given data identifier, or None if replacement cannot be found.

        Args:
            data_identifier: locator for the replacement data

        Returns:
            either the found replacement data (of any type), or None if no data is found
        """

    def _callback_wrapper(self, match: re.Match) -> str:
        """Extracts replacement string from given match and calls for its replacement."""
        return str(self._replace(match.group(0)))

    def _is_agent_replacement(self, value: str) -> bool:
        """Returns true if given value contains placeholder and agent iterable placeholder."""
        return re.search(self._AGENT_PATTERN, value) is not None

    def _replace_agent(self, value) -> str:
        """Replace all occurrences of agent iterable pattern in given string."""
        return re.sub(self._AGENT_PATTERN, str(self._current_agent), value)

    def _is_column_replacement(self, value: str) -> bool:
        """Returns true if given value contains placeholder and agent iterable placeholder."""
        return re.search(self._COLUMN_PATTERN, value) is not None

    def _replace_column(self, value) -> str:
        """Replace all occurrences of column iterable pattern in given string."""
        return re.sub(self._COLUMN_PATTERN, str(self._current_column), value)

    def _is_per_column(self, value: str) -> bool:
        """Returns true if given value is the 'perColumn' section."""
        return value.strip().lower() == self._PER_COLUMN_PATTERN

    def _per_column(self) -> list:
        """Returns list of metadata for all columns of current agent."""
        column_metadata = []
        if len(self._per_column_template) > 0:
            for column in self._agent_columns[self._current_agent]:
                template = self._per_column_template
                self._current_column = column
                column_metadata.append(self._fill_dict(template))
        return column_metadata

    def _is_per_agent(self, value: str) -> bool:
        """Returns true if given value is the 'perAgent' section."""
        return value.strip().lower() == self._PER_AGENT_PATTERN

    def _per_agent(self) -> list:
        """Returns list of metadata for all agents.

        Returns empty list if either the per-agent template is missing, or no agents are registered for output.
        """
        agent_metadata = []
        if len(self._per_agent_template) > 0:
            for agent in self._agent_columns.keys():
                template = self._per_agent_template
                self._current_agent = agent
                agent_metadata.append(self._fill_dict(template))
        return agent_metadata
