"""
Form builder sencillo para EasyUI.

Uso básico:

    from easyui import Form, form, Label, Input, Button

    # Opción 1: estilo directo
    f = form("Mi Formulario", width=420, height=300)
    f.add(Label(text="Nombre:"), Input())
    f.row(Button(text="Aceptar"), Button(text="Cancelar"))
    f.show()

    # Opción 2: con contexto
    with form("Demo", width=420, height=300) as f:
        f.add(Label(text="Correo:"), Input())
        f.row(Button(text="Enviar"), Button(text="Salir"))
        # al salir del with NO se muestra automáticamente; llama f.show() si lo deseas

Este builder es azúcar sintáctico sobre Window + VBox/HBox para prototipado rápido.
"""

from __future__ import annotations

from typing import Optional

from .window import Window
from .layout import VBox, HBox
from .components import UIComponent


class Form:
    """Crea un formulario simple basado en un contenedor vertical (VBox).

    - `add(*components)`: agrega los componentes tal cual a la columna principal.
    - `row(*components)`: agrega una fila horizontal (HBox) con los componentes.
    - `show()`: muestra la ventana.
    """

    def __init__(self, title: str, width: int = 800, height: int = 600, **kwargs):
        """
        Inicializa un formulario.

        Args:
            title (str): Título del formulario
            width (int): Ancho de la ventana
            height (int): Alto de la ventana
            **kwargs: Parámetros CSS-style adicionales
        """
        self._window = Window(title, width=width, height=height, **kwargs)
        self._root = VBox()
        self._window.add_component(self._root)

    # Soporte para "with form(...) as f: ..."
    def __enter__(self) -> "Form":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        # No auto-show; retornar False para no suprimir excepciones
        return False

    @property
    def window(self) -> Window:
        return self._window

    def add(self, *components: UIComponent) -> "Form":
        for c in components:
            self._root.add(c)
        return self

    def row(self, *components: UIComponent) -> HBox:
        row = HBox(*components)
        self._root.add(row)
        return row

    def clear(self) -> "Form":
        self._root.clear()
        return self

    def show(self) -> None:
        self._window.show()


def form(title: str, width: int = 800, height: int = 600, **kwargs) -> Form:
    """Atajo para crear `Form`.

    Ejemplo:
        f = form("Título", 420, 300)
        f.add(Label(text="Hola"))
        f.show()
    """
    return Form(title, width=width, height=height, **kwargs)

