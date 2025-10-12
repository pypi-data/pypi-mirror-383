""
Módulo para cargar y gestionar temas de la interfaz de usuario.
"""
from typing import Dict, Optional, Any
import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Theme:
    """Clase que representa un tema de la interfaz de usuario."""
    name: str
    data: dict = field(default_factory=dict)
    parent: Optional['Theme'] = None
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor del tema, con soporte para herencia.
        
        Args:
            key: Clave del valor a obtener (puede usar notación de puntos)
            default: Valor por defecto si la clave no existe
            
        Returns:
            El valor de la clave o el valor por defecto
        """
        # Buscar en el tema actual
        value = self._get_nested(self.data, key.split('.'), None)
        
        # Si no se encuentra y hay un tema padre, buscar en él
        if value is None and self.parent is not None:
            return self.parent.get(key, default)
            
        return default if value is None else value
    
    def _get_nested(self, data: dict, keys: list, default: Any) -> Any:
        """Obtiene un valor anidado de un diccionario."""
        if not keys:
            return data
            
        key = keys[0]
        if key in data:
            if len(keys) == 1:
                return data[key]
            elif isinstance(data[key], dict):
                return self._get_nested(data[key], keys[1:], default)
        return default

class ThemeLoader:
    """Cargador y gestor de temas."""
    
    def __init__(self):
        self._themes: Dict[str, Theme] = {}
        self._current_theme: Optional[Theme] = None
    
    @property
    def current_theme(self) -> Theme:
        """Obtiene el tema actualmente activo."""
        if self._current_theme is None and 'default' in self._themes:
            self.set_current_theme('default')
        return self._current_theme or self._load_default_theme()
    
    def _load_default_theme(self) -> Theme:
        """Carga un tema por defecto si no hay ninguno definido."""
        default_data = {
            'name': 'default',
            'colors': {
                'primary': '#007bff',
                'secondary': '#6c757d',
                'success': '#28a745',
                'danger': '#dc3545',
                'warning': '#ffc107',
                'info': '#17a2b8',
                'light': '#f8f9fa',
                'dark': '#343a40',
                'background': '#ffffff',
                'surface': '#ffffff',
                'text': {'primary': '#212529', 'secondary': '#6c757d'},
            },
            'typography': {
                'font_family': 'Arial, sans-serif',
                'font_size': '14px',
                'font_weights': {
                    'light': 300,
                    'regular': 400,
                    'medium': 500,
                    'bold': 700
                }
            },
            'spacing': {
                'unit': 8,
                'container': 1200
            },
            'shape': {
                'border_radius': '4px',
                'border_width': '1px'
            },
            'transition': {
                'duration': '0.2s',
                'easing': 'cubic-bezier(0.4, 0, 0.2, 1)'
            }
        }
        theme = Theme('default', default_data)
        self._themes['default'] = theme
        self._current_theme = theme
        return theme
    
    def register_theme(self, name: str, theme_data: dict, parent: str = None):
        """
        Registra un nuevo tema.
        
        Args:
            name: Nombre único del tema
            theme_data: Diccionario con la definición del tema
            parent: Nombre del tema padre (opcional)
        """
        parent_theme = self._themes.get(parent) if parent else None
        self._themes[name] = Theme(name, theme_data, parent_theme)
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """
        Obtiene un tema por su nombre.
        
        Args:
            name: Nombre del tema a obtener
            
        Returns:
            El tema solicitado o None si no existe
        """
        return self._themes.get(name)
    
    def set_current_theme(self, name: str) -> bool:
        """
        Establece el tema actual.
        
        Args:
            name: Nombre del tema a establecer
            
        Returns:
            True si el tema se estableció correctamente, False en caso contrario
        """
        if name in self._themes:
            self._current_theme = self._themes[name]
            return True
        return False
    
    def load_from_file(self, file_path: str, name: str = None):
        """
        Carga un tema desde un archivo YAML.
        
        Args:
            file_path: Ruta al archivo YAML del tema
            name: Nombre del tema (opcional, si no se proporciona se usa el nombre del archivo)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = yaml.safe_load(f)
                
            if not name:
                name = Path(file_path).stem
                
            parent = theme_data.get('extends')
            self.register_theme(name, theme_data, parent)
            return True
            
        except Exception as e:
            print(f"Error al cargar el tema desde {file_path}: {e}")
            return False
    
    def load_from_dir(self, dir_path: str):
        """
        Carga todos los temas de un directorio.
        
        Args:
            dir_path: Ruta al directorio que contiene los archivos de tema (.yaml)
        """
        try:
            path = Path(dir_path)
            for file in path.glob('*.yaml'):
                self.load_from_file(str(file))
        except Exception as e:
            print(f"Error al cargar temas desde {dir_path}: {e}")

# Exportar la clase Theme para uso externo
__all__ = ['Theme', 'ThemeLoader']
