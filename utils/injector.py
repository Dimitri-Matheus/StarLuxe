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
    def __init__(self, code: dict, base: str, script: dict, package: dict, xxmi_enabled: bool):
        self.code = code
        self.base = base
        self.script = script
        self.package = package
        self.xxmi_enabled = xxmi_enabled

        self.game_base = Path(self.base)
        self.shaders_src = resource_path(script["shaders_dir"])
        self.ini_src = resource_path(script["reshade_file"])
        self.injector = resource_path(script["injector_file"])
        self.xxmi_src = resource_path(script["xxmi_file"])
        self.reshade_dll = resource_path(script["reshade_dll"])
        self.download_src = resource_path(package["download_dir"])

    #TODO: Refatorar essa parte
    def verification(self):
        try:
            if not self.base or not self.game_base.is_dir():
                logging.error(f"Caminho do jogo não encontrado {self.game_base} ou game_folder é vazio!")
                raise FileNotFoundError("Game installation folder not found!")
            
            for code_games, cfg in self.code.items():
                exe_path = (self.game_base / cfg["subpath"] / cfg["exe"]).resolve()
                if exe_path.is_file():
                    self.selected_code = code_games
                    self.game_info = cfg
                    self.game_dir = exe_path.parent
                    self.exe_path = exe_path
                    break
            else:
                logging.error("Executável do jogo não encontrado em nenhuma configuração!")
                raise FileNotFoundError("Game executable not found!")

            if not self.script.get("shaders_dir", "") or not self.shaders_src.is_dir():
                logging.error(f"Pasta de shaders não encontrado {self.shaders_src} ou shaders_dir é vazio!")
                raise FileNotFoundError("Shaders folder not found!")

            if not self.script.get("reshade_file", "") or not self.ini_src.is_file():
                logging.error(f"ReShade.ini não encontrado {self.ini_src} ou reshade_file é vazio!")
                raise FileNotFoundError("ReShade.ini file not found!")

            if not self.script.get("injector_file", "") or not self.injector.is_file():
                logging.error(f"Injector.exe não encontrado {self.injector} ou injector_file é vazio!")
                raise FileNotFoundError("Injector executable not found!")

            if self.xxmi_enabled:
                if not self.script.get("xxmi_file", "") or not self.xxmi_src.is_file() or self.xxmi_src.name != "XXMI Launcher Config.json":
                    logging.error(f"XXMI Settings não encontrado {self.xxmi_src} ou xxmi_file é vazio!")
                    raise FileNotFoundError("XXMI Settings.json not found!")
            
        except Exception as e:
            return {
                "status": False,
                "message": str(e)
            }

        logging.info(f"All checks passed for {self.selected_code} at {self.game_base}")
        return {
            "status": True,
            "game_code": self.selected_code
        }

    def inject_game(self):
        self.game_info = {
            "exe": self.code.get("exe", ""),
            "subpath": self.code.get("subpath", "")
        }
        self.game_dir = (self.game_base / self.game_info["subpath"]).resolve()
        self.exe_path = self.game_dir / self.game_info["exe"] if self.game_dir else None

        link_shader = self.game_dir / Path(self.script["shaders_dir"]).name
        if not link_shader.exists():
            try:
                logging.info(f"Criando link simbólico: {link_shader} -> {resource_path(self.script["shaders_dir"])}")
                link_shader.symlink_to(resource_path(self.script["shaders_dir"]), target_is_directory=True)
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
            shutil.copy2(str(self.ini_src), str(ini_dest))
        
        # Run the Injector.exe
        logging.info("Injetando Reshade no jogo...")
        cmd_inject = [
            'powershell',
            '-Command',
            'Start-Process',
            f'-FilePath "{self.injector}"',
            f'-ArgumentList "{self.exe_path.name}"',
            '-WorkingDirectory', f'"{self.injector.parent}"',
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
            logging.warning(f"Standard mode (XXMI inactive)")
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
#setup_reshade = ReshadeSetup(config["Games"]["honkai_star_rail"], config["Games"]["honkai_star_rail"]["folder"], config["Script"], config["Packages"], config["Launcher"]["xxmi_feature_enabled"])
#setup_reshade.verification()
#setup_reshade.inject_game(game_code)
#setup_reshade.xxmi_integration()