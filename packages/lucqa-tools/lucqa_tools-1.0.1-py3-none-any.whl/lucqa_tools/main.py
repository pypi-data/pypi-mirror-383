"""
Aplicación principal de Lucqa Tools
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import os
from PIL import Image

from .config import LucqaColors, AppConfig
from .ui.components import ModernButton, ModernFrame
from .ui.base64_converter import Base64ConverterApp

# Importar módulos opcionales
try:
    from .kubernetes import K8sLogViewerUI, K8sLogic
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False

try:
    from .converters.img_base64 import ImageBase64ConverterApp
    IMG_CONVERTER_AVAILABLE = True
except ImportError:
    IMG_CONVERTER_AVAILABLE = False

try:
    from .converters.base64_pdf import PDFBase64ConverterApp  # Corregir nombre del import
    PDF_CONVERTER_AVAILABLE = True
except ImportError:
    PDF_CONVERTER_AVAILABLE = False

class MainApp:
    """Aplicación principal de Lucqa Tools"""
    
    def __init__(self):
        # Configurar CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title(AppConfig.WINDOW_TITLE)
        self.root.geometry(AppConfig.WINDOW_SIZE)
        self.root.configure(fg_color=LucqaColors.BACKGROUND)
        
        # Variables
        self.current_app = None
        
        self.setup_ui()
        self.show_main_menu()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Header con logo
        self.create_header()
        
        # Área principal
        self.main_frame = ModernFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def create_header(self):
        """Crear el header de la aplicación"""
        header_frame = ModernFrame(self.root)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        # Cargar logo
        logo_image = self.load_logo_image()
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=20)
        
        if logo_image:
            logo_label = ctk.CTkLabel(
                title_frame,
                image=logo_image,
                text=""
            )
            logo_label.pack(side="left", padx=(20, 15))
        
        # Títulos
        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        
        main_title = ctk.CTkLabel(
            text_frame,
            text=AppConfig.APP_NAME,
            font=("Segoe UI", 28, "bold"),
            text_color=LucqaColors.WHITE
        )
        main_title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            text_frame,
            text="Suite de Herramientas para Desarrollo",
            font=("Segoe UI", 14),
            text_color=LucqaColors.GRAY_200
        )
        subtitle.pack(anchor="w")
        
        # Botón volver al menú
        self.back_button = ModernButton(
            title_frame,
            text="← Menú Principal",
            command=self.show_main_menu,
            width=150,
            fg_color=LucqaColors.GRAY_800,
            hover_color=LucqaColors.PRIMARY
        )
        self.back_button.pack(side="right", padx=20)
        self.back_button.pack_forget()  # Ocultar inicialmente
    
    def load_logo_image(self):
        """Cargar la imagen del logo"""
        try:
            # Obtener la ruta del directorio del módulo actual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Buscar logo en diferentes ubicaciones
            possible_paths = [
                os.path.join(current_dir, "assets", "img", "logo.png"),
                os.path.join(current_dir, "..", "assets", "img", "logo.png"),
                os.path.join("assets", "img", "logo.png"),
                os.path.join("img", "logo.png"),
                "logo.png"
            ]
            
            logo_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = path
                    print(f"Logo encontrado en: {path}")
                    break
            
            if logo_path:
                image = Image.open(logo_path)
                
                # Mantener proporción y redimensionar
                max_size = 50
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convertir a RGBA para mejor compatibilidad
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                return ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            else:
                print("Logo no encontrado en ninguna ubicación")
                print(f"Directorio actual: {current_dir}")
                return None
        except Exception as e:
            print(f"Error cargando logo: {e}")
            return None
    
    def show_main_menu(self):
        """Mostrar el menú principal"""
        # Limpiar frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Ocultar botón de volver
        self.back_button.pack_forget()
        
        # Título del menú
        menu_title = ctk.CTkLabel(
            self.main_frame,
            text="Selecciona una Herramienta",
            font=("Segoe UI", 24, "bold"),
            text_color=LucqaColors.WHITE
        )
        menu_title.pack(pady=(40, 30))
        
        # Grid de botones
        buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        buttons_frame.pack(expand=True)
        
        # Botón Kubernetes Log Viewer
        k8s_status = "Disponible" if K8S_AVAILABLE else "Requiere kubernetes"
        k8s_color = LucqaColors.PRIMARY if K8S_AVAILABLE else LucqaColors.GRAY_800
        
        k8s_button = ModernButton(
            buttons_frame,
            text=f"🚀 Kubernetes Log Viewer\n{k8s_status}",
            command=self.show_k8s_viewer,
            width=300,
            height=100,
            fg_color=k8s_color,
            state="normal" if K8S_AVAILABLE else "disabled"
        )
        k8s_button.grid(row=0, column=0, padx=20, pady=20)
        
        # Botón Base64 Converter
        base64_button = ModernButton(
            buttons_frame,
            text="🔐 Conversor Base64\nCodificar/Decodificar texto",
            command=self.show_base64_converter,
            width=300,
            height=100,
            fg_color=LucqaColors.ACCENT
        )
        base64_button.grid(row=0, column=1, padx=20, pady=20)
        
        # Botón Image Converter
        img_status = "Disponible" if IMG_CONVERTER_AVAILABLE else "Módulo opcional"
        img_color = LucqaColors.SUCCESS if IMG_CONVERTER_AVAILABLE else LucqaColors.GRAY_800
        
        img_button = ModernButton(
            buttons_frame,
            text=f"🖼️ Conversor de Imágenes\n{img_status}",
            command=self.show_img_converter,
            width=300,
            height=100,
            fg_color=img_color,
            state="normal" if IMG_CONVERTER_AVAILABLE else "disabled"
        )
        img_button.grid(row=1, column=0, padx=20, pady=20)
        
        # Botón PDF Converter
        pdf_status = "Disponible" if PDF_CONVERTER_AVAILABLE else "Módulo opcional"
        pdf_color = LucqaColors.WARNING if PDF_CONVERTER_AVAILABLE else LucqaColors.GRAY_800
        
        pdf_button = ModernButton(
            buttons_frame,
            text=f"📄 Conversor de PDF\n{pdf_status}",
            command=self.show_pdf_converter,
            width=300,
            height=100,
            fg_color=pdf_color,
            state="normal" if PDF_CONVERTER_AVAILABLE else "disabled"
        )
        pdf_button.grid(row=1, column=1, padx=20, pady=20)
        
        # Información adicional
        info_frame = ModernFrame(self.main_frame)
        info_frame.pack(fill="x", padx=40, pady=(40, 20))
        
        info_text = f"""
        💡 Herramientas Disponibles:
        
        • Kubernetes Log Viewer: Visualiza y gestiona logs de pods en clusters de Kubernetes
        • Conversor Base64: Codifica y decodifica texto en formato Base64
        • Conversor de Imágenes: Convierte imágenes a/desde Base64
        • Conversor de PDF: Convierte archivos PDF a/desde Base64
        
        🔧 Desarrollado con Python + CustomTkinter | v{AppConfig.APP_VERSION}
        """
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Segoe UI", 12),
            text_color=LucqaColors.GRAY_200,
            justify="left"
        )
        info_label.pack(pady=20)
    
    def show_k8s_viewer(self):
        """Mostrar el visor de Kubernetes"""
        if not K8S_AVAILABLE:
            messagebox.showerror(
                "Error", 
                "El módulo de Kubernetes no está disponible.\n"
                "Instala las dependencias: pip install kubernetes"
            )
            return
        
        # Mostrar botón de volver
        self.back_button.pack(side="right", padx=20)
        
        # Crear instancia del visor de K8s
        try:
            self.current_app = K8sLogViewerUI(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar K8s Log Viewer: {str(e)}")
            self.show_main_menu()
    
    def show_base64_converter(self):
        """Mostrar el conversor Base64"""
        # Mostrar botón de volver
        self.back_button.pack(side="right", padx=20)
        
        # Crear instancia del conversor Base64
        self.current_app = Base64ConverterApp(self.main_frame)
    
    def show_img_converter(self):
        """Mostrar el conversor de imágenes"""
        if not IMG_CONVERTER_AVAILABLE:
            messagebox.showerror(
                "Error", 
                "El conversor de imágenes no está disponible.\n"
                "Módulo en desarrollo."
            )
            return
        
        # Mostrar botón de volver
        self.back_button.pack(side="right", padx=20)
        
        # Crear instancia del conversor de imágenes
        try:
            self.current_app = ImageBase64ConverterApp(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar conversor de imágenes: {str(e)}")
            self.show_main_menu()
    
    def show_pdf_converter(self):
        """Mostrar el conversor de PDF"""
        if not PDF_CONVERTER_AVAILABLE:
            messagebox.showerror(
                "Error", 
                "El conversor de PDF no está disponible.\n"
                "Módulo en desarrollo."
            )
            return
        
        # Mostrar botón de volver
        self.back_button.pack(side="right", padx=20)
        
        # Crear instancia del conversor de PDF
        try:
            self.current_app = PDFBase64ConverterApp(self.main_frame)
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar conversor de PDF: {str(e)}")
            self.show_main_menu()
    
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()

def main():
    """Función principal para entry point"""
    app = MainApp()
    app.run()

if __name__ == "__main__":
    main()