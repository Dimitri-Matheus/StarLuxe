from tkinter import *
import customtkinter as ctk
import PIL.Image, PIL.ImageTk
import os
import sys
from core import run_command, verification
from data import download_from_github

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
        super().__init__(master, width=300, height=315)
        self.char_image_1 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/Trailblazer 1.png")), size=(256, 256))
        self.char_image_2 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/Trailblazer 2.png")), size=(256, 256))
        self.char_image_3 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/Trailblazer 3.png")), size=(256, 256))
        self.char_image_4 = ctk.CTkImage(PIL.Image.open(resource_path("assets\\logo/Pom-Pom.png")), size=(256, 256))

        self.char_label = ctk.CTkLabel(master=self, text="", image=self.char_image_1)
        self.char_label.place(relx=0.5, rely=0.45, anchor=CENTER)

    def update_image(self, new_image):
        self.char_label.configure(image=new_image)


class HSRS(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("")
        self.geometry("700x315")
        self.resizable(width=False, height=False)
        self.configure(fg_color="#432818")
        self.bind('<Return>', self.validate_enter)

        self.enter_bound = False

        self.iconbitmap("assets\\icon/Oniric_brown.ico")
        ctk.set_default_color_theme(resource_path("theme\\Trailblazer.json"))
        ctk.set_appearance_mode("dark")

        self.frame = Image_Frame(self)
        self.frame.place(relx=0, rely=0, anchor=NW)

        self.title = FadeInLabel(self, text="HSR+Script", font=ctk.CTkFont(size=58, weight="bold"), text_color="#ffffff", fg_color="#432818")
        self.title.place(relx=0.72, rely=0.4, anchor=CENTER)

        self.text_1 = FadeInLabel(self, text="Press enter to continue...", font=ctk.CTkFont(size=20, underline=False), fg_color="#432818")
        self.text_1.place(relx=0.72, rely=0.75, anchor=CENTER)

        self.text_2 = FadeInLabel(self, text="Hello,", font=ctk.CTkFont(size=20), fg_color="#432818")
        self.text_2.place(relx=0.45, rely=0.05, anchor=NW)

    def validate_enter(self, event):
        if not self.enter_bound:
            self.enter_bound = True
            self.pages("path_page")
        
    def pages(self, stats):
        if stats == "path_page":
            self.frame.update_image(self.frame.char_image_2)
            self.title.configure(font=ctk.CTkFont(size=50, weight="bold"))
            self.title.place(relx=0.72, rely=0.15, anchor=CENTER)
            self.text_1.configure(text="Paste the game folder here!", font=ctk.CTkFont(size=18))
            self.text_1.place(relx=0.72, rely=0.32, anchor=CENTER)
            self.text_2.place_forget()

            self.path_entry = ctk.CTkEntry(self, placeholder_text="C:/Games...", font=ctk.CTkFont(family="Verdana", size=14))
            self.path_entry.configure(width=270, height=64, corner_radius=8)
            self.path_entry.place(relx=0.72, rely=0.58, anchor=CENTER)

            def combined_action():
                verification(self.path_entry.get(), self.text_1)
                self.pages("reshade_page")

            self.patch_button = ctk.CTkButton(self, text="Patch", font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), command=lambda: combined_action())
            self.patch_button.configure(width=135, height=54, corner_radius=8)
            self.patch_button.place(relx=0.72, rely=0.85, anchor=CENTER)

        elif stats == "reshade_page":
            self.frame.update_image(self.frame.char_image_3)
            self.text_1.configure(text="Check the Reshade pack:")
            self.path_entry.place_forget()
            check_var_1 = ctk.StringVar(value="off")
            check_var_2 = ctk.StringVar(value="off")
            check_var_3 = ctk.StringVar(value="off")
            check_var_4 = ctk.StringVar(value="off")

            def check_download(*check_var):
                config = [
                    ("script/Presets/Luminescence", resource_path("script\\Presets")),
                    ("script/Presets/AstralAura", resource_path("script\\Presets")),
                    ("script/Presets/Spectrum", resource_path("script\\Presets")),
                    ("script/Presets/Galactic", resource_path("script\\Presets"))
                ]
                
                for i, c in enumerate(config):
                    if check_var[i].get() == "on":
                        download_from_github("Dimitri-Matheus", "HSR-Script", c[0], c[1])
                        self.text_1.configure(text="Pack downloaded!")
                    self.patch_button.configure(text="Next", command=lambda: self.pages("finish_page"))


            self.checkbox_1 = ctk.CTkCheckBox(self, text="Luminescence", variable=check_var_1, onvalue="on", offvalue="off")
            self.checkbox_1.configure(font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), checkbox_width=20, checkbox_height=20)
            self.checkbox_1.place(relx=0.63, rely=0.5, anchor=CENTER)

            self.checkbox_2 = ctk.CTkCheckBox(self, text="AstralAura", variable=check_var_2, onvalue="on", offvalue="off")
            self.checkbox_2.configure(font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), checkbox_width=20, checkbox_height=20)
            self.checkbox_2.place(relx=0.61, rely=0.6, anchor=CENTER)

            self.checkbox_3 = ctk.CTkCheckBox(self, text="Spectrum", variable=check_var_3, onvalue="on", offvalue="off")
            self.checkbox_3.configure(font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), checkbox_width=20, checkbox_height=20)
            self.checkbox_3.place(relx=0.83, rely=0.5, anchor=CENTER)

            self.checkbox_4 = ctk.CTkCheckBox(self, text="Galactic", variable=check_var_4, onvalue="on", offvalue="off")
            self.checkbox_4.configure(font=ctk.CTkFont(family="Verdana", size=14, weight="bold"), checkbox_width=20, checkbox_height=20)
            self.checkbox_4.place(relx=0.83, rely=0.6, anchor=CENTER)

            self.patch_button.configure(text="Download", command=lambda: check_download(check_var_1, check_var_2, check_var_3, check_var_4))

        elif stats == "finish_page":
            self.frame.update_image(self.frame.char_image_4)
            radio_var = IntVar(value=2)
            self.text_1.configure(text="The game has been patched! \n Open the HSR+ file")
            self.checkbox_1.place_forget()
            self.checkbox_2.place_forget()
            self.checkbox_3.place_forget()
            self.checkbox_4.place_forget()

            def combined_command():
                if radio_var.get() == 1:
                    print("The application ran successfully...")
                    run_command(self.path_entry.get(), True)
                    self.destroy()
                elif radio_var.get() == 2:
                    print("The application did not run...")
                    run_command(self.path_entry.get(), False)
                    self.destroy()

            self.radiobutton_1 = ctk.CTkRadioButton(self, text="Run", variable= radio_var, value=1, state="disabled")
            self.radiobutton_1.configure(font=ctk.CTkFont(family="Verdana", size=14), radiobutton_width=18, radiobutton_height=18, border_color="gray60")
            self.radiobutton_1.place(relx=0.73, rely=0.5, anchor=CENTER)

            self.radiobutton_2 = ctk.CTkRadioButton(self, text="Not run", variable= radio_var, value=2)
            self.radiobutton_2.configure(font=ctk.CTkFont(family="Verdana", size=14), radiobutton_width=18, radiobutton_height=18)
            self.radiobutton_2.place(relx=0.73, rely=0.6, anchor=CENTER)

            self.patch_button.configure(text="Finish", command=lambda: combined_command())


if __name__ == "__main__":
    app = HSRS()
    app.mainloop()