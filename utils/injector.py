"""Utils for all related to Reshade injection logic"""

import os, sys, shutil, subprocess, logging
from pathlib import Path
#from config import load_config

logging.basicConfig(level=logging.INFO)

def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = Path(__file__).parent.parent.resolve()

    return Path(base) / relative_path

# TODO: Criar um syslink para Presets e modificar o arquivo Reshade.ini
class ReshadeSetup():
    def __init__(self, code: dict, base: str, script: dict):
        self.base = base
        self.script = script

        self.game_base = Path(self.base)
        self.shaders_src = resource_path(script["shaders_dir"])
        self.ini_src = resource_path(script["reshade_file"])
        self.injector = resource_path(script["injector_file"])

        self.game_info = {
            "exe": code.get("exe", ""),
            "subpath": code.get("subpath", "")
        }
        self.game_dir = (self.game_base / self.game_info["subpath"]).resolve() if self.game_base else None
        self.exe_path = self.game_dir / self.game_info["exe"] if self.game_dir else None

    def verification(self):
        try:
            if not self.base or not self.game_base.is_dir():
                logging.error(f"Caminho do jogo não encontrado {self.game_base} ou game_folder é vazio!")
                raise FileNotFoundError("Game installation folder not found!")

            if not self.script.get("shaders_dir", "") or not self.shaders_src.is_dir():
                logging.error(f"Pasta de shaders não encontrado {self.shaders_src} ou shaders_dir é vazio!")
                raise FileNotFoundError("Shaders folder not found!")

            if not self.script.get("reshade_file", "") or not self.ini_src.is_file():
                logging.error(f"ReShade.ini não encontrado {self.ini_src} ou reshade_file é vazio!")
                raise FileNotFoundError("ReShade.ini file not found!")

            if not self.script.get("injector_file", "") or not self.injector.is_file():
                logging.error(f"Injector.exe não encontrado {self.injector} ou injector_file é vazio!")
                raise FileNotFoundError("Injector executable not found!")
            
            if not self.exe_path.is_file():
                logging.error(f"Executável não encontrado {self.exe_path}")
                raise FileNotFoundError("Game executable not found!")
            
        except Exception as e:
            return {
                "status": False,
                "message": str(e)
            }

        logging.info(f"All checks passed for {self.game_info['exe']} at {self.game_base}")
        return True

    def inject_game(self):
        link_dest = self.game_dir / Path(self.script["shaders_dir"]).name
        if not link_dest.exists():
            try:
                logging.info(f"Criando link simbólico: {link_dest} -> {resource_path(self.script["shaders_dir"])}")
                link_dest.symlink_to(resource_path(self.script["shaders_dir"]), target_is_directory=True)
            except Exception:
                logging.info("Falha ao criar o link simbólico")
        
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


#! Test functions
#config = load_config()
#setup_reshade = ReshadeSetup(config["Games"]["honkai_star_rail"], config["Games"]["honkai_star_rail"]["folder"], config["Script"])
#setup_reshade.verification()
#setup_reshade.inject_game()