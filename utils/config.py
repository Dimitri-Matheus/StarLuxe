"""Utils for all related to the configuration file"""

import os, json, copy
import win32security, ntsecuritycon
from utils.path import resource_path

config_path = resource_path("settings.json")

default = {
    "Launcher": {
        "auto_check_update": True,
        "gui_theme": "Default",
        "last_played_game": "",
        "xxmi_feature_enabled": False,
        "reshade_feature_enabled": False
    },
    "Packages": {
        "selected": "",
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
        "reshade_dll": "script/ReShade64.dll",
        "reshade_config": "script/ReShade64.json",
        "reshade_xr_config": "script/ReShade64_XR.json",
        "xxmi_file": ""
    },
    "Games": {
        "genshin_impact": {
            "icon_path": "assets/games/GI.png",
            "folder": "",
            "exe": "GenshinImpact.exe",
            "subpath": ""
        },
        "honkai_star_rail": {
            "icon_path": "assets/games/HSR.png",
            "folder": "",
            "exe": "StarRail.exe",
            "subpath": ""
        },
        "wuthering_waves": {
            "icon_path": "assets/games/WuWa.png",
            "folder": "",
            "exe": "Client-Win64-Shipping.exe",
            "subpath":  "Client/Binaries/Win64"
        },
        "zenless_zone_zero": {
            "icon_path": "assets/games/ZZZ.png",
            "folder": "",
            "exe": "ZenlessZoneZero.exe",
            "subpath": ""
        },
        "duet_night_abyss": {
            "icon_path": "assets/games/DNA.png",
            "folder": "",
            "exe": "EM-Win64-Shipping.exe",
            "subpath": "EM/Binaries/Win64"
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


def update_config(base, template):
    updated = False
    new_base = {}

    for key, var in template.items():
        if key not in base:
            new_base[key] = copy.deepcopy(var)
            updated = True
        
        elif isinstance(var, dict) and isinstance(base[key], dict):
            sub_dict = base[key] 
            if update_config(sub_dict, var):
                updated = True
            new_base[key] = sub_dict
            
        else:
            new_base[key] = base[key]
    if list(base.keys()) != list(new_base.keys()):
        updated = True

    if updated:
        base.clear()
        base.update(new_base)

    return updated


def load_config() -> dict:
    if not os.path.exists(config_path):
        save_config(default)
        return default.copy()
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            user_config = json.load(file)
            update = update_config(user_config, default)
            if update:
                save_config(user_config)
            return user_config
        
    except json.JSONDecodeError:
        save_config(default)
        return default.copy()
    

def load_metadata() -> dict:
    try:
        metadata_path = resource_path("script/Presets/metadata.json")
        with open(metadata_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"presets": []}


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