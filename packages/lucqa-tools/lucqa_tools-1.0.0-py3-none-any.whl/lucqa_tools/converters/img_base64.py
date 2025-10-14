import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
import base64
from PIL import Image, ImageTk
import io
import os

# Importar desde la configuración centralizada
from ..config import LucqaColors
from ..ui.components import ModernButton, ModernFrame

class ImageBase64ConverterApp:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.current_image_path = None
        self.current_image_data = None
        self.build_ui()
    
    def build_ui(self):
        # Limpiar frame padre
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = ModernFrame(self.parent_frame)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Conversor de Imágenes ↔ Base64",
            font=("Segoe UI", 24, "bold"),
            text_color=LucqaColors.WHITE
        )
        title_label.pack(pady=20)
        
        # Crear notebook para pestañas
        self.notebook = ctk.CTkTabview(self.parent_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Pestaña: Imagen a Base64
        self.tab_img_to_b64 = self.notebook.add("Imagen → Base64")
        self.create_image_to_base64_tab()
        
        # Pestaña: Base64 a Imagen
        self.tab_b64_to_img = self.notebook.add("Base64 → Imagen")
        self.create_base64_to_image_tab()
    
    def create_image_to_base64_tab(self):
        # Frame principal
        main_frame = ModernFrame(self.tab_img_to_b64)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sección de carga de imagen
        upload_frame = ModernFrame(main_frame)
        upload_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            upload_frame,
            text="Seleccionar Imagen:",
            font=("Segoe UI", 16, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(pady=(15, 10))
        
        # Botones de carga
        button_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        self.load_image_btn = ModernButton(
            button_frame,
            text="📁 Cargar Imagen",
            command=self.load_image_file,
            width=150
        )
        self.load_image_btn.pack(side="left", padx=10)
        
        self.clear_image_btn = ModernButton(
            button_frame,
            text="🗑️ Limpiar",
            command=self.clear_image_data,
            width=120,
            fg_color=LucqaColors.ERROR,
            hover_color="#DC2626"
        )
        self.clear_image_btn.pack(side="left", padx=10)
        
        # Preview de imagen
        self.image_preview_frame = ModernFrame(upload_frame)
        self.image_preview_frame.pack(fill="x", padx=20, pady=10)
        
        self.image_preview_label = ctk.CTkLabel(
            self.image_preview_frame,
            text="No hay imagen cargada",
            font=("Segoe UI", 12),
            text_color=LucqaColors.GRAY_200
        )
        self.image_preview_label.pack(pady=20)
        
        # Información de la imagen
        self.image_info_label = ctk.CTkLabel(
            upload_frame,
            text="",
            font=("Segoe UI", 10),
            text_color=LucqaColors.GRAY_200
        )
        self.image_info_label.pack(pady=(0, 15))
        
        # Resultado Base64
        result_frame = ModernFrame(main_frame)
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            result_frame,
            text="Resultado Base64:",
            font=("Segoe UI", 14, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.base64_output = ctk.CTkTextbox(
            result_frame,
            height=200,
            font=("Consolas", 10),
            fg_color=LucqaColors.BACKGROUND,
            text_color=LucqaColors.SUCCESS,
            border_color=LucqaColors.SUCCESS,
            border_width=2
        )
        self.base64_output.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Botones de acción
        action_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.convert_to_b64_btn = ModernButton(
            action_frame,
            text="🔄 Convertir a Base64",
            command=self.convert_image_to_base64,
            width=180
        )
        self.convert_to_b64_btn.pack(side="left", padx=(0, 10))
        
        self.copy_b64_btn = ModernButton(
            action_frame,
            text="📋 Copiar Base64",
            command=self.copy_base64_result,
            width=150,
            fg_color=LucqaColors.SUCCESS,
            hover_color="#059669"
        )
        self.copy_b64_btn.pack(side="left", padx=10)
        
        self.save_b64_btn = ModernButton(
            action_frame,
            text="💾 Guardar Base64",
            command=self.save_base64_to_file,
            width=150,
            fg_color=LucqaColors.ACCENT,
            hover_color=LucqaColors.SECONDARY
        )
        self.save_b64_btn.pack(side="left", padx=10)
    
    def create_base64_to_image_tab(self):
        # Frame principal
        main_frame = ModernFrame(self.tab_b64_to_img)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Entrada de Base64
        input_frame = ModernFrame(main_frame)
        input_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            input_frame,
            text="Código Base64:",
            font=("Segoe UI", 14, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.base64_input = ctk.CTkTextbox(
            input_frame,
            height=150,
            font=("Consolas", 10),
            fg_color=LucqaColors.BACKGROUND,
            text_color=LucqaColors.WHITE,
            border_color=LucqaColors.PRIMARY,
            border_width=2
        )
        self.base64_input.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Botones de entrada
        input_buttons_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_buttons_frame.pack(fill="x", padx=20, pady=10)
        
        self.load_b64_file_btn = ModernButton(
            input_buttons_frame,
            text="📁 Cargar desde Archivo",
            command=self.load_base64_from_file,
            width=180
        )
        self.load_b64_file_btn.pack(side="left", padx=(0, 10))
        
        self.clear_b64_btn = ModernButton(
            input_buttons_frame,
            text="🗑️ Limpiar",
            command=self.clear_base64_input,
            width=120,
            fg_color=LucqaColors.ERROR,
            hover_color="#DC2626"
        )
        self.clear_b64_btn.pack(side="left", padx=10)
        
        # Preview de imagen decodificada
        preview_frame = ModernFrame(main_frame)
        preview_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            preview_frame,
            text="Vista Previa:",
            font=("Segoe UI", 14, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.decoded_image_frame = ModernFrame(preview_frame)
        self.decoded_image_frame.pack(fill="x", padx=20, pady=10)
        
        self.decoded_image_label = ctk.CTkLabel(
            self.decoded_image_frame,
            text="Ingresa código Base64 y convierte",
            font=("Segoe UI", 12),
            text_color=LucqaColors.GRAY_200
        )
        self.decoded_image_label.pack(pady=20)
        
        # Botones de acción
        action_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        self.convert_to_img_btn = ModernButton(
            action_frame,
            text="🔄 Convertir a Imagen",
            command=self.convert_base64_to_image,
            width=180
        )
        self.convert_to_img_btn.pack(side="left", padx=(0, 10))
        
        self.save_img_btn = ModernButton(
            action_frame,
            text="💾 Guardar Imagen",
            command=self.save_decoded_image,
            width=150,
            fg_color=LucqaColors.SUCCESS,
            hover_color="#059669"
        )
        self.save_img_btn.pack(side="left", padx=10)
    
    def load_image_file(self):
        """Cargar archivo de imagen"""
        file_types = [
            ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("GIF", "*.gif"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff"),
            ("WebP", "*.webp"),
            ("Todos los archivos", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=file_types
        )
        
        if file_path:
            try:
                # Cargar y mostrar información de la imagen
                with Image.open(file_path) as img:
                    self.current_image_path = file_path
                    
                    # Mostrar información
                    file_size = os.path.getsize(file_path)
                    size_mb = file_size / (1024 * 1024)
                    
                    info_text = f"Archivo: {os.path.basename(file_path)}\n"
                    info_text += f"Dimensiones: {img.size[0]} x {img.size[1]} px\n"
                    info_text += f"Formato: {img.format}\n"
                    info_text += f"Modo: {img.mode}\n"
                    info_text += f"Tamaño: {size_mb:.2f} MB"
                    
                    self.image_info_label.configure(text=info_text)
                    
                    # Crear preview
                    self.create_image_preview(img)
                    
                    messagebox.showinfo("Éxito", f"Imagen cargada: {os.path.basename(file_path)}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")
    
    def create_image_preview(self, img):
        """Crear vista previa de la imagen"""
        try:
            # Redimensionar para preview manteniendo proporción
            max_size = (200, 200)
            img_copy = img.copy()
            img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convertir para tkinter
            photo = ImageTk.PhotoImage(img_copy)
            
            # Actualizar label
            self.image_preview_label.configure(
                image=photo,
                text=""
            )
            self.image_preview_label.image = photo  # Mantener referencia
            
        except Exception as e:
            print(f"Error creando preview: {e}")
    
    def convert_image_to_base64(self):
        """Convertir imagen a Base64"""
        if not self.current_image_path:
            messagebox.showwarning("Advertencia", "Primero carga una imagen.")
            return
        
        try:
            with open(self.current_image_path, "rb") as image_file:
                # Leer archivo binario
                image_data = image_file.read()
                
                # Convertir a base64
                base64_string = base64.b64encode(image_data).decode('utf-8')
                
                # Agregar prefijo de data URL (opcional)
                file_ext = os.path.splitext(self.current_image_path)[1].lower()
                mime_types = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.bmp': 'image/bmp',
                    '.webp': 'image/webp'
                }
                
                mime_type = mime_types.get(file_ext, 'image/png')
                data_url = f"data:{mime_type};base64,{base64_string}"
                
                # Mostrar resultado
                self.base64_output.delete("1.0", tk.END)
                self.base64_output.insert("1.0", data_url)
                
                messagebox.showinfo("Éxito", "Imagen convertida a Base64 exitosamente!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al convertir imagen: {str(e)}")
    
    def copy_base64_result(self):
        """Copiar resultado Base64 al portapapeles"""
        try:
            result = self.base64_output.get("1.0", tk.END).strip()
            if result:
                self.parent_frame.clipboard_clear()
                self.parent_frame.clipboard_append(result)
                messagebox.showinfo("Éxito", "Base64 copiado al portapapeles!")
            else:
                messagebox.showwarning("Advertencia", "No hay Base64 para copiar.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al copiar: {str(e)}")
    
    def save_base64_to_file(self):
        """Guardar Base64 en archivo de texto"""
        try:
            result = self.base64_output.get("1.0", tk.END).strip()
            if not result:
                messagebox.showwarning("Advertencia", "No hay Base64 para guardar.")
                return
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar Base64",
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(result)
                messagebox.showinfo("Éxito", f"Base64 guardado en: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def load_base64_from_file(self):
        """Cargar Base64 desde archivo"""
        file_path = filedialog.askopenfilename(
            title="Cargar archivo Base64",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                
                self.base64_input.delete("1.0", tk.END)
                self.base64_input.insert("1.0", content)
                
                messagebox.showinfo("Éxito", "Base64 cargado desde archivo!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")
    
    def convert_base64_to_image(self):
        """Convertir Base64 a imagen"""
        try:
            base64_text = self.base64_input.get("1.0", tk.END).strip()
            if not base64_text:
                messagebox.showwarning("Advertencia", "Ingresa código Base64.")
                return
            
            # Limpiar data URL si existe
            if base64_text.startswith('data:'):
                base64_text = base64_text.split(',', 1)[1]
            
            # Decodificar Base64
            image_data = base64.b64decode(base64_text)
            
            # Crear imagen desde bytes
            image = Image.open(io.BytesIO(image_data))
            self.current_image_data = image_data
            
            # Crear preview
            self.create_decoded_image_preview(image)
            
            messagebox.showinfo("Éxito", "Base64 convertido a imagen exitosamente!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al convertir Base64: {str(e)}\nVerifica que el código sea válido.")
    
    def create_decoded_image_preview(self, img):
        """Crear vista previa de la imagen decodificada"""
        try:
            # Redimensionar para preview
            max_size = (200, 200)
            img_copy = img.copy()
            img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convertir para tkinter
            photo = ImageTk.PhotoImage(img_copy)
            
            # Actualizar label
            self.decoded_image_label.configure(
                image=photo,
                text=""
            )
            self.decoded_image_label.image = photo  # Mantener referencia
            
        except Exception as e:
            print(f"Error creando preview decodificado: {e}")
    
    def save_decoded_image(self):
        """Guardar imagen decodificada"""
        if not self.current_image_data:
            messagebox.showwarning("Advertencia", "Primero convierte Base64 a imagen.")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                title="Guardar imagen",
                defaultextension=".png",
                filetypes=[
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg"),
                    ("GIF", "*.gif"),
                    ("BMP", "*.bmp"),
                    ("Todos los archivos", "*.*")
                ]
            )
            
            if file_path:
                with open(file_path, "wb") as f:
                    f.write(self.current_image_data)
                
                messagebox.showinfo("Éxito", f"Imagen guardada en: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar imagen: {str(e)}")
    
    def clear_image_data(self):
        """Limpiar datos de imagen"""
        self.current_image_path = None
        self.base64_output.delete("1.0", tk.END)
        self.image_info_label.configure(text="")
        self.image_preview_label.configure(image="", text="No hay imagen cargada")
        if hasattr(self.image_preview_label, 'image'):
            self.image_preview_label.image = None
    
    def clear_base64_input(self):
        """Limpiar entrada Base64"""
        self.base64_input.delete("1.0", tk.END)
        self.current_image_data = None
        self.decoded_image_label.configure(image="", text="Ingresa código Base64 y convierte")
        if hasattr(self.decoded_image_label, 'image'):
            self.decoded_image_label.image = None

# Para uso independiente
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title("Conversor de Imágenes ↔ Base64")
    root.geometry("900x700")
    
    app = ImageBase64ConverterApp(root)
    root.mainloop()