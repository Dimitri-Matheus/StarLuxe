"""Defines the preset management for the application"""

from tkinter import *
import customtkinter as ctk
import PIL.Image, PIL.ImageTk
import logging
from CTkListbox import *
# from CTkToolTip import *
from utils.config import save_config
from utils.path import resource_path

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

        #? Como adicionar um Preview do Preset
        # self.game_1 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\Galactic.png")), size=(128, 71))
        # CTkToolTip(listbox, message="", image=self.game_1, corner_radius=8, bg_color="#000001", fg_color="transparent", padding=(1.5, 1.5), alpha=0.95)

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
        super().wm_iconbitmap(resource_path('assets\\icon/window_icon.ico'))