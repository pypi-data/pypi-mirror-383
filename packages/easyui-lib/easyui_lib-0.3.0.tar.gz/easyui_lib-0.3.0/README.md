# 🎨 EasyUI - Librería Moderna para Interfaces de Usuario en Python

[![PyPI version](https://badge.fury.io/py/easyui-lib.svg)](https://badge.fury.io/py/easyui-lib)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/personalized-badge/easyui-lib?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/easyui-lib)

**EasyUI** es una librería revolucionaria para crear interfaces gráficas en Python de manera **increíblemente simple** pero **extremadamente poderosa**. Construida sobre Tkinter pero con una API moderna inspirada en frameworks web.

## 🌟 Características Principales

### ⚡ **API Ultra-Minimalista**
```python
from easyui import *

# ¡Solo 3 líneas para una aplicación completa!
f = form("Mi App").add(
    label("¡Hola Mundo!"),
    button("Click me")
).show()
```

### 🎨 **Parámetros CSS-Style**
```python
# Estilos modernos como en CSS
boton = (button("Enviar")
        .background("#007bff")
        .color("white")
        .padding(15)
        .font_size(14)
        .border(2))
```

### 📊 **Tablas Avanzadas Profesionales**
```python
# Tablas con funcionalidades empresariales
tabla = table(columns=["Nombre", "Edad", "Ciudad"],
             data=usuarios,
             sortable=True,        # Ordenable por columnas
             editable=True,        # Edición directa
             show_row_numbers=True) # Números de fila

# Funcionalidades avanzadas
tabla.filter_rows("Nombre", "Juan")  # Filtrar
datos = tabla.get_selected_rows()    # Obtener seleccionados
tabla.export_to_csv("datos.csv")     # Exportar
```

### 🔧 **Configuración Fluida (Method Chaining)**
```python
# Configuración elegante en cadena
formulario = (form("Contacto")
             .background("#f8f9fa")
             .width(800)
             .height(600))
```

### 🚀 **Funciones Helper Globales**
```python
# API aún más simple
from easyui import *

# Crea controles con configuración automática
formulario = form("Registro")
formulario.add(
    label("Nombre:"),
    input("Escribe tu nombre"),
    button("Guardar")
)
```

## 📦 Instalación

### Instalación Estable
```bash
pip install easyui-lib
```

### Instalación con Funcionalidades Avanzadas
```bash
# Para tablas estilo Excel y funcionalidades premium
pip install easyui-lib[tables]
```

### Desarrollo Local
```bash
git clone https://github.com/tuusuario/easyui.git
cd easyui
pip install -e .
```

## 🚀 Inicio Rápido

### Ejemplo Básico (3 líneas)
```python
from easyui import form, label

f = form("Hola Mundo")
f.add(label("¡Hola, EasyUI!"))
f.show()
```

### Ejemplo Avanzado con Estilos
```python
from easyui import *

# Formulario con estilos CSS modernos
f = (form("Aplicación Profesional", width=800, height=600)
    .background("#f8f9fa"))

# Botones con diferentes estilos
f.add(
    button("Primario", background_color="#007bff", color="white"),
    button("Secundario", background_color="#6c757d", color="white"),
    button("Peligro", background_color="#dc3545", color="white")
)

# Campos de entrada con estilos
f.row(
    label("Nombre:", font_size=14, color="#333"),
    input(placeholder="Escribe tu nombre", padding=10, border=1)
)

f.show()
```

### Ejemplo con Tablas Profesionales
```python
from easyui import *

# Datos de ejemplo
usuarios = [
    {"Nombre": "Ana García", "Edad": 25, "Ciudad": "Madrid"},
    {"Nombre": "Carlos López", "Edad": 30, "Ciudad": "Barcelona"},
    {"Nombre": "María Rodríguez", "Edad": 28, "Ciudad": "Valencia"}
]

# Tabla avanzada con funcionalidades empresariales
tabla = (table(columns=["Nombre", "Edad", "Ciudad"],
              data=usuarios,
              sortable=True,
              editable=True,
              show_row_numbers=True)
        .height(300))

# Funcionalidades interactivas
def filtrar_por_edad():
    tabla.filter_rows("Edad", "25")

def exportar_datos():
    tabla.export_to_csv("usuarios.csv")

# Controles para la tabla
f = form("Gestión de Usuarios")
f.add(tabla)
f.row(
    button("Filtrar Mayores de 25", on_click=filtrar_por_edad),
    button("Exportar CSV", on_click=exportar_datos)
)
f.show()
```

## 📚 Documentación Completa

### Componentes Disponibles

#### **Contenedores y Layout**
- `form(title, width, height, **styles)` - Formulario principal
- `Window(title, width, height)` - Ventana básica
- `VBox(*components)` - Layout vertical
- `HBox(*components)` - Layout horizontal

#### **Controles Básicos**
- `label(text, **styles)` - Etiquetas de texto
- `button(text, on_click, **styles)` - Botones interactivos
- `input(placeholder, **styles)` - Campos de entrada
- `checkbox(text, **styles)` - Casillas de verificación
- `radio(text, group, **styles)` - Botones de opción
- `dropdown(options, **styles)` - Menús desplegables

#### **Datos Avanzados**
- `table(columns, data, **options)` - Tablas profesionales
- `listview(items, **styles)` - Listas simples

#### **Multimedia**
- `image(path, **styles)` - Imágenes raster
- `icon(name, **styles)` - Iconos vectoriales

### Parámetros CSS-Style Soportados

#### **Dimensiones y Espaciado**
- `width`, `height` - Dimensiones
- `padding`, `margin` - Espaciado interno/externo
- `padding-left`, `padding-top`, etc. - Espaciado específico

#### **Colores y Apariencia**
- `background`, `background-color` - Fondo
- `color`, `foreground` - Color de texto
- `border`, `border-width` - Bordes

#### **Tipografía**
- `font-size` - Tamaño de fuente
- `font-family` - Familia tipográfica
- `font-weight` - Grosor (normal, bold)

#### **Alineación**
- `text-align` - Alineación de texto
- `vertical-align` - Alineación vertical

### Funcionalidades Avanzadas de Tablas

#### **Características Principales**
```python
tabla = table(
    columns=["Nombre", "Edad", "Ciudad"],
    data=usuarios,
    sortable=True,        # Ordenable por columnas
    editable=True,        # Edición directa con doble clic
    show_row_numbers=True # Numeración automática
)
```

#### **Operaciones Disponibles**
```python
# Manipulación de datos
datos = tabla.get_data()           # Obtener todos los datos
seleccionados = tabla.get_selected_rows()  # Filas seleccionadas
tabla.set_data(nuevos_datos)       # Establecer nuevos datos

# Edición programática
tabla.set_cell_value(0, "Nombre", "Nuevo Nombre")
valor = tabla.get_cell_value(1, "Edad")

# Filtrado y búsqueda
tabla.filter_rows("Ciudad", "Madrid")

# Exportación
tabla.export_to_csv("datos.csv")

# Ajustes visuales
tabla.auto_resize_columns()
ancho = tabla.get_column_widths()
```

## 🎯 Ejemplos Completos

### **Aplicación de Gestión de Datos**
```python
from easyui import *

# Datos de empleados
empleados = [
    {"Nombre": "Ana García", "Departamento": "Ventas", "Salario": "€45,000"},
    {"Nombre": "Carlos López", "Departamento": "Desarrollo", "Salario": "€52,000"},
    {"Nombre": "María Rodríguez", "Departamento": "Marketing", "Salario": "€48,000"}
]

# Aplicación empresarial completa
f = form("Sistema de Gestión Empresarial", width=1000, height=700)

# Tabla con funcionalidades avanzadas
tabla = (table(columns=["Nombre", "Departamento", "Salario"],
              data=empleados,
              sortable=True,
              editable=True)
        .height(400))

# Controles interactivos
def filtrar_ventas():
    tabla.filter_rows("Departamento", "Ventas")

def exportar_datos():
    tabla.export_to_csv("empleados.csv")

f.add(tabla)
f.row(
    button("Empleados de Ventas", on_click=filtrar_ventas),
    button("Exportar Datos", on_click=exportar_datos)
)
f.show()
```

## 🔧 Configuración Avanzada

### Dependencias Opcionales
```toml
# pyproject.toml
[project.optional-dependencies]
tables = [
    "pandastable>=0.13.0",  # Tablas estilo Excel
    "tkintertable>=1.0.0",   # Alternativa moderna
]
```

### Instalación con Funcionalidades Premium
```bash
pip install easyui-lib[tables]
```

## 📈 Versiones y Estado

- **Versión actual:** `0.3.0`
- **Estado:** `Beta` - Funcionalidades principales implementadas y probadas
- **Próxima versión:** `1.0.0` - Estable para producción

## 🤝 Contribuir

¡Contribuciones bienvenidas! Puedes:

1. Reportar bugs en [GitHub Issues](https://github.com/tuusuario/easyui/issues)
2. Enviar Pull Requests con mejoras
3. Crear ejemplos y tutoriales
4. Ayudar con la documentación

## 📝 Licencia

Este proyecto está bajo la licencia **MIT**. Ver el archivo `LICENSE` para más detalles.

## 🙏 Autores

- **Cascade** - Arquitecto principal
- **Kalum** - Desarrollador core
- **Ashriel** - Diseñador de UX

---

**⭐ Si te gusta EasyUI, ¡dale una estrella en GitHub!**

[🌟 Ver en GitHub](https://github.com/tuusuario/easyui) | [📚 Documentación completa](https://easyui.readthedocs.io/) | [💬 Comunidad](https://discord.gg/easyui)
