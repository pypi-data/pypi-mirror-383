# EasyUI

EasyUI es una librería Python que facilita la creación de interfaces de usuario de manera sencilla e intuitiva.

## Características

- Creación rápida de interfaces gráficas
- Sintaxis simple y legible
- Componentes preconstruidos
- Personalización fácil

## Instalación

```bash
pip install easyui
```

## Uso básico

```python
from easyui import Window, Button, Label

def on_click():
    print("¡Botón presionado!")

# Crear una ventana
window = Window("Mi Aplicación", width=400, height=300)

# Agregar componentes
label = Label("¡Bienvenido a EasyUI!")
button = Button("Haz clic aquí", on_click=on_click)

# Mostrar la ventana
window.show()
```

## Autores

- Cascade
- Kalum
- Ashriel

## Licencia

MIT
