"""
EasyUI - Una librería para crear interfaces de usuario de manera sencilla.
"""

__version__ = "0.3.0"

from .components import (
    Button,
    Checkbox,
    Dropdown,
    Icon,
    Image,
    Input,
    Label,
    ListView,
    Radio,
    Table,
    make_font,
    register_icon,
    register_icon_dir,
    table,
)

# Importar layout y formularios (evitar redefinir 'form')
from .form import Form
from .layout import HBox, VBox

# Importar threading para operaciones en background
from .threading import (
    async_button_action,
    execute_after_delay,
    get_background_task_status,
    get_threading_info,
    process_ui_queue,
    run_in_background,
    run_in_ui_thread,
    schedule_repeating_task,
    stop_repeating_task,
    wait_for_task,
)

# Importar componentes básicos primero
from .window import Window


# Funciones helper globales para API minimalista (después de imports)
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


__all__ = [
    "Window",
    "Button",
    "Label",
    "Input",
    "Checkbox",
    "Radio",
    "Dropdown",
    "VBox",
    "HBox",
    "Image",
    "Icon",
    "ListView",
    "Table",
    "table",
    "make_font",
    "register_icon",
    "register_icon_dir",
    "Form",
    "form",
    # Funciones helper minimalistas
    "label",
    "button",
    "input",
    "checkbox",
    # Funciones de threading
    "run_in_background",
    "run_in_ui_thread",
    "get_background_task_status",
    "wait_for_task",
    "execute_after_delay",
    "schedule_repeating_task",
    "stop_repeating_task",
    "async_button_action",
    "get_threading_info",
    "process_ui_queue",
]
