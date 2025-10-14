# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: CC0-1.0
"""Classes and modules to compile metadata associated with output files."""

from fameio.output import OutputError


class MetadataCompilationError(OutputError):
    """An error occurred while compiling output metadata."""
