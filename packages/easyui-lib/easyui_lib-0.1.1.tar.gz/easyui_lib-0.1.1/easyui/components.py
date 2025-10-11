import tkinter as tk
from typing import Optional, Callable, List, Dict, Any
from abc import ABC, abstractmethod

class UIComponent(ABC):
    """
    Clase base abstracta para todos los componentes de la interfaz de usuario.
    """
    
    def __init__(self, **kwargs):
        self.widget = None
        self.parent = None
        self._setup_widget()
        self._configure(**kwargs)
    
    @abstractmethod
    def _setup_widget(self):
        """
        Método abstracto para configurar el widget subyacente.
        Debe ser implementado por las clases hijas.
        """
        pass
    
    def _configure(self, **kwargs):
        """
        Configura las propiedades del widget.
        
        Args:
            **kwargs: Propiedades a configurar
        """
        if self.widget and kwargs:
            for key, value in kwargs.items():
                try:
                    self.widget[key] = value
                except tk.TclError:
                    pass  # Ignorar propiedades no válidas
    
    def _add_to_container(self, container):
        """
        Agrega el componente a un contenedor.
        
        Args:
            container: Contenedor al que se agregará el componente
        """
        if self.widget:
            self.widget.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    
    def pack(self, **kwargs):
        """
        Empaqueta el widget en su contenedor.
        
        Args:
            **kwargs: Argumentos para el método pack()
        """
        if self.widget:
            self.widget.pack(**kwargs)
    
    def grid(self, **kwargs):
        """
        Coloca el widget en una cuadrícula.
        
        Args:
            **kwargs: Argumentos para el método grid()
        """
        if self.widget:
            self.widget.grid(**kwargs)
    
    def place(self, **kwargs):
        """
        Coloca el widget en una posición específica.
        
        Args:
            **kwargs: Argumentos para el método place()
        """
        if self.widget:
            self.widget.place(**kwargs)


class Button(UIComponent):
    """
    Componente de botón.
    """
    
    def _setup_widget(self):
        self.widget = tk.Button()
    
    def __init__(self, text: str = "", on_click: Optional[Callable] = None, **kwargs):
        """
        Inicializa un nuevo botón.
        
        Args:
            text (str): Texto del botón
            on_click (Callable, optional): Función a ejecutar al hacer clic
            **kwargs: Argumentos adicionales para el botón
        """
        self.on_click = on_click
        super().__init__(text=text, **kwargs)
    
    def _setup_widget(self):
        self.widget = tk.Button(command=self._on_click_handler)
    
    def _on_click_handler(self):
        """Manejador del evento de clic."""
        if self.on_click:
            self.on_click()
    
    @property
    def text(self) -> str:
        """Obtiene el texto del botón."""
        return self.widget['text']
    
    @text.setter
    def text(self, value: str):
        """Establece el texto del botón."""
        self.widget.config(text=value)


class Label(UIComponent):
    """
    Componente de etiqueta de texto.
    """
    
    def _setup_widget(self):
        self.widget = tk.Label()
    
    @property
    def text(self) -> str:
        """Obtiene el texto de la etiqueta."""
        return self.widget['text']
    
    @text.setter
    def text(self, value: str):
        """Establece el texto de la etiqueta."""
        self.widget.config(text=value)


class Input(UIComponent):
    """
    Componente de campo de entrada de texto.
    """
    
    def _setup_widget(self):
        self.widget = tk.Entry()
    
    @property
    def value(self) -> str:
        """Obtiene el valor actual del campo de entrada."""
        return self.widget.get()
    
    @value.setter
    def value(self, text: str):
        """
        Establece el valor del campo de entrada.
        
        Args:
            text (str): Texto a establecer
        """
        self.widget.delete(0, tk.END)
        self.widget.insert(0, text)
    
    def clear(self):
        """Limpia el contenido del campo de entrada."""
        self.widget.delete(0, tk.END)


class Checkbox(UIComponent):
    """
    Componente de casilla de verificación.
    """
    
    def _setup_widget(self):
        self.var = tk.BooleanVar()
        self.widget = tk.Checkbutton(variable=self.var)
    
    @property
    def checked(self) -> bool:
        """Obtiene el estado de la casilla."""
        return self.var.get()
    
    @checked.setter
    def checked(self, value: bool):
        """
        Establece el estado de la casilla.
        
        Args:
            value (bool): True para marcar, False para desmarcar
        """
        self.var.set(value)


class Radio(UIComponent):
    """
    Componente de botón de opción.
    """
    
    _groups: Dict[str, List['Radio']] = {}
    
    def _setup_widget(self):
        self.var = tk.StringVar()
        self.widget = tk.Radiobutton(variable=self.var)
    
    def __init__(self, text: str = "", group: str = "default", **kwargs):
        """
        Inicializa un nuevo botón de opción.
        
        Args:
            text (str): Texto del botón
            group (str): Grupo al que pertenece el botón
            **kwargs: Argumentos adicionales
        """
        self.group = group
        if group not in self._groups:
            self._groups[group] = []
        self._groups[group].append(self)
        super().__init__(text=text, **kwargs)
    
    @property
    def selected(self) -> bool:
        """Verifica si el botón está seleccionado."""
        return self.var.get() == self.widget['value']
    
    @selected.setter
    def selected(self, value: bool):
        """
        Establece si el botón está seleccionado.
        
        Args:
            value (bool): True para seleccionar, False para deseleccionar
        """
        if value:
            self.var.set(self.widget['value'])
    
    def _configure(self, **kwargs):
        """Configura el widget del botón de opción."""
        if 'value' not in kwargs:
            kwargs['value'] = f"radio_{id(self)}"
        super()._configure(**kwargs)


class Dropdown(UIComponent):
    """
    Componente de menú desplegable.
    """
    
    def _setup_widget(self):
        self.var = tk.StringVar()
        self.widget = tk.OptionMenu(None, self.var, "")
    
    def __init__(self, options: List[str] = None, **kwargs):
        """
        Inicializa un nuevo menú desplegable.
        
        Args:
            options (List[str], optional): Lista de opciones
            **kwargs: Argumentos adicionales
        """
        self._options = options or []
        super().__init__(**kwargs)
        self._update_options()
    
    def _update_options(self):
        """Actualiza las opciones del menú desplegable."""
        if not self.widget:
            return
            
        menu = self.widget["menu"]
        menu.delete(0, tk.END)
        
        for option in self._options:
            menu.add_command(
                label=option,
                command=lambda v=option: self.var.set(v)
            )
        
        if self._options:
            self.var.set(self._options[0])
    
    @property
    def options(self) -> List[str]:
        """Obtiene la lista de opciones."""
        return self._options.copy()
    
    @options.setter
    def options(self, value: List[str]):
        """
        Establece las opciones del menú desplegable.
        
        Args:
            value (List[str]): Lista de opciones
        """
        self._options = value or []
        self._update_options()
    
    @property
    def value(self) -> str:
        """Obtiene el valor seleccionado actualmente."""
        return self.var.get()
    
    @value.setter
    def value(self, value: str):
        """
        Establece el valor seleccionado.
        
        Args:
            value (str): Valor a seleccionar
        """
        if value in self._options:
            self.var.set(value)
