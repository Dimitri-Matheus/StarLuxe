"""Defines the preset management for the application"""

from tkinter import *
import customtkinter as ctk
import logging
from CTkListbox import *
from utils.config import save_config
from utils.path import resource_path
from .widgets import StyledToolTip

logging.basicConfig(level=logging.INFO)

class PresetsDialog(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict):
        super().__init__(master)
        self.transient(master)
        self.settings = settings_load

        self.title("Select Preset")
        self.geometry("300x300")
        self.resizable(width=False, height=False)
        self.grab_set()

        self.selected_presets = []

        def show_value(selected_option):
            logging.info(f"Select: {selected_option}")
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

        StyledToolTip(listbox, message=(
            "Select the ReShade presets you want to download.\n"
            "You can choose multiple items."
        ))

    def save_preset(self):
        if self.selected_presets:
            self.settings["Packages"]["selected"] = self.selected_presets
        else:
            self.settings["Packages"]["selected"] = ""
        
        save_config(self.settings)
        logging.info(f"Saved preset: {self.settings["Packages"]["selected"]}")
        self.destroy()

    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets/icon/window_icon.ico'))