"""Utils for all related to the configuration file"""

import os, json
import win32security, ntsecuritycon
from utils.path import resource_path

config_path = resource_path("settings.json")

default = {
    "Launcher": {
        "gui_theme": "theme/default.json",
        "last_played_game": "",
        "xxmi_feature_enabled": False,
        "reshade_feature_enabled": False
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
        "injector_file": "script/Injector.exe",
        "reshade_dll": "script/ReShade64.dll",
        "reshade_config": "script/ReShade64.json",
        "reshade_xr_config": "script/ReShade64_XR.json",
        "xxmi_file": ""
    },
    "Games": {
        "genshin_impact": {
            "icon_path": "assets/icon/GI.png",
            "folder": "",
            "exe": "GenshinImpact.exe",
            "subpath": ""
        },
        "honkai_star_rail": {
            "icon_path": "assets/icon/HSR.png",
            "folder": "",
            "exe": "StarRail.exe",
            "subpath": ""
        },
        "wuthering_waves": {
            "icon_path": "assets/icon/WuWa.png",
            "folder": "",
            "exe": "Client-Win64-Shipping.exe",
            "subpath":  "Client/Binaries/Win64"
        },
        "zenless_zone_zero": {
            "icon_path": "assets/icon/ZZZ.png",
            "folder": "",
            "exe": "ZenlessZoneZero.exe",
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
        print(f"Failed to set permissions for the file {filepath}: {e}")


def load_config() -> dict:
    if not os.path.exists(config_path):
        save_config(default)
        return default.copy()
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        save_config(default)
        return default.copy()


def save_config(config: dict):
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4, ensure_ascii=False)
    grant_user_access(str(config_path))


def delete_config():
    try:
        if config_path.is_file():
            config_path.unlink()
    except Exception as e:
        print(f"Failed to delete the configuration file: {e}")


#! Test functions
# config = load_config()
# config["theme"] = "dark"
# save_config(config)
# delete_config()