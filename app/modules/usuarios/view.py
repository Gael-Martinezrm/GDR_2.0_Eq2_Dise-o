"""
app/modules/usuarios/view.py

Interfaz gráfica del módulo de usuarios.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from app.modules.usuarios import model as usuarios_model
from app.ui.components import styled_button, make_treeview, page_header

C_BG    = "#F0F2F5"
C_WHITE = "#FFFFFF"
C_TEXT  = "#212121"
C_ACCENT= "#1976D2"
C_DANGER= "#C62828"

ROLES = ["administrador", "gerente", "operador"]


class UsuariosView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self.parent = parent
        self.tabla  = None
        self._create_widgets()
        self._refresh_usuarios()

    def _create_widgets(self):
        page_header(self, "Gestión de Usuarios").pack(fill="x")

        # Barra de botones
        frm_acc = tk.Frame(self, bg=C_BG, pady=10, padx=16)
        frm_acc.pack(fill="x")

        styled_button(frm_acc, "Nuevo Usuario",
                      self._on_nuevo_usuario).pack(side="left", padx=(0, 8))
        styled_button(frm_acc, "Editar",
                      self._on_editar_usuario).pack(side="left", padx=(0, 8))
        styled_button(frm_acc, "Cambiar Password",
                      self._on_cambiar_password, width=16).pack(side="left", padx=(0, 8))
        styled_button(frm_acc, "Activar/Desactivar",
                      self._on_toggle_usuario, width=18).pack(side="left", padx=(0, 8))
        styled_button(frm_acc, "Eliminar",
                      self._on_eliminar_usuario, danger=True).pack(side="left")

        # Tabla
        frm_tabla = tk.Frame(self, bg=C_BG, padx=16, pady=4)
        frm_tabla.pack(fill="both", expand=True)

        columnas = ["ID", "Nombre", "Usuario", "Rol", "Estado"]
        anchos   = [50, 200, 140, 120, 90]
        frm_tree, self.tabla = make_treeview(frm_tabla, columnas, anchos)
        frm_tree.pack(fill="both", expand=True)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _on_nuevo_usuario(self):
        dialogo = _DialogoUsuario(self)
        self.wait_window(dialogo)
        if dialogo.resultado:
            nombre, usuario, password, rol = dialogo.resultado
            try:
                usuarios_model.insertar_usuario(nombre, usuario, password, rol)
                messagebox.showinfo("Éxito", f"Usuario '{usuario}' creado.", parent=self)
                self._refresh_usuarios()
            except Exception as e:
                msg = f"El nombre de usuario '{usuario}' ya existe." \
                      if "UNIQUE" in str(e).upper() else str(e)
                messagebox.showerror("Error", msg, parent=self)

    def _on_editar_usuario(self):
        u = self._get_seleccionado()
        if not u:
            messagebox.showwarning("Selección", "Selecciona un usuario.", parent=self)
            return
        dialogo = _DialogoUsuario(self, usuario=u)
        self.wait_window(dialogo)
        if dialogo.resultado:
            nombre, usuario, _, rol = dialogo.resultado
            try:
                usuarios_model.actualizar_usuario(u["id"], nombre, usuario, rol)
                messagebox.showinfo("Éxito", "Usuario actualizado.", parent=self)
                self._refresh_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _on_cambiar_password(self):
        u = self._get_seleccionado()
        if not u:
            messagebox.showwarning("Selección", "Selecciona un usuario.", parent=self)
            return
        dialogo = _DialogoPassword(self, nombre=u["nombre"])
        self.wait_window(dialogo)
        if dialogo.resultado:
            try:
                usuarios_model.cambiar_password(u["id"], dialogo.resultado)
                messagebox.showinfo("Éxito", "Contraseña actualizada.", parent=self)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _on_toggle_usuario(self):
        u = self._get_seleccionado()
        if not u:
            messagebox.showwarning("Selección", "Selecciona un usuario.", parent=self)
            return
        accion = "desactivar" if u["activo"] else "activar"
        if messagebox.askyesno("Confirmar",
                               f"¿Deseas {accion} al usuario '{u['usuario']}'?",
                               parent=self):
            try:
                usuarios_model.toggle_activo(u["id"])
                self._refresh_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _on_eliminar_usuario(self):
        u = self._get_seleccionado()
        if not u:
            messagebox.showwarning("Selección", "Selecciona un usuario.", parent=self)
            return
        if messagebox.askyesno("Confirmar",
                               f"¿Eliminar al usuario '{u['usuario']}'?\n"
                               "Esta acción no se puede deshacer.",
                               parent=self):
            try:
                usuarios_model.eliminar_usuario(u["id"])
                self._refresh_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _refresh_usuarios(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for u in usuarios_model.obtener_usuarios(solo_activos=False):
            estado = "Activo" if u["activo"] else "Inactivo"
            tag    = "activo" if u["activo"] else "inactivo"
            self.tabla.insert("", "end",
                iid=str(u["id"]),
                values=(u["id"], u["nombre"], u["usuario"], u["rol"], estado),
                tags=(tag,),
            )
        self.tabla.tag_configure("activo",   foreground="#2E7D32")
        self.tabla.tag_configure("inactivo", foreground="#C62828")

    def _get_seleccionado(self):
        sel = self.tabla.selection()
        if not sel:
            return None
        return usuarios_model.obtener_usuario_por_id(int(sel[0]))


# ── Diálogo: Nuevo / Editar usuario ──────────────────────────────────────────

class _DialogoUsuario(tk.Toplevel):

    def __init__(self, parent, usuario=None):
        super().__init__(parent)
        self.resultado = None
        self.es_edicion = usuario is not None
        self.title("Editar Usuario" if self.es_edicion else "Nuevo Usuario")
        self.resizable(False, False)
        self.configure(bg=C_WHITE)
        self.grab_set()
        self._centrar(400, 310 if not self.es_edicion else 280)
        self._build(usuario)

    def _build(self, u):
        frm = tk.Frame(self, bg=C_WHITE, padx=28, pady=24)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text=self.title(), bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 12, "bold")).grid(
                     row=0, column=0, columnspan=2,
                     sticky="w", pady=(0, 16))

        # Nombre
        tk.Label(frm, text="Nombre completo *", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=1, column=0, columnspan=2, sticky="w")
        self.var_nombre = tk.StringVar(value=u["nombre"] if u else "")
        tk.Entry(frm, textvariable=self.var_nombre, font=("Arial", 11),
                 relief="solid", bd=1).grid(
                     row=2, column=0, columnspan=2, sticky="ew",
                     ipady=5, pady=(3, 12))

        # Usuario
        tk.Label(frm, text="Usuario (login) *", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=3, column=0, sticky="w")
        self.var_usuario = tk.StringVar(value=u["usuario"] if u else "")
        tk.Entry(frm, textvariable=self.var_usuario, font=("Arial", 11),
                 relief="solid", bd=1, width=16).grid(
                     row=4, column=0, sticky="ew", ipady=5,
                     pady=(3, 12), padx=(0, 10))

        # Rol
        tk.Label(frm, text="Rol *", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=3, column=1, sticky="w")
        self.var_rol = tk.StringVar(value=u["rol"] if u else ROLES[2])
        ttk.Combobox(frm, textvariable=self.var_rol, values=ROLES,
                     state="readonly", font=("Arial", 11), width=14).grid(
                         row=4, column=1, sticky="ew", ipady=5, pady=(3, 12))

        # Contraseña (solo en alta)
        self.var_password = None
        if not self.es_edicion:
            tk.Label(frm, text="Contraseña *", bg=C_WHITE, fg=C_TEXT,
                     font=("Arial", 10)).grid(
                         row=5, column=0, columnspan=2, sticky="w")
            self.var_password = tk.StringVar()
            tk.Entry(frm, textvariable=self.var_password, show="●",
                     font=("Arial", 11), relief="solid", bd=1).grid(
                         row=6, column=0, columnspan=2, sticky="ew",
                         ipady=5, pady=(3, 16))

        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)

        # Botones
        frm_btns = tk.Frame(frm, bg=C_WHITE)
        row_btns = 7 if not self.es_edicion else 5
        frm_btns.grid(row=row_btns, column=0, columnspan=2, sticky="e")

        tk.Button(frm_btns, text="Cancelar", command=self.destroy,
                  bg="#ECEFF1", fg=C_TEXT, relief="flat", cursor="hand2",
                  font=("Arial", 10), padx=12, pady=6).pack(
                      side="left", padx=(0, 8))
        tk.Button(frm_btns, text="Guardar", command=self._guardar,
                  bg=C_ACCENT, fg=C_WHITE, activebackground="#1565C0",
                  activeforeground=C_WHITE, relief="flat", cursor="hand2",
                  font=("Arial", 10, "bold"), padx=14, pady=6).pack(side="left")

        self.bind("<Return>", lambda e: self._guardar())
        self.bind("<Escape>", lambda e: self.destroy())

    def _guardar(self):
        nombre  = self.var_nombre.get().strip()
        usuario = self.var_usuario.get().strip()
        rol     = self.var_rol.get()
        password = self.var_password.get() if self.var_password else ""

        if not nombre or not usuario:
            messagebox.showerror("Error", "Nombre y Usuario son obligatorios.",
                                 parent=self)
            return
        if not self.es_edicion and not password:
            messagebox.showerror("Error", "La contraseña es obligatoria.",
                                 parent=self)
            return

        self.resultado = (nombre, usuario, password, rol)
        self.destroy()

    def _centrar(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - ancho) // 2
        y = (self.winfo_screenheight() - alto)  // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")


# ── Diálogo: Cambiar contraseña ───────────────────────────────────────────────

class _DialogoPassword(tk.Toplevel):

    def __init__(self, parent, nombre):
        super().__init__(parent)
        self.resultado = None
        self.title("Cambiar Contraseña")
        self.resizable(False, False)
        self.configure(bg=C_WHITE)
        self.grab_set()
        self._centrar(360, 220)
        self._build(nombre)

    def _build(self, nombre):
        frm = tk.Frame(self, bg=C_WHITE, padx=28, pady=24)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text=f"Nueva contraseña para:\n{nombre}",
                 bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 16))

        tk.Label(frm, text="Nueva contraseña *",
                 bg=C_WHITE, fg=C_TEXT, font=("Arial", 10)).pack(anchor="w")
        self.var_pw = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_pw, show="●",
                 font=("Arial", 11), relief="solid", bd=1).pack(
                     fill="x", ipady=6, pady=(3, 16))

        frm_btns = tk.Frame(frm, bg=C_WHITE)
        frm_btns.pack(anchor="e")
        tk.Button(frm_btns, text="Cancelar", command=self.destroy,
                  bg="#ECEFF1", fg=C_TEXT, relief="flat", cursor="hand2",
                  font=("Arial", 10), padx=12, pady=6).pack(
                      side="left", padx=(0, 8))
        tk.Button(frm_btns, text="Guardar", command=self._guardar,
                  bg=C_ACCENT, fg=C_WHITE, relief="flat", cursor="hand2",
                  font=("Arial", 10, "bold"), padx=14, pady=6).pack(side="left")

        self.bind("<Return>", lambda e: self._guardar())
        self.bind("<Escape>", lambda e: self.destroy())

    def _guardar(self):
        pw = self.var_pw.get()
        if not pw:
            messagebox.showerror("Error", "Ingresa una contraseña.", parent=self)
            return
        self.resultado = pw
        self.destroy()

    def _centrar(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - ancho) // 2
        y = (self.winfo_screenheight() - alto)  // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")