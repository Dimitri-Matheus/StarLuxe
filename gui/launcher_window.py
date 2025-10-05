"""Defines the main game selection for the application"""

from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import PIL.Image, PIL.ImageTk
from pathlib import Path
import logging, re
from CTkMessagebox import CTkMessagebox
from utils.config import save_config
from utils.path import resource_path
from utils.injector import ReshadeSetup

logging.basicConfig(level=logging.INFO)

class LauncherDialog(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict):
        super().__init__(master)
        self.transient(master)
        self.settings = settings_load
        self.current_page = None

        self.title("Start Your Game")
        self.geometry("700x340")
        self.resizable(width=False, height=False)
        self.grab_set()

        self.prev_icon = ctk.CTkImage(PIL.Image.open(resource_path("assets\\icon/back_icon.png")), size=(32, 32))
        self.next_icon = ctk.CTkImage(PIL.Image.open(resource_path("assets\\icon/next_icon.png")), size=(32, 32))

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Container
        self.container_frame = ctk.CTkFrame(self)
        self.container_frame.grid(row=0, column=0, sticky="nsew")
        self.container_frame.grid_rowconfigure(0, weight=1)
        self.container_frame.grid_columnconfigure(0, weight=1)

        # Buttons Frame
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.grid(row=1, column=0, pady=(10, 30), sticky="ew")

        self.nav_frame.grid_columnconfigure((0, 3), weight=1)

        self.prev_button = ctk.CTkButton(self.nav_frame, text="", image=self.prev_icon, command=lambda: self.show_page("GamePage1"))
        self.prev_button.configure(width=0, height=0, fg_color="transparent")
        self.prev_button.grid(row=0, column=1, padx=10)

        self.next_button = ctk.CTkButton(self.nav_frame, text="", image=self.next_icon, command=lambda: self.show_page("GamePage2"))
        self.next_button.configure(width=0, height=0, fg_color="transparent")
        self.next_button.grid(row=0, column=2, padx=10)

        # Controller the pages
        self.pages = {}
        for PageClass in (GamePage1, GamePage2):
            page = PageClass(self.container_frame, self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("GamePage1")

    # Manager the pages
    def show_page(self, page_name: str):
        if self.current_page == page_name:
            logging.info(f"{page_name} is already active")
            return
        page = self.pages[page_name]
        page.tkraise()
        self.current_page = page_name
        logging.info(f"Navigated to {page_name}")

    def refresh_page(self):
        logging.info("Refreshing all pages...")
        for page in self.pages.values():
            if hasattr(page, "page_update"):
                page.page_update()

    def open_game(self, game_code):
        game_data = self.settings["Games"][game_code]
        folder = game_data.get("folder", "").strip()

        if not folder:
            msbox_error = CTkMessagebox(title="Info", message="Please set the game folder first in Settings", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_error.title_label.configure(fg_color="gray14")
            return

        self.settings["Launcher"]["last_played_game"] = game_code
        save_config(self.settings)

        setup = ReshadeSetup(self.settings, folder, self.settings["Launcher"]["xxmi_feature_enabled"])
        setup.verify_installation()
        setup.addon_support()
        setup.xxmi_integration(game_code)
        setup.inject_game()
        self.destroy()

    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/window_icon.ico'))


class GamePage1(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure((0, 4), weight=1)
        self.grid_columnconfigure((1, 2, 3), weight=0)
        self.grid_rowconfigure((0, 3), weight=1)

        game_list  = list(self.controller.settings["Games"].items())
        for j, (game_id, game_data) in enumerate(game_list[:3], start=1):
            name = game_data.get("display_name", game_id).replace("_", " ").title()
            img = ctk.CTkImage(PIL.Image.open(resource_path(game_data.get("icon_path", ""))), size=(128, 128))

            self.button = ctk.CTkButton(self, text="", image=img, command=lambda gid=game_id: self.controller.open_game(gid))
            self.button.configure(width=128, height=128, corner_radius=8, fg_color="transparent")
            self.button.grid(row=1, column=j, padx=20, sticky="n")

            self.text = ctk.CTkLabel(self, text=f"{name}", font=ctk.CTkFont(size=20))
            self.text.grid(row=2, column=j, pady=(10, 0), sticky="n")


class GamePage2(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.modal = None
        self.page_update()

    def page_update(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_columnconfigure((0, 4), weight=1)
        self.grid_columnconfigure((1, 2, 3), weight=0)
        self.grid_rowconfigure((0, 3), weight=1)

        game_list = list(self.controller.settings["Games"].items())
        for j, (game_id, game_data) in enumerate(game_list[3:], start=1):
            name = game_data.get("display_name", game_id).replace("_", " ").title()
            img = ctk.CTkImage(PIL.Image.open(resource_path(game_data.get("icon_path", ""))), size=(128, 128))

            if "slot" in game_id.lower():
                button_command = lambda gid=game_id: self.open_modal(gid)
            else:
                button_command = lambda gid=game_id: self.controller.open_game(gid)

            self.button = ctk.CTkButton(self, text="", image=img, command=button_command)
            self.button.configure(width=128, height=128, corner_radius=8, fg_color="transparent")
            self.button.grid(row=1, column=j, padx=20, sticky="n")

            self.text = ctk.CTkLabel(self, text=f"{name}", font=ctk.CTkFont(size=20))
            self.text.grid(row=2, column=j, pady=(10, 0), sticky="n")

    def open_modal(self, slot_name: str):
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = InputGame(self, self.controller.settings, slot_name, callback=self.controller.refresh_page)
        else:
            self.modal.focus()

class InputGame(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict, slot_name: str, callback):
        super().__init__(master)
        self.transient(master)
        self.settings = settings_load
        self.slot_name = slot_name
        self.callback = callback

        self.title("New Game")
        self.geometry("520x480")
        self.resizable(width=False, height=False)
        self.grab_set()
        r = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Container 1
        self.icon_image = resource_path("assets\\icon/empty.png")
        self.icon = ctk.CTkImage(PIL.Image.open(self.icon_image), size=(128, 128))
        self.icon_preview = ctk.CTkLabel(self, text="", image=self.icon)
        self.icon_preview.grid(row=r, column=0, columnspan=2, pady=30, sticky="ew"); r += 1

        self.text_1 = ctk.CTkLabel(self, text="Display name", font=ctk.CTkFont(size=18))
        self.text_1.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1

        self.name_input = ctk.CTkEntry(self, placeholder_text="Enter game name", font=ctk.CTkFont(family="Verdana", size=14))
        self.name_input.configure(width=478, height=38, corner_radius=8)
        self.name_input.grid(row=r, column=0, padx=25, pady=5, sticky="ew")

        self.icon_button = ctk.CTkButton(self, text="Choose Icon", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_icon())
        self.icon_button.configure(width=123, height=38, corner_radius=8)
        self.icon_button.grid(row=r, column=1, padx=(0, 20), pady=5, sticky="e"); r += 1

        self.text_2 = ctk.CTkLabel(self, text="Game Executable", font=ctk.CTkFont(size=18))
        self.text_2.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1

        self.path_entry = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
        self.path_entry.configure(width=478, height=38, corner_radius=8)
        self.path_entry.grid(row=r, column=0, padx=25, pady=5, sticky="ew")

        self.browser_button = ctk.CTkButton(self, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_file(self.path_entry, self.name_input))
        self.browser_button.configure(width=123, height=38, corner_radius=8)
        self.browser_button.grid(row=r, column=1, padx=(0, 20), pady=5, sticky="e"); r += 1

        # Container 2
        button_container = ctk.CTkFrame(self, fg_color="transparent")
        button_container.grid(row=r, column=0, columnspan=2, pady=20, sticky="ew")
        button_container.grid_columnconfigure((0, 3), weight=1)
        button_container.grid_columnconfigure((1, 2), weight=0)

        self.button_4 = ctk.CTkButton(button_container, text="Ok", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.save_game())
        self.button_4.configure(width=135, height=38, corner_radius=8, fg_color="#1DBD73")
        self.button_4.grid(row=0, column=1, padx=10, pady=15)

        self.button_5 = ctk.CTkButton(button_container, text="Cancel", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.destroy())
        self.button_5.configure(width=135, height=38, corner_radius=8, fg_color="#E73B3C")
        self.button_5.grid(row=0, column=2, padx=10, pady=15)

    def select_file(self, path, name):
        filename = filedialog.askopenfilename(parent=self, title="Select Game Executable", initialdir="/", defaultextension=".exe", filetypes=[("Executable files","*.exe"), ("All files", "*.*")])

        display_name = Path(filename).stem
        if filename:
            path.delete(0, "end")
            path.insert(0, filename)
            name.delete(0, "end")
            name.insert(0, display_name)

    def select_icon(self):
        icon_path = filedialog.askopenfilename(parent=self, title="Select Your Icon", initialdir="/", defaultextension=".png", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.ico"), ("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*")])

        if icon_path:
            try:
                new_icon = ctk.CTkImage(PIL.Image.open(resource_path(icon_path)), size=(128, 128))
                self.icon_preview.configure(image=new_icon)
                self.icon_image = str(icon_path)
                logging.info(f"Load selected icon: {icon_path}")

            except Exception as e:
                logging.error(f"Failed to load selected icon: {e}")

    def save_game(self):
        game_name = re.sub(r'(?<=[a-z])(?=[A-Z])|[^a-zA-Z]', ' ', self.name_input.get()).replace(' ', '_').strip("_").lower()
        game_base = self.path_entry.get().strip()
        game_folder = Path(game_base)

        if any([not game_base, not game_name, not game_folder.is_file(), game_folder.suffix.lower() != ".exe"]):
            msbox_error = CTkMessagebox(title="Error", message="Please fill in all required fields", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_error.title_label.configure(fg_color="gray14")
            return
        
        if game_name in self.settings["Games"]:
            msbox_error = CTkMessagebox(title="Info", message="Game name already exists!", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_error.title_label.configure(fg_color="gray14")
            return
        
        self.settings["Games"][game_name] = self.settings["Games"].pop(self.slot_name)
        self.settings["Games"][game_name].update({
            "icon_path": resource_path(self.icon_image),
            "folder": str(game_folder.parent),
            "exe": str(game_folder.name)
        })
        save_config(self.settings)
        self.callback()
        self.destroy()
        
    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/window_icon.ico'))

    