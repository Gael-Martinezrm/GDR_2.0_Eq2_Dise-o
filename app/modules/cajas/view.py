"""
app/modules/cajas/view.py

Interfaz gráfica del módulo de cajas.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from app.auth.session import Session
from app.modules.cajas import model as cajas_model
from app.ui.components import styled_button, make_treeview, page_header

C_BG    = "#F0F2F5"
C_WHITE = "#FFFFFF"
C_TEXT  = "#212121"
C_ACCENT= "#1976D2"
C_DANGER= "#C62828"


class CajasView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self.parent = parent
        self.tabla  = None
        self._create_widgets()
        self._refresh_cajas()

    def _create_widgets(self):
        sesion = Session()

        # Encabezado
        page_header(self, "Gestión de Cajas").pack(fill="x")

        # Barra de botones
        frm_acc = tk.Frame(self, bg=C_BG, pady=10, padx=16)
        frm_acc.pack(fill="x")

        if sesion.is_admin() or sesion.is_gerente():
            styled_button(frm_acc, "Nueva Caja",
                          self._on_nueva_caja).pack(side="left", padx=(0, 8))
            styled_button(frm_acc, "Editar",
                          self._on_editar_caja).pack(side="left", padx=(0, 8))
            styled_button(frm_acc, "Activar/Desactivar",
                          self._on_toggle_caja, width=18).pack(side="left", padx=(0, 8))

        if sesion.is_admin():
            styled_button(frm_acc, "Eliminar",
                          self._on_eliminar_caja, danger=True).pack(side="left")

        # Tabla — make_treeview devuelve (frame_contenedor, treeview)
        frm_tabla = tk.Frame(self, bg=C_BG, padx=16, pady=4)
        frm_tabla.pack(fill="both", expand=True)

        columnas = ["ID", "Nombre", "N° Caja", "Ubicación", "Estado"]
        anchos   = [50, 180, 90, 200, 90]
        frm_tree, self.tabla = make_treeview(frm_tabla, columnas, anchos)
        frm_tree.pack(fill="both", expand=True)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _on_nueva_caja(self):
        dialogo = _DialogoCaja(self)
        self.wait_window(dialogo)
        if dialogo.resultado:
            nombre, numero, ubicacion = dialogo.resultado
            try:
                cajas_model.insertar_caja(nombre, numero, ubicacion)
                messagebox.showinfo("Éxito", f"Caja '{nombre}' creada.", parent=self)
                self._refresh_cajas()
            except Exception as e:
                msg = "El nombre de caja ya existe." if "UNIQUE" in str(e).upper() else str(e)
                messagebox.showerror("Error", msg, parent=self)

    def _on_editar_caja(self):
        caja = self._get_seleccionada()
        if not caja:
            messagebox.showwarning("Selección", "Selecciona una caja.", parent=self)
            return
        dialogo = _DialogoCaja(self, caja=caja)
        self.wait_window(dialogo)
        if dialogo.resultado:
            nombre, numero, ubicacion = dialogo.resultado
            try:
                cajas_model.actualizar_caja(caja["id"], nombre, numero, ubicacion)
                messagebox.showinfo("Éxito", "Caja actualizada.", parent=self)
                self._refresh_cajas()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _on_toggle_caja(self):
        caja = self._get_seleccionada()
        if not caja:
            messagebox.showwarning("Selección", "Selecciona una caja.", parent=self)
            return
        accion = "desactivar" if caja["activa"] else "activar"
        if messagebox.askyesno("Confirmar",
                               f"¿Deseas {accion} '{caja['nombre']}'?\n\n"
                               "El historial de retiros no se verá afectado.",
                               parent=self):
            try:
                cajas_model.toggle_activa(caja["id"])
                self._refresh_cajas()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _on_eliminar_caja(self):
        caja = self._get_seleccionada()
        if not caja:
            messagebox.showwarning("Selección", "Selecciona una caja.", parent=self)
            return
        if messagebox.askyesno("Confirmar",
                               f"¿Eliminar '{caja['nombre']}'?\nEsta acción no se puede deshacer.",
                               parent=self):
            try:
                cajas_model.eliminar_caja(caja["id"])
                self._refresh_cajas()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _refresh_cajas(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for i, caja in enumerate(cajas_model.obtener_cajas(solo_activas=False)):
            estado = "Activa" if caja["activa"] else "Inactiva"
            tag    = "activa" if caja["activa"] else "inactiva"
            self.tabla.insert("", "end",
                iid=str(caja["id"]),
                values=(caja["id"], caja["nombre"], caja["numero_caja"],
                        caja.get("ubicacion", ""), estado),
                tags=(tag,),
            )
        self.tabla.tag_configure("activa",   foreground="#2E7D32")
        self.tabla.tag_configure("inactiva", foreground="#C62828")

    def _get_seleccionada(self):
        sel = self.tabla.selection()
        if not sel:
            return None
        return cajas_model.obtener_caja_por_id(int(sel[0]))


# ── Diálogo modal ─────────────────────────────────────────────────────────────

class _DialogoCaja(tk.Toplevel):

    def __init__(self, parent, caja=None):
        super().__init__(parent)
        self.resultado = None
        self.title("Editar Caja" if caja else "Nueva Caja")
        self.resizable(False, False)
        self.configure(bg=C_WHITE)
        self.grab_set()
        self._centrar(380, 240)
        self._build(caja)

    def _build(self, caja):
        frm = tk.Frame(self, bg=C_WHITE, padx=28, pady=24)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text=self.title(), bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 12, "bold")).grid(
                     row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        # Nombre
        tk.Label(frm, text="Nombre *", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=1, column=0, sticky="w")
        self.var_nombre = tk.StringVar(value=caja["nombre"] if caja else "")
        tk.Entry(frm, textvariable=self.var_nombre, font=("Arial", 11),
                 relief="solid", bd=1, width=20).grid(
                     row=2, column=0, sticky="ew", ipady=5,
                     pady=(3, 12), padx=(0, 10))

        # Número
        tk.Label(frm, text="N° Caja *", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=1, column=1, sticky="w")
        self.var_numero = tk.StringVar(value=caja["numero_caja"] if caja else "")
        tk.Entry(frm, textvariable=self.var_numero, font=("Arial", 11),
                 relief="solid", bd=1, width=10).grid(
                     row=2, column=1, sticky="ew", ipady=5, pady=(3, 12))

        # Ubicación
        tk.Label(frm, text="Ubicación", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(
                     row=3, column=0, columnspan=2, sticky="w")
        self.var_ubicacion = tk.StringVar(
            value=caja.get("ubicacion", "") if caja else "")
        tk.Entry(frm, textvariable=self.var_ubicacion, font=("Arial", 11),
                 relief="solid", bd=1).grid(
                     row=4, column=0, columnspan=2, sticky="ew",
                     ipady=5, pady=(3, 18))

        frm.columnconfigure(0, weight=3)
        frm.columnconfigure(1, weight=1)

        # Botones
        frm_btns = tk.Frame(frm, bg=C_WHITE)
        frm_btns.grid(row=5, column=0, columnspan=2, sticky="e")

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
        nombre    = self.var_nombre.get().strip()
        numero    = self.var_numero.get().strip()
        ubicacion = self.var_ubicacion.get().strip()
        if not nombre or not numero:
            messagebox.showerror("Error", "Nombre y N° de caja son obligatorios.",
                                 parent=self)
            return
        self.resultado = (nombre, numero, ubicacion)
        self.destroy()

    def _centrar(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - ancho) // 2
        y = (self.winfo_screenheight() - alto)  // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")