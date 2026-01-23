"""Utils for everything related path to a resource"""

import json, logging
from pathlib import Path
from utils.path import resource_path
# from config import load_config

logging.basicConfig(level=logging.INFO)

class ThemeManager:
    data: dict = {}
    current_theme_path: Path = None

    def __init__(self, theme_path):
        self.themes_root = Path(theme_path)

    def get_available_themes(self):
        if not self.themes_root.exists():
            return ["Default"]
        
        themes = []
        for folder in self.themes_root.iterdir():
            if folder.is_dir():
                files = list(folder.glob("*.json"))
                if files:
                    themes.append(folder.name)
        
        return sorted(themes, key=lambda value: (value != "Default", value))
    
    def find_theme(self, theme_folder: Path) -> Path | None:
        json_files = list(theme_folder.glob("*.json"))
        return json_files[0] if json_files else None
    
    def load_theme(self, name: str) -> dict:
        ThemeManager.current_theme_path = self.themes_root / name
        theme_json = self.find_theme(ThemeManager.current_theme_path)

        if not theme_json or not theme_json.exists():
            logging.warning(f"Theme not found! Loading default theme")
            ThemeManager.current_theme_path = self.themes_root / "Default"
            theme_json = self.find_theme(ThemeManager.current_theme_path)

            if not theme_json:
                logging.error("Default theme not found!")
                return ""
        
        try:
            with open(theme_json, "r", encoding="utf-8") as file:
                ThemeManager.data = json.load(file)
        except Exception as e:
            logging.error(f"Error loading theme: {e}")
            ThemeManager.data = {}

        # logging.info(f"Theme {name} loaded successfully!")
        return str(theme_json)
    
    @classmethod
    def get_custom_color(cls, color_name: str) -> list | str | None:
        custom_colors = cls.data.get("custom_colors", {})
        return custom_colors.get(color_name)
    
    @classmethod
    def find_image(cls, base_path: Path):
        Extensions = [".png", ".jpg", ".jpeg"]
        if base_path.suffix.lower() in Extensions and base_path.exists():
            return base_path
        
        for filename in Extensions:
            img_name = base_path.with_suffix(filename)
            if img_name.exists():
                return img_name 
        return None
    
    @classmethod
    def get_images(cls, relative_path: str, fallback: str = None) -> str | None:
        if cls.current_theme_path:
            base_path = cls.current_theme_path / relative_path
            image_path = cls.find_image(base_path)
            if image_path:
                return str(image_path)
        if fallback:
            return fallback
        
        default_path = cls.current_theme_path.parent / "Default" / relative_path
        if default_path.exists():
            return str(default_path)
        return None


#! Test functions
# config = load_config()
# theme_manager = ThemeManager(resource_path("themes"))
# logging.info(theme_manager.get_available_themes())
# logging.info(f"Data: {theme_manager.load_theme(config["Launcher"]["gui_theme"])}")
