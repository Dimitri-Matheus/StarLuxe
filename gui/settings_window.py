"""Defines the settings window for the application"""

from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import os, sys, logging
from CTkMessagebox import CTkMessagebox
from utils.config import save_config, delete_config
from utils.path import resource_path
from utils.injector import ReshadeSetup
from .widgets import StyledToolTip

logging.basicConfig(level=logging.INFO)

class GamePathFrame(ctk.CTkFrame):
    def __init__(self, master, settings):
        super().__init__(master)
        self.settings = settings
        self.path_entries = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        game_list = list(self.settings["Games"].items())
        for i, (game_id, game_data) in enumerate(game_list[:5]):
            name = game_data.get("display_name", game_id).replace("_", " ").title()

            game_path = ctk.CTkLabel(self, text=f"Path Game - {name}", font=ctk.CTkFont(size=18))
            game_path.grid(row=i*2, column=0, padx=20, pady=(15, 5), sticky="w")
            
            path_entry = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
            path_entry.configure(width=478, height=38, corner_radius=8)
            path_entry.grid(row=i*2 + 1, column=0, padx=20, pady=5, sticky="w")
            StyledToolTip(path_entry, message=(
                f"Path to folder with \"{name}.exe\" and related subfolders.\n"
                "🔍 Open HoYoPlay/WuWa Launcher → Game Settings → Game Directory."
            ))

            folder_path = self.settings["Games"][game_id].get("folder", "")
            if folder_path:
                path_entry.insert(0, folder_path)

            self.button = ctk.CTkButton(self, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda entry=path_entry: self.select_folder(entry))
            self.button.configure(width=123, height=38, corner_radius=8)
            self.button.grid(row=i*2 + 1, column=1, padx=(0, 20), pady=5, sticky="w")

            self.path_entries[game_id] = path_entry

    def select_folder(self, widget):
        foldername = filedialog.askdirectory(parent=self, title='Open folder', initialdir='/')
        if foldername:
            widget.delete(0, "end")
            widget.insert(0, foldername)


