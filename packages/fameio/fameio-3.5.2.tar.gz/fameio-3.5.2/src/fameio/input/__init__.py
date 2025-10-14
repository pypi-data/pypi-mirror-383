# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
"""Classes and modules required for the compilation of FAME simulation input files in protobuf format."""


class InputError(Exception):
    """An error that occurred while preparing a fame input file."""


class SchemaError(InputError):
    """An error that occurred while parsing a Schema."""


class ScenarioError(InputError):
    """An error that occurred while parsing a Scenario."""


class YamlLoaderError(InputError):
    """An error that occurred while parsing a YAML file."""
