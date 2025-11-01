"""Defines the main game selection for the application"""

from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import PIL.Image, PIL.ImageTk
from pathlib import Path
import logging, re, math, shutil
from CTkMessagebox import CTkMessagebox
from CTkMenuBar import CustomDropdownMenu
from utils.config import save_config
from utils.path import resource_path
from utils.injector import ReshadeSetup
from .widgets import StyledToolTip

logging.basicConfig(level=logging.INFO)

class LauncherDialog(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict):
        super().__init__(master)
        self.transient(master)
        self.settings = settings_load
        self.modal = None

        self.title("Start Your Game")
        self.geometry("700x340")
        self.resizable(width=False, height=False)
        self.grab_set()

        self.prev_icon = ctk.CTkImage(PIL.Image.open(resource_path("assets/icon/back_icon.png")), size=(32, 32))
        self.next_icon = ctk.CTkImage(PIL.Image.open(resource_path("assets/icon/next_icon.png")), size=(32, 32))
        self.add_icon = ctk.CTkImage(PIL.Image.open(resource_path("assets/icon/add_icon.png")), size=(32, 32))

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Container
        self.container_frame = ctk.CTkFrame(self)
        self.container_frame.grid(row=0, column=0, sticky="nsew")
        self.container_frame.grid_rowconfigure(0, weight=1)
        self.container_frame.grid_columnconfigure(0, weight=1)

        self.add_button = ctk.CTkButton(self, text="", image=self.add_icon, command=lambda: self.open_modal(None))
        self.add_button.configure(width=0, height=0, fg_color="transparent")
        self.add_button.grid(row=0, column=0, padx=20, pady=10, sticky="nw")
        StyledToolTip(self.add_button, message="Add New Game")

        # Buttons Frame
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.grid(row=1, column=0, pady=(10, 30), sticky="ew")
        self.nav_frame.grid_columnconfigure((0, 3), weight=1)

        self.prev_button = ctk.CTkButton(self.nav_frame, text="", image=self.prev_icon, command=lambda: self.prev_page())
        self.prev_button.configure(width=0, height=0, fg_color="transparent")
        self.prev_button.grid(row=0, column=1, padx=10)

        self.next_button = ctk.CTkButton(self.nav_frame, text="", image=self.next_icon, command=lambda: self.next_page())
        self.next_button.configure(width=0, height=0, fg_color="transparent")
        self.next_button.grid(row=0, column=2, padx=10)

        self.controller_pages()
        self.show_page(0)

    # Controller the pages
    def controller_pages(self):
        for widget in self.container_frame.winfo_children():
            widget.destroy()

        self.games = list(self.settings.get("Games", {}).items())
        self.items = 3
        self.total_pages = math.ceil(len(self.games) / self.items)
        self.current_page_index = 0

        self.pages = []
        for i in range(self.total_pages):
            start = i * self.items
            end = start + self.items
            page_games = self.games[start:end]

            page = GamePage(self.container_frame, self, page_games)
            self.pages.append(page)
            page.grid(row=0, column=0, sticky="nsew")

    # Manager the pages
    def show_page(self, page_index: int):
        if not (0 <= page_index < self.total_pages):
            return
        
        page_show = self.pages[page_index]
        page_show.tkraise()
        self.current_page_index = page_index
        logging.info(f"Navigated to page {page_index}")

    def next_page(self):
        self.show_page(self.current_page_index + 1)

    def prev_page(self):
        self.show_page(self.current_page_index - 1)

    def refresh_page(self):
        logging.info("Refreshing all pages...")
        current_page = self.current_page_index
        self.controller_pages()
        self.show_page(current_page)

    def open_modal(self, game_id: str):
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = InputGame(self, self.settings, self.refresh_page, game_edit=game_id)
        else:
            self.modal.focus()

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
        super().wm_iconbitmap(resource_path('assets/icon/window_icon.ico'))


