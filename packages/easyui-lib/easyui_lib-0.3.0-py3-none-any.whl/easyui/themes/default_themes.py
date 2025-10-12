""
Módulo que define los temas predeterminados de EasyUI.
"""
from .theme_loader import ThemeLoader

def register_default_themes():
    """Registra los temas predeterminados en el cargador de temas."""
    theme_loader = ThemeLoader()
    
    # Tema Claro (light)
    light_theme = {
        'name': 'light',
        'colors': {
            'primary': '#1976d2',
            'secondary': '#9c27b0',
            'success': '#2e7d32',
            'error': '#d32f2f',
            'warning': '#ed6c02',
            'info': '#0288d1',
            'background': '#f5f5f5',
            'surface': '#ffffff',
            'text': {
                'primary': 'rgba(0, 0, 0, 0.87)',
                'secondary': 'rgba(0, 0, 0, 0.6)',
                'disabled': 'rgba(0, 0, 0, 0.38)',
                'hint': 'rgba(0, 0, 0, 0.38)'
            },
            'divider': 'rgba(0, 0, 0, 0.12)'
        },
        'typography': {
            'font_family': '"Roboto", "Helvetica", "Arial", sans-serif',
            'font_size': '14px',
            'font_weights': {
                'light': 300,
                'regular': 400,
                'medium': 500,
                'bold': 700
            },
            'h1': {'size': '6rem', 'weight': 300, 'line_height': 1.167, 'letter_spacing': '-0.01562em'},
            'h2': {'size': '3.75rem', 'weight': 300, 'line_height': 1.2, 'letter_spacing': '-0.00833em'},
            'h3': {'size': '3rem', 'weight': 400, 'line_height': 1.167, 'letter_spacing': '0em'},
            'h4': {'size': '2.125rem', 'weight': 400, 'line_height': 1.235, 'letter_spacing': '0.00735em'},
            'h5': {'size': '1.5rem', 'weight': 400, 'line_height': 1.334, 'letter_spacing': '0em'},
            'h6': {'size': '1.25rem', 'weight': 500, 'line_height': 1.6, 'letter_spacing': '0.0075em'},
            'subtitle1': {'size': '1rem', 'weight': 400, 'line_height': 1.75, 'letter_spacing': '0.00938em'},
            'subtitle2': {'size': '0.875rem', 'weight': 500, 'line_height': 1.57, 'letter_spacing': '0.00714em'},
            'body1': {'size': '1rem', 'weight': 400, 'line_height': 1.5, 'letter_spacing': '0.00938em'},
            'body2': {'size': '0.875rem', 'weight': 400, 'line_height': 1.43, 'letter_spacing': '0.01071em'},
            'button': {'size': '0.875rem', 'weight': 500, 'line_height': 1.75, 'letter_spacing': '0.02857em', 'text_transform': 'uppercase'},
            'caption': {'size': '0.75rem', 'weight': 400, 'line_height': 1.66, 'letter_spacing': '0.03333em'},
            'overline': {'size': '0.75rem', 'weight': 400, 'line_height': 2.66, 'letter_spacing': '0.08333em', 'text_transform': 'uppercase'}
        },
        'shape': {
            'border_radius': '4px',
            'border_width': '1px',
            'border_style': 'solid',
            'border_color': 'rgba(0, 0, 0, 0.23)'
        },
        'spacing': {
            'unit': 8,
            'container': 1200,
            'gutter': 24
        },
        'shadows': [
            'none',
            '0px 2px 1px -1px rgba(0,0,0,0.2),0px 1px 1px 0px rgba(0,0,0,0.14),0px 1px 3px 0px rgba(0,0,0,0.12)',
            '0px 3px 1px -2px rgba(0,0,0,0.2),0px 2px 2px 0px rgba(0,0,0,0.14),0px 1px 5px 0px rgba(0,0,0,0.12)',
            '0px 3px 3px -2px rgba(0,0,0,0.2),0px 3px 4px 0px rgba(0,0,0,0.14),0px 1px 8px 0px rgba(0,0,0,0.12)'
        ],
        'transitions': {
            'easing': {
                'easeInOut': 'cubic-bezier(0.4, 0, 0.2, 1)',
                'easeOut': 'cubic-bezier(0.0, 0, 0.2, 1)',
                'easeIn': 'cubic-bezier(0.4, 0, 1, 1)',
                'sharp': 'cubic-bezier(0.4, 0, 0.6, 1)'
            },
            'duration': {
                'shortest': 150,
                'shorter': 200,
                'short': 250,
                'standard': 300,
                'complex': 375,
                'enteringScreen': 225,
                'leavingScreen': 195
            }
        },
        'z_index': {
            'mobile_stepper': 1000,
            'speed_dial': 1050,
            'app_bar': 1100,
            'drawer': 1200,
            'modal': 1300,
            'snackbar': 1400,
            'tooltip': 1500
        }
    }
    
    # Tema Oscuro (dark)
    dark_theme = {
        'name': 'dark',
        'colors': {
            'primary': '#90caf9',
            'secondary': '#ce93d8',
            'success': '#81c784',
            'error': '#f44336',
            'warning': '#ffb74d',
            'info': '#64b5f6',
            'background': '#121212',
            'surface': '#1e1e1e',
            'text': {
                'primary': 'rgba(255, 255, 255, 0.87)',
                'secondary': 'rgba(255, 255, 255, 0.7)',
                'disabled': 'rgba(255, 255, 255, 0.5)',
                'hint': 'rgba(255, 255, 255, 0.5)'
            },
            'divider': 'rgba(255, 255, 255, 0.12)'
        },
        'typography': {
            'font_family': '"Roboto", "Helvetica", "Arial", sans-serif',
            'font_size': '14px',
            'font_weights': {
                'light': 300,
                'regular': 400,
                'medium': 500,
                'bold': 700
            },
            'h1': {'size': '6rem', 'weight': 300, 'line_height': 1.167, 'letter_spacing': '-0.01562em'},
            'h2': {'size': '3.75rem', 'weight': 300, 'line_height': 1.2, 'letter_spacing': '-0.00833em'},
            'h3': {'size': '3rem', 'weight': 400, 'line_height': 1.167, 'letter_spacing': '0em'},
            'h4': {'size': '2.125rem', 'weight': 400, 'line_height': 1.235, 'letter_spacing': '0.00735em'},
            'h5': {'size': '1.5rem', 'weight': 400, 'line_height': 1.334, 'letter_spacing': '0em'},
            'h6': {'size': '1.25rem', 'weight': 500, 'line_height': 1.6, 'letter_spacing': '0.0075em'},
            'subtitle1': {'size': '1rem', 'weight': 400, 'line_height': 1.75, 'letter_spacing': '0.00938em'},
            'subtitle2': {'size': '0.875rem', 'weight': 500, 'line_height': 1.57, 'letter_spacing': '0.00714em'},
            'body1': {'size': '1rem', 'weight': 400, 'line_height': 1.5, 'letter_spacing': '0.00938em'},
            'body2': {'size': '0.875rem', 'weight': 400, 'line_height': 1.43, 'letter_spacing': '0.01071em'},
            'button': {'size': '0.875rem', 'weight': 500, 'line_height': 1.75, 'letter_spacing': '0.02857em', 'text_transform': 'uppercase'},
            'caption': {'size': '0.75rem', 'weight': 400, 'line_height': 1.66, 'letter_spacing': '0.03333em'},
            'overline': {'size': '0.75rem', 'weight': 400, 'line_height': 2.66, 'letter_spacing': '0.08333em', 'text_transform': 'uppercase'}
        },
        'shape': {
            'border_radius': '4px',
            'border_width': '1px',
            'border_style': 'solid',
            'border_color': 'rgba(255, 255, 255, 0.23)'
        },
        'spacing': {
            'unit': 8,
            'container': 1200,
            'gutter': 24
        },
        'shadows': [
            'none',
            '0px 2px 1px -1px rgba(0,0,0,0.4),0px 1px 1px 0px rgba(0,0,0,0.34),0px 1px 3px 0px rgba(0,0,0,0.32)',
            '0px 3px 1px -2px rgba(0,0,0,0.4),0px 2px 2px 0px rgba(0,0,0,0.34),0px 1px 5px 0px rgba(0,0,0,0.32)',
            '0px 3px 3px -2px rgba(0,0,0,0.4),0px 3px 4px 0px rgba(0,0,0,0.34),0px 1px 8px 0px rgba(0,0,0,0.32)'
        ],
        'transitions': {
            'easing': {
                'easeInOut': 'cubic-bezier(0.4, 0, 0.2, 1)',
                'easeOut': 'cubic-bezier(0.0, 0, 0.2, 1)',
                'easeIn': 'cubic-bezier(0.4, 0, 1, 1)',
                'sharp': 'cubic-bezier(0.4, 0, 0.6, 1)'
            },
            'duration': {
                'shortest': 150,
                'shorter': 200,
                'short': 250,
                'standard': 300,
                'complex': 375,
                'enteringScreen': 225,
                'leavingScreen': 195
            }
        },
        'z_index': {
            'mobile_stepper': 1000,
            'speed_dial': 1050,
            'app_bar': 1100,
            'drawer': 1200,
            'modal': 1300,
            'snackbar': 1400,
            'tooltip': 1500
        }
    }
    
    # Registrar los temas
    theme_loader.register_theme('light', light_theme)
    theme_loader.register_theme('dark', dark_theme)
    
    # Establecer el tema claro como predeterminado
    theme_loader.set_current_theme('light')

# Registrar los temas predeterminados al importar el módulo
register_default_themes()
