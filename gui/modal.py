"""Defines modal windows for the application"""

from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import PIL.Image, PIL.ImageTk
import os, sys, logging
from CTkListbox import *
from CTkToolTip import *
from CTkMessagebox import CTkMessagebox
from utils.config import save_config, default
from utils.paths import resource_path
from utils.injector import ReshadeSetup

logging.basicConfig(level=logging.INFO)

class ModalPresets(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict):
        super().__init__(master)
        self.settings = settings_load

        self.title("Select Preset")
        self.geometry("300x300")
        self.resizable(width=False, height=False)

        self.selected_presets = []

        def show_value(selected_option):
            logging.info(f"Selecionado: {selected_option}")
            self.selected_presets = selected_option
        
        
        listbox = CTkListbox(self, font=ctk.CTkFont(family="Verdana", size=15), multiple_selection=True, command=show_value, highlight_color="#515151")
        listbox.pack(fill="both", expand=True, padx=10, pady=20)

        for p in self.settings["Packages"]["available"]:
            listbox.insert("end", p)

        for i in range(listbox.size()):
            value = listbox.get(i)
            if value in self.settings["Packages"]["selected"]:
                listbox.activate(i)
    
        self.save_button = ctk.CTkButton(self, text="Save", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=self.save_preset)
        self.save_button.configure(width=135, height=44, corner_radius=8, fg_color="#A884F3")
        self.save_button.pack(pady=20)

        #! Adicionar um Preview do Preset
        #self.game_1 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\image_1.png")), size=(128, 71))
        #CTkToolTip(listbox, message="", image=self.game_1, corner_radius=8, bg_color="#000001", fg_color="transparent", padding=(1.5, 1.5), alpha=0.95)

    def save_preset(self):
        if self.selected_presets:
            self.settings["Packages"]["selected"] = self.selected_presets
        else:
            self.settings["Packages"]["selected"] = ""
        
        save_config(self.settings)
        logging.info(f"Presets salvo: {self.settings["Packages"]["selected"]}")
        self.destroy()

    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/window_icon.ico'))


