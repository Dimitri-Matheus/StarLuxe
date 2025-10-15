"""Utils for everything related path to a resource"""
import sys
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    """Return the absolute path to a resource, working both in development mode and when packaged."""
    if getattr(sys, 'frozen', False):
        base_path = Path(__file__).parent
    else:
        base_path = Path(__file__).parent.parent.resolve()

    return base_path / relative_path

