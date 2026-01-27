"""Utils for all related to Reshade injection logic"""

import psutil, shutil, subprocess, logging, json, hashlib, time, configparser
from pathlib import Path
from pymem import Pymem
from pymem.process import inject_dll_from_path
from utils.path import relative_path
# from config import load_config

logging.basicConfig(level=logging.INFO)

def get_filesystem(path: str) -> str:
    try:
        drive_path = Path(path).resolve().drive
        if not drive_path:
            return "Filesystem Unknown"

        for partition in psutil.disk_partitions():
            if partition.device.startswith(drive_path):
                return partition.fstype.upper()
        
    except Exception as e:
        logging.warning(f"Error detecting filesystem type: {e}")


class ReshadeSetup():
    def __init__(self, settings: dict, game_path: str, xxmi_enabled: bool):
        self.settings = settings
        self.game_base = game_path
        self.game_path = Path(self.game_base)

        self.game_config = self.settings.get("Games", {})
        self.script_config = self.settings.get("Script", {})
        self.package_config = self.settings.get("Packages", {})
        self.launcher_config = self.settings.get("Launcher", {})
        self.xxmi_enabled = xxmi_enabled

        self.reshade_src = relative_path(self.script_config.get("reshade_file"))
        self.shaders_src = relative_path(self.script_config.get("shaders_dir"))
        self.reshade_dll = relative_path(self.script_config.get("reshade_dll"))
        self.reshade_dxvk = relative_path(self.script_config.get("reshade_dxvk"))
        self.reshade_config = relative_path(self.script_config.get("reshade_config"))
        self.reshade_xr_config = relative_path(self.script_config.get("reshade_xr_config"))

        self.xxmi_src = relative_path(self.script_config.get("xxmi_file"))
        self.download_src = relative_path(self.package_config.get("download_dir"))
        self.reshade_enabled = self.launcher_config.get("reshade_feature_enabled")
        self.direct_enabled = self.launcher_config.get("direct_feature_enabled")

    def verify_installation(self):
        try:
            if not self.game_base or not self.game_path.is_dir():
                logging.error(f"Missing or invalid path: {self.game_path}")
                raise FileNotFoundError("Game installation not found!")

            for code, config in self.game_config.items():
                exe_path = (self.game_path / config["subpath"] / config["exe"]).resolve()
                if exe_path.is_file():
                    self.game_code = code
                    self.game_info = config
                    self.game_dir = exe_path.parent
                    self.exe_path = exe_path
                    break
            else:
                logging.error("Could not find a supported game executable in the selected folder")
                raise FileNotFoundError("Game executable not found!")

        except Exception as e:
            return {
                "status": False,
                "message": str(e),
                "error_type": "installation"
            }
        
        logging.info(f"All files for {self.game_code} verified successfully!")
        return {
            "status": True,
            "game_code": self.game_code
        }

    def verify_system(self):
        validation_items = [
                ("ReShade.ini", self.reshade_src, "file"),
                ("Shaders folder", self.shaders_src, "dir"),
                ("ReShade64.dll", self.reshade_dll, "file"),
                ("ReShade64.json", self.reshade_config, "file"),
                ("ReShade64_XR.json", self.reshade_xr_config, "file")
            ]
        
        if self.xxmi_enabled:
            validation_items.append(("XXMI Launcher Config", self.xxmi_src, "xxmi"))

        try:
            for name, path, item in validation_items:
                exists = path.is_file() if item != "dir" else path.is_dir()

                if not exists:
                    logging.error(f"Missing required {name}: {path}")
                    raise FileNotFoundError(f"{name} not found!")
                
                if item == "xxmi" and path.name != "XXMI Launcher Config.json":
                    logging.error(f"Invalid XXMI file name: {path.name}")
                    raise FileNotFoundError("Please select XXMI Launcher Config.json")

        except Exception as e:
            return {
                "status": False,
                "message": str(e),
                "error_type": "system"
            }

        logging.info(f"All system files have been successfully verified!")
        return {
            "status": True
        }

    def inject_game(self, timeout: int = 30):
        if not all([hasattr(self, 'game_dir'), hasattr(self, 'exe_path')]):
            raise RuntimeError("Installation check must complete successfully before injection")
        
        ini_dest = self.game_dir / "ReShade.ini"
        if not ini_dest.is_file():
            logging.info(f"Copying ReShade.ini -> {ini_dest}")
            shutil.copy2(str(self.reshade_src), str(ini_dest))

        try:
            ini_file = configparser.ConfigParser()
            ini_file.optionxform = str
            ini_file.read(ini_dest)

            if get_filesystem(str(self.game_dir)) == "NTFS":
                link_shader = self.game_dir / self.shaders_src.name
                if not link_shader.exists():
                    link_shader.symlink_to(self.shaders_src, target_is_directory=True)
                    logging.info(f"Creating symbolic link: {link_shader} -> {self.shaders_src}")

                link_preset = self.game_dir / self.download_src.name
                if not link_preset.exists():
                    link_preset.symlink_to(self.download_src, target_is_directory=True)
                    logging.info(f"Creating symbolic link: {link_preset} -> {self.download_src}")

            required_keys = ["EffectSearchPaths", "TextureSearchPaths", "PresetPath"]
            path_flag = False
            
            for key in required_keys:
                value = ini_file.get("GENERAL", key, fallback="")
                if value.startswith("."):
                    path_flag = True
                    break

            if get_filesystem(str(self.game_dir)) != "NTFS" and path_flag:
                shaders = self.shaders_src / "Shaders"
                textures = self.shaders_src / "Textures"
                presets = self.download_src / "ReShadePreset.ini"

                ini_file.set("GENERAL", "EffectSearchPaths", str(shaders.resolve()))
                ini_file.set("GENERAL", "TextureSearchPaths", str(textures.resolve()))
                ini_file.set("GENERAL", "PresetPath", str(presets.resolve()))

                with open(ini_dest, "w") as file:
                    ini_file.write(file)

                logging.info("ReShade.ini configured successfully with absolute paths!")

        except Exception as e:
            logging.error(f"ReShade.ini configuration failed: {e}")
            return
            
        try:
            args = [str(self.exe_path)]
            if self.direct_enabled:
                args.append("-force-d3d11")

            subprocess.Popen(args, cwd=str(self.game_dir))
            logging.info(f"Waiting for {self.exe_path.name} to start...")

            start = time.time()
            process_name = None

            while time.time() - start < timeout:
                try:
                    process_name = Pymem(self.exe_path.name)
                    break
                except:
                    time.sleep(0.5)

            if process_name:
                if self.direct_enabled:
                    inject_dll_from_path(process_name.process_handle, str(self.reshade_dxvk))
                    logging.info(f"{self.reshade_dxvk.name} injected successfully!")
                else:
                    inject_dll_from_path(process_name.process_handle, str(self.reshade_dll))
                    logging.info(f"{self.reshade_dll.name} injected successfully!")
            else:
                raise RuntimeError(f"Game process {self.exe_path.name} did not start within {timeout} seconds")

        except Exception as e:
            logging.error(f"Injection process failed: {e}")
    
    def xxmi_integration(self, game_code):
        if not self.xxmi_enabled:
            logging.info(f"XXMI Integration inactive")
            return

        IMPORTER_MAP = {
            "genshin_impact": "GIMI",
            "honkai_star_rail": "SRMI",
            "wuthering_waves": "WWMI",
            "zenless_zone_zero": "ZZMI"
        }

        importer_key = IMPORTER_MAP.get(game_code)
        if not importer_key:
            logging.warning(f"No XXMI importer mapped for game {game_code}!")
            return None

        logging.info(f"Mapping for {game_code} successfully found!")

        try:
            with open(self.xxmi_src, "r+", encoding="utf-8") as f:
                config_data = json.load(f)

                importer_settings = config_data["Importers"][importer_key]["Importer"]
                importer_settings["extra_libraries_enabled"] = True
                importer_settings["extra_libraries"] = str(self.reshade_dll)

                f.seek(0)
                json.dump(config_data, f, indent=4)
                f.truncate()
            
            logging.info("XXMI configuration file updated successfully!")

        except Exception as e:
            logging.error(e)

    # Define Hash files
    def _sha256(self, file_source: Path, file_destination: Path) -> bool:
        source_hash = hashlib.sha256()
        with open(file_source, "rb") as file_1:
            while chunk := file_1.read(4096):
                source_hash.update(chunk)

        destination_hash = hashlib.sha256()
        with open(file_destination, "rb") as file_2:
            while chunk := file_2.read(4096):
                destination_hash.update(chunk)

        return source_hash.hexdigest() != destination_hash.hexdigest()
    
    def dxvk_support(self):
        if self.direct_enabled and not self.reshade_dxvk.is_file():
            try:
                shutil.copy2(self.reshade_dll, self.reshade_dxvk)
                logging.info(f"File {self.reshade_dxvk.name} created successfully!")
            except Exception as e:
                logging.error(f"Failed to copy: {e}")
                return
        else:
            logging.info(f"DirectX inactive")

    def addon_support(self):
        standard_folder = relative_path("resources/standard")
        addon_folder = relative_path("resources/addon")

        if self.reshade_enabled:
            source_file = addon_folder
            logging.info("Reshade Addon active")
        else:
            source_file = standard_folder
            logging.info("Reshade Addon inactive")

        dll_name = self.reshade_dll.name
        dll_path = source_file / dll_name
        dll_dest = relative_path("script/") / dll_name

        if not dll_path.is_file():
            logging.warning(f"Source file not found: {dll_path}")
            return

        if self._sha256(dll_path, dll_dest):
            try:
                shutil.copy2(dll_path, dll_dest)
                logging.info("File updated successfully!")
            except Exception as e:
                logging.error(f"Failed to copy {dll_name}: {e}")
        else:
            logging.info(f"{dll_name} is already up to date!")


#! Test functions
# config = load_config()
# setup_reshade = ReshadeSetup(config, "C:/Games/EndField Game", False)
# result_install = setup_reshade.verify_installation()
# result_system = setup_reshade.verify_system()
# setup_reshade.inject_game()
# setup_reshade.xxmi_integration(game_code)
# setup_reshade.addon_support()
# setup_reshade.dxvk_support()
# print(get_filesystem("None"))

# message_1 = result_install.get("message", "Tudo certo!")
# error_type_1 = result_install.get("error_type", "Tudo certo!")

# message_2 = result_system.get("message", "Tudo certo!")
# error_type_2 = result_system.get("error_type", "Tudo certo!")

# print(f"\nA Mensagem: {message_1}\nO Tipo de erro: {error_type_1}")
# print(f"\nA Mensagem: {message_2}\nO Tipo de erro: {error_type_2}")