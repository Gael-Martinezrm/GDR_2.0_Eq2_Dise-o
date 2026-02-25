"""
main.py

Punto de entrada para la aplicación Sistema de Retiros.
Inicializa la base de datos y lanza la ventana de login.
"""

import tkinter as tk
from app.db.connection import init_db
from app.auth.login import LoginWindow


def main():
    """
    Función principal que inicializa la aplicación.

    1. Inicializa la base de datos (crea tablas si no existen)
    2. Carga datos iniciales (seed) si es la primera ejecución
    3. Lanza la ventana de login
    """
    # Inicializar base de datos
    init_db()

    # Crear y ejecutar la aplicación
    app = LoginWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
