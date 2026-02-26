"""
app/auth/login.py

Ventana de login para la aplicación.
Permite autenticación de usuarios.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from app.auth.session import Session
from app.modules.usuarios.model import obtener_usuario_por_username
from app.utils.helpers import verify_password

# Paleta de colores del sistema
C_BG      = "#F0F2F5"
C_SIDEBAR = "#1565C0"
C_ACCENT  = "#1976D2"
C_WHITE   = "#FFFFFF"
C_TEXT    = "#212121"
C_DANGER  = "#C62828"
C_GRAY    = "#B0BEC5"


class LoginWindow(tk.Tk):
    """
    Ventana de login para la aplicación.

    Permite que los usuarios se autentiquen en el sistema.
    Valida credenciales contra la base de datos.
    """

    def __init__(self):
        """
        Inicializa la ventana de login.

        Configura:
        - Dimensiones de la ventana
        - Componentes de la interfaz (campos de entrada, botones)
        - Iconos y estilos
        """
        super().__init__()
        self.title("Sistema de Retiros - Login")
        self.geometry("420x480")
        self.resizable(False, False)
        self.configure(bg=C_BG)
        self._centrar_ventana(420, 480)
        self._create_widgets()
        self.after(100, lambda: self.entry_usuario.focus())

    def _create_widgets(self):
        """
        Crea los widgets de la interfaz de login.

        Incluye:
        - Campo de usuario
        - Campo de contraseña
        - Botón de login
        """
        # ── Franja superior de color ──────────────────────────────────────────
        tk.Frame(self, bg=C_SIDEBAR, height=6).pack(fill="x")

        # ── Encabezado ────────────────────────────────────────────────────────
        frm_header = tk.Frame(self, bg=C_SIDEBAR, pady=28)
        frm_header.pack(fill="x")

        tk.Label(frm_header, text="Sistema de Retiros",
                 bg=C_SIDEBAR, fg=C_WHITE,
                 font=("Arial", 20, "bold")).pack()
        tk.Label(frm_header, text="Login",
                 bg=C_SIDEBAR, fg="#BBDEFB",
                 font=("Arial", 11)).pack()

        # ── Panel de formulario ───────────────────────────────────────────────
        frm_form = tk.Frame(self, bg=C_WHITE, padx=40, pady=32)
        frm_form.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(frm_form, text="Iniciar sesión",
                 bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 20))

        # Usuario
        tk.Label(frm_form, text="Usuario",
                 bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).pack(anchor="w")
        self.var_usuario = tk.StringVar()
        self.entry_usuario = tk.Entry(
            frm_form, textvariable=self.var_usuario,
            font=("Arial", 11), width=28,
            relief="solid", bd=1,
        )
        self.entry_usuario.pack(fill="x", ipady=6, pady=(3, 14))

        # Contraseña
        tk.Label(frm_form, text="Contraseña",
                 bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).pack(anchor="w")
        self.var_password = tk.StringVar()
        self.entry_password = tk.Entry(
            frm_form, textvariable=self.var_password,
            show="●", font=("Arial", 11), width=28,
            relief="solid", bd=1,
        )
        self.entry_password.pack(fill="x", ipady=6, pady=(3, 6))

        # Mensaje de error
        self.var_error = tk.StringVar()
        tk.Label(frm_form, textvariable=self.var_error,
                 bg=C_WHITE, fg=C_DANGER,
                 font=("Arial", 9), wraplength=300).pack(anchor="w", pady=(0, 14))

        # Botón login
        self.btn_login = tk.Button(
            frm_form, text="Entrar",
            command=self._validate_login,
            bg=C_SIDEBAR, fg=C_WHITE,
            activebackground=C_ACCENT, activeforeground=C_WHITE,
            font=("Arial", 11, "bold"),
            relief="flat", cursor="hand2",
            padx=12, pady=8,
        )
        self.btn_login.pack(fill="x")

        # Enter dispara login
        self.bind("<Return>", lambda e: self._validate_login())

    def _validate_login(self):
        """
        Valida las credenciales de login.

        Obtiene usuario y contraseña de los campos,
        verifica en la base de datos,
        y abre MainWindow si es correcto.
        """
        self.var_error.set("")
        self.btn_login.configure(state="disabled", text="Verificando...")
        self.update_idletasks()

        usuario_str = self.var_usuario.get().strip()
        password_str = self.var_password.get()

        if not usuario_str or not password_str:
            self.var_error.set("Ingresa usuario y contraseña.")
            self.btn_login.configure(state="normal", text="Entrar")
            return

        usuario = obtener_usuario_por_username(usuario_str)

        if usuario is None or not verify_password(password_str, usuario["password_hash"]):
            self.var_error.set("Usuario o contraseña incorrectos.")
            self.var_password.set("")
            self.entry_password.focus()
            self.btn_login.configure(state="normal", text="Entrar")
            return

        if not usuario["activo"]:
            self.var_error.set("Tu cuenta está desactivada. Contacta al administrador.")
            self.btn_login.configure(state="normal", text="Entrar")
            return

        # Guardar sesión
        sesion = Session()
        sesion.set_user(
            id_usuario=usuario["id"],
            nombre=usuario["nombre"],
            usuario=usuario["usuario"],
            rol=usuario["rol"],
        )

        self._open_main_window(sesion.get_user())

    def _open_main_window(self, usuario):
        """
        Abre la ventana principal después de login exitoso.

        Args:
            usuario (dict): Datos del usuario autenticado.
        """
        from app.ui.main_window import MainWindow
        self.destroy()
        ventana = MainWindow(usuario)
        ventana.mainloop()

    def _centrar_ventana(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - ancho) // 2
        y = (self.winfo_screenheight() - alto)  // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")