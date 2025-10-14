"""
Configuración y colores del tema Lucqa
"""

class LucqaColors:
    """Paleta de colores oficial de Lucqa"""
    PRIMARY = "#6366F1"      # Púrpura principal
    SECONDARY = "#8B5CF6"    # Púrpura secundario
    ACCENT = "#A855F7"       # Púrpura acento
    BACKGROUND = "#0F0F23"   # Fondo oscuro
    SURFACE = "#1A1A2E"      # Superficie
    WHITE = "#FFFFFF"        # Blanco
    GRAY_100 = "#F3F4F6"     # Gris claro
    GRAY_200 = "#E5E7EB"     # Gris medio
    GRAY_800 = "#1F2937"     # Gris oscuro
    SUCCESS = "#10B981"      # Verde éxito
    WARNING = "#F59E0B"      # Amarillo advertencia
    ERROR = "#EF4444"        # Rojo error

class AppConfig:
    """Configuración general de la aplicación"""
    APP_NAME = "Lucqa Tools"
    APP_VERSION = "1.0.0"
    WINDOW_SIZE = "1200x800"
    WINDOW_TITLE = "Lucqa Tools - Suite de Herramientas"
    
    # Rutas de recursos
    ASSETS_DIR = "assets"
    IMG_DIR = "assets/img"
    LOGO_FILE = "logo.png"