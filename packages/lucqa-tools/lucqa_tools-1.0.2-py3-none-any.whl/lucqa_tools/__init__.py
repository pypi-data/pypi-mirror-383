"""
Lucqa Tools - Suite de herramientas para desarrollo

Este paquete incluye:
- Kubernetes Log Viewer: Visualizador de logs de pods
- Conversor Base64: Codificador/decodificador de texto
- Conversor de Imágenes: Conversión de imágenes a/desde Base64
- Conversor de PDF: Conversión de PDFs a/desde Base64
"""

__version__ = "1.0.0"
__author__ = "Lucqa Development Team"
__email__ = "dev@lucqa.com"

from .main import MainApp

__all__ = ["MainApp"]