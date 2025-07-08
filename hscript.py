from tkinter import *
from tkinter import filedialog
import customtkinter as ctk
import PIL.Image, PIL.ImageTk
import os, sys, logging
from CTkListbox import *
from CTkMessagebox import CTkMessagebox
from utils.downloader import download_from_github
from utils.config import load_config, save_config
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

        #TODO: Mudar essa função para salvar em uma lista os presets
        def show_value(selected_option):
            print(selected_option)
        

        listbox = CTkListbox(self, font=ctk.CTkFont(family="Verdana", size=15), multiple_selection=True, command=show_value)
        listbox.pack(fill="both", expand=True, padx=10, pady=20)
        listbox.insert(0, "Luminescence")
        listbox.insert(1, "AstralAura")
        listbox.insert(2, "Spectrum")
        listbox.insert(3, "Galactic")

    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/Oniric_brown.ico'))


class HSRS(ctk.CTk):
    def __init__(self, settings: dict):
        super().__init__()
        logging.info("App started")

        self.title("")
        self.geometry("1024x768")
        self.resizable(width=False, height=False)
        self.modal = None
        self.settings = settings

        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.title_label = FadeInLabel(self, text="HSR+Script", font=ctk.CTkFont(size=64, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="N")

        self.frame = Image_Frame(self)
        self.frame.grid(row=1, column=0, columnspan=2, pady=20)

        self.text_1 = FadeInLabel(self, text="Welcome, Trailblazer!", font=ctk.CTkFont(size=26))
        self.text_1.grid(row=2, column=0, columnspan=2, pady=5)

        self.text_2 = FadeInLabel(self, text="Select the path to your game executable\n (e.g., " + r"C:\StarRail\Games\StarRail.exe" + ")", font=ctk.CTkFont(size=20))
        self.text_2.grid(row=3, column=0, columnspan=2, pady=20)

        self.path_entry = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
        self.path_entry.configure(width=717, height=48, corner_radius=8)
        self.path_entry.grid(row=4, column=0, columnspan=2, pady=20)

        self.function_button = ctk.CTkButton(self, text="Browser", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.select_folder())
        self.function_button.configure(width=135, height=54, corner_radius=8)
        self.function_button.grid(row=5, column=0, padx=(0, 5), pady=(10, 20), sticky="E")

        self.next_button = ctk.CTkButton(self, text="Next", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.save_path())
        self.next_button.configure(width=135, height=54, corner_radius=8)
        self.next_button.grid(row=5, column=1, padx=(5, 0), pady=(10, 20), sticky="W")

    def open_modal(self):
        if self.modal is None or not self.modal.winfo_exists():
            self.modal = Modal(self)
            self.modal.focus()
        else:
            self.modal.focus()


    def select_folder(self):
        foldername = filedialog.askdirectory(title='Open folder', initialdir='/')
        if foldername:
            msbox_info = CTkMessagebox(title="Selected Folder", message=f"{foldername}", icon="assets/icon/Oniric_brown.ico", header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_info.title_label.configure(fg_color="gray14")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, foldername)
    
    def save_path(self):
        game_path = self.path_entry.get()

        if not game_path:
            game_path = self.settings["Launcher"]["game_folder"]
        
        setup_reshade = ReshadeSetup(settings["Launcher"]["game_name"], game_path, settings["Script"])
        
        result = setup_reshade.verification()
        if result == True:
            self.settings["Launcher"]["game_folder"] = game_path
            save_config(self.settings)
            logging.info(f"Salvo: {game_path}")
            self.update_ui("preset_page")
        else:
            msbox_error = CTkMessagebox(title="Error", message=result["message"], icon="assets/icon/Oniric_brown.ico", header=False, sound=True, font=ctk.CTkFont(family="Verdana", size=14), fg_color="gray14", bg_color="gray14", justify="center", wraplength=300, border_width=0)
            msbox_error.title_label.configure(fg_color="gray14")

  
    def update_ui(self, states):
        if states == "preset_page":
            self.frame.update_image(self.frame.char_image_3)
            self.text_2.configure(text="Select your Reshade preset to enhance\n the game!")
            self.text_2.grid_configure(pady=(40, 60))
            self.text_1.grid_forget()
            self.path_entry.grid_forget()

            #TODO: Adicionar uma função para ler o arquivo de config.json para baixar os resources necessários
            def check_download(*check_var):
                config = [
                    ("script/Presets/Luminescence", resource_path("script\\Presets")),
                    ("script/Presets/AstralAura", resource_path("script\\Presets")),
                    ("script/Presets/Spectrum", resource_path("script\\Presets")),
                    ("script/Presets/Galactic", resource_path("script\\Presets"))
                ]
                
                #TODO: Adicionar ao button_download e atualizar o estado do botão de download
                #for i, c in enumerate(config):
                    #if check_var[i].get() == "on":
                        #download_from_github("Dimitri-Matheus", "HSR-Script", c[0], c[1])
                        #self.text_1.configure(text="Pack downloaded!")
                    #self.patch_button.configure(text="Next", command=lambda: self.update_ui("finish_page"))


            self.preset_button = ctk.CTkButton(self, text="Preset", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: self.open_modal())
            self.preset_button.configure(width=284, height=54, corner_radius=8)
            self.preset_button.grid(row=4, column=0, columnspan=2, pady=(20, 5))

            self.function_button.configure(text="Download", command=lambda: check_download(check_var_1, check_var_2, check_var_3, check_var_4), state="disabled")
            self.next_button.configure(command=lambda: self.update_ui("initial_page"))

        elif states == "initial_page":
            self.frame.update_image(self.frame.char_image_4)
            self.text_2.configure(text="Now launch the game via the program if\n you'd like to play with Reshade")
            self.text_2.grid_configure(pady=(140, 0))
            self.preset_button.grid_forget()

            #def combined_command():
                #if radio_var.get() == 1:
                    #print("The application ran successfully...")
                    #run_command(self.path_entry.get(), True)
                    #self.destroy()
                #elif radio_var.get() == 2:
                    #print("The application did not run...")
                    #run_command(self.path_entry.get(), False)
                    #self.destroy()

            self.function_button.configure(text="Settings", state="disabled")
            self.function_button.grid_configure(pady=(40, 20))

            self.next_button.configure(text="Start", command=lambda: ReshadeSetup(settings["Launcher"]["game_name"], settings["Launcher"]["game_folder"], settings["Script"]).inject_game())
            self.next_button.grid_configure(pady=(40, 20))

    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets\\icon/Oniric_brown.ico'))


if __name__ == "__main__":
    settings = load_config()

    #* Carrega as configurações antes de executar o aplicativo
    #TODO: Verificar se o caminho é vazio ou não
    #TODO: Carregar a "initial_page" caso o caminho exista
    #TODO: Carregar o "path_page" caso o caminho não exista
    ctk.set_default_color_theme(resource_path(settings["Launcher"]["gui_theme"]))
    logging.info("App loaded JSON")

    app = HSRS(settings)
    app.mainloop()