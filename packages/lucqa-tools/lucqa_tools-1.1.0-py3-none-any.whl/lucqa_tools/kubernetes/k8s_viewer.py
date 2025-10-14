"""
Interfaz de usuario para el visor de logs de Kubernetes
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
import threading
from typing import List, Optional, Dict
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
        
        # Variables para filtrado
        self.context_filter = tk.StringVar()
        self.namespace_filter = tk.StringVar()
        self.pod_filter = tk.StringVar()
        self.all_contexts = []
        self.all_namespaces = []
        self.all_pods = []
        self.filtered_contexts = []
        self.filtered_namespaces = []
        self.filtered_pods = []
        
        # Bind para filtrado en tiempo real
        self.context_filter.trace('w', self.filter_contexts)
        self.namespace_filter.trace('w', self.filter_namespaces)
        self.pod_filter.trace('w', self.filter_pods)
        
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
        
        # Primera fila - Selectores con filtros mejorados
        row1_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        row1_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        # Configurar grid responsivo con mejor espaciado
        row1_frame.grid_columnconfigure(1, weight=1)
        row1_frame.grid_columnconfigure(3, weight=1)
        
        # === SELECTOR DE CONTEXTO MEJORADO ===
        context_label = ctk.CTkLabel(
            row1_frame,
            text="🏢 Cluster:",
            font=("Segoe UI", 13, "bold"),
            text_color=LucqaColors.WHITE
        )
        context_label.grid(row=0, column=0, padx=(0, 15), pady=8, sticky="w")
        
        context_container = ctk.CTkFrame(row1_frame, fg_color="transparent")
        context_container.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        
        # Campo de búsqueda de contexto mejorado
        context_search_frame = ctk.CTkFrame(
            context_container, 
            fg_color=LucqaColors.SURFACE, 
            corner_radius=10,
            border_width=1,
            border_color=LucqaColors.GRAY_200
        )
        context_search_frame.pack(fill="x", pady=(0, 5))
        
        search_icon_context = ctk.CTkLabel(
            context_search_frame,
            text="🔍",
            font=("Segoe UI", 14),
            text_color=LucqaColors.GRAY_200
        )
        search_icon_context.pack(side="left", padx=(12, 8), pady=10)
        
        self.context_entry = ctk.CTkEntry(
            context_search_frame,
            textvariable=self.context_filter,
            placeholder_text="Buscar cluster...",
            fg_color="transparent",
            border_width=0,
            font=("Segoe UI", 12),
            text_color=LucqaColors.WHITE,
            placeholder_text_color=LucqaColors.GRAY_200
        )
        self.context_entry.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=10)
        
        # Menú desplegable de contexto mejorado
        self.context_menu = ctk.CTkOptionMenu(
            context_container,
            values=[""],  # Sin valores por defecto
            variable=self.current_context,
            command=self.on_context_change,
            fg_color=LucqaColors.PRIMARY,
            button_color=LucqaColors.SECONDARY,
            button_hover_color=LucqaColors.ACCENT,
            dropdown_fg_color=LucqaColors.SURFACE,
            font=("Segoe UI", 12),
            corner_radius=8,
            height=35
        )
        self.context_menu.pack(fill="x")
        
        # === SELECTOR DE NAMESPACE MEJORADO ===
        namespace_label = ctk.CTkLabel(
            row1_frame,
            text="📁 Namespace:",
            font=("Segoe UI", 13, "bold"),
            text_color=LucqaColors.WHITE
        )
        namespace_label.grid(row=0, column=2, padx=(30, 15), pady=8, sticky="w")
        
        namespace_container = ctk.CTkFrame(row1_frame, fg_color="transparent")
        namespace_container.grid(row=0, column=3, padx=10, pady=8, sticky="ew")
        
        # Campo de búsqueda de namespace mejorado
        namespace_search_frame = ctk.CTkFrame(
            namespace_container, 
            fg_color=LucqaColors.SURFACE, 
            corner_radius=10,
            border_width=1,
            border_color=LucqaColors.GRAY_200
        )
        namespace_search_frame.pack(fill="x", pady=(0, 5))
        
        search_icon_namespace = ctk.CTkLabel(
            namespace_search_frame,
            text="🔍",
            font=("Segoe UI", 14),
            text_color=LucqaColors.GRAY_200
        )
        search_icon_namespace.pack(side="left", padx=(12, 8), pady=10)
        
        self.namespace_entry = ctk.CTkEntry(
            namespace_search_frame,
            textvariable=self.namespace_filter,
            placeholder_text="Buscar namespace...",
            fg_color="transparent",
            border_width=0,
            font=("Segoe UI", 12),
            text_color=LucqaColors.WHITE,
            placeholder_text_color=LucqaColors.GRAY_200
        )
        self.namespace_entry.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=10)
        
        # Menú desplegable de namespace mejorado
        self.namespace_menu = ctk.CTkOptionMenu(
            namespace_container,
            values=[""],  # Sin valores por defecto
            variable=self.current_namespace,
            command=self.on_namespace_change,
            fg_color=LucqaColors.PRIMARY,
            button_color=LucqaColors.SECONDARY,
            button_hover_color=LucqaColors.ACCENT,
            dropdown_fg_color=LucqaColors.SURFACE,
            font=("Segoe UI", 12),
            corner_radius=8,
            height=35
        )
        self.namespace_menu.pack(fill="x")
        
        # Segunda fila - Botones de acción mejorados
        row2_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        row2_frame.pack(fill="x", padx=15, pady=(15, 15))
        
        # Botones principales con mejor espaciado
        buttons_left = ctk.CTkFrame(row2_frame, fg_color="transparent")
        buttons_left.pack(side="left")
        
        self.refresh_button = ModernButton(
            buttons_left,
            text="🔄 Cargar Pods",
            command=self.load_pods_async,
            width=140,
            height=40,
            fg_color=LucqaColors.PRIMARY,
            hover_color=LucqaColors.SECONDARY,
            font=("Segoe UI", 12, "bold"),
            corner_radius=10
        )
        self.refresh_button.pack(side="left", padx=(0, 15))
        
        self.logs_button = ModernButton(
            buttons_left,
            text="📋 Obtener Logs",
            command=self.show_logs_async,
            width=140,
            height=40,
            fg_color=LucqaColors.ACCENT,
            hover_color="#9333EA",
            font=("Segoe UI", 12, "bold"),
            corner_radius=10
        )
        self.logs_button.pack(side="left", padx=15)
        
        # Botones secundarios con mejor espaciado
        buttons_right = ctk.CTkFrame(row2_frame, fg_color="transparent")
        buttons_right.pack(side="right")
        
        self.save_button = ModernButton(
            buttons_right,
            text="💾 Guardar",
            command=self.save_logs,
            width=110,
            height=40,
            fg_color=LucqaColors.SUCCESS,
            hover_color="#059669",
            font=("Segoe UI", 12, "bold"),
            corner_radius=10
        )
        self.save_button.pack(side="left", padx=15)
        
        self.clear_button = ModernButton(
            buttons_right,
            text="🗑️ Limpiar",
            command=self.clear_logs,
            width=110,
            height=40,
            fg_color=LucqaColors.ERROR,
            hover_color="#DC2626",
            font=("Segoe UI", 12, "bold"),
            corner_radius=10
        )
        self.clear_button.pack(side="left", padx=15)
        
        # Opciones adicionales mejoradas
        self.follow_checkbox = ctk.CTkCheckBox(
            buttons_right,
            text="📜 Auto-scroll",
            variable=self.follow_logs_var,
            font=("Segoe UI", 12),
            text_color=LucqaColors.WHITE,
            fg_color=LucqaColors.PRIMARY,
            hover_color=LucqaColors.SECONDARY,
            corner_radius=6
        )
        self.follow_checkbox.pack(side="left", padx=(25, 0))
    
    def create_pods_panel(self):
        pods_frame = ModernFrame(self.parent_frame)
        pods_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Header con filtro de pods mejorado
        header_frame = ctk.CTkFrame(pods_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 15))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🚀 Pods Disponibles",
            font=("Segoe UI", 16, "bold"),
            text_color=LucqaColors.WHITE
        )
        title_label.pack(side="left")
        
        # Filtro de pods mejorado
        pod_filter_frame = ctk.CTkFrame(
            header_frame, 
            fg_color=LucqaColors.SURFACE, 
            corner_radius=10,
            border_width=1,
            border_color=LucqaColors.GRAY_200
        )
        pod_filter_frame.pack(side="right", padx=(15, 0))
        
        filter_icon = ctk.CTkLabel(
            pod_filter_frame,
            text="🔍",
            font=("Segoe UI", 14),
            text_color=LucqaColors.GRAY_200
        )
        filter_icon.pack(side="left", padx=(12, 8), pady=8)
        
        self.pod_filter_entry = ctk.CTkEntry(
            pod_filter_frame,
            textvariable=self.pod_filter,
            placeholder_text="Filtrar pods...",
            width=220,
            fg_color="transparent",
            border_width=0,
            font=("Segoe UI", 12),
            text_color=LucqaColors.WHITE,
            placeholder_text_color=LucqaColors.GRAY_200
        )
        self.pod_filter_entry.pack(side="left", padx=(0, 12), pady=8)
        
        # Tabla de pods con Treeview mejorada
        table_frame = ctk.CTkFrame(pods_frame, fg_color=LucqaColors.BACKGROUND, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Configurar estilo de la tabla mejorado
        style = ttk.Style()
        style.theme_use("clam")
        
        # Personalizar colores para tema oscuro con mejor contraste
        style.configure("Treeview",
                       background=LucqaColors.BACKGROUND,
                       foreground=LucqaColors.WHITE,
                       fieldbackground=LucqaColors.BACKGROUND,
                       borderwidth=0,
                       font=("Consolas", 11),
                       rowheight=28)
        
        style.configure("Treeview.Heading",
                       background=LucqaColors.SURFACE,
                       foreground=LucqaColors.WHITE,
                       borderwidth=1,
                       font=("Segoe UI", 12, "bold"),
                       relief="flat")
        
        style.map("Treeview",
                 background=[('selected', LucqaColors.PRIMARY)],
                 foreground=[('selected', LucqaColors.WHITE)])
        
        # Crear tabla
        columns = ("Nombre", "Estado", "Reintentos", "Edad", "IP")
        self.pods_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
            style="Treeview"
        )
        
        # Configurar columnas
        self.pods_tree.heading("Nombre", text="📦 Nombre del Pod")
        self.pods_tree.heading("Estado", text="⚡ Estado")
        self.pods_tree.heading("Reintentos", text="🔄 Reintentos")
        self.pods_tree.heading("Edad", text="⏰ Edad")
        self.pods_tree.heading("IP", text="🌐 IP")
        
        # Configurar ancho de columnas
        self.pods_tree.column("Nombre", width=300, minwidth=200)
        self.pods_tree.column("Estado", width=100, minwidth=80)
        self.pods_tree.column("Reintentos", width=80, minwidth=60)
        self.pods_tree.column("Edad", width=100, minwidth=80)
        self.pods_tree.column("IP", width=120, minwidth=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.pods_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.pods_tree.xview)
        
        self.pods_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar tabla y scrollbars
        self.pods_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        v_scrollbar.grid(row=0, column=1, sticky="ns", pady=5)
        h_scrollbar.grid(row=1, column=0, sticky="ew", padx=5)
        
        # Configurar grid
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind para selección
        self.pods_tree.bind('<<TreeviewSelect>>', self.on_pod_select)
        
        # Información de estado
        status_frame = ctk.CTkFrame(pods_frame, fg_color="transparent")
        status_frame.pack(fill="x", padx=15, pady=(5, 0))
        
        self.pods_count_label = ctk.CTkLabel(
            status_frame,
            text="📊 Pods: 0 | Filtrados: 0",
            font=("Segoe UI", 10),
            text_color=LucqaColors.GRAY_200
        )
        self.pods_count_label.pack(side="left")
        
        refresh_hint = ctk.CTkLabel(
            status_frame,
            text="💡 Tip: Usa Ctrl+R para refrescar",
            font=("Segoe UI", 10),
            text_color=LucqaColors.GRAY_200
        )
        refresh_hint.pack(side="right")
    
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
    
    def filter_contexts(self, *args):
        """Filtrar contextos en tiempo real"""
        filter_text = self.context_filter.get().lower()
        
        if not filter_text:
            self.filtered_contexts = self.all_contexts.copy()
        else:
            self.filtered_contexts = [
                ctx for ctx in self.all_contexts 
                if filter_text in ctx.lower()
            ]
        
        # Actualizar menú desplegable sin valores por defecto
        if self.filtered_contexts:
            self.context_menu.configure(values=self.filtered_contexts)
            
            # Auto-seleccionar solo si hay coincidencia exacta
            exact_match = next((ctx for ctx in self.filtered_contexts if ctx.lower() == filter_text), None)
            if exact_match and exact_match != self.current_context.get():
                self.current_context.set(exact_match)
                self.on_context_change(exact_match)
        else:
            self.context_menu.configure(values=[""])
    
    def filter_namespaces(self, *args):
        """Filtrar namespaces en tiempo real"""
        filter_text = self.namespace_filter.get().lower()
        
        if not filter_text:
            self.filtered_namespaces = self.all_namespaces.copy()
        else:
            self.filtered_namespaces = [
                ns for ns in self.all_namespaces 
                if filter_text in ns.lower()
            ]
        
        # Actualizar menú desplegable sin valores por defecto
        if self.filtered_namespaces:
            self.namespace_menu.configure(values=self.filtered_namespaces)
            
            # Auto-seleccionar solo si hay coincidencia exacta
            exact_match = next((ns for ns in self.filtered_namespaces if ns.lower() == filter_text), None)
            if exact_match and exact_match != self.current_namespace.get():
                self.current_namespace.set(exact_match)
                self.on_namespace_change(exact_match)
        else:
            self.namespace_menu.configure(values=[""])
    
    def filter_pods(self, *args):
        """Filtrar pods en tiempo real"""
        filter_text = self.pod_filter.get().lower()
        
        # Limpiar tabla
        for item in self.pods_tree.get_children():
            self.pods_tree.delete(item)
        
        if not filter_text:
            self.filtered_pods = self.all_pods.copy()
        else:
            self.filtered_pods = [
                pod for pod in self.all_pods 
                if filter_text in pod.get('name', '').lower() or 
                   filter_text in pod.get('status', '').lower()
            ]
        
        # Repoblar tabla con pods filtrados
        for pod in self.filtered_pods:
            # Determinar color según estado
            status = pod.get('status', 'Unknown')
            if status == 'Running':
                tags = ('running',)
            elif status in ['Pending', 'ContainerCreating', 'PodInitializing']:
                tags = ('pending',)
            elif status in ['Error', 'CrashLoopBackOff', 'Failed', 'ImagePullBackOff']:
                tags = ('error',)
            elif status in ['NotReady']:
                tags = ('warning',)
            else:
                tags = ('default',)
            
            self.pods_tree.insert("", "end", values=(
                pod.get('name', ''),
                pod.get('status', ''),
                pod.get('restarts', '0'),
                pod.get('age', ''),
                pod.get('ip', '')
            ), tags=tags)
        
        # Configurar colores por estado
        self.pods_tree.tag_configure('running', foreground='#10B981')  # Verde
        self.pods_tree.tag_configure('pending', foreground='#F59E0B')  # Amarillo
        self.pods_tree.tag_configure('warning', foreground='#F97316')  # Naranja
        self.pods_tree.tag_configure('error', foreground='#EF4444')    # Rojo
        self.pods_tree.tag_configure('default', foreground=LucqaColors.WHITE)
        
        # Actualizar contador
        total_pods = len(self.all_pods)
        filtered_count = len(self.filtered_pods)
        self.pods_count_label.configure(text=f"📊 Pods: {total_pods} | Filtrados: {filtered_count}")
    
    def initialize_app(self):
        """Inicializar la aplicación cargando kubeconfig"""
        self.status_indicator.set_status("loading", "Inicializando...")
        threading.Thread(target=self._initialize_k8s, daemon=True).start()
    
    def _initialize_k8s(self):
        """Inicializar Kubernetes en hilo separado"""
        success, message = self.k8s_logic.load_kubeconfig()
        
        def update_ui():
            if success:
                self.all_contexts = self.k8s_logic.contexts.copy()
                self.filtered_contexts = self.all_contexts.copy()
                
                if self.filtered_contexts:
                    self.context_menu.configure(values=self.filtered_contexts)
                    self.current_context.set(self.k8s_logic.current_context)
                    self.context_filter.set(self.k8s_logic.current_context)
                else:
                    self.context_menu.configure(values=["Cargando..."])
                self.status_indicator.set_status("success", message)
                
                # Cargar cliente para el contexto actual
                self.on_context_change(self.k8s_logic.current_context)
            else:
                self.status_indicator.set_status("error", message)
                messagebox.showerror("Error", message)
        
        self.parent_frame.after(0, update_ui)
    
    def _change_context(self, context):
        """Cambiar contexto en hilo separado"""
        self.status_indicator.set_status("loading", f"Conectando a {context}...")
        
        success, message = self.k8s_logic.load_client_for_context(context)
        
        def update_ui():
            if success:
                self.status_indicator.set_status("success", message)
                success_ns, message_ns = self.k8s_logic.load_namespaces()
                
                if success_ns:
                    self.all_namespaces = self.k8s_logic.namespaces.copy()
                    self.filtered_namespaces = self.all_namespaces.copy()
                    
                    if self.filtered_namespaces:
                        self.namespace_menu.configure(values=self.filtered_namespaces)
                        default_ns = "default" if "default" in self.all_namespaces else self.all_namespaces[0]
                        self.current_namespace.set(default_ns)
                        self.namespace_filter.set(default_ns)
                    else:
                        self.namespace_menu.configure(values=["Sin namespaces"])
                else:
                    self.status_indicator.set_status("error", message_ns)
            else:
                self.status_indicator.set_status("error", message)
                messagebox.showerror("Error", message)
        
        self.parent_frame.after(0, update_ui)
    
    def on_context_change(self, context):
        """Cambio de cluster/contexto"""
        threading.Thread(target=self._change_context, args=(context,), daemon=True).start()
    
    def on_namespace_change(self, namespace):
        """Cambio de namespace"""
        # Limpiar tabla de pods
        for item in self.pods_tree.get_children():
            self.pods_tree.delete(item)
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
        
        success, message, pods_data = self.k8s_logic.load_pods_detailed(namespace)
        
        def update_ui():
            self.refresh_button.configure(state="normal", text="🔄 Cargar Pods")
            
            if success:
                self.all_pods = pods_data
                self.filtered_pods = self.all_pods.copy()
                
                # Limpiar y repoblar tabla
                for item in self.pods_tree.get_children():
                    self.pods_tree.delete(item)
                
                for pod in self.all_pods:
                    status = pod.get('status', 'Unknown')
                    if status == 'Running':
                        tags = ('running',)
                    elif status in ['Pending', 'ContainerCreating', 'PodInitializing']:
                        tags = ('pending',)
                    elif status in ['Error', 'CrashLoopBackOff', 'Failed', 'ImagePullBackOff']:
                        tags = ('error',)
                    elif status in ['NotReady']:
                        tags = ('warning',)
                    else:
                        tags = ('default',)
                    
                    self.pods_tree.insert("", "end", values=(
                        pod.get('name', ''),
                        pod.get('status', ''),
                        pod.get('restarts', '0'),
                        pod.get('age', ''),
                        pod.get('ip', '')
                    ), tags=tags)
                
                # Configurar colores por estado
                self.pods_tree.tag_configure('running', foreground='#10B981')
                self.pods_tree.tag_configure('pending', foreground='#F59E0B')
                self.pods_tree.tag_configure('warning', foreground='#F97316')
                self.pods_tree.tag_configure('error', foreground='#EF4444')
                self.pods_tree.tag_configure('default', foreground=LucqaColors.WHITE)
                
                # Actualizar contador
                total_pods = len(self.all_pods)
                self.pods_count_label.configure(text=f"📊 Pods: {total_pods} | Filtrados: {total_pods}")
                
                self.status_indicator.set_status("success", message)
                
                if not pods_data:
                    self.status_indicator.set_status("warning", f"No se encontraron pods en {namespace}")
            else:
                self.status_indicator.set_status("error", message)
                messagebox.showerror("Error", message)
        
        self.parent_frame.after(0, update_ui)
    
    def on_pod_select(self, event):
        """Selección de pod en la tabla"""
        selection = self.pods_tree.selection()
        if selection:
            item = self.pods_tree.item(selection[0])
            pod_name = item['values'][0]
            pod_status = item['values'][1]
            self.current_pod_name = pod_name
            self.status_indicator.set_status("success", f"Pod seleccionado: {pod_name} ({pod_status})")
    
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