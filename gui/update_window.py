"""Defines the window for downloading dependencies with a progress bar"""

import customtkinter as ctk
import PIL.Image, threading, logging
from .widgets import center_window
from utils.path import resource_path
from utils.downloader import DownloadCancelled

logger = logging.getLogger(__name__)

class DownloadDialog(ctk.CTkToplevel):
    def __init__(self, master, message, download_thread=None):
        super().__init__(master)
        self.transient(master)
        self.download_thread = download_thread
        self.message = message
        self.cancel_event = threading.Event()
        self.download_running = False

        self.title("")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.cancel_download)
        self.grab_set()
        center_window(self, master, 400, 200)

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

    def cancel_download(self):
        if self.download_running:
            self.cancel_event.set()
            self.title_label.configure(text="Cancelling download...")
        else:
            self.app_close()

    def app_close(self):
        self.destroy()

    def run_download(self):
        self.protocol("WM_DELETE_WINDOW", self.cancel_download)
        thread = threading.Thread(target=self.execute_download, daemon=True)
        thread.start()

    def execute_download(self):
        try:
            self.download_running = True
            self.title_label.configure(text=self.message)
            self.button.grid_forget()
            result = self.download_thread(self.update_progress)
            self.download_running = False

            if not result["status"]:
                self.title_label.configure(text=result["message"])
                self.progress_bar.set(0)
                self.button.grid(row=4, column=0, pady=10)
                self.protocol("WM_DELETE_WINDOW", self.app_close)
            else:
                self.after(500, self.destroy)

        except DownloadCancelled:
            logger.info("Download cancelled by user")
            self.after(0, self.app_close)

        except Exception as e:
            logger.error(f"Error during download: {e}")
            self.download_running = False
            self.button.grid(row=4, column=0, pady=10)
            self.protocol("WM_DELETE_WINDOW", self.app_close)

    def update_progress(self, value: float):
        if self.cancel_event.is_set():
            raise DownloadCancelled()
        if 0.0 <= value <= 1.0:
            self.progress_bar.set(value)
            self.update_idletasks()

    def iconbitmap(self, bitmap):
        self._iconbitmap_method_called = False
        super().wm_iconbitmap(resource_path('assets/icon/window_icon.ico'))