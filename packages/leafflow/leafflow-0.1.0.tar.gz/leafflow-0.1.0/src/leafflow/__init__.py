"""
Leafflow - Behavior Tree Runtime with Python DSL

A framework for declaring and executing Behavior Trees using Python's operator
overloading, with safe integration of external systems (LLMs, HTTP, SQL, scripts).

This is a placeholder release (v0.1.0) to reserve the PyPI package name.
Full implementation is under active development.

License: Apache-2.0
Homepage: https://github.com/leafflow-org/leafflow
"""

__version__ = "0.1.0"
__author__ = "Leafflow Contributors"
__license__ = "Apache-2.0"

# Placeholder API - will be fully implemented in future releases

class _PlaceholderRegistry:
    """Placeholder for ProfileRegistry - not yet implemented."""
    def __init__(self):
        pass
    
    def register_from_file(self, name: str, path: str):
        """Register a leaf profile from YAML file (placeholder)."""
        raise NotImplementedError(
            "ProfileRegistry is not yet implemented in this placeholder release. "
            "See https://github.com/leafflow-org/leafflow for development status."
        )


class _PlaceholderRunner:
    """Placeholder for Runner - not yet implemented."""
    def __init__(self, tree, registry, **kwargs):
        pass
    
    def run(self):
        """Execute the behavior tree (placeholder)."""
        raise NotImplementedError(
            "Runner is not yet implemented in this placeholder release. "
            "See https://github.com/leafflow-org/leafflow for development status."
        )


class _PlaceholderBlackboard:
    """Placeholder for Blackboard reference - not yet implemented."""
    def __getattr__(self, name: str):
        raise NotImplementedError(
            "Blackboard is not yet implemented in this placeholder release. "
            "See https://github.com/leafflow-org/leafflow for development status."
        )


def call(name: str):
    """
    Create a leaf node reference (placeholder).
    
    Args:
        name: The profile name to call
        
    Returns:
        A callable that creates leaf nodes
    """
    raise NotImplementedError(
        "call() is not yet implemented in this placeholder release. "
        "See https://github.com/leafflow-org/leafflow for development status."
    )


# Public API (placeholder exports)
ProfileRegistry = _PlaceholderRegistry
Runner = _PlaceholderRunner
BB = _PlaceholderBlackboard()

__all__ = [
    "__version__",
    "ProfileRegistry",
    "Runner",
    "BB",
    "call",
]


# Development status message
def _show_status():
    """Display current development status."""
    print(f"""
Leafflow v{__version__} - Placeholder Release

This is a placeholder release to reserve the package name on PyPI.
Full implementation is under development.

Repository: https://github.com/leafflow-org/leafflow
    """.strip())


# Show status on import (only in interactive sessions)
import sys
if hasattr(sys, 'ps1'):  # Check if running in interactive mode
    _show_status()

