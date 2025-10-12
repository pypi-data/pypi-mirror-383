import tkinter as tk
from typing import Optional, List, Dict, Any
from .components import UIComponent

class Window:
    """
    Clase principal que representa una ventana de la aplicación.

    Soporta parámetros CSS-style para configuración avanzada.
    """

    def __init__(self, title: str, width: int = 800, height: int = 600, **kwargs):
        """
        Inicializa una nueva ventana.

        Args:
            title (str): Título de la ventana
            width (int, optional): Ancho en píxeles. Por defecto 800.
            height (int, optional): Alto en píxeles. Por defecto 600.
            **kwargs: Parámetros CSS-style adicionales
        """
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")

        # Aplicar parámetros CSS-style a la ventana
        self._configure_window(**kwargs)

        self.components: List[UIComponent] = []

    def _configure_window(self, **kwargs):
        """Configura la ventana con parámetros CSS-style."""
        if not kwargs:
            return

        # Configurar colores de fondo
        if 'background_color' in kwargs:
            self.root.configure(bg=kwargs['background_color'])
        if 'background' in kwargs:
            self.root.configure(bg=kwargs['background'])

        # Configurar otros parámetros de ventana
        for key, value in kwargs.items():
            if key in ['bg', 'background', 'background_color']:
                self.root.configure(bg=value)
            elif key == 'resizable':
                self.root.resizable(value[0] if isinstance(value, tuple) else value,
                                   value[1] if isinstance(value, tuple) else value)
            elif key == 'minsize':
                self.root.minsize(value[0], value[1])
            elif key == 'maxsize':
                self.root.maxsize(value[0], value[1])
            elif key == 'alpha':
                self.root.attributes('-alpha', value)
            elif key == 'topmost':
                self.root.attributes('-topmost', value)
            elif key == 'fullscreen':
                if value:
                    self.root.attributes('-fullscreen', True)
            elif key == 'icon':
                self.root.iconbitmap(value)

    def add_component(self, component: 'UIComponent'):
        """
        Agrega un componente a la ventana.

        Args:
            component (UIComponent): Componente a agregar
        """
        self.components.append(component)
        component._add_to_container(self.root)

    def show(self):
        """
        Muestra la ventana y comienza el bucle principal de la aplicación.
        """
        self.root.mainloop()

    def set_title(self, title: str):
        """
        Establece el título de la ventana.

        Args:
            title (str): Nuevo título para la ventana
        """
        self.root.title(title)

    def set_size(self, width: int, height: int):
        """
        Establece el tamaño de la ventana.

        Args:
            width (int): Ancho en píxeles
            height (int): Alto en píxeles
        """
        self.root.geometry(f"{width}x{height}")

    # Métodos de conveniencia para configuración fluida
    def background(self, color): self.root.configure(bg=color); return self
    def resizable(self, width=True, height=True): self.root.resizable(width, height); return self
    def alpha(self, value): self.root.attributes('-alpha', value); return self
