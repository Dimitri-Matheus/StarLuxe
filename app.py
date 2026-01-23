# Compilation mode, command options
# nuitka-project: --mode=standalone
# nuitka-project: --output-dir=build
# nuitka-project: --output-filename=Starluxe.exe
# nuitka-project: --windows-console-mode=disable

# UAC Configuration
# nuitka-project: --windows-uac-admin
# nuitka-project: --report=compilation-report.xml
# nuitka-project: --windows-icon-from-ico=assets/icon/favicon.ico

# Metadata
# nuitka-project: --product-version='1.5'
# nuitka-project: --company-name='Dimit'
# nuitka-project: --product-name='Starluxe'
# nuitka-project: --file-description='StarLuxe Launcher'

# Data files
# nuitka-project: --user-package-configuration-file={MAIN_DIRECTORY}/package-files.yml

# The Tkinter plugin
# nuitka-project: --enable-plugin=tk-inter

from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import PIL.Image, PIL.ImageTk
import logging, os, queue
from CTkMessagebox import CTkMessagebox
from utils.downloader import download_from_github, download_r2_dependencies, check_for_updates, download_update, sync_metadata
from utils.config import load_config, save_config
from utils.injector import ReshadeSetup
from utils.path import resource_path
from utils.theme import ThemeManager
from gui import SettingsDialog, PresetsDialog, LauncherDialog, DownloadDialog
from gui.widgets import StyledToolTip

logging.basicConfig(level=logging.INFO)

# Animations
class FadeInLabel(ctk.CTkLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields = ('text_color', 'fg_color')
        self.colors = {key: self.cget(key) for key in self.fields }
        self.colors['base'] = self.master.cget('fg_color')
        self.configure(**{key: self.colors['base'] for key in self.fields})
        
        for key, color in self.colors.items():
            if isinstance(color, str):
                rgb_color = self.winfo_rgb(color)
                self.colors[key] = (rgb_color, rgb_color)
            else:
                self.colors[key] = self.winfo_rgb(color[0]), self.winfo_rgb(color[1])
        
        self.transition = 0
        self.change_color()
        
    def get_curr(self, start, end):
        rgb_to_hex = lambda rgb : '#{:02x}{:02x}{:02x}'.format(*[int(val * 255 / 65535) for val in rgb])
        return rgb_to_hex([start[i] + (end[i]-start[i])*self.transition for i in range(3)])
        
    def change_color(self):
        self.configure(
            **{key:(self.get_curr(self.colors['base'][0], self.colors[key][0]),
                    self.get_curr(self.colors['base'][1], self.colors[key][1])) for key in self.fields}
        )
        self.transition += 0.1
        if self.transition < 1:
            self.after(60, self.change_color)


class Image_Frame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=256, height=256)
        self.default_image = ctk.CTkImage(PIL.Image.open(resource_path("themes/Default/MainFrame/logo-app.png")), size=(157, 147))
        self.custom_size = (256, 256)

        self.image_label = ctk.CTkLabel(master=self, text="", image=self.default_image)
        self.image_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    def process_image(self, path):
        if path and os.path.exists(path):
            try:
                return ctk.CTkImage(PIL.Image.open(path), size=self.custom_size)
            except Exception as e:
                logging.error(f"Failed to load custom image: {e}")
        return None

    def update_image(self, new_image):
        image = self.process_image(new_image)
        self.image_label.configure(image=image)

    def load_theme_image(self, theme_name: str):
        image_path = ThemeManager.get_images(theme_name)
        if image_path:
            self.update_image(image_path)


