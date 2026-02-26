"""
app/ui/components.py

Componentes reutilizables de la interfaz gráfica.
Funciones auxiliares para crear componentes estilizados.
"""

import tkinter as tk
from tkinter import ttk


# Paleta de colores
C_BG     = "#F0F2F5"
C_SIDEBAR= "#1565C0"
C_ACCENT = "#1976D2"
C_WHITE  = "#FFFFFF"
C_TEXT   = "#212121"
C_HEADER = "#1565C0"
C_BTN    = "#1565C0"
C_DANGER = "#C62828"


def styled_button(parent, text, command=None, color=C_BTN, width=15, danger=False):
    if danger:
        color = C_DANGER
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=C_WHITE,
        activebackground="#0D47A1" if not danger else "#B71C1C",
        activeforeground=C_WHITE,
        font=("Arial", 10), width=width,
        relief=tk.FLAT, cursor="hand2",
        padx=6, pady=5,
    )
    return btn


def make_treeview(parent, columns, widths, height=15):
    """
    Crea un Treeview estilizado dentro de un frame contenedor.

    Returns:
        tuple: (frame_contenedor, treeview)
        El frame_contenedor debe colocarse con pack/grid por el llamador.
        El treeview ya está dentro del frame con sus scrollbars.
    """
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("App.Treeview",
        background=C_WHITE, foreground=C_TEXT,
        fieldbackground=C_WHITE, rowheight=28,
        font=("Arial", 10),
    )
    style.configure("App.Treeview.Heading",
        background=C_SIDEBAR, foreground=C_WHITE,
        font=("Arial", 10, "bold"), relief="flat",
    )
    style.map("App.Treeview",
        background=[("selected", C_ACCENT)],
        foreground=[("selected", C_WHITE)],
    )

    # Frame contenedor — el llamador decide cómo colocarlo
    frm = tk.Frame(parent, bg=C_BG)

    col_ids = [f"col{i}" for i in range(len(columns))]
    tree = ttk.Treeview(frm, columns=col_ids, show="headings",
                        height=height, style="App.Treeview")

    for col_id, col_name, col_width in zip(col_ids, columns, widths):
        tree.heading(col_id, text=col_name, anchor="w")
        tree.column(col_id, width=col_width, anchor="w",
                    stretch=(col_name == columns[-1]))

    vsb = ttk.Scrollbar(frm, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    hsb = ttk.Scrollbar(frm, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    frm.rowconfigure(0, weight=1)
    frm.columnconfigure(0, weight=1)

    # Retorna tupla (frame, treeview)
    return frm, tree


def page_header(parent, titulo, color=C_HEADER):
    frm = tk.Frame(parent, bg=color, pady=14, padx=16)
    tk.Label(frm, text=titulo, bg=color, fg=C_WHITE,
             font=("Arial", 14, "bold")).pack(anchor="w")
    return frm


def make_labeled_entry(parent, label_text, default_value="", width=20):
    label = tk.Label(parent, text=label_text, font=("Arial", 10),
                     fg=C_TEXT, bg=parent.cget("bg"))
    entry = tk.Entry(parent, width=width, font=("Arial", 10),
                     relief="solid", bd=1)
    if default_value:
        entry.insert(0, default_value)
    return label, entry


def make_combobox(parent, label_text, values, default_value="", width=18):
    label = tk.Label(parent, text=label_text, font=("Arial", 10),
                     fg=C_TEXT, bg=parent.cget("bg"))
    combo = ttk.Combobox(parent, values=values, width=width,
                         state="readonly", font=("Arial", 10))
    if default_value:
        combo.set(default_value)
    return label, combo


def create_info_card(parent, titulo, valor, bg_color=C_ACCENT):
    frm = tk.Frame(parent, bg=bg_color, padx=20, pady=16)
    tk.Label(frm, text=titulo, bg=bg_color, fg="#BBDEFB",
             font=("Arial", 9)).pack(anchor="w")
    tk.Label(frm, text=valor, bg=bg_color, fg=C_WHITE,
             font=("Arial", 20, "bold")).pack(anchor="w", pady=(4, 0))
    return frm


def create_separator(parent, height=2, color=C_ACCENT):
    return tk.Frame(parent, bg=color, height=height)