class AppFrame(ctk.CTkFrame):
    def __init__(self, master, settings: dict):
        super().__init__(master)
        self.settings = settings

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Load Variables
        self.xxmi_var = ctk.BooleanVar(value=self.settings["Launcher"]["xxmi_feature_enabled"])
        self.xxmi_file_path = self.settings["Script"]["xxmi_file"]
        self.addon_var = ctk.BooleanVar(value=self.settings["Launcher"]["reshade_feature_enabled"])
        self.update_var = ctk.BooleanVar(value=self.settings["Launcher"]["auto_check_update"])

        # Themes
        self.theme_subtitle = ctk.CTkLabel(self, text="Theme", font=ctk.CTkFont(size=18))
        self.theme_subtitle.grid(row=0, column=0, padx=25, pady=(15, 5), sticky="w")

        self.themes_option = ctk.CTkOptionMenu(self, values=["..."], font=ctk.CTkFont(family="Verdana", size=14), state="disabled")
        self.themes_option.configure(width=180, height=36)
        self.themes_option.grid(row=1, column=0, padx=25, pady=5, sticky="w")
        StyledToolTip(self.themes_option, message = "✦ Coming soon... ✦")

        # Integration/Features
        self.integration_subtitle = ctk.CTkLabel(self, text="Integration/Features", font=ctk.CTkFont(size=18))
        self.integration_subtitle.grid(row=2, column=0, padx=25, pady=(15, 5), sticky="w")
    
        self.switch_xxmi = ctk.CTkSwitch(self, text="XXMI", font=ctk.CTkFont(family="Verdana", size=15), onvalue=True, offvalue=False, command=lambda: self.switch_toogle_xxmi())
        self.switch_xxmi.configure(switch_width=36, switch_height=20, variable=self.xxmi_var)
        self.switch_xxmi.grid(row=3, column=0, padx=25, pady=(10, 5), sticky="w")
        StyledToolTip(self.switch_xxmi, message = (
            "Enabled: Integrates ReShade settings with the XXMI Launcher.\n"
            "Disabled: Leaves the XXMI Launcher unchanged.\n"
            "Requires the path to be set below."
        ))

        self.switch_addon = ctk.CTkSwitch(self, text="Reshade+", font=ctk.CTkFont(family="Verdana", size=15), onvalue=True, offvalue=False)
        self.switch_addon.configure(switch_width=36, switch_height=20, variable=self.addon_var)
        self.switch_addon.grid(row=4, column=0, padx=25, pady=(10, 5), sticky="w")
        StyledToolTip(self.switch_addon, message = (
            "Enabled: Switches to the enhanced ReShade build with Addon support.\n"
            "Disabled: Keeps the regular ReShade version active."
        ))

        self.switch_update = ctk.CTkSwitch(self, text="Check for updates", font=ctk.CTkFont(family="Verdana", size=15), onvalue=True, offvalue=False)
        self.switch_update.configure(switch_width=36, switch_height=20, variable=self.update_var)
        self.switch_update.grid(row=5, column=0, padx=25, pady=(10, 5), sticky="w")
        StyledToolTip(self.switch_update, message = (
            "Enabled: The app will automatically check for updates at startup.\n"
            "Disabled: The app will not check for updates automatically.\n"
            "Recommended to keep enabled for automatic updates."
        ))

        # XXMI Path
        self.config_file = ctk.CTkLabel(self, text="Configuration File", font=ctk.CTkFont(size=18))
        self.config_file.grid(row=6, column=0, padx=25, pady=(15, 5), sticky="w")

        self.xxmi_settings = ctk.CTkEntry(self, placeholder_text="C:/Path/to/XXMI Launcher Config.json", font=ctk.CTkFont(family="Verdana", size=14))
        self.xxmi_settings.configure(width=478, height=38, corner_radius=8, state="disabled", fg_color="#333333", border_color="#333333")
        self.xxmi_settings.grid(row=7, column=0, padx=25, pady=5, sticky="w")
        StyledToolTip(self.xxmi_settings, message = "Usually located in the \"XXMI Launcher folder\" or \"AppData\\Roaming\\XXMI Launcher\".")

        self.browser_button = ctk.CTkButton(self, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_file(self.xxmi_settings))
        self.browser_button.configure(width=123, height=38, corner_radius=8, state="disabled", fg_color="#222222")
        self.browser_button.grid(row=7, column=1, padx=(0, 20), pady=5, sticky="w")

        self.switch_toogle_xxmi()

    def switch_toogle_xxmi(self):
        if self.xxmi_var.get():
            self.xxmi_settings.configure(state="normal", fg_color="#515151", border_color="#515151")
            self.browser_button.configure(state="normal", fg_color="#4b9be5")
            file_path = self.settings["Script"].get("xxmi_file", "")
            if file_path:
                self.xxmi_settings.insert(0, file_path)
        else:
            self.xxmi_settings.configure(state="disabled", fg_color="#333333", border_color="#333333")
            self.browser_button.configure(state="disabled", fg_color="#222222")

    def select_file(self, widget):
        filename = filedialog.askopenfilename(parent=self, title="Open XXMI Settings", initialdir="/", defaultextension=".json", filetypes=[("JSON files","*.json"), ("All files", "*.*")])
        if filename:
            self.xxmi_file_path = filename
            widget.delete(0, "end")
            widget.insert(0, filename)


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

        scrollable_frame = ctk.CTkScrollableFrame(self)
        scrollable_frame.grid(row=0, column=0, sticky="nsew")
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(0, weight=1)

        # Sections
        self.game_section = ctk.CTkLabel(scrollable_frame, text="Game Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.game_section.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 5))
        
        self.game_content_frame = GamePathFrame(scrollable_frame, self.settings)
        self.game_content_frame.grid(row=1, column=0, padx=5, sticky="ew")

        self.app_section = ctk.CTkLabel(scrollable_frame, text="App Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.app_section.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 5))

        self.app_content_frame = AppFrame(scrollable_frame, self.settings)
        self.app_content_frame.grid(row=3, column=0, padx=5, sticky="ew")

        # Settings Manager
        button_content_frame = ctk.CTkFrame(self)
        button_content_frame.grid(row=1, column=0, padx=20, pady=(10, 18), sticky="ew")

        self.button_4 = ctk.CTkButton(button_content_frame, text="Save Config", font=ctk.CTkFont(size=18), command=lambda: self.save_path(self.game_content_frame.path_entries))
        self.button_4.configure(width=0, height=0, fg_color="transparent", hover_color="#4B9BE5")
        self.button_4.grid(row=0, column=0, sticky="w")

        self.button_5 = ctk.CTkButton(button_content_frame, text="Reset Config", font=ctk.CTkFont(size=18), command=lambda: self.reset_config())
        self.button_5.configure(width=0, height=0, fg_color="transparent", hover_color="#4B9BE5")
        self.button_5.grid(row=0, column=1, padx=15, sticky="w")


    def save_path(self, path_entries: dict[str, ctk.CTkEntry]):
        errors = []

        xxmi_enabled = self.app_content_frame.xxmi_var.get()
        reshade_enabled = self.app_content_frame.addon_var.get()
        update_enabled = self.app_content_frame.update_var.get()
        xxmi_config_path = self.app_content_frame.xxmi_settings.get().strip()

        self.settings["Script"]["xxmi_file"] = xxmi_config_path
        self.settings["Launcher"]["reshade_feature_enabled"] = reshade_enabled
        self.settings["Launcher"]["auto_check_update"] = update_enabled

        setup_system = ReshadeSetup(self.settings, "", xxmi_enabled)
        result_system = setup_system.verify_system()

        if not result_system["status"]:
            errors.append(result_system.get("message"))
        else:
            self.settings["Launcher"]["xxmi_feature_enabled"] = xxmi_enabled
        
        for game_code, entry in path_entries.items():
            game_path = entry.get().strip()
            if not game_path:
                continue

            setup_install = ReshadeSetup(self.settings, game_path, xxmi_enabled)
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