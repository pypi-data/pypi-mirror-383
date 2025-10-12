import tkinter as tk
import tkinter.font as tkfont
from abc import ABC, abstractmethod
from tkinter import ttk
from typing import Any, Callable, Dict, Iterable, List, Literal, Optional, Union

try:
    from PIL import Image as PILImage
    from PIL import ImageTk
except Exception:  # Pillow opcional
    PILImage = None
    ImageTk = None


def make_font(
    family: str,
    size: int,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
) -> tkfont.Font:
    """
    Crea y devuelve una fuente de Tk configurada.

    Args:
        family: Familia tipográfica (por ejemplo, 'Arial').
        size: Tamaño en puntos.
        bold: Negrita.
        italic: Cursiva.
        underline: Subrayado.

    Returns:
        tkfont.Font: Fuente lista para usar en la opción 'font' de los widgets.
    """
    weight: Literal["normal", "bold"] = "bold" if bold else "normal"
    slant: Literal["roman", "italic"] = "italic" if italic else "roman"
    return tkfont.Font(
        family=family, size=size, weight=weight, slant=slant, underline=underline
    )


class UIComponent(ABC):
    """
    Clase base abstracta para todos los componentes de la interfaz de usuario.

    Soporta parámetros CSS-style que se traducen automáticamente a opciones de Tkinter.
    """

    # Mapeo de parámetros CSS a opciones de Tkinter
    CSS_TO_TKINTER = {
        # Dimensiones y posición
        "width": "width",
        "height": "height",
        "min-width": "width",
        "min-height": "height",
        "max-width": "width",
        "max-height": "height",
        # Espaciado (CSS)
        "padding": "padx",  # Se traduce a padx/pady
        "padding-left": "padx",
        "padding-right": "padx",
        "padding-top": "pady",
        "padding-bottom": "pady",
        "margin": "padx",  # Similar a padding para simplicidad
        "margin-left": "padx",
        "margin-right": "padx",
        "margin-top": "pady",
        "margin-bottom": "pady",
        # Bordes (CSS)
        "border": "borderwidth",
        "border-width": "borderwidth",
        "border-left-width": "borderwidth",
        "border-right-width": "borderwidth",
        "border-top-width": "borderwidth",
        "border-bottom-width": "borderwidth",
        "border-radius": "borderwidth",  # Tkinter no soporta border-radius directamente
        # Colores (CSS)
        "background-color": "bg",
        "background": "bg",
        "bg-color": "bg",
        "color": "fg",
        "foreground": "fg",
        "text-color": "fg",
        # Tipografía (CSS)
        "font-family": "font",
        "font-size": "font",
        "font-weight": "font",
        "font-style": "font",
        # Alineación (CSS)
        "text-align": "anchor",
        "vertical-align": "anchor",
        "justify": "justify",
        # Otros estilos
        "cursor": "cursor",
        "opacity": "alpha",
        # Propiedades específicas de Tkinter
        "relief": "relief",
        "state": "state",
        "activebackground": "activebackground",
        "activeforeground": "activeforeground",
        "disabledforeground": "disabledforeground",
        "highlightbackground": "highlightbackground",
        "highlightcolor": "highlightcolor",
        "highlightthickness": "highlightthickness",
        "insertbackground": "insertbackground",
        "insertborderwidth": "insertborderwidth",
        "insertwidth": "insertwidth",
        "insertontime": "insertontime",
        "insertofftime": "insertofftime",
        "selectbackground": "selectbackground",
        "selectforeground": "selectforeground",
        "selectborderwidth": "selectborderwidth",
        "takefocus": "takefocus",
        "xscrollcommand": "xscrollcommand",
        "yscrollcommand": "yscrollcommand",
    }

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
        Configura las propiedades del widget con soporte para parámetros CSS-style.

        Args:
            **kwargs: Propiedades a configurar (CSS o Tkinter)
        """
        if not self.widget or not kwargs:
            return

        # Procesar parámetros CSS-style
        processed_kwargs = {}
        for key, value in kwargs.items():
            if key in self.CSS_TO_TKINTER:
                tk_key = self.CSS_TO_TKINTER[key]
                if tk_key == "padx" or tk_key == "pady":
                    # Manejar padding/margin como tupla
                    if isinstance(value, (int, float)):
                        processed_kwargs[tk_key] = int(value)
                    elif isinstance(value, str) and value.isdigit():
                        processed_kwargs[tk_key] = int(value)
                    else:
                        processed_kwargs[key] = value
                else:
                    processed_kwargs[tk_key] = value
            else:
                processed_kwargs[key] = value

        # Aplicar configuración
        for key, value in processed_kwargs.items():
            try:
                if key == "font" and isinstance(value, dict):
                    # Crear fuente personalizada
                    font = make_font(
                        family=value.get("family", "Arial"),
                        size=value.get("size", 12),
                        bold=value.get("weight") == "bold",
                        italic=value.get("style") == "italic",
                    )
                    self.widget[key] = font
                else:
                    self.widget[key] = value
            except tk.TclError:
                # Ignorar propiedades no válidas para este widget
                pass

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

    # Métodos de conveniencia para configuración fluida
    def width(self, value):
        self._configure(width=value)
        return self

    def height(self, value):
        self._configure(height=value)
        return self

    def padding(self, value):
        self._configure(padx=value, pady=value)
        return self

    def margin(self, value):
        self._configure(padx=value, pady=value)
        return self

    def background(self, color):
        self._configure(bg=color)
        return self

    def color(self, color):
        self._configure(fg=color)
        return self

    def font_size(self, size):
        self._configure(font=("Arial", size))
        return self

    def font_family(self, family):
        self._configure(font=(family, 12))
        return self

    def font_weight(self, weight):
        self._configure(font=("Arial", 12, weight))
        return self

    def border(self, width):
        self._configure(borderwidth=width)
        return self

    def text_align(self, align):
        self._configure(anchor=align)
        return self

    def position(self, x, y):
        self.place(x=x, y=y)
        return self


class Button(UIComponent):
    """
    Componente de botón.
    """

    def _setup_widget(self):
        self._on_click_cb: Optional[Callable] = None
        self.widget = tk.Button(command=self._on_click_handler)

    def _on_click_handler(self):
        """Manejador del evento de clic."""
        if self._on_click_cb:
            self._on_click_cb()

    @property
    def text(self) -> str:
        """Obtiene el texto del botón."""
        return self.widget["text"]

    @text.setter
    def text(self, value: str):
        """Establece el texto del botón."""
        self.widget.config(text=value)

    def on_click(self, callback: Callable) -> "Button":
        """
        Establece la función a ejecutar al hacer clic.

        Args:
            callback: Función a ejecutar

        Returns:
            Button: La instancia actual para method chaining
        """
        self._on_click_cb = callback
        if self.widget:
            self.widget.config(command=self._on_click_handler)
        return self


class Label(UIComponent):
    """
    Componente de etiqueta de texto.
    """

    def _setup_widget(self):
        self.widget = tk.Label()

    @property
    def text(self) -> str:
        """Obtiene el texto de la etiqueta."""
        return self.widget["text"]

    @text.setter
    def text(self, value: str):
        """Establece el texto de la etiqueta."""
        self.widget.config(text=value)


class Input(UIComponent):
    """
    Componente de campo de entrada de texto.
    """

    def __init__(self, placeholder: str = "", **kwargs):
        """
        Inicializa un campo de entrada de texto.

        Args:
            placeholder (str): Texto placeholder a mostrar
            **kwargs: Argumentos adicionales para configuración
        """
        self._placeholder_text = placeholder
        super().__init__(**kwargs)

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

    def placeholder(self, text: str):
        """Establece el texto placeholder del campo de entrada."""
        # Nota: Tkinter no tiene placeholder nativo, pero podemos simularlo
        # con configuración visual y texto inicial
        current_value = self.widget.get()
        if not current_value:  # Solo si está vacío
            self._placeholder_text = text
            self._configure(fg="gray")  # Color gris para indicar placeholder
            # Insertar texto placeholder si el campo está vacío
            if not current_value:
                self.widget.insert(0, text)
        return self

    def _configure(self, **kwargs):
        """Configuración especial para Input con manejo de placeholder."""
        # Manejar placeholder especial
        if "placeholder" in kwargs:
            placeholder_text = kwargs.pop("placeholder")
            if not self.widget.get():  # Solo establecer si está vacío
                self.widget.insert(0, placeholder_text)
                self.widget.config(fg="gray")

        super()._configure(**kwargs)

        # Si se configura texto y había placeholder, restaurar color normal
        if (
            "fg" not in kwargs
            and self.widget.get()
            and hasattr(self, "_placeholder_text")
        ):
            if self.widget.get() != self._placeholder_text:
                self.widget.config(fg="black")


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

    _groups: Dict[str, List["Radio"]] = {}

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
        return self.var.get() == self.widget["value"]

    @selected.setter
    def selected(self, value: bool):
        """
        Establece si el botón está seleccionado.

        Args:
            value (bool): True para seleccionar, False para deseleccionar
        """
        if value:
            self.var.set(self.widget["value"])

    def _configure(self, **kwargs):
        """Configura el widget del botón de opción."""
        if "value" not in kwargs:
            kwargs["value"] = f"radio_{id(self)}"
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
            menu.add_command(label=option, command=lambda v=option: self.var.set(v))

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


# -----------------
# Medios e Iconos
# -----------------

_ICON_REGISTRY: Dict[str, str] = {}


def register_icon(name: str, path: str) -> None:
    """Registra un icono por nombre apuntando a un archivo de imagen."""
    _ICON_REGISTRY[name] = path


def register_icon_dir(mapping: Dict[str, str]) -> None:
    """Registra varios iconos con un mapeo nombre->ruta."""
    _ICON_REGISTRY.update(mapping)


class Image(UIComponent):
    """
    Componente de imagen raster (PNG/JPEG, etc.). Requiere Pillow.
    """

    def __init__(
        self,
        path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        keep_aspect: bool = True,
        **kwargs,
    ):
        self.path = path
        self.req_width = width
        self.req_height = height
        self.keep_aspect = keep_aspect
        self._img_ref = None  # Mantener referencia
        super().__init__(**kwargs)

    def _setup_widget(self):
        self.widget = tk.Label()
        self._load_image()

    def _load_image(self):
        if PILImage is None or ImageTk is None:
            raise ImportError("Pillow es requerido para Image")
        img = PILImage.open(self.path)
        if self.req_width or self.req_height:
            w, h = img.size
            if self.keep_aspect:
                if self.req_width and self.req_height:
                    ratio = min(self.req_width / w, self.req_height / h)
                elif self.req_width:
                    ratio = self.req_width / w
                else:
                    ratio = self.req_height / h  # type: ignore
                new_size = (max(1, int(w * ratio)), max(1, int(h * ratio)))
            else:
                new_size = (
                    self.req_width or img.size[0],
                    self.req_height or img.size[1],
                )
            img = img.resize(new_size, getattr(PILImage, "LANCZOS", PILImage.BICUBIC))
        self._img_ref = ImageTk.PhotoImage(img)
        self.widget.configure(image=self._img_ref)


class Icon(UIComponent):
    """
    Icono por nombre (registrado) o por ruta directa. Internamente usa Label con imagen.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        path: Optional[str] = None,
        size: Optional[int] = 16,
        **kwargs,
    ):
        self.name = name
        self.path = path
        self.size = size
        self._img_ref = None
        super().__init__(**kwargs)

    def _setup_widget(self):
        self.widget = tk.Label()
        self._load_icon()

    def _load_icon(self):
        target = self.path
        if not target and self.name:
            target = _ICON_REGISTRY.get(self.name)
        if not target:
            return
        if PILImage is None or ImageTk is None:
            raise ImportError("Pillow es requerido para Icon")
        img = PILImage.open(target)
        if self.size:
            img = img.resize(
                (self.size, self.size), getattr(PILImage, "LANCZOS", PILImage.BICUBIC)
            )
        self._img_ref = ImageTk.PhotoImage(img)
        self.widget.configure(image=self._img_ref)


