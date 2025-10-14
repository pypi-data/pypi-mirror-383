"""
Conversor de texto Base64
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import base64
from ..config import LucqaColors
from .components import ModernButton, ModernFrame

class Base64ConverterApp:
    """Aplicación para convertir texto a/desde Base64"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.build_ui()
    
    def build_ui(self):
        """Construir la interfaz de usuario"""
        # Limpiar frame padre
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = ModernFrame(self.parent_frame)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Conversor Base64",
            font=("Segoe UI", 24, "bold"),
            text_color=LucqaColors.WHITE
        )
        title_label.pack(pady=20)
        
        # Área de entrada
        input_frame = ModernFrame(self.parent_frame)
        input_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Texto a codificar
        ctk.CTkLabel(
            input_frame,
            text="Texto a convertir:",
            font=("Segoe UI", 14, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.input_text = ctk.CTkTextbox(
            input_frame,
            height=150,
            font=("Consolas", 12),
            fg_color=LucqaColors.BACKGROUND,
            text_color=LucqaColors.WHITE,
            border_color=LucqaColors.PRIMARY,
            border_width=2
        )
        self.input_text.pack(fill="x", padx=20, pady=(0, 10))
        
        # Botones de acción
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        encode_btn = ModernButton(
            button_frame,
            text="Codificar a Base64",
            command=self.encode_to_base64,
            width=200
        )
        encode_btn.pack(side="left", padx=(0, 10))
        
        decode_btn = ModernButton(
            button_frame,
            text="Decodificar desde Base64",
            command=self.decode_from_base64,
            width=200,
            fg_color=LucqaColors.ACCENT,
            hover_color=LucqaColors.SECONDARY
        )
        decode_btn.pack(side="left", padx=10)
        
        clear_btn = ModernButton(
            button_frame,
            text="Limpiar",
            command=self.clear_all,
            width=120,
            fg_color=LucqaColors.ERROR,
            hover_color="#DC2626"
        )
        clear_btn.pack(side="right")
        
        # Resultado
        ctk.CTkLabel(
            input_frame,
            text="Resultado:",
            font=("Segoe UI", 14, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.output_text = ctk.CTkTextbox(
            input_frame,
            height=150,
            font=("Consolas", 12),
            fg_color=LucqaColors.BACKGROUND,
            text_color=LucqaColors.SUCCESS,
            border_color=LucqaColors.SUCCESS,
            border_width=2
        )
        self.output_text.pack(fill="x", padx=20, pady=(0, 20))
        
        # Botón copiar resultado
        copy_btn = ModernButton(
            input_frame,
            text="Copiar Resultado",
            command=self.copy_result,
            width=150,
            fg_color=LucqaColors.SUCCESS,
            hover_color="#059669"
        )
        copy_btn.pack(pady=(0, 20))
    
    def encode_to_base64(self):
        """Codificar texto a Base64"""
        try:
            text = self.input_text.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Advertencia", "Por favor ingresa texto para codificar.")
                return
            
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", encoded)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al codificar: {str(e)}")
    
    def decode_from_base64(self):
        """Decodificar texto desde Base64"""
        try:
            text = self.input_text.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Advertencia", "Por favor ingresa texto Base64 para decodificar.")
                return
            
            decoded = base64.b64decode(text).decode('utf-8')
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", decoded)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al decodificar: {str(e)}\nVerifica que el texto sea Base64 válido.")
    
    def clear_all(self):
        """Limpiar todos los campos"""
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
    
    def copy_result(self):
        """Copiar resultado al portapapeles"""
        try:
            result = self.output_text.get("1.0", tk.END).strip()
            if result:
                self.parent_frame.clipboard_clear()
                self.parent_frame.clipboard_append(result)
                messagebox.showinfo("Éxito", "Resultado copiado al portapapeles!")
            else:
                messagebox.showwarning("Advertencia", "No hay resultado para copiar.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al copiar: {str(e)}")