"""Utils for everything related to pyinstaller and its path to a resource"""
import os, sys
from pathlib import Path

def resource_path(relative_path):
    """
    Return the absolute path to a resource, working both in
    development mode and when packaged by PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)