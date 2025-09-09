from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import PIL.Image, PIL.ImageTk
import os, sys, logging, threading, queue
from CTkMessagebox import CTkMessagebox
from utils.downloader import download_from_github
from utils.config import load_config, save_config
from utils.injector import ReshadeSetup
from utils.path import resource_path
from gui.modal import ModalPresets, ModalConfig, ModalStarted

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
        self.char_image_1 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/logo.png")), size=(157, 147))
        #self.char_image_2 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/logo.png")), size=(157, 147))
        #self.char_image_3 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/logo.png")), size=(157, 147))
        #self.char_image_4 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/logo.png")), size=(157, 147))

        self.image_label = ctk.CTkLabel(master=self, text="", image=self.char_image_1)
        self.image_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    def update_image(self, new_image):
        self.image_label.configure(image=new_image)


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
        for PageClass in (HomePage, ReshadePage, ConfigPage):
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
            self.show_page("ConfigPage")

    # Manager the pages
    def show_page(self, page_name: str):
        page = self.pages[page_name]
        page.tkraise()
        logging.info(f"Page initialized: {page_name}")
    
    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/window_icon.ico'))


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
        self.button_icon = ctk.CTkImage(PIL.Image.open(resource_path("assets\\icon/back_icon.png")), size=(32, 32))
        #self.frame.update_image(self.frame.char_image_4)
        self.frame.grid(pady=40)

        self.back_button = ctk.CTkButton(self, text="", image=self.button_icon, command=self.on_back)
        self.back_button.configure(width=0, height=0, fg_color="transparent")
        self.back_button.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        self.text_1.grid_forget()
        
        self.text_2.configure(text="Now launch the game via the program if\n you'd like to play with Reshade")
        self.text_2.grid_configure(pady=(100, 10))

        self.button_1.configure(text="Settings", command=lambda: self.open_modal())
        self.button_1.grid_configure(pady=(40, 10))

        self.button_2.configure(text="Start", command=lambda: self.open_modal_start(), fg_color="#1DBD73")
        self.button_2.grid_configure(pady=(40, 10))

    def open_modal_start(self):
        last_game = self.settings["Launcher"].get("last_played_game", "")
        game_data = self.settings["Games"].get(last_game, {})
        folder = game_data.get("folder", "").strip()

        if last_game and folder:
            msbox_question = CTkMessagebox(title="Quick Launch", message=f"Do you want to start {last_game.replace("_", " ").title()}?", icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0, option_1="Yes", option_2="No")
            msbox_question.title_label.configure(fg_color="gray14")

            if msbox_question.get() == "Yes":
                setup_reshade = ReshadeSetup(self.settings, folder, self.settings["Launcher"]["xxmi_feature_enabled"])
                setup_reshade.verify_installation()
                setup_reshade.inject_game()
                return
        
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = ModalStarted(self, self.settings)
        else:
            self.modal.focus()


    def open_modal(self):
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = ModalConfig(self, self.settings)
        else:
            self.modal.focus()


    def on_back(self):
        self.controller.show_page(self.previous_page)


# Second Page
class ReshadePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.modal = None
        #self.frame.update_image(self.frame.char_image_1)
        self.download_queue = queue.Queue()

        self.text_1.grid_forget()

        self.text_2.configure(text="Select your Reshade preset to enhance\n the game!")
        self.text_2.grid_configure(pady=(70, 60))

        self.preset_button = ctk.CTkButton(self, text="Preset", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.open_modal())
        self.preset_button.configure(width=284, height=54, corner_radius=8, fg_color="#A884F3")
        self.preset_button.grid(row=4, column=0, columnspan=2)

        self.button_1.configure(text="Download", command=lambda: self.download_preset())
        self.button_1.grid_configure(pady=(10, 20))

        self.button_2.configure(text="Next", command=lambda: self.controller.show_page("HomePage"), fg_color="#1DBD73")
        self.button_2.grid_configure(pady=(10, 20))

    def download_preset(self):
        self.button_1.configure(text="Downloading...", state="disabled")

        response_args = (
            settings["Account"]["github_name"], 
            settings["Account"]["repository_name"],
            settings["Account"]["preset_folder"],
            settings["Packages"]["selected"],
            settings["Packages"].get("download_dir", ""),
            self.download_queue
        )
            
        threading.Thread(target=download_from_github, args=response_args, daemon=True).start()
        self.after(100, self.check_download)


    def check_download(self):
        try:
            response = self.download_queue.get(block=False)
            if isinstance(response, dict) and response.get("status") is False:
                msbox_error = CTkMessagebox(title="Error", message=response["message"], icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
                msbox_error.title_label.configure(fg_color="gray14")

                self.button_1.configure(text="Download", state="normal")
            else:
                msbox_info = CTkMessagebox(title="Info", message=response["message"], icon=None, header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
                msbox_info.title_label.configure(fg_color="gray14")

                self.button_1.configure(text="Download", state="normal")

        except queue.Empty:
            self.after(100, self.check_download)


    def open_modal(self):
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = ModalPresets(self, self.settings)
        else:
            self.modal.focus()


# Third Page
class ConfigPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        #self.frame.update_image(self.frame.char_image_1)
        self.path_var = ctk.StringVar()

        self.text_1.configure(text="Welcome, Trailblazer!")

        self.path_entry = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
        self.path_entry.configure(width=717, height=48, corner_radius=8, textvariable=self.path_var)
        self.path_entry.grid(row=4, column=0, columnspan=2, pady=20)

        self.button_1.configure(text="Browser", command=lambda: self.select_folder())

        self.button_2.configure(text="Next", command=lambda: self.save_path())

        self.path_var.trace_add("write", self.validate_realtime)

    def validate_realtime(self, *args):
        current_path = self.path_var.get()
        if os.path.isdir(current_path):
            self.path_entry.configure(border_color="green")
        else:
            self.path_entry.configure(border_color="red")


    # Check and saves the path in settings.json
    def save_path(self):
        game_path = self.path_entry.get().strip()

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


if __name__ == "__main__":
    settings = load_config()

    #* Load settings before starting the application
    ctk.set_default_color_theme(resource_path(settings["Launcher"]["gui_theme"]))
    logging.info("Settings loaded")

    app = Starluxe(settings)
    app.mainloop()