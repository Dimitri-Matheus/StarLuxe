"""Defines the settings window for the application"""

from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import os, sys, logging
# from CTkToolTip import *
from CTkMessagebox import CTkMessagebox
from utils.config import save_config, delete_config
from utils.path import resource_path
from utils.injector import ReshadeSetup

logging.basicConfig(level=logging.INFO)

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict, controller):
        super().__init__(master)
        self.transient(master)
        self.controller = controller
        self.settings = settings_load

        self.title("Settings")
        self.geometry("700x550")
        self.resizable(width=False, height=False)
        self.grab_set()

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=0)

        self.path_entries = {}
        self.xxmi_file_path = ""
        self.game_list = list(self.settings["Games"].items())
        r = 0

        # Title #1
        self.title_1 = ctk.CTkLabel(self.scrollable_frame, text="Game Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_1.grid(row=r, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 5)); r += 1

        for game_id, game_data in self.game_list[:4]:
            name = game_data.get("display_name", game_id).replace("_", " ").title()

            self.text_1 = ctk.CTkLabel(self.scrollable_frame, text=f"Path Game - {name}", font=ctk.CTkFont(size=18))
            self.text_1.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1
            
            self.path_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
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
        self.title_2.grid(row=r, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 5)); r += 1

        # Themes
        self.text_2 = ctk.CTkLabel(self.scrollable_frame, text="Theme", font=ctk.CTkFont(size=18))
        self.text_2.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1

        self.themes_option = ctk.CTkOptionMenu(self.scrollable_frame, values=["..."], font=ctk.CTkFont(family="Verdana", size=14), state="disabled")
        self.themes_option.configure(width=180, height=36)
        self.themes_option.grid(row=r, column=0, padx=25, pady=5, sticky="w"); r += 1

        self.text_3 = ctk.CTkLabel(self.scrollable_frame, text="Integration", font=ctk.CTkFont(size=18))
        self.text_3.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1

        # Load Variables
        self.xxmi_var = ctk.BooleanVar(value=self.settings["Launcher"]["xxmi_feature_enabled"])
        self.xxmi_file_path = self.settings["Script"]["xxmi_file"]
        self.addon_var = ctk.BooleanVar(value=self.settings["Launcher"]["reshade_feature_enabled"])
        
        # Integration
        self.switch_xxmi = ctk.CTkSwitch(self.scrollable_frame, text="XXMI", font=ctk.CTkFont(family="Verdana", size=15), onvalue=True, offvalue=False, command=lambda: self.switch_toogle_xxmi())
        self.switch_xxmi.configure(switch_width=36, switch_height=20, variable=self.xxmi_var)
        self.switch_xxmi.grid(row=r, column=0, padx=25, pady=(10, 5), sticky="w"); r += 1

        self.switch_addon = ctk.CTkSwitch(self.scrollable_frame, text="Reshade+", font=ctk.CTkFont(family="Verdana", size=15), onvalue=True, offvalue=False)
        self.switch_addon.configure(switch_width=36, switch_height=20, variable=self.addon_var)
        self.switch_addon.grid(row=r, column=0, padx=25, pady=(10, 5), sticky="w"); r += 1

        #? Como adicionar um Preview do Preset
        # CTkToolTip(self.switch_addon, message="Scroll down and enable the XXMI feature. Then click the Browser button", corner_radius=8, bg_color="#DCDCDC", fg_color="transparent", padding=(1.5, 1.5), alpha=0.95, font=ctk.CTkFont(family="Verdana", size=14), border_color="gray20", border_width=1, justify="center", text_color="#000001")

        # XXMI Path
        self.text_4 = ctk.CTkLabel(self.scrollable_frame, text="Configuration File", font=ctk.CTkFont(size=18))
        self.text_4.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1

        self.settings_entry = ctk.CTkEntry(self.scrollable_frame, placeholder_text="C:/Path/to/XXMI Launcher Config.json", font=ctk.CTkFont(family="Verdana", size=14))
        self.settings_entry.configure(width=478, height=38, corner_radius=8, state="disabled", fg_color="#333333", border_color="#333333")
        self.settings_entry.grid(row=r, column=0, padx=25, pady=5, sticky="w"); r + 1

        self.browser_button = ctk.CTkButton(self.scrollable_frame, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_file(self.settings_entry))
        self.browser_button.configure(width=123, height=38, corner_radius=8, state="disabled", fg_color="#222222")
        self.browser_button.grid(row=r, column=1, padx=(0, 20), pady=5, sticky="w"); r += 1

        self.switch_toogle_xxmi()

        # Settings Manager
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=r, column=0, padx=20, pady=(10, 18), sticky="ew")

        self.button_4 = ctk.CTkButton(self.button_frame, text="Save Config", font=ctk.CTkFont(size=18), command=lambda: self.save_path(self.path_entries))
        self.button_4.configure(width=0, height=0, fg_color="transparent", hover_color="#4B9BE5")
        self.button_4.grid(row=0, column=0, sticky="w")

        self.button_5 = ctk.CTkButton(self.button_frame, text="Reset Config", font=ctk.CTkFont(size=18), command=lambda: self.reset_config())
        self.button_5.configure(width=0, height=0, fg_color="transparent", hover_color="#4B9BE5")
        self.button_5.grid(row=0, column=1, padx=15, sticky="w")

    def switch_toogle_xxmi(self):
        if self.xxmi_var.get():
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
        self.settings["Launcher"]["reshade_feature_enabled"] = self.addon_var.get()

        setup_system = ReshadeSetup(self.settings, "", self.xxmi_var.get())
        result_system = setup_system.verify_system()

        if not result_system["status"]:
            errors.append(result_system.get("message"))
        else:
            self.settings["Launcher"]["xxmi_feature_enabled"] = self.xxmi_var.get()
        
        for game_code, entry in path_entries.items():
            game_path = entry.get().strip()
            if not game_path:
                continue

            setup_install = ReshadeSetup(self.settings, game_path, self.xxmi_var.get())
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
        msbox_warning = CTkMessagebox(title="Warning", message="Restore defaults and restart the app?", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0, option_1="Ok", option_2="Cancel")
        msbox_warning.title_label.configure(fg_color="gray14")

        if msbox_warning.get() == "Ok":
            delete_config()
            logging.info("Settings have been restored to default!")
            try:
                exec_path = sys.argv[0]
                os.startfile(exec_path)
                self.controller.destroy()
            except Exception as e:
                logging.error(f"Failed to restart the application: {e}")
    
    
    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets/icon/window_icon.ico'))