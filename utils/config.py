"""Utils for all related to the configuration file"""

import os, json

config_file = "settings.json"

default = {
    "Launcher": {
        "game_name": "honkai_star_rail",
        "game_folder": "",
        "gui_theme": "theme\\Trailblazer.json"
    },
    "Packages": {
        "selected": "",
        "available": ["Luminescence", "AstralAura", "Spectrum", "Galactic"],
        "download_dir": ""
    },
    "Account": {
        "github_name": "",
        "preset_resource": "",
        "repository_name": ""
    },
    "Script": {
        "shaders_dir": "script/reshade-shaders",
        "reshade_file": "script/ReShade.ini",
        "injector_file": "script/Injector.exe"
    }
}

#TODO: Ajustar para verificar se tem alterações na variáveis e atualizar
def load_config() -> dict:
    if not os.path.exists(config_file):
        save_config(default)
        return default.copy()
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        save_config(default)
        return default.copy()

def save_config(config: dict):
    with open(config_file, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4, ensure_ascii=False)


#! Test functions
#config = load_config()
#config["theme"] = "dark"
#save_config(config)