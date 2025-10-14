"""
Lógica de negocio para Kubernetes
"""

from kubernetes import client, config
from typing import List, Optional, Tuple

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