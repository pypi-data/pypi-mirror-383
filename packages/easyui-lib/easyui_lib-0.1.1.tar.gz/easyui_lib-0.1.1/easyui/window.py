import tkinter as tk
from typing import Optional, List
from .components import UIComponent

class Window:
    """
    Clase principal que representa una ventana de la aplicación.
    """
    
    def __init__(self, title: str, width: int = 800, height: int = 600):
        """
        Inicializa una nueva ventana.
        
        Args:
            title (str): Título de la ventana
            width (int, optional): Ancho en píxeles. Por defecto 800.
            height (int, optional): Alto en píxeles. Por defecto 600.
        """
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.components: List[UIComponent] = []
    
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