class GamePage(ctk.CTkFrame):
    def __init__(self, parent, controller, page_games: list):
        super().__init__(parent)
        self.controller = controller
        self.page_games = page_games
        self.page_update()

    def page_update(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_columnconfigure((0, 4), weight=1)
        self.grid_columnconfigure((1, 2, 3), weight=0)
        self.grid_rowconfigure((0, 3), weight=1)

        protected_games = ("genshin_impact", "honkai_star_rail", "wuthering_waves", "zenless_zone_zero")
        for j, (game_id, game_data) in enumerate(self.page_games, start=1):
            name = game_data.get("display_name", game_id).replace("_", " ").title()
            img_1 = ctk.CTkImage(PIL.Image.open(resource_path(game_data.get("icon_path", ""))), size=(128, 128))

            launch_button = ctk.CTkButton(self, text="", image=img_1)
            launch_button.configure(width=128, height=128, corner_radius=8, fg_color="transparent")
            launch_button.grid(row=1, column=j, padx=20, pady=(20, 0), sticky="n")

            text = ctk.CTkLabel(self, text=f"{name}", font=ctk.CTkFont(size=20))
            text.grid(row=2, column=j, pady=(10, 0), sticky="n")

            if game_id not in protected_games:
                context_menu = CustomDropdownMenu(master=self.controller, widget=launch_button, font=ctk.CTkFont(family="Verdana",size=12))
                context_menu.configure(border_color="gray20", border_width=1)
                context_menu.add_option("Edit", command=lambda gid=game_id: self.controller.open_modal(gid))
                context_menu.add_option("Remove", command=lambda gid=game_id: self.remove_game(gid))

                launch_button.bind("<Button-3>", lambda event, menu=context_menu: menu._show())
                launch_button.configure(command=lambda gid=game_id: self.controller.open_game(gid))
                StyledToolTip(launch_button, message="Right-click to manage this item", delay=0.5)
            else:
                launch_button.configure(command=lambda gid=game_id: self.controller.open_game(gid))

    def remove_game(self, game_id: str):
        msbox_warning = CTkMessagebox(title="Warning", message="Do you really want to remove this game?", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0, option_1="Ok", option_2="Cancel")
        msbox_warning.title_label.configure(fg_color="gray14")
        if msbox_warning.get() != "Ok":
            return
        path = self.controller.settings["Games"][game_id].get("icon_path")
        full_path = Path(resource_path(path)).resolve()

        if full_path.name != "empty.png":
            full_path.unlink()
            logging.info(f"Icon file '{full_path.name}' removed successfully!")
        else:
            logging.info(f"Icon '{full_path.name}' is a default file and will not be removed!")

        self.controller.settings["Games"].pop(game_id, None)
        save_config(self.controller.settings)
        self.controller.refresh_page()
        logging.info(f"Game '{game_id}' removed from configuration!")


class InputGame(ctk.CTkToplevel):
    def __init__(self, master, settings_load: dict, callback, game_edit: str):
        super().__init__(master)
        self.transient(master)
        self.settings = settings_load
        self.callback = callback
        self.game_edit = game_edit
        self.icon_source = None

        self.title("New Game")
        self.geometry("520x480")
        self.resizable(width=False, height=False)
        self.grab_set()
        r = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Container 1
        self.icon_image = resource_path("assets/icon/empty.png")
        self.icon = ctk.CTkImage(PIL.Image.open(self.icon_image), size=(128, 128))
        self.icon_preview = ctk.CTkLabel(self, text="", image=self.icon)
        self.icon_preview.grid(row=r, column=0, columnspan=2, pady=30, sticky="ew"); r += 1

        self.text_1 = ctk.CTkLabel(self, text="Display name", font=ctk.CTkFont(size=18))
        self.text_1.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1

        self.name_input = ctk.CTkEntry(self, placeholder_text="Enter game name", font=ctk.CTkFont(family="Verdana", size=14))
        self.name_input.configure(width=478, height=38, corner_radius=8)
        self.name_input.grid(row=r, column=0, padx=25, pady=5, sticky="ew")
        StyledToolTip(self.name_input, message="The name will update automatically after selecting the executable.")

        self.icon_button = ctk.CTkButton(self, text="Choose Icon", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_icon())
        self.icon_button.configure(width=123, height=38, corner_radius=8)
        self.icon_button.grid(row=r, column=1, padx=(0, 20), pady=5, sticky="e"); r += 1
        StyledToolTip(self.icon_button, message=(
            "Select and update the default icon:\n"
            "1. Choose an image in a compatible format (PNG, JPG, etc.).\n" 
            "2. Recommended size: 128x128 pixels."
        ))

        self.text_2 = ctk.CTkLabel(self, text="Game Executable", font=ctk.CTkFont(size=18))
        self.text_2.grid(row=r, column=0, padx=25, pady=(15, 5), sticky="w"); r += 1

        self.path_entry = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
        self.path_entry.configure(width=478, height=38, corner_radius=8)
        self.path_entry.grid(row=r, column=0, padx=25, pady=5, sticky="ew")
        StyledToolTip(self.path_entry, message=(
            "Path to the folder containing the selected game's executable.\n"
            "Note: Make sure to select the correct .exe file."
        ))

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

        if self.game_edit is not None:
            self.title("Edit Game")
            game_data = self.settings["Games"].get(self.game_edit, {})
            loaded_icon = ctk.CTkImage(PIL.Image.open(resource_path(game_data.get("icon_path"))), size=(128, 128))
            self.icon_preview.configure(image=loaded_icon)
            self.name_input.insert(0, game_data.get("display_name", game_edit.replace("_", " ").title()))
            self.path_entry.insert(0, str(Path(game_data.get("folder")) / game_data.get("exe")))
            logging.info("Data loaded successfully!")

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
                self.icon_source = icon_path
                logging.info(f"Load selected icon: {icon_path}")

            except Exception as e:
                logging.error(f"Failed to load selected icon: {e}")

    def save_game(self):
        game_name = re.sub(r'(?<=[a-z])(?=[A-Z])|[^a-zA-Z]', ' ', self.name_input.get()).replace(' ', '_').strip("_").lower()
        game_base = self.path_entry.get().strip()
        game_folder = Path(game_base)

        if any([not game_base, not game_name, not game_folder.is_file(), game_folder.suffix.lower() != ".exe"]):
            msbox_info = CTkMessagebox(title="Info", message="Please fill in all required fields", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_info.title_label.configure(fg_color="gray14")
            return
        
        if game_name in self.settings["Games"] and game_name != self.game_edit:
            msbox_info = CTkMessagebox(title="Info", message="Game name already exists!", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_info.title_label.configure(fg_color="gray14")
            return
        
        # Copy icons
        icon_save = self.icon_image
        if self.icon_source:
            try:
                file_name = Path(self.icon_source).name 
                dest_folder = Path(resource_path("assets/icon"))
                dest_path = dest_folder / file_name
                dest_folder.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.icon_source, dest_path)

                icon_save = f"assets/icon/{file_name}"
                logging.info(f"Icon copied to: {dest_folder}")
            except Exception:
                logging.exception("Failed to copy new icon!")
        elif self.game_edit:
            icon_save = self.settings["Games"].get(self.game_edit, {}).get("icon_path", "assets/icon/empty.png")
        
        settings_data =  {
            "icon_path": str(icon_save),
            "folder": str(game_folder.parent),
            "exe": str(game_folder.name),
            "subpath": ""
        }
        games = self.settings.setdefault("Games", {})

        if not self.game_edit:
            games[game_name] = settings_data
            logging.info(f"Game added: {game_name}")
        elif game_name == self.game_edit:
            games[game_name].update(settings_data)
            logging.info(f"Game updated: {game_name}")
        else:
            games[game_name] = games.pop(self.game_edit, {})
            games[game_name].update(settings_data)
            logging.info(f"Game '{self.game_edit}' was renamed to '{game_name}'")
        
        save_config(self.settings)
        self.callback()
        self.destroy()
        
    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets/icon/window_icon.ico'))

    