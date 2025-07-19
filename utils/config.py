"""Utils for all related to the configuration file"""

import os, json

config_file = "settings.json"

#TODO: Modificar o "download_dir": "Presets/" para ele criar a pasta de Presets
#TODO: Modificar as chaves github_name, preset_resource e repository_name
default = {
    "Launcher": {
        "gui_theme": "theme\\Trailblazer.json"
    },
    "Packages": {
        "selected": "",
        "available": ["Luminescence", "AstralAura", "Spectrum", "Galactic"],
        "download_dir": "Presets/"
    },
    "Account": {
        "github_name": "Dimitri-Matheus",
        "preset_resource": "script/",
        "repository_name": "HSR-Script"
    },
    "Script": {
        "shaders_dir": "script/reshade-shaders",
        "reshade_file": "script/ReShade.ini",
        "injector_file": "script/Injector.exe"
    },
    "Games": {
        "wuthering_waves": {
            "folder": "",
            "exe": "Client-Win64-Shipping.exe",
            "subpath":  "Client/Binaries/Win64"
        },
        "genshin_impact": {
            "folder": "",
            "exe": "GenshinImpact.exe",
            "subpath": ""
        },
        "honkai_star_rail": {
            "folder": "",
            "exe": "StarRail.exe",
            "subpath": ""
        }
    }
}

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