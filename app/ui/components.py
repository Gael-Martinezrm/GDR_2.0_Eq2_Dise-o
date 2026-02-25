"""
app/ui/components.py

Componentes reutilizables de la interfaz gráfica.
Funciones auxiliares para crear componentes estilizados.
"""

import tkinter as tk
from tkinter import ttk


# Paleta de colores
C_BG = "#F0F2F5"
C_SIDEBAR = "#1565C0"
C_ACCENT = "#1976D2"
C_WHITE = "#FFFFFF"
C_TEXT = "#212121"
C_HEADER = "#1565C0"
C_BTN = "#1565C0"
C_DANGER = "#C62828"


def styled_button(parent, text, command=None, color=C_BTN, width=15, danger=False):
    """
    Crea un botón estilizado con la paleta de colores del sistema.

    Args:
        parent: Widget padre.
        text (str): Texto del botón.
        command (callable): Función a ejecutar al hacer click.
        color (str): Color de fondo (hex). Usar C_DANGER para botones destructivos.
        width (int): Ancho del botón.
        danger (bool): Si True, usa color rojo (C_DANGER).

    Returns:
        tk.Button: Botón estilizado.
    """
    if danger:
        color = C_DANGER

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=C_WHITE,
        font=("Arial", 10),
        width=width,
        relief=tk.FLAT,
        cursor="hand2"
    )
    return btn


def make_treeview(parent, columns, widths, height=15):
    """
    Crea un Treeview (tabla) estilizado.

    Args:
        parent: Widget padre.
        columns (list): Lista de nombres de columnas.
        widths (list): Lista de anchos para cada columna.
        height (int): Altura de la tabla en filas.

    Returns:
        ttk.Treeview: Tabla estilizada.
    """
    # TODO: Implementar creación de Treeview
    # 1. Crear Treeview con las columnas
    # 2. Configurar ancho de columnas
    # 3. Aplicar estilos
    # 4. Agregar scrollbars (vertical y horizontal)
    pass


def page_header(parent, titulo, color=C_HEADER):
    """
    Crea un encabezado estilizado para una página/vista.

    Args:
        parent: Widget padre.
        titulo (str): Texto del encabezado.
        color (str): Color de fondo (hex).

    Returns:
        tk.Frame: Frame del encabezado.
    """
    # TODO: Implementar encabezado
    # 1. Crear frame con fondo azul
    # 2. Agregar label con título en blanco
    # 3. Retornar frame
    pass


def make_labeled_entry(parent, label_text, default_value="", width=20):
    """
    Crea un campo de entrada con etiqueta.

    Args:
        parent: Widget padre.
        label_text (str): Texto de la etiqueta.
        default_value (str): Valor inicial del campo.
        width (int): Ancho del campo de entrada.

    Returns:
        tuple: (tk.Label, tk.Entry) - Etiqueta y campo de entrada.
    """
    label = tk.Label(parent, text=label_text, font=("Arial", 10), fg=C_TEXT)
    entry = tk.Entry(parent, width=width, font=("Arial", 10))
    if default_value:
        entry.insert(0, default_value)
    return label, entry


def make_combobox(parent, label_text, values, default_value="", width=18):
    """
    Crea un combobox con etiqueta.

    Args:
        parent: Widget padre.
        label_text (str): Texto de la etiqueta.
        values (list): Lista de valores disponibles.
        default_value (str): Valor inicial.
        width (int): Ancho del combobox.

    Returns:
        tuple: (tk.Label, ttk.Combobox) - Etiqueta y combobox.
    """
    label = tk.Label(parent, text=label_text, font=("Arial", 10), fg=C_TEXT)
    combo = ttk.Combobox(parent, values=values, width=width, state="readonly", font=("Arial", 10))
    if default_value:
        combo.set(default_value)
    return label, combo


def create_info_card(parent, titulo, valor, bg_color=C_ACCENT):
    """
    Crea una tarjeta de información (para dashboard).

    Args:
        parent: Widget padre.
        titulo (str): Título de la tarjeta.
        valor (str): Valor a mostrar.
        bg_color (str): Color de fondo (hex).

    Returns:
        tk.Frame: Frame de la tarjeta.
    """
    # TODO: Implementar tarjeta de información
    # 1. Crear frame con color de fondo
    # 2. Agregar label con título (más pequeño)
    # 3. Agregar label con valor (más grande y destacado)
    # 4. Retornar frame
    pass


def create_separator(parent, height=2, color=C_ACCENT):
    """
    Crea una línea separadora.

    Args:
        parent: Widget padre.
        height (int): Alto de la línea en píxeles.
        color (str): Color de la línea (hex).

    Returns:
        tk.Frame: Frame separador.
    """
    sep = tk.Frame(parent, bg=color, height=height)
    return sep
