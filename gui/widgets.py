"""Custom and reusable widget components for GUI"""

import customtkinter as ctk
from CTkToolTip import CTkToolTip
from CTkMessagebox import CTkMessagebox

class StyledToolTip(CTkToolTip):
    def __init__(self, widget, message, **kwargs):
        default_style = {
            "corner_radius": 8,
            "bg_color": "#000001",
            "fg_color": "transparent",
            "padding": (6, 6),
            "alpha": 0.95,
            "font": ctk.CTkFont(family="Verdana", size=14),
            "border_color": "gray20",
            "border_width": 1,
            "justify": "left",
            "text_color": "#DCDCDC"
        }

        default_style.update(kwargs)
        super().__init__(widget, message=message, **default_style)

    def show(self):
        if self.widget.winfo_exists() and self.winfo_exists():
            super().show()

    def deiconify(self):
        if self.winfo_exists():
            super().deiconify()


# Popups
class StyledPopup(CTkMessagebox):
    def __init__(self, **kwargs):
        default_style = {
            "title": "Info",
            "icon": None,
            "header": False,
            "sound": True,
            "font": ctk.CTkFont(family="Verdana", size=14),
            "fg_color": "gray14",
            "bg_color": "gray14",
            "justify": "center",
            "wraplength": 300,
            "border_width": 0,
        }

        default_style.update(kwargs)
        super().__init__(**default_style)

        try:
            if hasattr(self, "title_label") and self.title_label:
                self.title_label.configure(fg_color=default_style["fg_color"])
        except Exception:
            pass