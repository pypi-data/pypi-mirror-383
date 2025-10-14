"""
Lógica de negocio para Kubernetes
"""

from kubernetes import client, config
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timezone
import re

class K8sLogic:
    """Lógica de negocio para Kubernetes separada de la UI"""
    
    def __init__(self):
        self.v1 = None
        self.contexts = []
        self.namespaces = []
        self.current_context = None
        
    def load_kubeconfig(self) -> Tuple[bool, str]:
        """Carga kubeconfig y obtiene todos los contextos"""
        try:
            contexts, active_context = config.list_kube_config_contexts()
            self.contexts = [c["name"] for c in contexts]
            self.current_context = active_context["name"]
            return True, f"Kubeconfig cargado. Contexto activo: {self.current_context}"
        except Exception as e:
            return False, f"Error cargando kubeconfig: {str(e)}"
    
    def load_client_for_context(self, context_name: str) -> Tuple[bool, str]:
        """Carga cliente de Kubernetes para un contexto específico"""
        try:
            config.load_kube_config(context=context_name)
            self.v1 = client.CoreV1Api()
            self.current_context = context_name
            return True, f"Conectado al contexto: {context_name}"
        except Exception as e:
            return False, f"Error conectando al contexto '{context_name}': {str(e)}"
    
    def load_namespaces(self) -> Tuple[bool, str]:
        """Carga los namespaces disponibles"""
        try:
            if not self.v1:
                return False, "Cliente de Kubernetes no inicializado"
            
            ns_list = self.v1.list_namespace()
            self.namespaces = [ns.metadata.name for ns in ns_list.items]
            return True, f"Cargados {len(self.namespaces)} namespaces"
        except Exception as e:
            return False, f"Error listando namespaces: {str(e)}"
    
    def load_pods(self, namespace: str) -> Tuple[bool, str, List[str]]:
        """Carga los pods de un namespace específico"""
        try:
            if not self.v1:
                return False, "Cliente de Kubernetes no inicializado", []
            
            pods = self.v1.list_namespaced_pod(namespace=namespace)
            pod_names = [pod.metadata.name for pod in pods.items]
            return True, f"Cargados {len(pod_names)} pods", pod_names
        except Exception as e:
            return False, f"Error listando pods: {str(e)}", []
    
    def load_pods_detailed(self, namespace: str) -> Tuple[bool, str, List[Dict]]:
        """Carga los pods de un namespace con información detallada"""
        try:
            if not self.v1:
                return False, "Cliente de Kubernetes no inicializado", []
            
            pods = self.v1.list_namespaced_pod(namespace=namespace)
            pods_data = []
            
            for pod in pods.items:
                # Información básica
                name = pod.metadata.name
                
                # Estado del pod
                phase = pod.status.phase
                
                # Calcular reintentos
                restart_count = 0
                if pod.status.container_statuses:
                    restart_count = sum(cs.restart_count for cs in pod.status.container_statuses)
                
                # Calcular edad
                creation_time = pod.metadata.creation_timestamp
                if creation_time:
                    age = self._calculate_age(creation_time)
                else:
                    age = "Unknown"
                
                # IP del pod
                pod_ip = pod.status.pod_ip or "None"
                
                # Estado más detallado
                detailed_status = self._get_detailed_status(pod)
                
                pods_data.append({
                    'name': name,
                    'status': detailed_status,
                    'restarts': str(restart_count),
                    'age': age,
                    'ip': pod_ip
                })
            
            return True, f"Cargados {len(pods_data)} pods con detalles", pods_data
        except Exception as e:
            return False, f"Error listando pods detallados: {str(e)}", []
    
    def _calculate_age(self, creation_time) -> str:
        """Calcula la edad de un pod"""
        try:
            now = datetime.now(timezone.utc)
            if creation_time.tzinfo is None:
                creation_time = creation_time.replace(tzinfo=timezone.utc)
            
            age_delta = now - creation_time
            
            days = age_delta.days
            hours, remainder = divmod(age_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d{hours}h"
            elif hours > 0:
                return f"{hours}h{minutes}m"
            else:
                return f"{minutes}m"
        except Exception:
            return "Unknown"
    
    def _get_detailed_status(self, pod) -> str:
        """Obtiene el estado detallado del pod"""
        try:
            phase = pod.status.phase
            
            # Si está en Running, verificar si todos los contenedores están listos
            if phase == "Running":
                if pod.status.container_statuses:
                    all_ready = all(cs.ready for cs in pod.status.container_statuses)
                    if not all_ready:
                        return "NotReady"
                return "Running"
            
            # Si está en Pending, buscar razón más específica
            if phase == "Pending":
                if pod.status.container_statuses:
                    for cs in pod.status.container_statuses:
                        if cs.state.waiting:
                            reason = cs.state.waiting.reason
                            if reason:
                                return reason
                return "Pending"
            
            # Para otros estados
            if phase in ["Succeeded", "Failed"]:
                return phase
            
            # Estado por defecto
            return phase or "Unknown"
        except Exception:
            return "Unknown"
    
    def get_pod_logs(self, pod_name: str, namespace: str, tail_lines: int = 300) -> Tuple[bool, str]:
        """Obtiene los logs de un pod específico"""
        try:
            if not self.v1:
                return False, "Cliente de Kubernetes no inicializado"
            
            logs = self.v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=tail_lines
            )
            return True, logs
        except Exception as e:
            return False, f"Error obteniendo logs del pod '{pod_name}': {str(e)}"