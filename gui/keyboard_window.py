"""Defines the keyboard Manager for the application"""

from tkinter import *
import customtkinter as ctk
import logging
from utils.path import resource_path
from gui.widgets import center_window

logger = logging.getLogger(__name__)

class KeyboardDialog(ctk.CTkToplevel):
    def __init__(self, master, key_var: ctk.StringVar, code_var: ctk.StringVar):
        super().__init__(master)
        self.transient(master)
        self.key_var = key_var
        self.code_var = code_var
        self.captured_key = None
        self.captured_key_code = None

        self.title("Select Key")
        center_window(self, master, 400, 200)
        self.resizable(width=False, height=False)
        self.grab_set()

        self.key_label = ctk.CTkLabel(self, text="Press a key...", font=ctk.CTkFont(size=28, weight="bold"))
        self.key_label.pack(fill="both", expand=True, padx=10, pady=20)

        self.key_label_info = ctk.CTkLabel(self, text=f"Current key: {self.key_var.get()}", font=ctk.CTkFont(size=18))
        self.key_label_info.pack(pady=(0, 5))

        self.confirm_button = ctk.CTkButton(self, text="Confirm", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), fg_color="#1DBD73", command=self.save_keybind)
        self.confirm_button.configure(width=123, height=38, corner_radius=8)
        self.confirm_button.pack(pady=20)

        self.bind("<KeyPress>", self.key_press)
        self.lift()
        self.focus_set()

    def key_press(self, event):
        if event.keysym == "Escape":
            self.destroy()
            return "break"

        self.captured_key = event.keysym
        self.captured_key_code = event.keycode
        self.key_label.configure(text=event.keysym)
        return "break"

    def save_keybind(self):
        if self.captured_key:
            self.key_var.set(self.captured_key)
            self.code_var.set(f"{self.captured_key_code},0,0,0")
            logger.info(f"Keybind selected: {self.captured_key} ({self.captured_key_code})")
        self.destroy()

    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets/icon/window_icon.ico'))