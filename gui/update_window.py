"""Defines the window for downloading dependencies with a progress bar"""

import customtkinter as ctk
import PIL.Image, threading, logging, sys
from utils.path import resource_path

logging.basicConfig(level=logging.INFO)

class DownloadDialog(ctk.CTkToplevel):
    def __init__(self, master, message, window_close, download_thread=None):
        super().__init__(master)
        self.transient(master)
        self.download_thread = download_thread
        self.message = message
        self.window_close = window_close

        self.title("")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.disable_close)
        self.grab_set()

        # Center window on screen or over the master window
        self.master_window = master
        if self.master_window is None:
            spawn_x = int((self.winfo_screenwidth() - self.width) / 2)
            spawn_y = int((self.winfo_screenheight() - self.height) / 2)
        else:
            spawn_x = int(self.master_window.winfo_width() * 0.5 + self.master_window.winfo_x() - 0.5 * 400 + 7)
            spawn_y = int(self.master_window.winfo_height() * 0.5 + self.master_window.winfo_y() - 0.5 * 200 + 20)
        
        self.after(10)
        self.geometry(f"400x200+{spawn_x}+{spawn_y}")

        self.download_icon = ctk.CTkImage(PIL.Image.open(resource_path("assets/icon/download.png")), size=(32, 32))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 3), weight=1)
        
        self.download_label = ctk.CTkLabel(self, text="", image=self.download_icon)
        self.download_label.grid(row=1, column=0, pady=(0, 10))

        self.title_label = ctk.CTkLabel(self, text=self.message, font=ctk.CTkFont(size=18))
        self.title_label.grid(row=2, column=0, pady=10)

        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal")
        self.progress_bar.configure(width=256, height=6)
        self.progress_bar.grid(row=3, column=0, pady=10)

        self.button = ctk.CTkButton(self, text="Retry", font=ctk.CTkFont(family="Verdana", size=12, weight="bold"), command=self.run_download)
        self.button.configure(width=135, height=34, corner_radius=8, fg_color="#D8D8D8", text_color="#000000")
        self.button.grid_forget()

        if self.download_thread:
            self.run_download()

    def disable_close(self):
        logging.warning("Cannot close window during download!")

    def app_close(self):
        if self.window_close:
            self.destroy()
            self.master_window.destroy()
        else:
            self.destroy()

    def run_download(self):
        thread = threading.Thread(target=self.execute_download, daemon=True)
        thread.start()

    def execute_download(self):
        try:
            self.title_label.configure(text=self.message)
            self.button.grid_forget()
            result = self.download_thread(self.update_progress)

            if not result["status"]:
                self.title_label.configure(text=result["message"])
                self.progress_bar.set(0)
                self.button.grid(row=4, column=0, pady=10)
                self.protocol("WM_DELETE_WINDOW", self.app_close)
            else:
                self.after(500, self.destroy)

        except Exception as e:
            logging.error(f"Error during download: {e}")
            self.button.grid(row=4, column=0, pady=10)
            self.protocol("WM_DELETE_WINDOW", self.app_close)

    def update_progress(self, value: float):
        if 0.0 <= value <= 1.0:
            self.progress_bar.set(value)
            self.update_idletasks()

    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets/icon/window_icon.ico'))