# -----------------
# Listas y Tablas
# -----------------


class ListView(UIComponent):
    """
    Lista simple de ítems con selección.
    """

    def __init__(
        self, items: Optional[List[str]] = None, selectmode: str = "browse", **kwargs
    ):
        self._items = items or []
        self.selectmode = selectmode
        super().__init__(**kwargs)

    def _setup_widget(self):
        self.widget = tk.Listbox(selectmode=self.selectmode)
        for it in self._items:
            self.widget.insert(tk.END, it)

    @property
    def items(self) -> List[str]:
        return [self.widget.get(i) for i in range(self.widget.size())]

    @items.setter
    def items(self, value: Iterable[str]):
        self.widget.delete(0, tk.END)
        for it in value:
            self.widget.insert(tk.END, it)

    def selected_indices(self) -> List[int]:
        return list(self.widget.curselection())

    def selected_values(self) -> List[str]:
        return [self.widget.get(i) for i in self.selected_indices()]

    def clear(self):
        self.widget.delete(0, tk.END)

    def add(self, item: str):
        self.widget.insert(tk.END, item)

    def remove_at(self, index: int):
        self.widget.delete(index)


class Table(UIComponent):
    """
    Tabla avanzada basada en ttk.Treeview con funcionalidades mejoradas.

    Uso básico:
        tabla = table(columns=["Nombre", "Edad", "Ciudad"])
        tabla.add_row(["Juan", 25, "Madrid"])
        tabla.add_row(["Ana", 30, "Barcelona"])

    Uso avanzado con datos:
        data = [
            {"Nombre": "Juan", "Edad": 25, "Ciudad": "Madrid"},
            {"Nombre": "Ana", "Edad": 30, "Ciudad": "Barcelona"}
        ]
        tabla.set_data(data)
    """

    def __init__(
        self,
        columns: List[str] = None,
        data: Optional[List] = None,
        show_row_numbers: bool = False,
        sortable: bool = True,
        editable: bool = False,
        **kwargs,
    ):
        """
        Inicializa una tabla avanzada.

        Args:
            columns (List[str]): Lista de nombres de columnas
            data (List, optional): Datos iniciales para la tabla
            show_row_numbers (bool): Mostrar números de fila
            sortable (bool): Permitir ordenamiento por columnas
            editable (bool): Permitir edición directa de celdas
            **kwargs: Parámetros CSS-style adicionales
        """
        self.columns = columns or []
        self._data = data or []
        self.show_row_numbers = show_row_numbers
        self.sortable = sortable
        self.editable = editable
        self._sort_column = None
        self._sort_reverse = False

        super().__init__(**kwargs)

        # Cargar datos iniciales
        if self._data:
            self.set_data(self._data)

    def _setup_widget(self):
        """Configura el widget Treeview avanzado."""
        # Configurar columnas
        if self.show_row_numbers:
            self.widget = ttk.Treeview(columns=self.columns, show="headings")
            # Agregar columna de números de fila
            self.widget.heading("#0", text="#", anchor=tk.W)
            self.widget.column("#0", width=50, anchor=tk.W, stretch=False)
        else:
            self.widget = ttk.Treeview(columns=self.columns, show="headings")

        # Configurar encabezados y columnas
        for col in self.columns:
            self.widget.heading(
                col, text=col, command=lambda c=col: self._sort_by_column(c)
            )
            self.widget.column(col, anchor=tk.W, stretch=True, minwidth=100)

        # Configurar eventos para edición si está habilitado
        if self.editable:
            self.widget.bind("<Double-1>", self._on_double_click)

    def _sort_by_column(self, column):
        """Ordena la tabla por la columna especificada."""
        if not self.sortable:
            return

        # Obtener datos actuales
        data = []
        for item in self.widget.get_children():
            values = self.widget.item(item, "values")
            if self.show_row_numbers:
                row_num = self.widget.item(item, "text")
                data.append((row_num, values))
            else:
                data.append(values)

        # Ordenar por la columna seleccionada
        col_index = self.columns.index(column)
        data.sort(
            key=lambda x: x[col_index] if col_index < len(x) else "",
            reverse=self._sort_reverse,
        )

        # Actualizar tabla
        self.clear()
        for row in data:
            if self.show_row_numbers:
                self.widget.insert("", tk.END, text=row[0], values=row[1])
            else:
                self.widget.insert("", tk.END, values=row)

        # Alternar orden para siguiente click
        self._sort_reverse = not self._sort_reverse

    def _on_double_click(self, event):
        """Maneja doble click para edición."""
        if not self.editable:
            return

        item = self.widget.identify_row(event.y)
        column = self.widget.identify_column(event.x)

        if item and column:
            # Crear entrada de edición
            x, y, width, height = self.widget.bbox(item, column)

            # Crear entry para edición
            self._edit_entry = tk.Entry(self.widget)
            self._edit_entry.place(x=x, y=y, width=width, height=height)

            # Obtener valor actual
            current_value = self.widget.item(item, "values")[
                self.columns.index(column) - 1
                if self.show_row_numbers
                else self.columns.index(column)
            ]

            self._edit_entry.insert(0, current_value)
            self._edit_entry.focus()
            self._edit_entry.select_all()

            # Bindings para confirmar/cancelar edición
            self._edit_entry.bind(
                "<Return>", lambda e: self._confirm_edit(item, column)
            )
            self._edit_entry.bind("<Escape>", lambda e: self._cancel_edit())

    def _confirm_edit(self, item, column):
        """Confirma la edición de una celda."""
        new_value = self._edit_entry.get()
        self._edit_entry.destroy()

        # Actualizar valor en la tabla
        values = list(self.widget.item(item, "values"))
        if self.show_row_numbers:
            col_index = self.columns.index(column) - 1
        else:
            col_index = self.columns.index(column)

        values[col_index] = new_value
        self.widget.item(item, values=values)

    def _cancel_edit(self):
        """Cancela la edición."""
        self._edit_entry.destroy()

    def clear(self):
        """Limpia todos los datos de la tabla."""
        for item in self.widget.get_children():
            self.widget.delete(item)

    def add_row(self, values: Union[Dict[str, Any], List[Any], tuple]):
        """
        Agrega una fila a la tabla.

        Args:
            values: Valores de la fila (dict, lista o tupla)
        """
        if isinstance(values, dict):
            row = [values.get(c, "") for c in self.columns]
        else:
            row = list(values)

        # Asegurar que tenga el número correcto de columnas
        while len(row) < len(self.columns):
            row.append("")

        if self.show_row_numbers:
            row_num = len(self.widget.get_children()) + 1
            self.widget.insert("", tk.END, text=str(row_num), values=row)
        else:
            self.widget.insert("", tk.END, values=row)

    def set_data(self, rows: Iterable[Union[Dict[str, Any], List[Any], tuple]]):
        """
        Establece todos los datos de la tabla.

        Args:
            rows: Iterable de filas de datos
        """
        self.clear()
        for row in rows:
            self.add_row(row)

    def get_data(self) -> List[List[str]]:
        """
        Obtiene todos los datos de la tabla.

        Returns:
            Lista de listas con los valores de cada fila
        """
        data = []
        for item in self.widget.get_children():
            values = list(self.widget.item(item, "values"))
            if self.show_row_numbers:
                row_num = self.widget.item(item, "text")
                data.append([row_num] + values)
            else:
                data.append(values)
        return data

    def get_selected_rows(self) -> List[List[str]]:
        """
        Obtiene las filas seleccionadas.

        Returns:
            Lista de listas con los valores de las filas seleccionadas
        """
        selected_items = self.widget.selection()
        data = []
        for item in selected_items:
            values = list(self.widget.item(item, "values"))
            if self.show_row_numbers:
                row_num = self.widget.item(item, "text")
                data.append([row_num] + values)
            else:
                data.append(values)
        return data

    def delete_selected_rows(self):
        """Elimina las filas seleccionadas."""
        selected_items = self.widget.selection()
        for item in selected_items:
            self.widget.delete(item)

    def get_cell_value(self, row_index: int, column: str) -> str:
        """
        Obtiene el valor de una celda específica.

        Args:
            row_index: Índice de la fila (0-based)
            column: Nombre de la columna

        Returns:
            Valor de la celda
        """
        items = self.widget.get_children()
        if 0 <= row_index < len(items):
            item = items[row_index]
            values = list(self.widget.item(item, "values"))
            col_index = self.columns.index(column)
            return values[col_index]
        return ""

    def set_cell_value(self, row_index: int, column: str, value: str):
        """
        Establece el valor de una celda específica.

        Args:
            row_index: Índice de la fila (0-based)
            column: Nombre de la columna
            value: Nuevo valor para la celda
        """
        items = self.widget.get_children()
        if 0 <= row_index < len(items):
            item = items[row_index]
            values = list(self.widget.item(item, "values"))
            col_index = self.columns.index(column)
            values[col_index] = value
            self.widget.item(item, values=values)

    def filter_rows(self, column: str, filter_text: str):
        """
        Filtra las filas que contienen el texto en la columna especificada.

        Args:
            column: Nombre de la columna a filtrar
            filter_text: Texto a buscar
        """
        # Ocultar todas las filas
        for item in self.widget.get_children():
            self.widget.detach(item)

        # Mostrar solo las que coinciden con el filtro
        filter_lower = filter_text.lower()
        for item in self.widget.get_children():
            values = list(self.widget.item(item, "values"))
            col_index = self.columns.index(column)
            if filter_lower in str(values[col_index]).lower():
                self.widget.reattach(item, "", tk.END)

    def export_to_csv(self, filename: str):
        """
        Exporta los datos de la tabla a un archivo CSV.

        Args:
            filename: Nombre del archivo CSV
        """
        import csv

        data = self.get_data()
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # Escribir encabezados
            headers = ["#"] + self.columns if self.show_row_numbers else self.columns
            writer.writerow(headers)
            # Escribir datos
            writer.writerows(data)

    def get_column_widths(self) -> Dict[str, int]:
        """
        Obtiene los anchos actuales de las columnas.

        Returns:
            Diccionario con nombres de columna y sus anchos
        """
        widths = {}
        for col in self.columns:
            widths[col] = self.widget.column(col, "width")
        return widths

    def set_column_width(self, column: str, width: int):
        """
        Establece el ancho de una columna específica.

        Args:
            column: Nombre de la columna
            width: Ancho en píxeles
        """
        self.widget.column(column, width=width)

    def auto_resize_columns(self):
        """Ajusta automáticamente el ancho de las columnas al contenido."""
        for col in self.columns:
            # Obtener el ancho máximo del contenido
            max_width = len(col) * 10  # Ancho mínimo basado en el encabezado

            # Buscar el contenido más ancho en esta columna
            for item in self.widget.get_children():
                values = list(self.widget.item(item, "values"))
                col_index = self.columns.index(col)
                if col_index < len(values):
                    content_width = len(str(values[col_index])) * 8
                    max_width = max(max_width, content_width)

            self.widget.column(col, width=max_width)


def table(columns: List[str] = None, data: Optional[List] = None, **kwargs) -> Table:
    """
    Función helper para crear tablas fácilmente.

    Args:
        columns: Lista de nombres de columnas
        data: Datos iniciales opcionales
        **kwargs: Parámetros adicionales

    Returns:
        Table: Nueva instancia de tabla
    """
    return Table(columns=columns, data=data, **kwargs)
