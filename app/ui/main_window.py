"""
app/ui/main_window.py

Ventana principal de la aplicación.
Contiene sidebar de navegación y área de contenido intercambiable.
"""

import tkinter as tk
from tkinter import ttk

from app.auth.session import Session

# Paleta de colores
C_BG            = "#F0F2F5"
C_SIDEBAR       = "#1565C0"
C_ACCENT        = "#1976D2"
C_WHITE         = "#FFFFFF"
C_TEXT          = "#212121"
C_HEADER        = "#1565C0"
C_BTN           = "#1565C0"
C_DANGER        = "#C62828"
C_SIDEBAR_BTN_H = "#0D47A1"
C_SIDEBAR_ACTV  = "#0D47A1"   # Fondo del ítem activo
C_SIDEBAR_IND   = "#FFFFFF"   # Color del indicador lateral


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
        super().__init__()
        self.usuario = usuario
        self.current_frame = None
        self._active_btn = None          # Botón actualmente seleccionado
        self._active_indicator = None    # Barra indicadora lateral

        self.title("Sistema de Retiros - OfficeMax")
        self.geometry("1200x800")  # tamaño mínimo de referencia
        self.state("zoomed")       # maximiza al iniciar
        self.configure(bg=C_BG)
        self._centrar_ventana(1200, 800)
        self._create_widgets()
        self._show_dashboard()

    def _create_widgets(self):
        sesion = Session()

        # ── Sidebar ───────────────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=C_SIDEBAR, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / título en sidebar
        tk.Label(self.sidebar, text="OfficeMax",
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
            # Contenedor de fila: permite colocar la barra indicadora a la izquierda
            fila = tk.Frame(self.sidebar, bg=C_SIDEBAR)
            fila.pack(fill="x")

            # Barra indicadora (inicialmente invisible — mismo color que sidebar)
            indicador = tk.Frame(fila, bg=C_SIDEBAR, width=4)
            indicador.pack(side="left", fill="y")

            btn = tk.Button(
                fila, text=texto,
                command=lambda cmd=comando, b=None, f=fila, ind=indicador: self._nav_click(cmd, f, ind),
                bg=C_SIDEBAR, fg=C_WHITE,
                activebackground=C_SIDEBAR_BTN_H, activeforeground=C_WHITE,
                font=("Arial", 11), relief="flat", anchor="w",
                padx=16, pady=10, cursor="hand2",
            )
            btn.pack(side="left", fill="x", expand=True)

            # Guardar referencia del botón en el lambda correctamente
            btn.configure(command=lambda cmd=comando, f=fila, ind=indicador, b=btn:
                          self._nav_click(cmd, f, ind, b))

            btn.bind("<Enter>", lambda e, b=btn, f=fila: self._on_hover_enter(b, f))
            btn.bind("<Leave>", lambda e, b=btn, f=fila: self._on_hover_leave(b, f))

            self.nav_buttons.append((fila, btn, indicador))

        # ── Columna derecha (header + contenido) ──────────────────────────────
        self.frm_derecha = tk.Frame(self, bg=C_BG)
        self.frm_derecha.pack(side="left", fill="both", expand=True)

        # Header superior
        frm_header = tk.Frame(self.frm_derecha, bg=C_HEADER, pady=10, padx=16)
        frm_header.pack(fill="x")

        self.lbl_titulo = tk.Label(frm_header, text="",
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

    # ── Manejo de estado activo en sidebar ───────────────────────────────────

    def _nav_click(self, comando, fila_activa, indicador_activo, btn_activo):
        """Marca el ítem seleccionado y ejecuta la navegación."""
        self._set_active(fila_activa, indicador_activo, btn_activo)
        comando()

    def _set_active(self, fila_activa, indicador_activo, btn_activo):
        """
        Quita el estilo activo del ítem anterior y aplica el nuevo.
        """
        # Restaurar ítem anterior
        if self._active_btn is not None:
            fila_prev, btn_prev, ind_prev = self._active_btn
            fila_prev.configure(bg=C_SIDEBAR)
            btn_prev.configure(bg=C_SIDEBAR, fg=C_WHITE,
                               font=("Arial", 11))
            ind_prev.configure(bg=C_SIDEBAR)

        # Aplicar estilo activo
        fila_activa.configure(bg=C_SIDEBAR_ACTV)
        btn_activo.configure(bg=C_SIDEBAR_ACTV, fg=C_WHITE,
                             font=("Arial", 11, "bold"))
        indicador_activo.configure(bg=C_SIDEBAR_IND)

        self._active_btn = (fila_activa, btn_activo, indicador_activo)

    def _on_hover_enter(self, btn, fila):
        """Hover: resalta solo si no es el ítem activo."""
        if self._active_btn and fila == self._active_btn[0]:
            return
        fila.configure(bg=C_SIDEBAR_BTN_H)
        btn.configure(bg=C_SIDEBAR_BTN_H)

    def _on_hover_leave(self, btn, fila):
        """Hover leave: restaura solo si no es el ítem activo."""
        if self._active_btn and fila == self._active_btn[0]:
            return
        fila.configure(bg=C_SIDEBAR)
        btn.configure(bg=C_SIDEBAR)

    # ── Navegación ───────────────────────────────────────────────────────────

    def _show_dashboard(self):
        from app.ui.dashboard import DashboardView
        self.lbl_titulo.configure(text="")
        self._activate_nav_by_index(0)
        self._change_view(DashboardView(self.frm_contenido))

    def _show_retiros(self):
        from app.modules.retiros.view import RetirosView
        self.lbl_titulo.configure(text="")
        self._activate_nav_by_command(self._show_retiros)
        self._change_view(RetirosView(self.frm_contenido))

    def _show_cajas(self):
        from app.modules.cajas.view import CajasView
        self.lbl_titulo.configure(text="")
        self._activate_nav_by_command(self._show_cajas)
        self._change_view(CajasView(self.frm_contenido))

    def _show_usuarios(self):
        from app.modules.usuarios.view import UsuariosView
        self.lbl_titulo.configure(text="")
        self._activate_nav_by_command(self._show_usuarios)
        self._change_view(UsuariosView(self.frm_contenido))

    def _show_reportes(self):
        from app.modules.reportes.view import ReportesView
        self.lbl_titulo.configure(text="")
        self._activate_nav_by_command(self._show_reportes)
        self._change_view(ReportesView(self.frm_contenido))

    def _activate_nav_by_index(self, index):
        """Activa el ítem del sidebar por posición (para el dashboard inicial)."""
        if index < len(self.nav_buttons):
            fila, btn, ind = self.nav_buttons[index]
            self._set_active(fila, ind, btn)

    def _activate_nav_by_command(self, metodo):
        """
        Activa el ítem del sidebar cuyo texto coincide con el método llamado.
        Usa el orden de inserción de nav_buttons para encontrar el índice correcto.
        """
        metodos = [
            self._show_dashboard,
            self._show_retiros,
            self._show_cajas,
            self._show_usuarios,
            self._show_reportes,
        ]
        metodos_disponibles = [m for m in metodos if any(True for _ in [None])]

        # Mapa de método → índice en nav_buttons
        sesion = Session()
        orden = [self._show_dashboard]
        if sesion.is_admin() or sesion.is_gerente() or sesion.is_operador():
            orden.append(self._show_retiros)
        if sesion.is_admin() or sesion.is_gerente():
            orden.append(self._show_cajas)
        if sesion.is_admin():
            orden.append(self._show_usuarios)
        if sesion.is_admin() or sesion.is_gerente():
            orden.append(self._show_reportes)

        try:
            idx = orden.index(metodo)
            self._activate_nav_by_index(idx)
        except ValueError:
            pass

    def _change_view(self, new_frame):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = new_frame
        self.current_frame.pack(fill="both", expand=True)

    def _on_logout(self):
        from tkinter import messagebox
        confirmar = messagebox.askyesno(
            "Cerrar sesión",
            "¿Estás seguro que deseas cerrar sesión?",
            parent=self
        )
        if confirmar:
            self.destroy()()
            ventana.mainloop()

    def _centrar_ventana(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - ancho) // 2
        y = (self.winfo_screenheight() - alto)  // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")