"""
Componentes de UI reutilizables
"""

import customtkinter as ctk
from ..config import LucqaColors

class ModernButton(ctk.CTkButton):
    """Botón moderno con estilo Lucqa"""
    
    def __init__(self, master, **kwargs):
        default_kwargs = {
            "font": ("Segoe UI", 14, "bold"),
            "height": 50,
            "corner_radius": 12,
            "fg_color": LucqaColors.PRIMARY,
            "hover_color": LucqaColors.SECONDARY,
            "text_color": LucqaColors.WHITE,
            "border_width": 0
        }
        default_kwargs.update(kwargs)
        super().__init__(master, **default_kwargs)

class ModernFrame(ctk.CTkFrame):
    """Frame moderno con estilo Lucqa"""
    
    def __init__(self, master, **kwargs):
        default_kwargs = {
            "corner_radius": 15,
            "fg_color": LucqaColors.SURFACE,
            "border_width": 1,
            "border_color": LucqaColors.GRAY_800
        }
        default_kwargs.update(kwargs)
        super().__init__(master, **default_kwargs)

class StatusIndicator(ctk.CTkFrame):
    """Indicador de estado con colores dinámicos"""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Listo",
            font=("Segoe UI", 11),
            text_color=LucqaColors.GRAY_200
        )
        self.status_label.pack(side="left", padx=5)
        
        self.indicator = ctk.CTkLabel(
            self,
            text="●",
            font=("Segoe UI", 16),
            text_color=LucqaColors.SUCCESS
        )
        self.indicator.pack(side="left")
    
    def set_status(self, status: str, message: str):
        """Actualizar el estado del indicador"""
        colors = {
            "success": LucqaColors.SUCCESS,
            "error": LucqaColors.ERROR,
            "warning": LucqaColors.WARNING,
            "loading": LucqaColors.PRIMARY
        }
        
        self.status_label.configure(text=message)
        self.indicator.configure(text_color=colors.get(status, LucqaColors.GRAY_200))