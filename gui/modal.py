"""Defines modal windows for the application"""

from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import PIL.Image, PIL.ImageTk
import os, sys, logging
from CTkListbox import *
#from CTkToolTip import *
from CTkMessagebox import CTkMessagebox
from utils.config import save_config, default
from utils.path import resource_path
from utils.injector import ReshadeSetup

logging.basicConfig(level=logging.INFO)

#TODO: Otimizar o uso do ícone nas janelas
class ModalPresets(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict):
        super().__init__(master)
        self.settings = settings_load

        self.title("Select Preset")
        self.geometry("300x300")
        self.resizable(width=False, height=False)
        self.attributes("-topmost",True)

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

        #? Como adicionar um Preview do Preset
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
        self.geometry("700x550")
        self.resizable(width=False, height=False)
        self.attributes("-topmost",True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)

        game_configs = [
            ("genshin_impact",   "Genshin Impact"),
            ("honkai_star_rail", "Honkai Star Rail"),
            ("wuthering_waves",  "Wuthering Waves")
        ]

        self.path_entries = {}
        self.xxmi_file_path = ""
        r = 0

        # Title #1
        self.title_1 = ctk.CTkLabel(self.scrollable_frame, text="Game Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_1.grid(row=r, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 5)); r += 1

        for game_id, game_name in game_configs:
            self.text_1 = ctk.CTkLabel(self.scrollable_frame, text=f"Path Game - {game_name}", font=ctk.CTkFont(size=18))
            self.text_1.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1
            
            self.path_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14), )
            self.path_entry.configure(width=478, height=38, corner_radius=8)
            self.path_entry.grid(row=r, column=0, padx=25, pady=5, sticky="w")

            folder_path = self.settings["Games"][game_id].get("folder", "")
            if folder_path:
                self.path_entry.insert(0, folder_path)

            self.button = ctk.CTkButton(self.scrollable_frame, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda entry=self.path_entry: self.select_folder(entry))
            self.button.configure(width=123, height=38, corner_radius=8)
            self.button.grid(row=r, column=1, padx=(0, 20), pady=5, sticky="w"); r += 1

            self.path_entries[game_id] = self.path_entry

        # Title #2
        self.title_2 = ctk.CTkLabel(self.scrollable_frame, text="App Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_2.grid(row=r, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 5)); r += 1

        # Themes
        self.text_2 = ctk.CTkLabel(self.scrollable_frame, text="Theme", font=ctk.CTkFont(size=18))
        self.text_2.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1

        self.themes_option = ctk.CTkOptionMenu(self.scrollable_frame, values=["..."], font=ctk.CTkFont(family="Verdana", size=14), state="disabled")
        self.themes_option.configure(width=180, height=36)
        self.themes_option.grid(row=r, column=0, padx=25, pady=5, sticky="w"); r += 1

        self.text_3 = ctk.CTkLabel(self.scrollable_frame, text="Integration", font=ctk.CTkFont(size=18))
        self.text_3.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1

        # Integration
        self.switch_var = ctk.BooleanVar(value=self.settings["Launcher"]["xxmi_feature_enabled"])
        self.xxmi_file_path = self.settings["Script"]["xxmi_file"]
        
        self.switch = ctk.CTkSwitch(self.scrollable_frame, text="XXMI", font=ctk.CTkFont(family="Verdana", size=15), onvalue=True, offvalue=False, command=lambda: self.switch_toogle())
        self.switch.configure(switch_width=36, switch_height=20, variable=self.switch_var)
        self.switch.grid(row=r, column=0, padx=25, pady=(10, 5), sticky="w"); r += 1

        self.switch_2 = ctk.CTkSwitch(self.scrollable_frame, text="Reshade+", font=ctk.CTkFont(family="Verdana", size=15), onvalue=True, offvalue=False)
        self.switch_2.configure(switch_width=36, switch_height=20)
        self.switch_2.grid(row=r, column=0, padx=25, pady=(10, 5), sticky="w"); r += 1

        # XXMI Path
        self.text_4 = ctk.CTkLabel(self.scrollable_frame, text="XXMI Settings", font=ctk.CTkFont(size=18))
        self.text_4.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1

        self.settings_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="C:/Path/to/config.json", font=ctk.CTkFont(family="Verdana", size=14))
        self.settings_entry.configure(width=478, height=38, corner_radius=8, state="disabled", fg_color="#333333", border_color="#333333")
        self.settings_entry.grid(row=r, column=0, padx=25, pady=5, sticky="w"); r + 1

        self.browser_button = ctk.CTkButton(self.scrollable_frame, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_file(self.settings_entry))
        self.browser_button.configure(width=123, height=38, corner_radius=8, state="disabled", fg_color="#222222")
        self.browser_button.grid(row=r, column=1, padx=(0, 20), pady=5, sticky="w"); r += 1

        self.switch_toogle()

        # Settings Manager
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=r, column=0, padx=20, pady=(10, 18), sticky="ew")

        self.button_4 = ctk.CTkButton(self.button_frame, text="Save Config", font=ctk.CTkFont(size=18), command=lambda: self.save_path(self.path_entries))
        self.button_4.configure(width=0, height=0, fg_color="transparent", hover_color="#4B9BE5")
        self.button_4.grid(row=0, column=0, sticky="w")

        self.button_5 = ctk.CTkButton(self.button_frame, text="Reset Config", font=ctk.CTkFont(size=18), command=lambda: self.reset_config())
        self.button_5.configure(width=0, height=0, fg_color="transparent", hover_color="#4B9BE5")
        self.button_5.grid(row=0, column=1, padx=15, sticky="w")

    def switch_toogle(self):
        if self.switch_var.get():
            self.settings_entry.configure(state="normal", fg_color="#515151", border_color="#515151")
            self.browser_button.configure(state="normal", fg_color="#4b9be5")
            file_path = self.settings["Script"].get("xxmi_file", "")
            if file_path:
                self.settings_entry.insert(0, file_path)
        else:
            self.settings_entry.configure(state="disabled", fg_color="#333333", border_color="#333333")
            self.browser_button.configure(state="disabled", fg_color="#222222")


    def select_folder(self, widget):
        foldername = filedialog.askdirectory(parent=self, title='Open folder', initialdir='/')
        if foldername:
            widget.delete(0, "end")
            widget.insert(0, foldername)


    def select_file(self, widget):
        filename = filedialog.askopenfilename(parent=self, title="Open XXMI Settings", initialdir="/", defaultextension=".json", filetypes=[("JSON files","*.json"), ("All files", "*.*")])
        if filename:
            self.xxmi_file_path = filename
            widget.delete(0, "end")
            widget.insert(0, filename)


    def save_path(self, path_entries: dict[str, ctk.CTkEntry]):
        errors = []

        xxmi_config_path = self.settings_entry.get().strip()
        self.settings["Script"]["xxmi_file"] = xxmi_config_path

        setup_system = ReshadeSetup(self.settings, "", self.switch_var.get())
        result_system = setup_system.verify_system()

        if not result_system["status"]:
            errors.append(result_system.get("message"))
        else:
            self.settings["Launcher"]["xxmi_feature_enabled"] = self.switch_var.get()
        
        for game_code, entry in path_entries.items():
            game_path = entry.get().strip()
            if not game_path:
                continue

            setup_install = ReshadeSetup(self.settings, game_path, self.switch_var.get())
            result_install = setup_install.verify_installation()
            
            if not result_install["status"]:
                name = game_code.replace("_", " ").title()
                errors.append(result_install.get("message").replace("Game", name))
            else:
                game_code = result_install["game_code"]
                self.settings["Games"][game_code]["folder"] = game_path
    
        errors = list(dict.fromkeys(errors))
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
        self.attributes("-topmost",True)

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

        setup_reshade = ReshadeSetup(self.settings, folder, self.settings["Launcher"]["xxmi_feature_enabled"])
        setup_reshade.verify_installation()
        setup_reshade.xxmi_integration(game_code)
        setup_reshade.inject_game()
        self.destroy()

    
    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/window_icon.ico'))