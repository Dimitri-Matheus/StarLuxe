"""Utils for all related to the configuration file"""

import os, json
import win32security, win32api, ntsecuritycon

config_file = "settings.json"

default = {
    "Launcher": {
        "gui_theme": "theme\\default.json",
        "last_played_game": ""
    },
    "Packages": {
        "selected": "",
        "available": ["Luminescence", "AstralAura", "Spectrum", "Galactic", "Legacy"],
        "download_dir": "script/Presets"
    },
    "Account": {
        "github_name": "Dimitri-Matheus",
        "preset_folder": "script/",
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

def grant_user_access(filepath: str):
    if not os.path.exists(filepath):
        return

    try:
        sd = win32security.GetFileSecurity(filepath, win32security.DACL_SECURITY_INFORMATION)
        dacl = sd.GetSecurityDescriptorDacl()
        if dacl is None:
            dacl = win32security.ACL()

        authenticated_users_sid = win32security.CreateWellKnownSid(win32security.WinAuthenticatedUserSid)
        dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_ALL_ACCESS, authenticated_users_sid)
        sd.SetSecurityDescriptorDacl(1, dacl, 0)
        win32security.SetFileSecurity(filepath, win32security.DACL_SECURITY_INFORMATION, sd)

    except Exception as e:
        print(f"Falha ao definir permissões para o arquivo {filepath}: {e}")


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
    grant_user_access(config_file)


#! Test functions
#config = load_config()
#config["theme"] = "dark"
#save_config(config)