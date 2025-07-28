from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import PIL.Image, PIL.ImageTk
import os, sys, logging
from CTkListbox import *
from CTkMessagebox import CTkMessagebox
from utils.downloader import download_from_github
from utils.config import load_config, save_config, default
from utils.injector import ReshadeSetup

logging.basicConfig(level=logging.INFO)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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
        self.char_image_1 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/Trailblazer 1.png")), size=(256, 256))
        self.char_image_2 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/Trailblazer 2.png")), size=(256, 256))
        self.char_image_3 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/Trailblazer 3.png")), size=(256, 256))
        self.char_image_4 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/Pom-Pom.png")), size=(256, 256))

        self.image_label = ctk.CTkLabel(master=self, text="", image=self.char_image_1)
        self.image_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    def update_image(self, new_image):
        self.image_label.configure(image=new_image)


class Modal(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Select Preset")
        self.geometry("300x300")
        self.resizable(width=False, height=False)

        self.settings = settings
        self.selected_presets = []

        def show_value(selected_option):
            logging.info(f"Selecionado: {selected_option}")
            self.selected_presets = selected_option
        
        
        listbox = CTkListbox(self, font=ctk.CTkFont(family="Verdana", size=15), multiple_selection=True, command=show_value)
        listbox.pack(fill="both", expand=True, padx=10, pady=20)

        for p in self.settings["Packages"]["available"]:
            listbox.insert("end", p)

        for i in range(listbox.size()):
            value = listbox.get(i)
            if value in self.settings["Packages"]["selected"]:
                listbox.activate(i)
    
        self.save_button = ctk.CTkButton(self, text="Save", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=self.save_preset)
        self.save_button.configure(width=135, height=44, corner_radius=8)
        self.save_button.pack(pady=20)

    def save_preset(self):
        if self.selected_presets:
            self.settings["Packages"]["selected"] = self.selected_presets
        else:
            self.settings["Packages"]["selected"] = ""
        
        save_config(self.settings)
        logging.info(f"Presets salvo: {self.settings["Packages"]["selected"]}")
        self.destroy()

    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/Oniric_brown.ico'))


#TODO: Fazer a janela do Settings.json
class Modal_Config(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Settings")
        self.geometry("700x530")
        self.resizable(width=False, height=False)
        self.settings = settings

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Path Entry #1
        self.text_1 = ctk.CTkLabel(self, text="Path Game - Genshin Impact", font=ctk.CTkFont(size=20))
        self.text_1.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.path_entry_1 = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14), )
        self.path_entry_1.configure(width=478, height=48, corner_radius=8)
        self.path_entry_1.grid(row=1, column=0, padx=20, pady=(5, 5), sticky="w")

        self.button_1 = ctk.CTkButton(self, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_folder(self.path_entry_1))
        self.button_1.configure(width=135, height=48, corner_radius=8)
        self.button_1.grid(row=1, column=1, padx=0, pady=(5, 5), sticky="w")

        # Path Entry #2
        self.text_2 = ctk.CTkLabel(self, text="Path Game - Honkai Star Rail", font=ctk.CTkFont(size=20))
        self.text_2.grid(row=2, column=0, padx=20, pady=(15, 5), sticky="w")

        self.path_entry_2 = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
        self.path_entry_2.configure(width=478, height=48, corner_radius=8)
        self.path_entry_2.grid(row=3, column=0, padx=20, pady=(5, 5), sticky="w")

        self.button_2 = ctk.CTkButton(self, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_folder(self.path_entry_2))
        self.button_2.configure(width=135, height=48, corner_radius=8)
        self.button_2.grid(row=3, column=1, padx=0, pady=(5, 5), sticky="w")

        # Path Entry #3
        self.text_3 = ctk.CTkLabel(self, text="Path Game - Wuthering Waves", font=ctk.CTkFont(size=20))
        self.text_3.grid(row=4, column=0, padx=20, pady=(15, 5), sticky="w")

        self.path_entry_3 = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
        self.path_entry_3.configure(width=478, height=48, corner_radius=8)
        self.path_entry_3.grid(row=5, column=0, padx=20, pady=(5, 5), sticky="w")

        self.button_3 = ctk.CTkButton(self, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_folder(self.path_entry_3))
        self.button_3.configure(width=135, height=48, corner_radius=8)
        self.button_3.grid(row=5, column=1, padx=0, pady=(5, 5), sticky="w")

        # Themes
        self.text_4 = ctk.CTkLabel(self, text="Themes", font=ctk.CTkFont(size=20))
        self.text_4.grid(row=6, column=0, padx=20, pady=(15, 5), sticky="w")

        self.themes_option = ctk.CTkOptionMenu(self, values=["Default"], font=ctk.CTkFont(family="Verdana", size=14), state="disabled")
        self.themes_option.configure(width=216, height=44)
        self.themes_option.grid(row=7, column=0, padx=20, pady=(5,5), sticky="w")

        # Settings Manager
        self.button_4 = ctk.CTkButton(self, text="Save Config", font=ctk.CTkFont(size=20), command=lambda: self.save_path([self.path_entry_1, self.path_entry_2, self.path_entry_3]))
        self.button_4.configure(width=0, height=0, fg_color="transparent")
        self.button_4.grid(row=8, column=0, padx=2, pady=(15, 5), sticky="e")

        self.button_5 = ctk.CTkButton(self, text="Reset Config", font=ctk.CTkFont(size=20), command=lambda: self.reset_config())
        self.button_5.configure(width=0, height=0, fg_color="transparent")
        self.button_5.grid(row=8, column=1, padx=2, pady=(15, 5), sticky="w")

        self.path_entry_1.insert(0, settings["Games"]["genshin_impact"]["folder"])
        self.path_entry_2.insert(0, settings["Games"]["honkai_star_rail"]["folder"])
        self.path_entry_3.insert(0, settings["Games"]["wuthering_waves"]["folder"])
        

    def select_folder(self, path_widget):
        foldername = filedialog.askdirectory(title='Open folder', initialdir='/')
        if foldername:
            msbox_info = CTkMessagebox(title="Selected Folder", message=f"{foldername}", icon="assets/icon/Oniric_brown.ico", header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_info.title_label.configure(fg_color="gray14")
            path_widget.delete(0, "end")
            path_widget.insert(0, foldername)


    def save_path(self, path_widgets: list[ctk.CTkEntry]):
        errors = []
        for entry in path_widgets:
            game_path = entry.get()
            if not game_path:
                continue

            setup_reshade = ReshadeSetup(self.settings["Games"], game_path, self.settings["Script"], settings["Packages"])
            result = setup_reshade.verification()
            if result["status"] == True:
                game_code = result["game_code"]
                self.settings["Games"][game_code]["folder"] = game_path
            else:
                errors.append(f"{entry}: {result['message']}")
        if errors:
            msbox_error = CTkMessagebox(title="Error", message=result["message"], icon="assets/icon/Oniric_brown.ico", header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_error.title_label.configure(fg_color="gray14")
            return
        save_config(self.settings)
        self.destroy()

    def reset_config(self):
        save_config(default.copy())
        self.settings.clear()
        self.settings.update(default)
        self.destroy()
        logging.info("Configurações restauradas para o padrão!")
        python = sys.executable
        os.execv(python, [python] + sys.argv)
    
    
    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/Oniric_brown.ico'))



#! Otimizar isso, para o futuro
"""
class Modal_Started(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Start the your game")
        self.geometry("700x340")
        self.resizable(width=False, height=False)

        for col in range(3):
            self.grid_columnconfigure(col, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)

        self.game_1 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\icon/GI.png")), size=(128, 128))
        self.game_2 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\icon/HSR.png")), size=(128, 128))
        self.game_3 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\icon/WuWa.png")), size=(128, 128))

        self.button_1 = ctk.CTkButton(self, text="", image=self.game_1, command=lambda: self.destroy())
        self.button_1.configure(width=128, height=128, corner_radius=8, fg_color="transparent")
        self.button_1.grid(row=1, column=0, sticky="n", padx=10)

        self.button_2 = ctk.CTkButton(self, text="", image=self.game_2, command=lambda: self.destroy())
        self.button_2.configure(width=128, height=128, corner_radius=8, fg_color="transparent")
        self.button_2.grid(row=1, column=1, sticky="n", padx=10)

        self.button_3 = ctk.CTkButton(self, text="", image=self.game_3, command=lambda: self.destroy())
        self.button_3.configure(width=128, height=128, corner_radius=8, fg_color="transparent")
        self.button_3.grid(row=1, column=2, sticky="n", padx=10)

        self.text_1 = ctk.CTkLabel(self, text="GI", font=ctk.CTkFont(size=20))
        self.text_1.grid(row=2, column=0, sticky="n", pady=(10, 0))

        self.text_2 = ctk.CTkLabel(self, text="HSR", font=ctk.CTkFont(size=20))
        self.text_2.grid(row=2, column=1, sticky="n", pady=(10, 0))

        self.text_3 = ctk.CTkLabel(self, text="WuWa", font=ctk.CTkFont(size=20))
        self.text_3.grid(row=2, column=2, sticky="n", pady=(10, 0))

    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/Oniric_brown.ico'))
"""

class HSRS(ctk.CTk):
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
        super().wm_iconbitmap(resource_path('assets\\icon/Oniric_brown.ico'))


# Default Layout
class BasePage(ctk.CTkFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.settings = controller.settings

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.title_label = FadeInLabel(self, text="HSR+Script", font=ctk.CTkFont(size=64, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="N")

        self.frame = Image_Frame(self)
        self.frame.grid(row=1, column=0, columnspan=2, pady=20)

        self.text_1 = FadeInLabel(self, text="", font=ctk.CTkFont(size=26))
        self.text_1.grid(row=2, column=0, columnspan=2, pady=5)

        self.text_2 = FadeInLabel(self, text="Select the path to your game executable\n (e.g., " + r"C:\StarRail\Games\StarRail.exe" + ")", font=ctk.CTkFont(size=20))
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
        self.frame.update_image(self.frame.char_image_4)
        self.frame.grid(pady=40)

        self.text_1.grid_forget()
        
        self.text_2.configure(text="Now launch the game via the program if\n you'd like to play with Reshade")
        self.text_2.grid_configure(pady=(100, 10))

        self.button_1.configure(text="Settings", command=lambda: self.open_modal(), state="normal")
        self.button_1.grid_configure(pady=(40, 10))

        #! Ajustar esse botão para exibir uma janela e selecionar o jogo necessário
        self.button_2.configure(text="Start", command=lambda: ReshadeSetup(settings["Games"]["genshin_impact"], settings["Games"]["genshin_impact"]["folder"], settings["Script"], settings["Packages"]).inject_game())
        self.button_2.grid_configure(pady=(40, 10))

    def open_modal(self):
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = Modal_Config(self)
            self.modal.focus()
        else:
            self.modal.focus()

# Second Page
class ReshadePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.modal = None
        self.frame.update_image(self.frame.char_image_3)

        self.text_1.grid_forget()

        self.text_2.configure(text="Select your Reshade preset to enhance\n the game!")
        self.text_2.grid_configure(pady=(70, 60))

        self.preset_button = ctk.CTkButton(self, text="Preset", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.open_modal())
        self.preset_button.configure(width=284, height=54, corner_radius=8)
        self.preset_button.grid(row=4, column=0, columnspan=2)

        self.button_1.configure(text="Download", command=lambda: self.download_preset(), state="normal")
        self.button_1.grid_configure(pady=(10, 20))

        self.button_2.configure(text="Next", command=lambda: self.controller.show_page("HomePage"))
        self.button_2.grid_configure(pady=(10, 20))

    def download_preset(self):
        response = download_from_github(
                settings["Account"]["github_name"], 
                settings["Account"]["repository_name"],
                settings["Account"]["preset_resource"],
                settings["Packages"]["selected"],
                settings["Packages"].get("download_dir", "")
            )

        if isinstance(response, dict) and response.get("status") is False:
            msbox_error = CTkMessagebox(title="Error", message=response["message"], icon="assets/icon/Oniric_brown.ico", header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_error.title_label.configure(fg_color="gray14")
        else:
            msbox_info = CTkMessagebox(title="Info", message=response["message"], icon="assets/icon/Oniric_brown.ico", header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_info.title_label.configure(fg_color="gray14")
            self.button_1.configure(text="Downloaded",state="disabled")


    def open_modal(self):
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = Modal(self)
            self.modal.focus()
        else:
            self.modal.focus()


# Third Page
class ConfigPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.frame.update_image(self.frame.char_image_1)

        self.text_1.configure(text="Welcome, Trailblazer!")

        self.path_entry = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
        self.path_entry.configure(width=717, height=48, corner_radius=8)
        self.path_entry.grid(row=4, column=0, columnspan=2, pady=20)

        self.button_1.configure(text="Browser", command=lambda: self.select_folder())

        self.button_2.configure(text="Next", command=lambda: self.save_path())

    # Check and saves the path in settings.json
    def save_path(self):
        game_path = self.path_entry.get()
        setup_reshade = ReshadeSetup(self.settings["Games"], game_path, self.settings["Script"], settings["Packages"])
        result = setup_reshade.verification()

        if result["status"] == True:
            game_code = result["game_code"]
            self.settings["Games"][game_code]["folder"] = game_path
            save_config(self.settings)
            self.controller.show_page("ReshadePage")
        else:
            msbox_error = CTkMessagebox(title="Error", message=result["message"], icon="assets/icon/Oniric_brown.ico", header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_error.title_label.configure(fg_color="gray14")

    
    # Function to select the path
    def select_folder(self):
        foldername = filedialog.askdirectory(title='Open folder', initialdir='/')
        if foldername:
            msbox_info = CTkMessagebox(title="Selected Folder", message=f"{foldername}", icon="assets/icon/Oniric_brown.ico", header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_info.title_label.configure(fg_color="gray14")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, foldername)


if __name__ == "__main__":
    settings = load_config()

    #* Carrega as configurações antes de executar o aplicativo
    ctk.set_default_color_theme(resource_path(settings["Launcher"]["gui_theme"]))
    logging.info("Settings loaded")

    app = HSRS(settings)
    app.mainloop()