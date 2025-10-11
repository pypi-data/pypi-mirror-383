# SPDX-License-Identifier: MIT
"""Hook registration for Hatch."""

from hatchling.plugin import hookimpl

from hatch_simple_cython.plugin import SimpleCythonBuildHook


@hookimpl
def hatch_register_build_hook():
    """Register the Simple Cython build hook with Hatch."""
    return SimpleCythonBuildHook