# Window #2
class ModalConfig(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict):
        super().__init__(master)
        self.settings = settings_load

        self.title("Settings")
        self.geometry("700x530")
        self.resizable(width=False, height=False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Path Entry #1
        self.text_1 = ctk.CTkLabel(self, text="Path Game - Genshin Impact", font=ctk.CTkFont(size=20))
        self.text_1.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.path_entry_1 = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14), )
        self.path_entry_1.configure(width=478, height=48, corner_radius=8)
        self.path_entry_1.grid(row=1, column=0, padx=20, pady=(5, 5), sticky="w")

        self.button_1 = ctk.CTkButton(self, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_folder(self.path_entry_1))
        self.button_1.configure(width=135, height=48, corner_radius=8)
        self.button_1.grid(row=1, column=1, padx=0, pady=(5, 5), sticky="w")

        # Path Entry #2
        self.text_2 = ctk.CTkLabel(self, text="Path Game - Honkai Star Rail", font=ctk.CTkFont(size=20))
        self.text_2.grid(row=2, column=0, padx=20, pady=(15, 5), sticky="w")

        self.path_entry_2 = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
        self.path_entry_2.configure(width=478, height=48, corner_radius=8)
        self.path_entry_2.grid(row=3, column=0, padx=20, pady=(5, 5), sticky="w")

        self.button_2 = ctk.CTkButton(self, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_folder(self.path_entry_2))
        self.button_2.configure(width=135, height=48, corner_radius=8)
        self.button_2.grid(row=3, column=1, padx=0, pady=(5, 5), sticky="w")

        # Path Entry #3
        self.text_3 = ctk.CTkLabel(self, text="Path Game - Wuthering Waves", font=ctk.CTkFont(size=20))
        self.text_3.grid(row=4, column=0, padx=20, pady=(15, 5), sticky="w")

        self.path_entry_3 = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
        self.path_entry_3.configure(width=478, height=48, corner_radius=8)
        self.path_entry_3.grid(row=5, column=0, padx=20, pady=(5, 5), sticky="w")

        self.button_3 = ctk.CTkButton(self, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_folder(self.path_entry_3))
        self.button_3.configure(width=135, height=48, corner_radius=8)
        self.button_3.grid(row=5, column=1, padx=0, pady=(5, 5), sticky="w")

        # Themes
        self.text_4 = ctk.CTkLabel(self, text="Themes", font=ctk.CTkFont(size=20))
        self.text_4.grid(row=6, column=0, padx=20, pady=(15, 5), sticky="w")

        self.themes_option = ctk.CTkOptionMenu(self, values=["Default"], font=ctk.CTkFont(family="Verdana", size=14), state="disabled")
        self.themes_option.configure(width=216, height=44)
        self.themes_option.grid(row=7, column=0, padx=20, pady=(5,5), sticky="w")

        # Settings Manager
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=8, column=0, padx=20, pady=(30, 5), sticky="w")

        self.button_4 = ctk.CTkButton(self.button_frame, text="Save Config", font=ctk.CTkFont(size=20), command=lambda: self.save_path(self.path_entries))
        self.button_4.configure(width=0, height=0, fg_color="transparent", hover_color="#4B9BE5")
        self.button_4.grid(row=0, column=0, sticky="w")

        self.button_5 = ctk.CTkButton(self.button_frame, text="Reset Config", font=ctk.CTkFont(size=20), command=lambda: self.reset_config())
        self.button_5.configure(width=0, height=0, fg_color="transparent", hover_color="#4B9BE5")
        self.button_5.grid(row=0, column=1, padx=15, sticky="w")

        self.path_entries = {
            "genshin_impact":self.path_entry_1,
            "honkai_star_rail":self.path_entry_2,
            "wuthering_waves":self.path_entry_3,
        }

        for code, entry in self.path_entries.items():
            entry.delete(0, "end")
            folder = self.settings["Games"][code]["folder"]
            if folder:
                entry.insert(0, folder)

    def select_folder(self, path_widget):
        foldername = filedialog.askdirectory(title='Open folder', initialdir='/')
        if foldername:
            msbox_info = CTkMessagebox(title="Selected Folder", message=f"{foldername}", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_info.title_label.configure(fg_color="gray14")
            path_widget.delete(0, "end")
            path_widget.insert(0, foldername)


    def save_path(self, path_entries: dict[str, ctk.CTkEntry]):
        errors = []
        
        for game_code, entry in path_entries.items():
            game_path = entry.get().strip()
            if not game_path:
                continue

            setup_reshade = ReshadeSetup(self.settings["Games"], game_path, self.settings["Script"], self.settings["Packages"])
            result = setup_reshade.verification()
            if result["status"] == True:
                game_code = result["game_code"]
                self.settings["Games"][game_code]["folder"] = game_path
            else:
                pretty_name = game_code.replace("_", " ").title()
                errors.append(f"{pretty_name}: {result.get('message','Unknown error')}")

        if errors:
            msbox_error = CTkMessagebox(title="Error", message="\n".join(errors), icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_error.title_label.configure(fg_color="gray14")
            return
        save_config(self.settings)
        self.destroy()

    def reset_config(self):
        save_config(default.copy())
        self.settings.clear()
        self.settings.update(default)
        self.destroy()
        logging.info("Configurações restauradas para o padrão!")
        python = sys.executable
        os.execv(python, [python] + sys.argv)
    
    
    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/window_icon.ico'))


# Window #3
class ModalStarted(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict):
        super().__init__(master)
        self.settings = settings_load

        self.title("Start Your Game")
        self.geometry("700x340")
        self.resizable(width=False, height=False)

        for col in range(3):
            self.grid_columnconfigure(col, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)

        self.game_1 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\icon/GI.png")), size=(128, 128))
        self.game_2 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\icon/HSR.png")), size=(128, 128))
        self.game_3 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\icon/WuWa.png")), size=(128, 128))

        self.button_1 = ctk.CTkButton(self, text="", image=self.game_1, command=lambda: self.open_game("genshin_impact"))
        self.button_1.configure(width=128, height=128, corner_radius=8, fg_color="transparent")
        self.button_1.grid(row=1, column=0, sticky="n", padx=10)

        self.button_2 = ctk.CTkButton(self, text="", image=self.game_2, command=lambda: self.open_game("honkai_star_rail"))
        self.button_2.configure(width=128, height=128, corner_radius=8, fg_color="transparent")
        self.button_2.grid(row=1, column=1, sticky="n", padx=10)

        self.button_3 = ctk.CTkButton(self, text="", image=self.game_3, command=lambda: self.open_game("wuthering_waves"))
        self.button_3.configure(width=128, height=128, corner_radius=8, fg_color="transparent")
        self.button_3.grid(row=1, column=2, sticky="n", padx=10)

        self.text_1 = ctk.CTkLabel(self, text="Genshin Impact", font=ctk.CTkFont(size=20))
        self.text_1.grid(row=2, column=0, sticky="n", pady=(10, 0))

        self.text_2 = ctk.CTkLabel(self, text="Honkai Star Rail", font=ctk.CTkFont(size=20))
        self.text_2.grid(row=2, column=1, sticky="n", pady=(10, 0))

        self.text_3 = ctk.CTkLabel(self, text="Wuthering Waves", font=ctk.CTkFont(size=20))
        self.text_3.grid(row=2, column=2, sticky="n", pady=(10, 0))

    def open_game(self, game_code):
        game_data = self.settings["Games"][game_code]
        folder = game_data.get("folder", "").strip()

        if not folder:
            msbox_error = CTkMessagebox(title="Info", message="Please set the game folder first in Settings", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_error.title_label.configure(fg_color="gray14")
            return

        self.settings["Launcher"]["last_played_game"] = game_code
        save_config(self.settings)

        reshade = ReshadeSetup(game_data, folder, self.settings["Script"], self.settings["Packages"])
        reshade.inject_game()
        self.destroy()

    #! Otimizar o uso do ícone nas janelas
    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/window_icon.ico'))