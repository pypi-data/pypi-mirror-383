# SPDX-License-Identifier: MIT
"""Simplified Cython build hook for Hatch."""

__version__ = "0.1.0"

from hatch_simple_cython.plugin import SimpleCythonBuildHook

__all__ = ["SimpleCythonBuildHook"]
