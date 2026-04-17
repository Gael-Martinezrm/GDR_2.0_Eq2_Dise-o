"""
app/modules/retiros/view.py

Interfaz gráfica del módulo de retiros.
Permite registrar, editar, eliminar y visualizar retiros de efectivo.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import calendar

from app.auth.session import Session
from app.modules.retiros import model as retiros_model
from app.modules.cajas import model as cajas_model
from app.ui.components import styled_button, make_treeview, page_header

# Paleta de colores
C_BG      = "#F0F2F5"
C_WHITE   = "#FFFFFF"
C_TEXT    = "#212121"
C_ACCENT  = "#1976D2"
C_DANGER  = "#C62828"
C_SUCCESS = "#2E7D32"
C_WARN    = "#E65100"


# ── Selector de fecha (calendario popup) ────────────────────────────────────

class _CalendarioPopup(tk.Toplevel):
    def __init__(self, parent, var_fecha: tk.StringVar):
        super().__init__(parent)
        self.var_fecha = var_fecha
        self.overrideredirect(True)
        self.configure(bg=C_WHITE)
        self.grab_set()

        try:
            fecha_ini = datetime.strptime(var_fecha.get(), "%d/%m/%Y")
        except ValueError:
            fecha_ini = datetime.now()

        self._año  = fecha_ini.year
        self._mes  = fecha_ini.month
        self._dia  = fecha_ini.day

        self._build()
        self._posicionar(parent)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<FocusOut>", self._on_focus_out)

    def _build(self):
        frm = tk.Frame(self, bg=C_WHITE, relief="solid", bd=1, padx=8, pady=8)
        frm.pack(fill="both", expand=True)

        frm_nav = tk.Frame(frm, bg=C_WHITE)
        frm_nav.pack(fill="x", pady=(0, 6))

        tk.Button(frm_nav, text="◀", command=self._mes_anterior,
                  bg=C_WHITE, fg=C_ACCENT, relief="flat", cursor="hand2",
                  font=("Arial", 11, "bold")).pack(side="left")

        self.lbl_mes_año = tk.Label(frm_nav, bg=C_WHITE, fg=C_TEXT,
                                    font=("Arial", 10, "bold"), width=16)
        self.lbl_mes_año.pack(side="left", expand=True)

        tk.Button(frm_nav, text="▶", command=self._mes_siguiente,
                  bg=C_WHITE, fg=C_ACCENT, relief="flat", cursor="hand2",
                  font=("Arial", 11, "bold")).pack(side="right")

        DIAS_SEMANA = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]
        frm_dias = tk.Frame(frm, bg=C_WHITE)
        frm_dias.pack()
        for col, d in enumerate(DIAS_SEMANA):
            tk.Label(frm_dias, text=d, bg=C_WHITE, fg=C_ACCENT,
                     font=("Arial", 8, "bold"), width=3).grid(row=0, column=col)

        self.frm_grid = tk.Frame(frm, bg=C_WHITE)
        self.frm_grid.pack()

        tk.Button(frm, text="Hoy", command=self._seleccionar_hoy,
                  bg=C_BG, fg=C_ACCENT, relief="flat", cursor="hand2",
                  font=("Arial", 9)).pack(pady=(6, 0))

        self._renderizar_mes()

    def _renderizar_mes(self):
        for w in self.frm_grid.winfo_children():
            w.destroy()

        MESES_ES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_mes_año.config(text=f"{MESES_ES[self._mes]} {self._año}")

        semanas = calendar.monthcalendar(self._año, self._mes)
        hoy = datetime.now().date()

        for fila, semana in enumerate(semanas):
            for col, dia in enumerate(semana):
                if dia == 0:
                    tk.Label(self.frm_grid, text="", bg=C_WHITE, width=3).grid(row=fila, column=col)
                    continue

                es_hoy = (dia == hoy.day and self._mes == hoy.month and self._año == hoy.year)
                btn = tk.Button(self.frm_grid, text=str(dia), width=3,
                                bg="#E3F2FD" if es_hoy else C_WHITE, fg=C_TEXT,
                                relief="flat", cursor="hand2", font=("Arial", 9),
                                command=lambda d=dia: self._seleccionar_dia(d))
                btn.grid(row=fila, column=col, padx=1, pady=1, ipady=2)

    def _mes_anterior(self):
        if self._mes == 1:
            self._mes, self._año = 12, self._año - 1
        else:
            self._mes -= 1
        self._renderizar_mes()

    def _mes_siguiente(self):
        if self._mes == 12:
            self._mes, self._año = 1, self._año + 1
        else:
            self._mes += 1
        self._renderizar_mes()

    def _seleccionar_dia(self, dia):
        fecha = datetime(self._año, self._mes, dia)
        self.var_fecha.set(fecha.strftime("%d/%m/%Y"))
        self.destroy()

    def _seleccionar_hoy(self):
        hoy = datetime.now()
        self._seleccionar_dia(hoy.day)

    def _posicionar(self, widget_referencia):
        self.update_idletasks()
        x = widget_referencia.winfo_rootx()
        y = widget_referencia.winfo_rooty() + widget_referencia.winfo_height() + 2
        self.geometry(f"+{x}+{y}")

    def _on_focus_out(self, event):
        self.after(100, self._verificar_foco)

    def _verificar_foco(self):
        try:
            if self.focus_get() is None: self.destroy()
        except: self.destroy()


# ── Vista principal ──────────────────────────────────────────────────────────

class RetirosView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self.parent = parent
        self.tabla = None
        self.cajas_cache = []
        self._create_widgets()
        self._cargar_cajas()
        self._refresh_retiros()

    def _create_widgets(self):
        page_header(self, "Registro de Retiros").pack(fill="x")

        # Panel superior — botones de acción
        frm_superior = tk.Frame(self, bg=C_BG, pady=10, padx=16)
        frm_superior.pack(fill="x")

        styled_button(frm_superior, "Nuevo Retiro", self._on_nuevo_retiro, width=14).pack(side="left", padx=(0, 6))

        # Botón Editar
        self.btn_editar = tk.Button(
            frm_superior, text="Editar",
            command=self._on_editar_retiro,
            bg=C_ACCENT, fg=C_WHITE,
            activebackground=C_ACCENT, activeforeground=C_WHITE,
            disabledforeground=C_WHITE,
            relief="flat", cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=10, pady=5,
            state="disabled"
        )
        self.btn_editar.pack(side="left", padx=(0, 6))

        # Botón Eliminar
        self.btn_eliminar = tk.Button(
            frm_superior, text="Eliminar",
            command=self._on_eliminar_retiro,
            bg=C_DANGER, fg=C_WHITE,
            activebackground=C_DANGER, activeforeground=C_WHITE,
            disabledforeground=C_WHITE,
            relief="flat", cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=10, pady=5,
            state="disabled"
        )
        self.btn_eliminar.pack(side="left", padx=(0, 20))

        # Filtros
        frm_filtros = tk.Frame(frm_superior, bg=C_BG)
        frm_filtros.pack(side="left", fill="x", expand=True)

        tk.Label(frm_filtros, text="Fecha:", bg=C_BG, fg=C_TEXT).pack(side="left", padx=(0, 5))
        self.filtro_fecha = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))

        frm_fecha = tk.Frame(frm_filtros, bg=C_BG)
        frm_fecha.pack(side="left", padx=(0, 15))
        self.entry_fecha = tk.Entry(frm_fecha, textvariable=self.filtro_fecha, width=12, relief="solid", bd=1)
        self.entry_fecha.pack(side="left", ipady=3)

        tk.Button(
            frm_fecha, text="📅",
            command=self._abrir_calendario,
            bg=C_BG, fg=C_ACCENT,
            relief="flat", cursor="hand2",
            font=("Arial", 16)
        ).pack(side="left", padx=5)

        self.filtro_caja = tk.StringVar(value="Todas las cajas")
        self.combo_caja = ttk.Combobox(frm_filtros, textvariable=self.filtro_caja,
                                       values=["Todas las cajas"], width=15, state="readonly")
        self.combo_caja.pack(side="left", padx=(0, 10))

        styled_button(frm_filtros, "Filtrar", self._on_filtrar, width=8).pack(side="left")

        # Tabla de retiros
        frm_tabla = tk.Frame(self, bg=C_BG, padx=16, pady=4)
        frm_tabla.pack(fill="both", expand=True)

        columnas = ["Retiro #", "Transacción #", "Fecha", "Hora Depósito",
                    "Caja", "Monto", "Acumulado", "Usuario", "Observaciones"]
        anchos   = [70, 100, 90, 100, 90, 80, 90, 130, 300]

        frm_tree, self.tabla = make_treeview(frm_tabla, columnas, anchos, height=18)
        frm_tree.pack(fill="both", expand=True)

        # make_treeview ya crea todas las columnas con anchor="w".
        # Solo sobreescribimos las columnas que deben ir centradas.
        COLUMNAS_CENTRADAS = {"col0", "col1", "col2", "col3", "col4", "col5", "col6", "col7"}
        for col_id in self.tabla["columns"]:
            if col_id in COLUMNAS_CENTRADAS:
                self.tabla.column(col_id, anchor="center")
                self.tabla.heading(col_id, anchor="center")

        # Eventos de selección / doble clic
        self.tabla.bind("<<TreeviewSelect>>", self._on_seleccion)
        self.tabla.bind("<ButtonRelease-1>", self._on_seleccion)
        self.tabla.bind("<Double-1>", self._on_ver_detalle)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _abrir_calendario(self):
        _CalendarioPopup(self.entry_fecha, self.filtro_fecha)

    def _cargar_cajas(self):
        try:
            self.cajas_cache = cajas_model.obtener_cajas(solo_activas=True)
            self.combo_caja['values'] = ["Todas las cajas"] + [c["nombre"] for c in self.cajas_cache]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las cajas: {e}")

    def _refresh_retiros(self):
        try:
            for item in self.tabla.get_children():
                self.tabla.delete(item)

            fecha_obj = datetime.strptime(self.filtro_fecha.get(), "%d/%m/%Y").date()

            if self.filtro_caja.get() == "Todas las cajas":
                retiros = retiros_model.obtener_retiros_por_fecha(fecha_obj)
            else:
                caja_sel = next((c for c in self.cajas_cache
                                 if c["nombre"] == self.filtro_caja.get()), None)
                retiros = (retiros_model.obtener_retiros_por_caja_y_fecha(caja_sel["id"], fecha_obj)
                           if caja_sel else [])

            for r in retiros:
                self.tabla.insert("", "end", iid=str(r["id"]), values=(
                    r.get("num_retiro", r["id"]),
                    r.get("num_transaccion", "N/A"),
                    r.get("fecha_solo", "N/A"),
                    r.get("hora_deposito", "N/A"),
                    r.get("nombre_caja", "N/A"),
                    f"${r['monto']:,.2f}",
                    f"${r.get('acumulado', 0):,.2f}",
                    r.get("nombre_usuario", "N/A"),
                    r.get("observaciones", "")[:50]
                ))

            # Al refrescar no hay nada seleccionado
            self._actualizar_botones_accion(hay_seleccion=False)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar retiros: {e}")

    def _retiro_seleccionado_id(self):
        """Devuelve el id (int) del retiro seleccionado, o None."""
        sel = self.tabla.selection()
        return int(sel[0]) if sel else None

    def _actualizar_botones_accion(self, hay_seleccion: bool):
        estado = "normal" if hay_seleccion else "disabled"
        self.btn_editar.config(state=estado)
        self.btn_eliminar.config(state=estado)

    # ── Eventos ─────────────────────────────────────────────────────────────

    def _on_seleccion(self, event=None):
        self._actualizar_botones_accion(hay_seleccion=bool(self.tabla.selection()))

    def _on_filtrar(self):
        self._refresh_retiros()

    def _on_nuevo_retiro(self):
        if not self.cajas_cache:
            messagebox.showerror("Error", "No hay cajas activas.")
            return

        dialogo = _DialogoRetiro(self, self.cajas_cache)
        self.wait_window(dialogo)

        if dialogo.resultado:
            try:
                retiros_model.insertar_retiro(
                    id_usuario=Session().get_id_usuario(),
                    id_caja=dialogo.resultado['id_caja'],
                    monto=dialogo.resultado['monto'],
                    motivo=dialogo.resultado['motivo'],
                    observaciones=dialogo.resultado['observaciones']
                )
                self._refresh_retiros()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {e}")

    def _on_editar_retiro(self):
        retiro_id = self._retiro_seleccionado_id()
        if retiro_id is None:
            return

        retiro = retiros_model.obtener_retiro_por_id(retiro_id)
        if not retiro:
            messagebox.showerror("Error", "No se encontró el retiro.")
            return

        dialogo = _DialogoRetiro(self, self.cajas_cache, retiro_existente=retiro)
        self.wait_window(dialogo)

        if dialogo.resultado:
            try:
                retiros_model.actualizar_retiro(
                    id_retiro=retiro_id,
                    id_caja=dialogo.resultado['id_caja'],
                    monto=dialogo.resultado['monto'],
                    motivo=dialogo.resultado['motivo'],
                    observaciones=dialogo.resultado['observaciones']
                )
                self._refresh_retiros()
                messagebox.showinfo("Éxito", "Retiro actualizado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar: {e}")

    def _on_eliminar_retiro(self):
        retiro_id = self._retiro_seleccionado_id()
        if retiro_id is None:
            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el retiro #{retiro_id}?\n"
            "Esta acción no se puede deshacer."
        )
        if confirmar:
            try:
                retiros_model.eliminar_retiro(retiro_id)
                self._refresh_retiros()
                messagebox.showinfo("Éxito", "Retiro eliminado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {e}")

    def _on_ver_detalle(self, event=None):
        retiro_id = self._retiro_seleccionado_id()
        if retiro_id is None:
            return
        retiro = retiros_model.obtener_retiro_por_id(retiro_id)
        if retiro:
            _DialogoDetalleRetiro(self, retiro)


# ── Diálogos ────────────────────────────────────────────────────────────────

class _DialogoRetiro(tk.Toplevel):
    """
    Diálogo reutilizable para crear y editar retiros.
    Si se pasa `retiro_existente`, precarga sus datos y actúa como editor.
    """
    def __init__(self, parent, cajas, retiro_existente=None):
        super().__init__(parent)
        self.cajas = cajas
        self.retiro_existente = retiro_existente
        self.resultado = None

        es_edicion = retiro_existente is not None
        self.title("Editar Retiro" if es_edicion else "Nuevo Retiro")
        self.configure(bg=C_WHITE)
        self.resizable(False, False)
        self.grab_set()
        self._build(es_edicion)

    def _build(self, es_edicion: bool):
        frm = tk.Frame(self, bg=C_WHITE, padx=24, pady=20)
        frm.pack()

        # Título del diálogo
        titulo = "Editar Retiro" if es_edicion else "Nuevo Retiro"
        tk.Label(frm, text=titulo, bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 13, "bold")).grid(row=0, column=0, columnspan=2,
                                                  sticky="w", pady=(0, 14))

        # Caja
        tk.Label(frm, text="Caja:", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=1, column=0, sticky="w")
        self.var_caja = tk.StringVar(value="— Seleccione una caja —")
        self.combo = ttk.Combobox(frm, textvariable=self.var_caja,
                                  values=[c["nombre"] for c in self.cajas],
                                  state="readonly", width=28)
        self.combo.grid(row=2, column=0, columnspan=2, pady=(2, 10), sticky="ew")

        # Monto
        tk.Label(frm, text="Monto ($):", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=3, column=0, sticky="w")
        self.var_monto = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_monto, relief="solid", bd=1,
                 width=30).grid(row=4, column=0, columnspan=2, pady=(2, 10), sticky="ew", ipady=4)

        # Observaciones
        tk.Label(frm, text="Observaciones:", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=5, column=0, sticky="w")
        self.txt_obs = tk.Text(frm, height=4, width=32, relief="solid", bd=1)
        self.txt_obs.grid(row=6, column=0, columnspan=2, pady=(2, 16))

        # Precargar datos si es edición
        if es_edicion:
            r = self.retiro_existente
            caja_nombre = r.get("nombre_caja", "")
            if caja_nombre in [c["nombre"] for c in self.cajas]:
                self.var_caja.set(caja_nombre)
            self.var_monto.set(str(r.get("monto", "")))
            self.txt_obs.insert("1.0", r.get("observaciones", ""))

        # Botones
        btn_frm = tk.Frame(frm, bg=C_WHITE)
        btn_frm.grid(row=7, column=0, columnspan=2, sticky="e")

        tk.Button(btn_frm, text="Cancelar", command=self.destroy,
                  bg=C_BG, fg=C_TEXT, relief="flat", cursor="hand2",
                  font=("Arial", 10), padx=10, pady=5).pack(side="right", padx=(8, 0))

        color_guardar = C_ACCENT
        tk.Button(btn_frm, text="Guardar cambios" if es_edicion else "Guardar",
                  command=self._guardar,
                  bg=color_guardar, fg=C_WHITE, relief="flat", cursor="hand2",
                  font=("Arial", 10, "bold"), padx=10, pady=5).pack(side="right")

    def _guardar(self):
        try:
            monto_txt = self.var_monto.get().strip().replace(",", ".")
            if not monto_txt:
                messagebox.showwarning("Campo requerido", "Ingrese un monto.", parent=self)
                return
            monto = float(monto_txt)
            if monto <= 0:
                messagebox.showwarning("Monto inválido", "El monto debe ser mayor a cero.", parent=self)
                return
            if not self.var_caja.get():
                messagebox.showwarning("Campo requerido", "Seleccione una caja.", parent=self)
                return

            caja_sel = next(c for c in self.cajas if c["nombre"] == self.var_caja.get())
            self.resultado = {
                'id_caja': caja_sel["id"],
                'monto': monto,
                'motivo': "Retiro de efectivo",
                'observaciones': self.txt_obs.get("1.0", "end-1c").strip()
            }
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido.", parent=self)
        except StopIteration:
            messagebox.showerror("Error", "Caja no encontrada.", parent=self)


class _DialogoDetalleRetiro(tk.Toplevel):
    def __init__(self, parent, retiro):
        super().__init__(parent)
        self.title(f"Detalle — Retiro #{retiro['id']}")
        self.configure(bg=C_WHITE)
        self.resizable(False, False)
        self.grab_set()

        frm = tk.Frame(self, bg=C_WHITE, padx=24, pady=20)
        frm.pack()

        tk.Label(frm, text=f"Retiro #{retiro['id']}", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 13, "bold")).grid(row=0, column=0, columnspan=2,
                                                  sticky="w", pady=(0, 14))

        campos = [
            ("Transacción #",  retiro.get("num_transaccion", "N/A")),
            ("Caja",           retiro.get("nombre_caja", "N/A")),
            ("Fecha",          retiro.get("fecha_solo", "N/A")),
            ("Hora Depósito",  retiro.get("hora_deposito", "N/A")),
            ("Monto",          f"${retiro['monto']:,.2f}"),
            ("Acumulado",      f"${retiro.get('acumulado', 0):,.2f}"),
            ("Usuario",        retiro.get("nombre_usuario", "N/A")),
            ("Observaciones",  retiro.get("observaciones", "") or "—"),
        ]

        for i, (k, v) in enumerate(campos, start=1):
            tk.Label(frm, text=f"{k}:", font=("Arial", 9, "bold"),
                     bg=C_WHITE, fg=C_TEXT, anchor="e").grid(
                row=i, column=0, sticky="e", pady=3, padx=(0, 8))
            tk.Label(frm, text=v, bg=C_WHITE, fg=C_TEXT, anchor="w",
                     wraplength=260, justify="left").grid(
                row=i, column=1, sticky="w", pady=3)

        tk.Button(frm, text="Cerrar", command=self.destroy,
                  bg=C_ACCENT, fg=C_WHITE, relief="flat", cursor="hand2",
                  font=("Arial", 10, "bold"), padx=12, pady=5).grid(
            row=len(campos) + 1, column=0, columnspan=2, pady=(16, 0))