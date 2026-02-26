"""
app/ui/main_window.py

Ventana principal de la aplicación.
Contiene sidebar de navegación y área de contenido intercambiable.
"""

import tkinter as tk
from tkinter import ttk

from app.auth.session import Session

# Paleta de colores
C_BG      = "#F0F2F5"
C_SIDEBAR = "#1565C0"
C_ACCENT  = "#1976D2"
C_WHITE   = "#FFFFFF"
C_TEXT    = "#212121"
C_HEADER  = "#1565C0"
C_BTN     = "#1565C0"
C_DANGER  = "#C62828"
C_SIDEBAR_BTN_H = "#0D47A1"


class MainWindow(tk.Tk):
    """
    Ventana principal de la aplicación.

    Estructura:
    - Sidebar izquierdo azul (#1565C0) con navegación
    - Área de contenido derecha intercambiable según opción seleccionada
    - Logout y usuario activo en el header

    Módulos disponibles:
    - Dashboard
    - Retiros
    - Cajas (solo admin/gerente)
    - Usuarios (solo admin)
    - Reportes
    """

    def __init__(self, usuario):
        """
        Inicializa la ventana principal.

        Args:
            usuario (dict): Datos del usuario autenticado.
        """
        super().__init__()
        self.usuario = usuario
        self.current_frame = None
        self.title("Sistema de Retiros")
        self.geometry("1200x800")
        self.configure(bg=C_BG)
        self._centrar_ventana(1200, 800)
        self._create_widgets()
        self._show_dashboard()

    def _create_widgets(self):
        """
        Crea los componentes principales de la ventana.

        Incluye:
        - Sidebar
        - Header
        - Área de contenido intercambiable
        """
        sesion = Session()

        # ── Sidebar ───────────────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=C_SIDEBAR, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / título en sidebar
        tk.Label(self.sidebar, text="Retiros",
                 bg=C_SIDEBAR, fg=C_WHITE,
                 font=("Arial", 16, "bold"), pady=20).pack(fill="x")
        tk.Frame(self.sidebar, bg="#1976D2", height=1).pack(fill="x", padx=12)

        # Botones de navegación
        nav_items = [("🏠  Dashboard", self._show_dashboard)]

        if sesion.is_admin() or sesion.is_gerente() or sesion.is_operador():
            nav_items.append(("💵  Retiros", self._show_retiros))

        if sesion.is_admin() or sesion.is_gerente():
            nav_items.append(("🏦  Cajas", self._show_cajas))

        if sesion.is_admin():
            nav_items.append(("👤  Usuarios", self._show_usuarios))

        if sesion.is_admin() or sesion.is_gerente():
            nav_items.append(("📊  Reportes", self._show_reportes))

        self.nav_buttons = []
        for texto, comando in nav_items:
            btn = tk.Button(
                self.sidebar, text=texto,
                command=comando,
                bg=C_SIDEBAR, fg=C_WHITE,
                activebackground=C_SIDEBAR_BTN_H, activeforeground=C_WHITE,
                font=("Arial", 11), relief="flat", anchor="w",
                padx=20, pady=10, cursor="hand2",
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=C_SIDEBAR_BTN_H))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=C_SIDEBAR))
            self.nav_buttons.append(btn)

        # ── Columna derecha (header + contenido) ──────────────────────────────
        self.frm_derecha = tk.Frame(self, bg=C_BG)
        self.frm_derecha.pack(side="left", fill="both", expand=True)

        # Header superior
        frm_header = tk.Frame(self.frm_derecha, bg=C_HEADER, pady=10, padx=16)
        frm_header.pack(fill="x")

        self.lbl_titulo = tk.Label(frm_header, text="Dashboard",
                                   bg=C_HEADER, fg=C_WHITE,
                                   font=("Arial", 13, "bold"))
        self.lbl_titulo.pack(side="left")

        # Info usuario + logout
        frm_user = tk.Frame(frm_header, bg=C_HEADER)
        frm_user.pack(side="right")

        tk.Label(frm_user,
                 text=f"👤 {sesion.get_user()['nombre']}  |  {sesion.get_rol().capitalize()}",
                 bg=C_HEADER, fg="#BBDEFB",
                 font=("Arial", 9)).pack(side="left", padx=(0, 14))

        tk.Button(frm_user, text="Cerrar sesión",
                  command=self._on_logout,
                  bg=C_DANGER, fg=C_WHITE,
                  activebackground="#B71C1C", activeforeground=C_WHITE,
                  relief="flat", cursor="hand2",
                  font=("Arial", 9), padx=10, pady=4).pack(side="left")

        # Área de contenido
        self.frm_contenido = tk.Frame(self.frm_derecha, bg=C_BG)
        self.frm_contenido.pack(fill="both", expand=True)

    def _show_dashboard(self):
        """
        Muestra la vista del dashboard.
        """
        from app.ui.dashboard import DashboardView
        self.lbl_titulo.configure(text="Dashboard")
        self._change_view(DashboardView(self.frm_contenido))

    def _show_retiros(self):
        """
        Muestra la vista de retiros.
        """
        from app.modules.retiros.view import RetirosView
        self.lbl_titulo.configure(text="Retiros")
        self._change_view(RetirosView(self.frm_contenido))

    def _show_cajas(self):
        """
        Muestra la vista de cajas (solo admin/gerente).
        """
        from app.modules.cajas.view import CajasView
        self.lbl_titulo.configure(text="Cajas")
        self._change_view(CajasView(self.frm_contenido))

    def _show_usuarios(self):
        """
        Muestra la vista de usuarios (solo admin).
        """
        from app.modules.usuarios.view import UsuariosView
        self.lbl_titulo.configure(text="Usuarios")
        self._change_view(UsuariosView(self.frm_contenido))

    def _show_reportes(self):
        """
        Muestra la vista de reportes.
        """
        from app.modules.reportes.view import ReportesView
        self.lbl_titulo.configure(text="Reportes")
        self._change_view(ReportesView(self.frm_contenido))

    def _change_view(self, new_frame):
        """
        Cambia la vista actual por una nueva.

        Args:
            new_frame (tk.Frame): Frame a mostrar.
        """
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = new_frame
        self.current_frame.pack(fill="both", expand=True)

    def _on_logout(self):
        """
        Cierra la sesión y vuelve a la ventana de login.
        """
        Session().logout()
        from app.auth.login import LoginWindow
        self.destroy()
        ventana = LoginWindow()
        ventana.mainloop()

    def _centrar_ventana(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - ancho) // 2
        y = (self.winfo_screenheight() - alto)  // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")