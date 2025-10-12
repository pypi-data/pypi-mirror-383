"""
EasyUI - Una librería para crear interfaces de usuario de manera sencilla.
"""

__version__ = "0.3.0"

# Funciones helper globales para API minimalista
def label(text="", **kwargs):
    """Crea un Label con texto y configuración automática"""
    return Label(text=text, **kwargs)

def button(text="Botón", **kwargs):
    """Crea un Button con texto y configuración automática"""
    return Button(text=text, **kwargs)

def input(placeholder="", **kwargs):
    """Crea un Input con placeholder y configuración automática"""
    return Input(placeholder=placeholder, **kwargs)

def checkbox(text="", **kwargs):
    """Crea un Checkbox con texto y configuración automática"""
    return Checkbox(text=text, **kwargs)

def form(title="Formulario", **kwargs):
    """Crea un Form con título y configuración automática"""
    return Form(title, **kwargs)

from .window import Window
from .components import (
    Button,
    Label,
    Input,
    Checkbox,
    Radio,
    Dropdown,
    Image,
    Icon,
    ListView,
    Table,
    table,
    make_font,
    register_icon,
    register_icon_dir,
)
from .form import Form, form
from .layout import VBox, HBox

__all__ = [
    'Window',
    'Button',
    'Label',
    'Input',
    'Checkbox',
    'Radio',
    'Dropdown',
    'VBox',
    'HBox',
    'Image',
    'Icon',
    'ListView',
    'Table',
    'table',
    'make_font',
    'register_icon',
    'register_icon_dir',
    'Form',
    'form',
    # Funciones helper minimalistas
    'label',
    'button',
    'input',
    'checkbox',
]
