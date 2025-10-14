import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
import base64
import os
import tempfile
import subprocess
import platform

# Importar desde la configuración centralizada
from ..config import LucqaColors
from ..ui.components import ModernButton, ModernFrame

class PDFBase64ConverterApp:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.current_pdf_path = None
        self.current_pdf_data = None
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
            text="Conversor de PDF ↔ Base64",
            font=("Segoe UI", 24, "bold"),
            text_color=LucqaColors.WHITE
        )
        title_label.pack(pady=20)
        
        # Crear notebook para pestañas
        self.notebook = ctk.CTkTabview(self.parent_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Pestaña: PDF a Base64
        self.tab_pdf_to_b64 = self.notebook.add("PDF → Base64")
        self.create_pdf_to_base64_tab()
        
        # Pestaña: Base64 a PDF
        self.tab_b64_to_pdf = self.notebook.add("Base64 → PDF")
        self.create_base64_to_pdf_tab()
    
    def create_pdf_to_base64_tab(self):
        # Frame principal
        main_frame = ModernFrame(self.tab_pdf_to_b64)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sección de carga de PDF
        upload_frame = ModernFrame(main_frame)
        upload_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            upload_frame,
            text="Seleccionar Archivo PDF:",
            font=("Segoe UI", 16, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(pady=(15, 10))
        
        # Botones de carga
        button_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        self.load_pdf_btn = ModernButton(
            button_frame,
            text="📁 Cargar PDF",
            command=self.load_pdf_file,
            width=150
        )
        self.load_pdf_btn.pack(side="left", padx=10)
        
        self.clear_pdf_btn = ModernButton(
            button_frame,
            text="🗑️ Limpiar",
            command=self.clear_pdf_data,
            width=120,
            fg_color=LucqaColors.ERROR,
            hover_color="#DC2626"
        )
        self.clear_pdf_btn.pack(side="left", padx=10)
        
        self.preview_pdf_btn = ModernButton(
            button_frame,
            text="👁️ Vista Previa",
            command=self.preview_pdf,
            width=150,
            fg_color=LucqaColors.ACCENT,
            hover_color=LucqaColors.SECONDARY
        )
        self.preview_pdf_btn.pack(side="left", padx=10)
        
        # Información del PDF
        self.pdf_info_frame = ModernFrame(upload_frame)
        self.pdf_info_frame.pack(fill="x", padx=20, pady=10)
        
        self.pdf_info_label = ctk.CTkLabel(
            self.pdf_info_frame,
            text="No hay PDF cargado",
            font=("Segoe UI", 12),
            text_color=LucqaColors.GRAY_200,
            justify="left"
        )
        self.pdf_info_label.pack(pady=20)
        
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
            font=("Consolas", 9),
            fg_color=LucqaColors.BACKGROUND,
            text_color=LucqaColors.SUCCESS,
            border_color=LucqaColors.SUCCESS,
            border_width=2,
            wrap="word"
        )
        self.base64_output.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Botones de acción
        action_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.convert_to_b64_btn = ModernButton(
            action_frame,
            text="🔄 Convertir a Base64",
            command=self.convert_pdf_to_base64,
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
    
    def create_base64_to_pdf_tab(self):
        # Frame principal
        main_frame = ModernFrame(self.tab_b64_to_pdf)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Entrada de Base64
        input_frame = ModernFrame(main_frame)
        input_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            input_frame,
            text="Código Base64 del PDF:",
            font=("Segoe UI", 14, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.base64_input = ctk.CTkTextbox(
            input_frame,
            height=200,
            font=("Consolas", 9),
            fg_color=LucqaColors.BACKGROUND,
            text_color=LucqaColors.WHITE,
            border_color=LucqaColors.PRIMARY,
            border_width=2,
            wrap="word"
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
        
        self.validate_b64_btn = ModernButton(
            input_buttons_frame,
            text="✅ Validar Base64",
            command=self.validate_base64,
            width=150,
            fg_color=LucqaColors.WARNING,
            hover_color="#D97706"
        )
        self.validate_b64_btn.pack(side="left", padx=10)
        
        # Información del PDF decodificado
        info_frame = ModernFrame(main_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Información del PDF:",
            font=("Segoe UI", 14, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.decoded_pdf_info_label = ctk.CTkLabel(
            info_frame,
            text="Ingresa código Base64 y convierte",
            font=("Segoe UI", 12),
            text_color=LucqaColors.GRAY_200,
            justify="left"
        )
        self.decoded_pdf_info_label.pack(padx=20, pady=(0, 20))
        
        # Botones de acción
        action_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.convert_to_pdf_btn = ModernButton(
            action_frame,
            text="🔄 Convertir a PDF",
            command=self.convert_base64_to_pdf,
            width=180
        )
        self.convert_to_pdf_btn.pack(side="left", padx=(0, 10))
        
        self.save_pdf_btn = ModernButton(
            action_frame,
            text="💾 Guardar PDF",
            command=self.save_decoded_pdf,
            width=150,
            fg_color=LucqaColors.SUCCESS,
            hover_color="#059669"
        )
        self.save_pdf_btn.pack(side="left", padx=10)
        
        self.preview_decoded_pdf_btn = ModernButton(
            action_frame,
            text="👁️ Vista Previa",
            command=self.preview_decoded_pdf,
            width=150,
            fg_color=LucqaColors.ACCENT,
            hover_color=LucqaColors.SECONDARY
        )
        self.preview_decoded_pdf_btn.pack(side="left", padx=10)
    
    def load_pdf_file(self):
        """Cargar archivo PDF"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                self.current_pdf_path = file_path
                
                # Obtener información del archivo
                file_size = os.path.getsize(file_path)
                size_mb = file_size / (1024 * 1024)
                
                info_text = f"📄 Archivo: {os.path.basename(file_path)}\n"
                info_text += f"📊 Tamaño: {size_mb:.2f} MB ({file_size:,} bytes)\n"
                info_text += f"📁 Ruta: {file_path}"
                
                self.pdf_info_label.configure(text=info_text)
                
                messagebox.showinfo("Éxito", f"PDF cargado: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el PDF: {str(e)}")
    
    def convert_pdf_to_base64(self):
        """Convertir PDF a Base64"""
        if not self.current_pdf_path:
            messagebox.showwarning("Advertencia", "Primero carga un archivo PDF.")
            return
        
        try:
            with open(self.current_pdf_path, "rb") as pdf_file:
                # Leer archivo binario
                pdf_data = pdf_file.read()
                
                # Convertir a base64
                base64_string = base64.b64encode(pdf_data).decode('utf-8')
                
                # Agregar prefijo de data URL
                data_url = f"data:application/pdf;base64,{base64_string}"
                
                # Mostrar resultado
                self.base64_output.delete("1.0", tk.END)
                self.base64_output.insert("1.0", data_url)
                
                # Mostrar estadísticas
                original_size = len(pdf_data)
                base64_size = len(base64_string)
                increase_percent = ((base64_size - original_size) / original_size) * 100
                
                stats_msg = f"Conversión completada!\n\n"
                stats_msg += f"Tamaño original: {original_size:,} bytes\n"
                stats_msg += f"Tamaño Base64: {base64_size:,} caracteres\n"
                stats_msg += f"Incremento: {increase_percent:.1f}%"
                
                messagebox.showinfo("Éxito", stats_msg)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al convertir PDF: {str(e)}")
    
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
            
            # Sugerir nombre basado en el PDF original
            default_name = "pdf_base64.txt"
            if self.current_pdf_path:
                base_name = os.path.splitext(os.path.basename(self.current_pdf_path))[0]
                default_name = f"{base_name}_base64.txt"
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar Base64",
                initialfile=default_name,
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
    
    def validate_base64(self):
        """Validar si el texto es Base64 válido"""
        try:
            base64_text = self.base64_input.get("1.0", tk.END).strip()
            if not base64_text:
                messagebox.showwarning("Advertencia", "Ingresa código Base64.")
                return
            
            # Limpiar data URL si existe
            if base64_text.startswith('data:'):
                base64_text = base64_text.split(',', 1)[1]
            
            # Intentar decodificar
            decoded_data = base64.b64decode(base64_text)
            
            # Verificar si parece ser un PDF
            is_pdf = decoded_data.startswith(b'%PDF')
            
            info_text = f"✅ Base64 válido\n"
            info_text += f"📊 Tamaño decodificado: {len(decoded_data):,} bytes\n"
            info_text += f"📄 Formato: {'PDF detectado' if is_pdf else 'Formato desconocido'}"
            
            if not is_pdf:
                info_text += "\n⚠️ Advertencia: No parece ser un PDF válido"
            
            self.decoded_pdf_info_label.configure(text=info_text)
            
            messagebox.showinfo("Validación", "Base64 válido!" + (" (PDF detectado)" if is_pdf else " (Formato desconocido)"))
            
        except Exception as e:
            self.decoded_pdf_info_label.configure(text="❌ Base64 inválido")
            messagebox.showerror("Error", f"Base64 inválido: {str(e)}")
    
    def convert_base64_to_pdf(self):
        """Convertir Base64 a PDF"""
        try:
            base64_text = self.base64_input.get("1.0", tk.END).strip()
            if not base64_text:
                messagebox.showwarning("Advertencia", "Ingresa código Base64.")
                return
            
            # Limpiar data URL si existe
            if base64_text.startswith('data:'):
                base64_text = base64_text.split(',', 1)[1]
            
            # Decodificar Base64
            pdf_data = base64.b64decode(base64_text)
            
            # Verificar si es un PDF
            if not pdf_data.startswith(b'%PDF'):
                if not messagebox.askyesno("Advertencia", "El archivo no parece ser un PDF válido. ¿Continuar de todos modos?"):
                    return
            
            self.current_pdf_data = pdf_data
            
            # Mostrar información
            size_mb = len(pdf_data) / (1024 * 1024)
            info_text = f"✅ PDF decodificado exitosamente\n"
            info_text += f"📊 Tamaño: {size_mb:.2f} MB ({len(pdf_data):,} bytes)\n"
            info_text += f"📄 Formato: PDF válido"
            
            self.decoded_pdf_info_label.configure(text=info_text)
            
            messagebox.showinfo("Éxito", "Base64 convertido a PDF exitosamente!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al convertir Base64: {str(e)}\nVerifica que el código sea válido.")
    
    def save_decoded_pdf(self):
        """Guardar PDF decodificado"""
        if not self.current_pdf_data:
            messagebox.showwarning("Advertencia", "Primero convierte Base64 a PDF.")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                title="Guardar PDF",
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
            )
            
            if file_path:
                with open(file_path, "wb") as f:
                    f.write(self.current_pdf_data)
                
                messagebox.showinfo("Éxito", f"PDF guardado en: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar PDF: {str(e)}")
    
    def preview_pdf(self):
        """Vista previa del PDF cargado"""
        if not self.current_pdf_path:
            messagebox.showwarning("Advertencia", "Primero carga un archivo PDF.")
            return
        
        self._open_file(self.current_pdf_path)
    
    def preview_decoded_pdf(self):
        """Vista previa del PDF decodificado"""
        if not self.current_pdf_data:
            messagebox.showwarning("Advertencia", "Primero convierte Base64 a PDF.")
            return
        
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(self.current_pdf_data)
                temp_path = temp_file.name
            
            self._open_file(temp_path)
            
            # Programar eliminación del archivo temporal
            self.parent_frame.after(5000, lambda: self._cleanup_temp_file(temp_path))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear vista previa: {str(e)}")
    
    def _open_file(self, file_path):
        """Abrir archivo con la aplicación predeterminada del sistema"""
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {str(e)}")
    
    def _cleanup_temp_file(self, file_path):
        """Limpiar archivo temporal"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass  # Ignorar errores de limpieza
    
    def clear_pdf_data(self):
        """Limpiar datos de PDF"""
        self.current_pdf_path = None
        self.base64_output.delete("1.0", tk.END)
        self.pdf_info_label.configure(text="No hay PDF cargado")
    
    def clear_base64_input(self):
        """Limpiar entrada Base64"""
        self.base64_input.delete("1.0", tk.END)
        self.current_pdf_data = None
        self.decoded_pdf_info_label.configure(text="Ingresa código Base64 y convierte")

# Para uso independiente
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title("Conversor de PDF ↔ Base64")
    root.geometry("900x700")
    
    app = PDFBase64ConverterApp(root)
    root.mainloop()