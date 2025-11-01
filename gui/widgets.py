"""Custom and reusable widget components for GUI"""

import customtkinter as ctk
from CTkToolTip import CTkToolTip

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