"""Defines the preset management for the application"""

from tkinter import *
import customtkinter as ctk
import logging
from CTkListbox import *
from utils.config import save_config, load_metadata
from utils.path import resource_path
from utils.theme import ThemeManager
from .widgets import StyledToolTip

logging.basicConfig(level=logging.INFO)

class PresetsDialog(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict):
        super().__init__(master)
        self.transient(master)
        self.settings = settings_load
        self.metadata = load_metadata()
        self.selected_presets = []

        self.title("Select Preset")
        self.geometry("300x300")
        self.resizable(width=False, height=False)
        self.grab_set()

        def show_value(selected_option):
            logging.info(f"Select: {selected_option}")
            self.selected_presets = selected_option
        
        
        listbox = CTkListbox(self, font=ctk.CTkFont(family="Verdana", size=15), multiple_selection=True, command=show_value, highlight_color="#515151")
        listbox.pack(fill="both", expand=True, padx=10, pady=20)

        for p in self.metadata["presets"]:
            listbox.insert("end", p["name"])

        for i in range(listbox.size()):
            value = listbox.get(i)
            if value in self.settings["Packages"]["selected"]:
                listbox.activate(i)
        
        self.after(100, lambda: self.tooltips_items(listbox))
    
        self.save_button = ctk.CTkButton(self, text="Save", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=self.save_preset)
        self.save_button.configure(width=135, height=44, corner_radius=8, fg_color=ThemeManager.get_custom_color("secondary_color"))
        self.save_button.pack(pady=20)

    def tooltips_items(self, listbox):
        for widget in listbox.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                name = widget.cget("text")
                msg = self.get_tooltips(name)
                StyledToolTip(widget, msg, wraplength=300)

    def get_tooltips(self, name: str) -> str:
        preset_info = next(
            (p for p in self.metadata["presets"] if p.get("name") == name),
            None
        )
        if preset_info:
            return (
                f"📦 {name} (v{preset_info["version"]})\n"
                f"👤 {preset_info["author"]}\n"
                f"🔗 {preset_info["source"]}\n"
                f"{preset_info["description"] or "No description"}"
            )
        else:
            return f"{name}\n\nNo additional info available."

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