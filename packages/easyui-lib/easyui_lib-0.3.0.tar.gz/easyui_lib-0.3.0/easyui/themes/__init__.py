"""
Módulo de temas para EasyUI.

Proporciona un sistema de temas personalizables para las interfaces de usuario.
"""

from .theme_loader import ThemeLoader, Theme
from .default_themes import register_default_themes

# Inicializar el cargador de temas
theme_loader = ThemeLoader()

# Registrar temas por defecto
register_default_themes()

def get_theme(name: str) -> Theme:
    """Obtiene un tema por su nombre."""
    return theme_loader.get_theme(name)

def set_theme(name: str):
    """Establece el tema activo."""
    theme_loader.set_current_theme(name)

def get_current_theme() -> Theme:
    """Obtiene el tema actualmente activo."""
    return theme_loader.current_theme

def register_theme(name: str, theme_data: dict):
    """Registra un nuevo tema personalizado."""
    theme_loader.register_theme(name, theme_data)