class Starluxe(ctk.CTk):
    def __init__(self, settings: dict):
        super().__init__()
        logging.info("App started")

        self.title("")
        self.geometry("1024x768")
        self.resizable(width=False, height=False)
        
        self.settings = settings

        ctk.set_appearance_mode("dark")

        # Container
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Grid config for container
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Controller the pages
        self.pages = {}
        for PageClass in (HomePage, ReshadePage, ConfigPage, SetupPage):
            page = PageClass(self.container, self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        initial_page = any(
            game_folder.get("folder", "").strip()
            for game_folder in self.settings["Games"].values()
        )
        if initial_page:
            self.show_page("HomePage")
        else:
            self.show_page("SetupPage")

    # Manager the pages
    def show_page(self, page_name: str):
        page = self.pages[page_name]
        page.tkraise()
        logging.info(f"Page initialized: {page_name}")
    
    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets/icon/window_icon.ico'))


# Default Layout
class BasePage(ctk.CTkFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.settings = controller.settings

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.title_label = FadeInLabel(self, text="StarLuxe", font=ctk.CTkFont(size=64, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="N")

        self.frame = Image_Frame(self)
        self.frame.grid(row=1, column=0, columnspan=2, pady=20)

        self.text_1 = FadeInLabel(self, text="", font=ctk.CTkFont(size=26))
        self.text_1.grid(row=2, column=0, columnspan=2, pady=5)

        self.text_2 = FadeInLabel(self, text="Select your game installation folder\n (e.g., " + r"C:\Program Files\MyGame" + ")", font=ctk.CTkFont(size=20))
        self.text_2.grid(row=3, column=0, columnspan=2, pady=20)

        self.button_1 = ctk.CTkButton(self, text="", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"))
        self.button_1.configure(width=135, height=54, corner_radius=8)
        self.button_1.grid(row=5, column=0, padx=(0, 5), pady=20, sticky="E")

        self.button_2 = ctk.CTkButton(self, text="", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"))
        self.button_2.configure(width=135, height=54, corner_radius=8)
        self.button_2.grid(row=5, column=1, padx=(5, 0), pady=20, sticky="W")


# First Page
class HomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.modal = None
        self.previous_page = "ReshadePage"
        self.button_icon = ctk.CTkImage(PIL.Image.open(resource_path("assets/icon/button-left.png")), size=(32, 32))
        self.frame.load_theme_image("MainFrame/logo-home")
        self.frame.grid(pady=40)

        self.back_button = ctk.CTkButton(self, text="", image=self.button_icon, command=self.on_back)
        self.back_button.configure(width=0, height=0, fg_color="transparent")
        self.back_button.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self.text_1.grid_forget()
        
        self.text_2.configure(text="Now launch the game via the program if\n you'd like to play with Reshade")
        self.text_2.grid_configure(pady=(100, 10))

        self.button_1.configure(text="Settings", command=lambda: self.open_modal())
        self.button_1.grid_configure(pady=(40, 10))

        self.button_2.configure(text="Start", command=lambda: self.open_modal_start(), fg_color=ThemeManager.get_custom_color("primary_color"))
        self.button_2.grid_configure(pady=(40, 10))

    def open_modal_start(self):
        last_game = self.settings["Launcher"].get("last_played_game", "")
        game_data = self.settings["Games"].get(last_game, {})
        folder = game_data.get("folder", "").strip()

        if last_game and folder:
            msbox_question = CTkMessagebox(title="Quick Launch", message=f"Do you want to start {last_game.replace("_", " ").title()}?", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0, option_1="Yes", option_2="No")
            msbox_question.title_label.configure(fg_color="gray14")

            if msbox_question.get() == "Yes":
                setup = ReshadeSetup(self.settings, folder, self.settings["Launcher"]["xxmi_feature_enabled"])
                setup.verify_installation()
                setup.addon_support()
                setup.xxmi_integration(last_game)
                setup.inject_game()
                return
        
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = LauncherDialog(self, self.settings)
        else:
            self.modal.focus()

    def open_modal(self):
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = SettingsDialog(self, self.settings, controller=self.controller)
        else:
            self.modal.focus()

    def on_back(self):
        self.controller.show_page(self.previous_page)


# Second Page
class ReshadePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.modal = None
        self.frame.load_theme_image("MainFrame/logo-preset")
        self.download_queue = queue.Queue()

        self.text_1.grid_forget()

        self.text_2.configure(text="Select your Reshade preset to enhance\n the game!")
        self.text_2.grid_configure(pady=(70, 60))

        self.preset_button = ctk.CTkButton(self, text="Preset", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.open_modal())
        self.preset_button.configure(width=284, height=54, corner_radius=8, fg_color=ThemeManager.get_custom_color("secondary_color"))
        self.preset_button.grid(row=4, column=0, columnspan=2)

        self.button_1.configure(text="Download", command=lambda: self.download_preset())
        self.button_1.grid_configure(pady=(10, 20))

        self.button_2.configure(text="Next", command=lambda: self.controller.show_page("HomePage"), fg_color=ThemeManager.get_custom_color("primary_color"))
        self.button_2.grid_configure(pady=(10, 20))

    def download_preset(self):
        selected_presets = self.settings["Packages"].get("selected", [])
        if not selected_presets or not any(preset.strip() for preset in selected_presets):
            msbox_warning = CTkMessagebox(title="Warning", message="Select a preset before downloading!", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_warning.title_label.configure(fg_color="gray14")
            logging.error("You haven't selected a preset!")
            return

        def download_task(progress_callback):
            download_from_github(
                settings["Account"]["github_name"], 
                settings["Account"]["repository_name"],
                settings["Account"]["preset_folder"],
                settings["Packages"]["selected"],
                settings["Packages"].get("download_dir", ""),
                self.download_queue,
                progress_callback
            )
            response = self.download_queue.get()
            if isinstance(response, dict):
                self.after(1000, lambda: self.download_result(response))
            return response
        DownloadDialog(self.controller, "Downloading Presets", False, download_task)

    def download_result(self, response):
        if response["status"]:
            msbox_info = CTkMessagebox(title="Info", message=response["message"], icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300,border_width=0)
            msbox_info.title_label.configure(fg_color="gray14")

    def open_modal(self):
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = PresetsDialog(self, self.settings)
        else:
            self.modal.focus()


# Third Page
class ConfigPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.frame.load_theme_image("MainFrame/logo-config")
        self.path_var = ctk.StringVar()

        self.path_entry = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
        self.path_entry.configure(width=717, height=48, corner_radius=8, textvariable=self.path_var)
        self.path_entry.grid(row=4, column=0, columnspan=2, pady=20)
        self.path_var.trace_add("write", self.update_button)
        StyledToolTip(self.path_entry, message="Supported games: Genshin Impact, Honkai: Star Rail, Wuthering Waves, Zenless Zone Zero and Duet Night Abyss.")

        self.button_1.configure(text="Browser", command=lambda: self.select_folder())

        self.button_2.configure(command=lambda: self.save_path())
        StyledToolTip(self.button_2, message="Skip this step to set up the game path later.")
        self.update_button()

    def update_button(self, *args):
        current_path = self.path_entry.get()
        self.path_entry.configure(placeholder_text="C:/Games...")
        if not current_path:
            self.button_2.configure(text="Skip")
        else:
            self.button_2.configure(text="Next")

    # Check and saves the path in settings.json
    def save_path(self):
        game_path = self.path_entry.get().strip()

        if not game_path:
            self.controller.show_page("ReshadePage")
            return

        setup_install = ReshadeSetup(self.settings, game_path, self.settings["Launcher"]["xxmi_feature_enabled"])
        result = setup_install.verify_installation()

        if result["status"] == True:
            game_code = result["game_code"]
            self.settings["Games"][game_code]["folder"] = game_path
            save_config(self.settings)
            self.controller.show_page("ReshadePage")
        else:
            msbox_error = CTkMessagebox(title="Error", message=result["message"], icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_error.title_label.configure(fg_color="gray14")
    
    # Function to select the path
    def select_folder(self):
        foldername = filedialog.askdirectory(title='Open folder', initialdir='/')
        if foldername:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, foldername)


# Fourth Page
class SetupPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.text_1.configure(text="Welcome, Trailblazer!")
        self.frame.load_theme_image("MainFrame/logo-setup")

        self.text_1.configure(text="Welcome, Trailblazer!")
        self.text_1.grid_configure(pady=(30, 5))
        self.text_2.configure(text="Enhance your game visuals with the \nReShade")
        self.text_2.grid_configure(pady=(20, 30))

        self.button_icon = ctk.CTkImage(PIL.Image.open(resource_path("assets/icon/button-next.png")), size=(32, 32))
        self.button_1.configure(image=self.button_icon, width=0, height=0, fg_color="transparent", command=lambda: self.controller.show_page("ConfigPage"))
        self.button_1.grid_configure(pady=(40, 10))
        StyledToolTip(self.button_1, message="🎉 Thanks for testing! Enjoy your experience!", delay=0.8)

        self.button_2.grid_forget()


if __name__ == "__main__":
    settings = load_config()
    __version__ = "1.0.5"

    #* Load settings before starting the application
    themes = ThemeManager(resource_path("themes"))
    ctk.set_default_color_theme(themes.load_theme(settings["Launcher"]["gui_theme"]))
    logging.info("Settings loaded")

    app = Starluxe(settings)
    setup_system = ReshadeSetup(settings, "", settings["Launcher"]["xxmi_feature_enabled"])
    result_system = setup_system.verify_system()
    result_update = check_for_updates("Dimitri-Matheus", __version__, settings["Launcher"]["auto_check_update"])
    sync_metadata(settings["Account"]["github_name"], settings["Account"]["repository_name"])

    if not result_system["status"]:
        def download_task(progress_callback):
            return download_r2_dependencies(settings["Packages"]["download_dir"], progress_callback)
        DownloadDialog(app, "Downloading Dependencies", True, download_task)
    
    if result_update["status"]:
        msbox_update = CTkMessagebox(title="New Version!", message=f"Good news! An update is ready. \n\n   Version {result_update['version']} ({result_update['size'] / 1_000_000:.2f} MB)", icon=None, header=False, topmost=True, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0, option_1="Update now", option_2="Later")
        msbox_update.title_label.configure(fg_color="gray14")

        if msbox_update.get() == "Update now":
            download_update(result_update["url"])
    
    app.mainloop()