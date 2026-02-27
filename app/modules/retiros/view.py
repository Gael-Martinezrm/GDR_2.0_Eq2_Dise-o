"""
app/modules/retiros/view.py

Interfaz gráfica del módulo de retiros.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

try:
    from tkcalendar import DateEntry
    _TKCAL = True
except ImportError:
    _TKCAL = False

from app.modules.cajas import model as cajas_model
from app.modules.retiros import model as retiros_model
from app.ui.components import styled_button, make_treeview, page_header

C_BG     = "#F0F2F5"
C_WHITE  = "#FFFFFF"
C_TEXT   = "#212121"
C_ACCENT = "#1976D2"
C_DANGER = "#C62828"


class RetirosView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self.parent = parent
        self.tabla  = None
        self._create_widgets()
        self._refresh_retiros()

    def _create_widgets(self):
        page_header(self, "Registro de Retiros").pack(fill="x")

        frm_acc = tk.Frame(self, bg=C_BG, pady=10, padx=16)
        frm_acc.pack(fill="x")

        styled_button(frm_acc, "Nuevo Retiro",
                      self._on_nuevo_retiro).pack(side="left", padx=(0, 8))
        styled_button(frm_acc, "Eliminar",
                      self._on_eliminar_retiro, danger=True).pack(side="left", padx=(0, 8))
        styled_button(frm_acc, "Actualizar",
                      self._refresh_retiros, width=12).pack(side="right")

        tk.Frame(self, bg=C_ACCENT, height=1).pack(fill="x", padx=16)

        frm_tabla = tk.Frame(self, bg=C_BG, padx=16, pady=8)
        frm_tabla.pack(fill="both", expand=True)

        columnas = [
            "ID", "No. Retiro", "No. Transacción", "Fecha",
            "Hora Retiro", "Hora Depósito", "Caja", "Importe ($)",
            "Acumulado ($)", "Usuario Responsable", "Observaciones", "Fecha Registro"
        ]
        anchos = [40, 90, 120, 90, 90, 100, 100, 90, 100, 150, 160, 130]
        frm_tree, self.tabla = make_treeview(frm_tabla, columnas, anchos)
        frm_tree.pack(fill="both", expand=True)

    def _on_nuevo_retiro(self):
        if not _TKCAL:
            messagebox.showerror(
                "Dependencia faltante",
                "Instala tkcalendar para usar esta función:\n\npip install tkcalendar",
                parent=self,
            )
            return
        cajas = []
        try:
            cajas = cajas_model.obtener_cajas(solo_activas=True) or []
        except Exception:
            pass
        if not cajas:
            messagebox.showwarning("Sin cajas", "No hay cajas activas disponibles.", parent=self)
            return
        dialogo = _DialogoRetiro(self, cajas=cajas)
        self.wait_window(dialogo)
        if dialogo.resultado:
            try:
                retiros_model.insertar_retiro(**dialogo.resultado)
                messagebox.showinfo("Éxito", "Retiro registrado correctamente.", parent=self)
                self._refresh_retiros()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _on_eliminar_retiro(self):
        retiro_id = self._get_seleccionado()
        if not retiro_id:
            messagebox.showwarning("Selección", "Selecciona un retiro.", parent=self)
            return
        if messagebox.askyesno("Confirmar",
                               f"¿Eliminar el retiro #{retiro_id}?\nEsta acción no se puede deshacer.",
                               parent=self):
            try:
                retiros_model.eliminar_retiro(retiro_id)
                self._refresh_retiros()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _refresh_retiros(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            retiros = retiros_model.obtener_retiros_por_fecha(date.today()) or []
            for r in retiros:
                self.tabla.insert("", "end",
                    iid=str(r.get("id_retiro", "")),
                    values=(
                        r.get("id_retiro", ""),
                        r.get("numero_retiro", ""),
                        r.get("numero_transaccion", ""),
                        r.get("fecha", ""),
                        r.get("hora_retiro", ""),
                        r.get("hora_deposito", ""),
                        r.get("caja", ""),
                        f"${r.get('importe', 0):,.2f}",
                        f"${r.get('acumulado', 0):,.2f}",
                        r.get("usuario_responsable", ""),
                        r.get("observaciones", ""),
                        r.get("fecha_registro", ""),
                    ),
                )
        except Exception:
            pass

    def _get_seleccionado(self):
        sel = self.tabla.selection()
        if not sel:
            return None
        return int(sel[0])


class _DialogoRetiro(tk.Toplevel):

    def __init__(self, parent, cajas=None):
        super().__init__(parent)
        self.resultado = None
        self.cajas     = cajas or []
        self.title("Nuevo Retiro")
        self.resizable(False, False)
        self.configure(bg=C_WHITE)
        self.grab_set()
        self._centrar(440, 560)
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=C_WHITE, padx=28, pady=24)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)

        tk.Label(frm, text="Nuevo Retiro", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 12, "bold")).grid(
                     row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

        tk.Label(frm,
                 text="No. Retiro y No. Transacción se asignan automáticamente.",
                 bg=C_WHITE, fg="#757575",
                 font=("Arial", 8, "italic")).grid(
                     row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))

        # ── Caja ──────────────────────────────────────────────────────────────
        tk.Label(frm, text="Caja *", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=2, column=0, columnspan=2, sticky="w")
        nombres_cajas = [f"{c['nombre']} (#{c['numero_caja']})" for c in self.cajas]
        self.var_caja = tk.StringVar()
        self.combo_caja = ttk.Combobox(frm, textvariable=self.var_caja,
                                       values=nombres_cajas, state="readonly",
                                       font=("Arial", 11))
        if nombres_cajas:
            self.combo_caja.current(0)
        self.combo_caja.grid(row=3, column=0, columnspan=2, sticky="ew",
                             ipady=4, pady=(3, 12))

        # ── Importe ───────────────────────────────────────────────────────────
        tk.Label(frm, text="Importe ($) *", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=4, column=0, columnspan=2, sticky="w")
        self.var_importe = tk.StringVar()
        vcmd = (self.register(self._validar_numerico), "%P")
        tk.Entry(frm, textvariable=self.var_importe, font=("Arial", 11),
                 relief="solid", bd=1, validate="key",
                 validatecommand=vcmd).grid(
                     row=5, column=0, columnspan=2, sticky="ew",
                     ipady=5, pady=(3, 12))

        # ── Fecha ─────────────────────────────────────────────────────────────
        tk.Label(frm, text="Fecha *", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=6, column=0, columnspan=2, sticky="w")
        hoy = date.today()
        self.date_entry = DateEntry(
            frm,
            font=("Arial", 11),
            date_pattern="yyyy-mm-dd",
            year=hoy.year, month=hoy.month, day=hoy.day,
            background=C_ACCENT, foreground=C_WHITE,
            selectbackground=C_ACCENT,
            width=18,
        )
        self.date_entry.grid(row=7, column=0, columnspan=2, sticky="ew",
                             ipady=4, pady=(3, 12))

        # ── Hora Retiro | Hora Depósito ───────────────────────────────────────
        tk.Label(frm, text="Hora Retiro *", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=8, column=0, sticky="w")
        tk.Label(frm, text="Hora Depósito", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=8, column=1, sticky="w")

        ahora = datetime.now()
        self.spin_retiro_h, self.spin_retiro_m = self._make_time_picker(
            frm, row=9, col=0, hora=ahora.hour, minuto=ahora.minute)
        self.spin_deposito_h, self.spin_deposito_m = self._make_time_picker(
            frm, row=9, col=1, hora=ahora.hour, minuto=ahora.minute)

        # ── Usuario Responsable ───────────────────────────────────────────────
        tk.Label(frm, text="Usuario Responsable *", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=10, column=0, columnspan=2,
                                          sticky="w", pady=(10, 0))
        self.var_usuario = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_usuario, font=("Arial", 11),
                 relief="solid", bd=1).grid(
                     row=11, column=0, columnspan=2, sticky="ew",
                     ipady=5, pady=(3, 12))

        # ── Observaciones ─────────────────────────────────────────────────────
        tk.Label(frm, text="Observaciones", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 10)).grid(row=12, column=0, columnspan=2, sticky="w")
        self.texto_obs = tk.Text(frm, height=3, font=("Arial", 11),
                                 relief="solid", bd=1)
        self.texto_obs.grid(row=13, column=0, columnspan=2, sticky="ew",
                            pady=(3, 18))

        # ── Botones ───────────────────────────────────────────────────────────
        frm_btns = tk.Frame(frm, bg=C_WHITE)
        frm_btns.grid(row=14, column=0, columnspan=2, sticky="e")

        tk.Button(frm_btns, text="Cancelar", command=self.destroy,
                  bg="#ECEFF1", fg=C_TEXT, relief="flat", cursor="hand2",
                  font=("Arial", 10), padx=12, pady=6).pack(
                      side="left", padx=(0, 8))
        tk.Button(frm_btns, text="Guardar", command=self._guardar,
                  bg=C_ACCENT, fg=C_WHITE, activebackground="#1565C0",
                  activeforeground=C_WHITE, relief="flat", cursor="hand2",
                  font=("Arial", 10, "bold"), padx=14, pady=6).pack(side="left")

        self.bind("<Escape>", lambda e: self.destroy())

    def _make_time_picker(self, parent, row, col, hora=0, minuto=0):
        contenedor = tk.Frame(parent, bg=C_WHITE)
        contenedor.grid(row=row, column=col, sticky="w", pady=(3, 12),
                        padx=(0, 10) if col == 0 else 0)

        var_h = tk.StringVar(value=f"{hora:02d}")
        var_m = tk.StringVar(value=f"{minuto:02d}")

        spin_h = tk.Spinbox(contenedor, from_=0, to=23, width=3,
                            textvariable=var_h, format="%02.0f",
                            font=("Arial", 11), relief="solid", bd=1,
                            justify="center")
        spin_h.pack(side="left")

        tk.Label(contenedor, text=":", bg=C_WHITE, fg=C_TEXT,
                 font=("Arial", 11, "bold")).pack(side="left", padx=2)

        spin_m = tk.Spinbox(contenedor, from_=0, to=59, width=3,
                            textvariable=var_m, format="%02.0f",
                            font=("Arial", 11), relief="solid", bd=1,
                            justify="center")
        spin_m.pack(side="left")

        return spin_h, spin_m

    def _validar_numerico(self, valor):
        if valor == "":
            return True
        try:
            float(valor)
            return True
        except ValueError:
            return False

    def _guardar(self):
        idx     = self.combo_caja.current()
        importe = self.var_importe.get().strip()
        usuario = self.var_usuario.get().strip()

        if idx < 0:
            messagebox.showerror("Error", "Selecciona una caja.", parent=self)
            return
        if not importe:
            messagebox.showerror("Error", "El importe es obligatorio.", parent=self)
            return
        try:
            importe = float(importe)
        except ValueError:
            messagebox.showerror("Error", "Ingresa un importe válido.", parent=self)
            return
        if importe <= 0:
            messagebox.showerror("Error", "El importe debe ser mayor a cero.", parent=self)
            return
        if not usuario:
            messagebox.showerror("Error", "El usuario responsable es obligatorio.", parent=self)
            return

        hora_retiro   = f"{self.spin_retiro_h.get():>02}:{self.spin_retiro_m.get():>02}"
        hora_deposito = f"{self.spin_deposito_h.get():>02}:{self.spin_deposito_m.get():>02}"

        self.resultado = {
            "id_caja":                self.cajas[idx]["id"],
            "importe":                importe,
            "fecha":                  self.date_entry.get_date(),
            "hora_retiro":            hora_retiro,
            "hora_deposito":          hora_deposito,
            "id_usuario_responsable": usuario,
            "observaciones":          self.texto_obs.get("1.0", "end-1c").strip(),
        }
        self.destroy()

    def _centrar(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - ancho) // 2
        y = (self.winfo_screenheight() - alto)  // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")