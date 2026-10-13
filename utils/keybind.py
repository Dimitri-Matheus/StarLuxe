"""Utils for everything related to keybinds in reshade."""

import configparser
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class KeyboardManager:
    @classmethod
    def apply_keybind(cls, ini_path: Path, key_code: str):
        if not key_code:
            logger.warning("No keybind code configured, keeping the ini unchanged")
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

            logger.info(f"Keybind code {key_code} applied to {ini_path}")

        except Exception as e:
            logger.error(f"Failed to apply keybind: {e}")