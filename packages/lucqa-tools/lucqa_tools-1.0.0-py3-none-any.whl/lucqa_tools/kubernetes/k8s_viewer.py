"""
Interfaz de usuario para el visor de logs de Kubernetes
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from typing import List, Optional
import time
import os

from ..config import LucqaColors
from ..ui.components import ModernButton, ModernFrame, StatusIndicator
from .k8s_logic import K8sLogic


class K8sLogViewerUI:
    """Interfaz de usuario para el visor de logs de Kubernetes"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.k8s_logic = K8sLogic()
        
        # Variables de UI
        self.current_context = tk.StringVar()
        self.current_namespace = tk.StringVar()
        self.current_pod_name = None
        self.auto_refresh_active = False
        self.follow_logs_var = tk.BooleanVar()
        
        self.build_ui()
        self.initialize_app()
    
    def build_ui(self):
        # Limpiar frame padre
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Header
        self.create_header()
        
        # Panel de control
        self.create_control_panel()
        
        # Panel de pods
        self.create_pods_panel()
        
        # Panel de logs
        self.create_logs_panel()
        
        # Footer con estado
        self.create_footer()
    
    def create_header(self):
        header_frame = ModernFrame(self.parent_frame)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Kubernetes Log Viewer",
            font=("Segoe UI", 20, "bold"),
            text_color=LucqaColors.WHITE
        )
        title_label.pack(pady=15)
    
    def create_control_panel(self):
        control_frame = ModernFrame(self.parent_frame)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # Primera fila - Selectores
        row1_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        row1_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        # Selector de contexto
        ctk.CTkLabel(
            row1_frame,
            text="Cluster:",
            font=("Segoe UI", 12, "bold"),
            text_color=LucqaColors.WHITE
        ).grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        
        self.context_menu = ctk.CTkOptionMenu(
            row1_frame,
            values=["Cargando..."],
            variable=self.current_context,
            command=self.on_context_change,
            width=200,
            fg_color=LucqaColors.PRIMARY,
            button_color=LucqaColors.SECONDARY,
            button_hover_color=LucqaColors.ACCENT
        )
        self.context_menu.grid(row=0, column=1, padx=5, pady=5)
        
        # Selector de namespace
        ctk.CTkLabel(
            row1_frame,
            text="Namespace:",
            font=("Segoe UI", 12, "bold"),
            text_color=LucqaColors.WHITE
        ).grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        
        self.namespace_menu = ctk.CTkOptionMenu(
            row1_frame,
            values=["Selecciona contexto"],
            variable=self.current_namespace,
            command=self.on_namespace_change,
            width=200,
            fg_color=LucqaColors.PRIMARY,
            button_color=LucqaColors.SECONDARY,
            button_hover_color=LucqaColors.ACCENT
        )
        self.namespace_menu.grid(row=0, column=3, padx=5, pady=5)
        
        # Segunda fila - Botones de acción
        row2_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        row2_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.refresh_button = ModernButton(
            row2_frame,
            text="Cargar Pods",
            command=self.load_pods_async,
            width=120
        )
        self.refresh_button.pack(side="left", padx=(0, 10))
        
        self.logs_button = ModernButton(
            row2_frame,
            text="Obtener Logs",
            command=self.show_logs_async,
            width=120
        )
        self.logs_button.pack(side="left", padx=10)
        
        self.save_button = ModernButton(
            row2_frame,
            text="Guardar Logs",
            command=self.save_logs,
            width=120,
            fg_color=LucqaColors.SUCCESS,
            hover_color="#059669"
        )
        self.save_button.pack(side="left", padx=10)
        
        self.clear_button = ModernButton(
            row2_frame,
            text="Limpiar",
            command=self.clear_logs,
            width=100,
            fg_color=LucqaColors.ERROR,
            hover_color="#DC2626"
        )
        self.clear_button.pack(side="left", padx=10)
        
        # Opciones adicionales
        options_frame = ctk.CTkFrame(row2_frame, fg_color="transparent")
        options_frame.pack(side="right")
        
        self.follow_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="Auto-scroll",
            variable=self.follow_logs_var,
            font=("Segoe UI", 11),
            text_color=LucqaColors.WHITE,
            fg_color=LucqaColors.PRIMARY,
            hover_color=LucqaColors.SECONDARY
        )
        self.follow_checkbox.pack(side="right", padx=10)
    
    def create_pods_panel(self):
        pods_frame = ModernFrame(self.parent_frame)
        pods_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            pods_frame,
            text="Pods Disponibles:",
            font=("Segoe UI", 14, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        # Frame para la lista con scrollbar
        list_frame = ctk.CTkFrame(pods_frame, fg_color=LucqaColors.BACKGROUND)
        list_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.pod_listbox = tk.Listbox(
            list_frame,
            height=8,
            bg=LucqaColors.BACKGROUND,
            fg=LucqaColors.WHITE,
            selectbackground=LucqaColors.PRIMARY,
            selectforeground=LucqaColors.WHITE,
            font=("Consolas", 10),
            borderwidth=0,
            highlightthickness=0
        )
        self.pod_listbox.pack(fill="x", padx=5, pady=5)
        self.pod_listbox.bind('<<ListboxSelect>>', self.on_pod_select)
    
    def create_logs_panel(self):
        logs_frame = ModernFrame(self.parent_frame)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            logs_frame,
            text="Logs:",
            font=("Segoe UI", 14, "bold"),
            text_color=LucqaColors.WHITE
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        # Frame para el texto con scrollbar
        text_frame = ctk.CTkFrame(logs_frame, fg_color=LucqaColors.BACKGROUND)
        text_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.log_text = tk.Text(
            text_frame,
            bg=LucqaColors.BACKGROUND,
            fg=LucqaColors.WHITE,
            insertbackground=LucqaColors.WHITE,
            font=("Consolas", 10),
            wrap="word",
            borderwidth=0,
            highlightthickness=0
        )
        
        # Scrollbar para el texto
        scrollbar = tk.Scrollbar(text_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Texto inicial
        self.log_text.insert(tk.END, "Selecciona un pod y obtén sus logs...")
    
    def create_footer(self):
        footer_frame = ModernFrame(self.parent_frame)
        footer_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.status_indicator = StatusIndicator(footer_frame)
        self.status_indicator.pack(side="left", padx=15, pady=10)
        
        # Información adicional
        info_label = ctk.CTkLabel(
            footer_frame,
            text="Powered by Lucqa",
            font=("Segoe UI", 10),
            text_color=LucqaColors.GRAY_200
        )
        info_label.pack(side="right", padx=15, pady=10)
    
    def initialize_app(self):
        """Inicializar la aplicación cargando kubeconfig"""
        self.status_indicator.set_status("loading", "Inicializando...")
        threading.Thread(target=self._initialize_k8s, daemon=True).start()
    
    def _initialize_k8s(self):
        """Inicializar Kubernetes en hilo separado"""
        success, message = self.k8s_logic.load_kubeconfig()
        
        def update_ui():
            if success:
                self.context_menu.configure(values=self.k8s_logic.contexts)
                self.current_context.set(self.k8s_logic.current_context)
                self.status_indicator.set_status("success", message)
                
                # Cargar cliente para el contexto actual
                self.on_context_change(self.k8s_logic.current_context)
            else:
                self.status_indicator.set_status("error", message)
                messagebox.showerror("Error", message)
        
        self.parent_frame.after(0, update_ui)
    
    def on_context_change(self, context):
        """Cambio de cluster/contexto"""
        threading.Thread(target=self._change_context, args=(context,), daemon=True).start()
    
    def _change_context(self, context):
        """Cambiar contexto en hilo separado"""
        self.status_indicator.set_status("loading", f"Conectando a {context}...")
        
        success, message = self.k8s_logic.load_client_for_context(context)
        
        def update_ui():
            if success:
                self.status_indicator.set_status("success", message)
                success_ns, message_ns = self.k8s_logic.load_namespaces()
                
                if success_ns:
                    self.namespace_menu.configure(values=self.k8s_logic.namespaces)
                    default_ns = "default" if "default" in self.k8s_logic.namespaces else self.k8s_logic.namespaces[0]
                    self.current_namespace.set(default_ns)
                else:
                    self.status_indicator.set_status("error", message_ns)
            else:
                self.status_indicator.set_status("error", message)
                messagebox.showerror("Error", message)
        
        self.parent_frame.after(0, update_ui)
    
    def on_namespace_change(self, namespace):
        """Cambio de namespace"""
        self.pod_listbox.delete(0, tk.END)
        self.status_indicator.set_status("success", f"Namespace cambiado a: {namespace}")
    
    def load_pods_async(self):
        """Cargar pods de forma asíncrona"""
        namespace = self.current_namespace.get()
        if not namespace:
            messagebox.showwarning("Advertencia", "Selecciona un namespace primero.")
            return
        
        self.refresh_button.configure(state="disabled", text="Cargando...")
        threading.Thread(target=self._load_pods, args=(namespace,), daemon=True).start()
    
    def _load_pods(self, namespace):
        """Cargar pods en hilo separado"""
        self.status_indicator.set_status("loading", f"Cargando pods de {namespace}...")
        
        success, message, pods = self.k8s_logic.load_pods(namespace)
        
        def update_ui():
            self.refresh_button.configure(state="normal", text="Cargar Pods")
            
            if success:
                self.pod_listbox.delete(0, tk.END)
                for pod in pods:
                    self.pod_listbox.insert(tk.END, pod)
                
                self.status_indicator.set_status("success", message)
                
                if not pods:
                    self.status_indicator.set_status("warning", f"No se encontraron pods en {namespace}")
            else:
                self.status_indicator.set_status("error", message)
                messagebox.showerror("Error", message)
        
        self.parent_frame.after(0, update_ui)
    
    def on_pod_select(self, event):
        """Selección de pod"""
        selection = self.pod_listbox.curselection()
        if selection:
            pod_name = self.pod_listbox.get(selection[0])
            self.current_pod_name = pod_name
            self.status_indicator.set_status("success", f"Pod seleccionado: {pod_name}")
    
    def show_logs_async(self):
        """Mostrar logs de forma asíncrona"""
        if not self.current_pod_name:
            messagebox.showwarning("Advertencia", "Selecciona un pod primero.")
            return
        
        namespace = self.current_namespace.get()
        self.logs_button.configure(state="disabled", text="Obteniendo...")
        threading.Thread(target=self._fetch_logs, args=(self.current_pod_name, namespace), daemon=True).start()
    
    def _fetch_logs(self, pod_name, namespace):
        """Obtener logs en hilo separado"""
        success, logs = self.k8s_logic.get_pod_logs(pod_name, namespace)
        
        def update_ui():
            self.logs_button.configure(state="normal", text="Obtener Logs")
            
            if success:
                self.status_indicator.set_status("success", f"Logs obtenidos de {pod_name}")
                self.log_text.delete(1.0, tk.END)
                
                # Agregar header con información del pod
                header = f"{'='*80}\n"
                header += f"LOGS DEL POD: {pod_name}\n"
                header += f"NAMESPACE: {namespace}\n"
                header += f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                header += f"{'='*80}\n\n"
                
                self.log_text.insert(tk.END, header)
                self.log_text.insert(tk.END, logs)
                
                # Auto-scroll si está habilitado
                if self.follow_logs_var.get():
                    self.log_text.see(tk.END)
            else:
                self.status_indicator.set_status("error", logs)
                messagebox.showerror("Error", logs)
                
        self.parent_frame.after(0, update_ui)
    
    def clear_logs(self):
        """Limpiar área de logs"""
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Logs limpiados - Selecciona un pod y obtén sus logs")
        self.status_indicator.set_status("success", "Logs limpiados")
    
    def save_logs(self):
        """Guardar logs en archivo usando el nombre del pod"""
        logs = self.log_text.get(1.0, tk.END).strip()
        if not logs or logs == "Logs limpiados - Selecciona un pod y obtén sus logs":
            messagebox.showinfo("Aviso", "No hay logs para guardar.")
            return
        
        # Generar nombre de archivo por defecto usando el pod actual
        default_filename = "kubernetes_logs.log"
        if self.current_pod_name:
            # Limpiar el nombre del pod para usar como nombre de archivo
            safe_pod_name = "".join(c for c in self.current_pod_name if c.isalnum() or c in ('-', '_'))
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            default_filename = f"{safe_pod_name}_{timestamp}.log"
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".log",
            initialfile=default_filename,
            filetypes=[
                ("Log files", "*.log"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(logs)
                self.status_indicator.set_status("success", f"Logs guardados en: {os.path.basename(filepath)}")
                messagebox.showinfo("Éxito", f"Logs guardados correctamente en:\n{filepath}")
            except Exception as e:
                error_msg = f"Error guardando archivo: {str(e)}"
                self.status_indicator.set_status("error", error_msg)
                messagebox.showerror("Error", error_msg)