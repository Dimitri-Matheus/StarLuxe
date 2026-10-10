"""Utils for everything related to keybinds in reshade."""

import configparser
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class KeyboardManager:
    KEYBIND_CODES = {
        "Insert": "45,0,0,0",
        "Home": "36,0,0,0",
        "End": "35,0,0,0",
        "PageUp": "33,0,0,0",
        "PageDown": "34,0,0,0",
        "F10": "121,0,0,0",
    }

    @classmethod
    def get_keybinds(cls) -> list:
        return list(cls.KEYBIND_CODES.keys())

    @classmethod
    def apply_keybind(cls, ini_path: Path, key_name: str):
        key_code = cls.KEYBIND_CODES.get(key_name)

        if not key_code:
            logger.warning(f"Unknown keybind {key_name}, keeping the ini unchanged")
            return

        try:
            ini_file = configparser.ConfigParser()
            ini_file.optionxform = str
            ini_file.read(ini_path)

            if not ini_file.has_section("INPUT"):
                ini_file.add_section("INPUT")

            if ini_file.get("INPUT", "KeyOverlay", fallback=None) == key_code:
                return

            ini_file.set("INPUT", "KeyOverlay", key_code)
            with open(ini_path, "w") as f:
                ini_file.write(f)

            logger.info(f"Keybind {key_name} applied to {ini_path}")

        except Exception as e:
            logger.error(f"Failed to apply keybind {key_name}: {e}")