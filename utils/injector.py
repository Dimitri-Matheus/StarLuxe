"""Utils for all related to Reshade injection logic"""

import os, sys, shutil, subprocess, logging, json
from pathlib import Path
#from config import load_config

logging.basicConfig(level=logging.INFO)

def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = Path(__file__).parent.parent.resolve()

    return Path(base) / relative_path


class ReshadeSetup():
    def __init__(self, settings: dict, game_path: str, xxmi_enabled: bool):
        self.settings = settings
        self.game_base = game_path
        self.game_path = Path(self.game_base)

        self.game_config = self.settings.get("Games", {})
        self.script_config = self.settings.get("Script", {})
        self.package_config = self.settings.get("Packages", {})
        self.xxmi_enabled = xxmi_enabled

        self.reshade_src = resource_path(self.script_config.get("reshade_file"))
        self.injector_src = resource_path(self.script_config.get("injector_file"))
        self.shaders_src = resource_path(self.script_config.get("shaders_dir"))
        self.reshade_dll = resource_path(self.script_config.get("reshade_dll"))
        self.xxmi_src = resource_path(self.script_config.get("xxmi_file"))
        self.download_src = resource_path(self.package_config.get("download_dir"))

    def verify_installation(self):
        try:
            if not self.game_base or not self.game_path.is_dir():
                logging.error(f"Caminho vazio ou não encontrado: {self.game_path}")
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
                logging.error("Nenhum executável válido encontrado nas configurações")
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
        try:
            if not self.reshade_src.is_file():
                logging.error(f"ReShade.ini não encontrado: {self.reshade_src}")
                raise FileNotFoundError("ReShade.ini file not found!")

            if not self.injector_src.is_file():
                logging.error(f"Injector.exe não encontrado: {self.injector_src}")
                raise FileNotFoundError("Injector executable not found!")

            if not self.shaders_src.is_dir():
                logging.error(f"Pasta de shaders não encontrada: {self.shaders_src}")
                raise FileNotFoundError("Shaders folder not found!")

            if not self.reshade_dll.is_file():
                logging.error(f"ReShade64.dll não encontrado: {self.reshade_dll}")
                raise FileNotFoundError("ReShade64.dll file not found!")
            
            if self.xxmi_enabled:
                if not self.xxmi_src.is_file() or self.xxmi_src.name != "XXMI Launcher Config.json":
                    logging.error(f"Caminho de XXMI Settings vazio ou não encontrado: {self.xxmi_src}")
                    raise FileNotFoundError("XXMI Settings not found!")

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

    def inject_game(self):
        link_shader = self.game_dir / self.shaders_src.name
        if not link_shader.exists():
            try:
                logging.info(f"Criando link simbólico: {link_shader} -> {self.shaders_src}")
                link_shader.symlink_to(self.shaders_src, target_is_directory=True)
            except Exception:
                logging.info("Falha ao criar o link simbólico!")

        link_preset = self.game_dir / self.download_src.name
        if not link_preset.exists():
            try:
                logging.info(f"Criando link simbólico: {link_preset} -> {self.download_src}")
                link_preset.symlink_to(self.download_src, target_is_directory=True)
            except Exception:
                logging.info("Falha ao criar o link simbólico!")
        
        ini_dest = self.game_dir / "ReShade.ini"
        if not ini_dest.is_file():
            logging.info(f"Copiando ReShade.ini -> {ini_dest}")
            shutil.copy2(str(self.reshade_src), str(ini_dest))
        
        # Run the Injector.exe
        logging.info("Injetando Reshade no jogo...")
        cmd_inject = [
            'powershell',
            '-Command',
            'Start-Process',
            f'-FilePath "{self.injector_src}"',
            f'-ArgumentList "{self.exe_path.name}"',
            '-WorkingDirectory', f'"{self.injector_src.parent}"',
            '-Verb RunAs'
        ]
        subprocess.run(cmd_inject, shell=False)

        # Run the game
        logging.info("Iniciando o jogo...")
        cmd_play = [
            'powershell',
            '-Command',
            f'Start-Process -FilePath "{self.exe_path}" -WorkingDirectory "{self.game_dir}" -Verb RunAs'
        ]
        subprocess.run(cmd_play, shell=False)

    
    def xxmi_integration(self, game_code):
        if not self.xxmi_enabled:
            logging.info(f"Standard mode (XXMI inactive)")
            return

        IMPORTER_MAP = {
            "genshin_impact": "GIMI",
            "honkai_star_rail": "SRMI",
            "wuthering_waves": "WWMI"
        }

        importer_key = IMPORTER_MAP.get(game_code)
        if not importer_key:
            logging.warning(f"O jogo {game_code} não possui um importador XXMI mapeado!")
            return None

        logging.info(f"Mapeamento para {game_code} encontrado com sucesso!")

        try:
            with open(self.xxmi_src, "r+", encoding="utf-8") as f:
                config_data = json.load(f)

                importer_settings = config_data["Importers"][importer_key]["Importer"]
                importer_settings["extra_libraries_enabled"] = True
                importer_settings["extra_libraries"] = str(self.reshade_dll)

                f.seek(0)
                json.dump(config_data, f, indent=4)
                f.truncate()
            
            logging.info("Arquivo de config do XXMI atualizado com sucesso!")

        except Exception as e:
            logging.error(e)



#! Test functions
#config = load_config()
# setup_reshade = ReshadeSetup(config, "", False)
# result_install = setup_reshade.verify_installation()
# result_system = setup_reshade.verify_system()

# message_1 = result_install.get("message", "Tudo certo!")
# error_type_1 = result_install.get("error_type", "Tudo certo!")

# message_2 = result_system.get("message", "Tudo certo!")
# error_type_2 = result_system.get("error_type", "Tudo certo!")

# print(f"\nA Mensagem: {message_1}\nO Tipo de erro: {error_type_1}")
# print(f"\nA Mensagem: {message_2}\nO Tipo de erro: {error_type_2}")

#setup_reshade.inject_game()
#setup_reshade.xxmi_integration(game_code)