"""
app/ui/vista_retiros.py

Punto de entrada independiente para la vista de retiros.
"""

import tkinter as tk
from app.modules.retiros.view import RetirosView

C_BG      = "#F0F2F5"
C_SIDEBAR = "#1565C0"


def main():
    ventana = tk.Tk()
    ventana.title("Sistema de Control de Retiros — Equipo 2")
    ventana.geometry("900x600")
    ventana.minsize(700, 480)
    ventana.configure(bg=C_BG)

    sidebar = tk.Frame(ventana, bg=C_SIDEBAR, width=56)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    contenido = tk.Frame(ventana, bg=C_BG)
    contenido.pack(side="left", fill="both", expand=True)

    RetirosView(contenido).pack(fill="both", expand=True)

    ventana.mainloop()


if __name__ == "__main__":
    main()