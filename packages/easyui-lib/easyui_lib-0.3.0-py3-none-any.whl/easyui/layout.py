import tkinter as tk
from typing import List, Optional, Union
from .components import UIComponent

class Container(UIComponent):
    """
    Clase base para contenedores de diseño.
    """
    
    def __init__(self, *components: UIComponent, **kwargs):
        """
        Inicializa un nuevo contenedor.
        
        Args:
            *components: Componentes a agregar al contenedor
            **kwargs: Argumentos adicionales
        """
        self._components: List[UIComponent] = []
        super().__init__(**kwargs)
        
        for component in components:
            self.add(component)
    
    def add(self, component: UIComponent) -> 'Container':
        """
        Agrega un componente al contenedor.
        
        Args:
            component (UIComponent): Componente a agregar
            
        Returns:
            Container: La instancia actual para encadenamiento de métodos
        """
        if component not in self._components:
            self._components.append(component)
            if self.widget and component.widget:
                component._add_to_container(self.widget)
        return self
    
    def remove(self, component: UIComponent) -> 'Container':
        """
        Elimina un componente del contenedor.
        
        Args:
            component (UIComponent): Componente a eliminar
            
        Returns:
            Container: La instancia actual para encadenamiento de métodos
        """
        if component in self._components:
            self._components.remove(component)
            if component.widget:
                component.widget.pack_forget()
        return self
    
    def clear(self) -> 'Container':
        """
        Elimina todos los componentes del contenedor.
        
        Returns:
            Container: La instancia actual para encadenamiento de métodos
        """
        for component in self._components[:]:
            self.remove(component)
        return self
    
    def _add_to_container(self, container):
        """
        Agrega el contenedor a otro contenedor.
        
        Args:
            container: Contenedor padre
        """
        if not self.widget:
            self._setup_widget()
        
        if self.widget:
            self.widget.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
            
            # Asegurarse de que los componentes se agreguen al contenedor correcto
            for component in self._components:
                component._add_to_container(self.widget)


class VBox(Container):
    """
    Contenedor que organiza los componentes verticalmente.
    """
    
    def _setup_widget(self):
        """Configura el widget del contenedor vertical."""
        self.widget = tk.Frame()
        
        # Configurar el empaquetado para los componentes hijos
        for component in self._components:
            component._add_to_container(self.widget)
            component.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=2)


class HBox(Container):
    """
    Contenedor que organiza los componentes horizontalmente.
    """
    
    def _setup_widget(self):
        """Configura el widget del contenedor horizontal."""
        self.widget = tk.Frame()
        
        # Configurar el empaquetado para los componentes hijos
        for component in self._components:
            component._add_to_container(self.widget)
            component.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=2, pady=5)
