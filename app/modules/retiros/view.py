"""
app/modules/retiros/view.py

Interfaz gráfica del módulo de retiros.
Permite registrar y visualizar retiros de efectivo.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from app.auth.session import Session
from app.modules.retiros import model as retiros_model
from app.modules.cajas import model as cajas_model
from app.ui.components import page_header

# Paleta de colores
C_BG     = "#F0F2F5"
C_WHITE  = "#FFFFFF"
C_TEXT   = "#212121"
C_ACCENT = "#1976D2"
C_DANGER = "#C62828"
C_SUCCESS = "#2E7D32"


def make_treeview(parent, columns, widths, height=15):
    """Crea un Treeview estilizado."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("App.Treeview",
        background=C_WHITE, foreground=C_TEXT,
        fieldbackground=C_WHITE, rowheight=28,
        font=("Arial", 10),
    )
    style.configure("App.Treeview.Heading",
        background="#1565C0", foreground=C_WHITE,
        font=("Arial", 10, "bold"), relief="flat",
    )
    style.map("App.Treeview",
        background=[("selected", C_ACCENT)],
        foreground=[("selected", C_WHITE)],
    )

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

    return frm, tree


class RetirosView(tk.Frame):
    """Vista del módulo de retiros."""

    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self.parent = parent
        self.sesion = Session()
        self.tabla = None
        self.cajas_cache = []
        self._create_widgets()
        self._cargar_cajas()
        self._refresh_retiros()

    def _create_widgets(self):
        """Crea los componentes de la interfaz."""
        
        # Encabezado
        page_header(self, "Registro de Retiros").pack(fill="x")

        # Panel superior con filtros y botones
        frm_superior = tk.Frame(self, bg=C_BG, pady=10, padx=16)
        frm_superior.pack(fill="x")

        # Fila 1: Botón Nuevo Retiro
        frm_fila1 = tk.Frame(frm_superior, bg=C_BG)
        frm_fila1.pack(fill="x", pady=(0, 10))
        
        btn_nuevo = tk.Button(
            frm_fila1, 
            text="➕ NUEVO RETIRO", 
            command=self._on_nuevo_retiro,
            bg=C_ACCENT, 
            fg="white",
            font=("Arial", 11, "bold"),
            padx=25, 
            pady=8,
            cursor="hand2",
            relief="raised",
            bd=2
        )
        btn_nuevo.pack(side="left")
        
        # Fila 2: Filtros y botón Eliminar
        frm_fila2 = tk.Frame(frm_superior, bg=C_BG)
        frm_fila2.pack(fill="x")
        
        # Fecha
        tk.Label(frm_fila2, text="Fecha:", bg=C_BG, fg=C_TEXT,
                font=("Arial", 10)).pack(side="left", padx=(0, 5))
        
        self.filtro_fecha = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.entry_fecha = tk.Entry(frm_fila2, textvariable=self.filtro_fecha,
                                   width=12, font=("Arial", 10))
        self.entry_fecha.pack(side="left", padx=(0, 15))

        # Caja
        tk.Label(frm_fila2, text="Caja:", bg=C_BG, fg=C_TEXT,
                font=("Arial", 10)).pack(side="left", padx=(0, 5))
        
        self.filtro_caja = tk.StringVar(value="Todas")
        self.combo_caja = ttk.Combobox(frm_fila2, textvariable=self.filtro_caja,
                                      values=["Todas"], width=15, state="readonly")
        self.combo_caja.pack(side="left", padx=(0, 10))

        # Botón Filtrar
        btn_filtrar = tk.Button(
            frm_fila2, 
            text="🔍 FILTRAR", 
            command=self._on_filtrar,
            bg="#1565C0", 
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15, 
            pady=5,
            cursor="hand2"
        )
        btn_filtrar.pack(side="left", padx=(0, 15))
        
        # Botón Eliminar
        btn_eliminar = tk.Button(
            frm_fila2, 
            text="🗑️ ELIMINAR RETIRO SELECCIONADO", 
            command=self._on_eliminar_retiro,
            bg="#C62828", 
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20, 
            pady=5,
            cursor="hand2",
            relief="raised",
            bd=2
        )
        btn_eliminar.pack(side="left")

        # Panel de estadísticas
        frm_stats = tk.Frame(self, bg=C_WHITE, relief="solid", bd=1, padx=16, pady=8)
        frm_stats.pack(fill="x", padx=16, pady=5)

        tk.Label(frm_stats, text="📊 Resumen del Día:", bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 10, "bold")).pack(side="left", padx=(0, 20))

        self.lbl_total = tk.Label(frm_stats, text="Total: $0.00", bg=C_WHITE, fg=C_SUCCESS,
                                 font=("Arial", 10, "bold"))
        self.lbl_total.pack(side="left", padx=(0, 15))

        self.lbl_cantidad = tk.Label(frm_stats, text="Cantidad: 0", bg=C_WHITE, fg=C_ACCENT,
                                    font=("Arial", 10, "bold"))
        self.lbl_cantidad.pack(side="left", padx=(0, 15))

        self.lbl_promedio = tk.Label(frm_stats, text="Promedio: $0.00", bg=C_WHITE, fg=C_TEXT,
                                    font=("Arial", 10, "bold"))
        self.lbl_promedio.pack(side="left")

        # Tabla de retiros
        frm_tabla = tk.Frame(self, bg=C_BG, padx=16, pady=4)
        frm_tabla.pack(fill="both", expand=True)

        columnas = ["ID", "Fecha", "Caja", "Usuario", "Monto", "Motivo"]
        anchos = [50, 130, 100, 120, 100, 250]
        frm_tree, self.tabla = make_treeview(frm_tabla, columnas, anchos, height=15)
        frm_tree.pack(fill="both", expand=True)

        # Vincular doble click para ver detalle
        self.tabla.bind("<Double-Button-1>", self._on_ver_detalle)

    def _cargar_cajas(self):
        """Carga las cajas activas para el combo de filtro"""
        try:
            self.cajas_cache = cajas_model.obtener_cajas(solo_activas=True)
            cajas_nombres = ["Todas"] + [c["nombre"] for c in self.cajas_cache]
            self.combo_caja['values'] = cajas_nombres
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las cajas: {e}", parent=self)

    def _refresh_retiros(self):
        """Refresca la tabla de retiros con los datos actualizados."""
        try:
            for item in self.tabla.get_children():
                self.tabla.delete(item)

            try:
                fecha_obj = datetime.strptime(self.filtro_fecha.get(), "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/AAAA", parent=self)
                return

            if self.filtro_caja.get() == "Todas":
                retiros = retiros_model.obtener_retiros_por_fecha(fecha_obj)
            else:
                caja_seleccionada = next(
                    (c for c in self.cajas_cache if c["nombre"] == self.filtro_caja.get()), 
                    None
                )
                if caja_seleccionada:
                    retiros = retiros_model.obtener_retiros_por_caja_y_fecha(
                        caja_seleccionada["id"], fecha_obj
                    )
                else:
                    retiros = []

            for r in retiros:
                if isinstance(r['fecha_retiro'], str):
                    fecha_str = r['fecha_retiro'][:16].replace('T', ' ')
                else:
                    fecha_str = str(r['fecha_retiro'])[:16]

                # Solo mostrar el motivo en la tabla (sin observaciones)
                motivo = r.get('motivo', '')[:50] if r.get('motivo') else "(sin motivo)"

                self.tabla.insert("", "end",
                    iid=str(r["id"]),
                    values=(
                        r["id"],
                        fecha_str,
                        r.get("nombre_caja", "N/A"),
                        r.get("nombre_usuario", r.get("username", "N/A")),
                        f"${r['monto']:,.2f}",
                        motivo
                    )
                )

            self._actualizar_estadisticas(fecha_obj)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar retiros: {e}", parent=self)

    def _actualizar_estadisticas(self, fecha):
        """Actualiza las estadísticas mostradas"""
        try:
            stats = retiros_model.obtener_estadisticas_diarias(fecha)
            
            self.lbl_total.config(text=f"Total: ${stats['total']:,.2f}")
            self.lbl_cantidad.config(text=f"Cantidad: {stats['cantidad']}")
            self.lbl_promedio.config(text=f"Promedio: ${stats['promedio']:,.2f}")
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")

    def _on_nuevo_retiro(self):
        """Abre el diálogo para registrar un nuevo retiro."""
        if not self.cajas_cache:
            messagebox.showerror("Error", "No hay cajas activas disponibles", parent=self)
            return

        dialogo = _DialogoRetiro(self, self.cajas_cache)
        self.wait_window(dialogo)
        
        if dialogo.resultado:
            try:
                id_retiro = retiros_model.insertar_retiro(
                    id_usuario=self.sesion.get_id_usuario(),
                    id_caja=dialogo.resultado['id_caja'],
                    monto=dialogo.resultado['monto'],
                    motivo=dialogo.resultado['motivo'],
                    observaciones=dialogo.resultado['observaciones']
                )
                messagebox.showinfo("Éxito", f"✅ Retiro #{id_retiro} registrado correctamente.", parent=self)
                self._refresh_retiros()
            except ValueError as e:
                messagebox.showerror("Error de validación", str(e), parent=self)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el retiro: {e}", parent=self)

    def _on_eliminar_retiro(self):
        """Elimina el retiro seleccionado (previa confirmación)."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("⚠️ Selección", "Selecciona un retiro para eliminar.", parent=self)
            return

        id_retiro = int(seleccion[0])
        
        retiro = retiros_model.obtener_retiro_por_id(id_retiro)
        if not retiro:
            messagebox.showerror("Error", "El retiro ya no existe.", parent=self)
            self._refresh_retiros()
            return

        if messagebox.askyesno("⚠️ Confirmar Eliminación",
                               f"¿Eliminar el retiro #{id_retiro}?\n\n"
                               f"💰 Monto: ${retiro['monto']:,.2f}\n"
                               f"🏦 Caja: {retiro.get('nombre_caja', 'N/A')}\n"
                               f"📅 Fecha: {retiro['fecha_retiro']}\n"
                               f"👤 Registrado por: {retiro.get('nombre_usuario', 'N/A')}\n\n"
                               "❌ Esta acción NO se puede deshacer.",
                               parent=self):
            try:
                if retiros_model.eliminar_retiro(id_retiro):
                    messagebox.showinfo("✅ Éxito", f"Retiro #{id_retiro} eliminado correctamente.", parent=self)
                    self._refresh_retiros()
                else:
                    messagebox.showerror("Error", "El retiro no existe.", parent=self)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _on_filtrar(self):
        """Filtra retiros según fecha y caja seleccionadas."""
        self._refresh_retiros()

    def _on_ver_detalle(self, event):
        """Muestra el detalle del retiro seleccionado (doble click)."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Información", "Selecciona un retiro para ver el detalle.", parent=self)
            return

        id_retiro = int(seleccion[0])
        
        retiro = retiros_model.obtener_retiro_por_id(id_retiro)
        
        if retiro:
            _DialogoDetalleRetiro(self, retiro)
        else:
            messagebox.showerror("Error", f"No se encontró el retiro con ID {id_retiro}", parent=self)


# ── Diálogo para nuevo retiro ─────────────────────────────────────────

class _DialogoRetiro(tk.Toplevel):
    """Diálogo para registrar un nuevo retiro."""

    def __init__(self, parent, cajas):
        super().__init__(parent)
        self.parent = parent
        self.cajas = cajas
        self.resultado = None
        
        self.title("Nuevo Retiro")
        self.geometry("500x550")
        self.resizable(False, False)
        self.configure(bg=C_WHITE)
        self.grab_set()
        self._centrar(500, 550)
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=C_WHITE, padx=28, pady=24)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="📝 Nuevo Retiro", bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 16))

        # Caja
        tk.Label(frm, text="Caja *", bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 10)).pack(anchor="w")
        
        cajas_nombres = [c["nombre"] for c in self.cajas]
        self.var_caja = tk.StringVar()
        self.combo_caja = ttk.Combobox(frm, textvariable=self.var_caja,
                                      values=cajas_nombres, state="readonly",
                                      font=("Arial", 11), width=40)
        self.combo_caja.pack(fill="x", pady=(3, 12))
        if cajas_nombres:
            self.combo_caja.current(0)

        # Monto
        tk.Label(frm, text="Monto ($) *", bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 10)).pack(anchor="w")
        
        vcmd = (self.register(self._validar_monto), '%P')
        self.var_monto = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_monto, font=("Arial", 11),
                validate="key", validatecommand=vcmd,
                relief="solid", bd=1).pack(fill="x", pady=(3, 12))

        # Motivo
        tk.Label(frm, text="Motivo", bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 10)).pack(anchor="w")
        
        self.var_motivo = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_motivo, font=("Arial", 11),
                relief="solid", bd=1).pack(fill="x", pady=(3, 12))

        # Observaciones
        tk.Label(frm, text="Observaciones", bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 10)).pack(anchor="w")
        
        self.text_observaciones = tk.Text(frm, height=5, width=40, font=("Arial", 11),
                                         relief="solid", bd=1)
        self.text_observaciones.pack(fill="x", pady=(3, 20))

        # Botones
        frm_btns = tk.Frame(frm, bg=C_WHITE)
        frm_btns.pack(fill="x", pady=(10, 0))

        tk.Button(frm_btns, text="Cancelar", command=self.destroy,
                 bg="#ECEFF1", fg=C_TEXT, relief="flat", cursor="hand2",
                 font=("Arial", 10), padx=20, pady=8).pack(side="right", padx=(5, 0))
        
        tk.Button(frm_btns, text="Guardar Retiro", command=self._guardar,
                 bg=C_ACCENT, fg=C_WHITE, relief="flat", cursor="hand2",
                 font=("Arial", 10, "bold"), padx=20, pady=8).pack(side="right")

        self.bind("<Return>", lambda e: self._guardar())
        self.bind("<Escape>", lambda e: self.destroy())

    def _validar_monto(self, valor):
        if valor == "":
            return True
        try:
            float(valor)
            return True
        except ValueError:
            return False

    def _guardar(self):
        """Guarda el retiro si los datos son válidos"""
        if not self.var_caja.get():
            messagebox.showerror("Error", "Selecciona una caja.", parent=self)
            return

        if not self.var_monto.get():
            messagebox.showerror("Error", "Ingresa el monto.", parent=self)
            return

        try:
            monto = float(self.var_monto.get())
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a cero.", parent=self)
                return
        except ValueError:
            messagebox.showerror("Error", "Monto inválido.", parent=self)
            return

        caja_seleccionada = next(
            (c for c in self.cajas if c["nombre"] == self.var_caja.get()),
            None
        )
        if not caja_seleccionada:
            messagebox.showerror("Error", "Caja no válida.", parent=self)
            return

        motivo = self.var_motivo.get().strip()
        observaciones = self.text_observaciones.get("1.0", "end-1c").strip()

        self.resultado = {
            'id_caja': caja_seleccionada["id"],
            'monto': monto,
            'motivo': motivo,
            'observaciones': observaciones
        }
        self.destroy()

    def _centrar(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

class _DialogoDetalleRetiro(tk.Toplevel):

    def __init__(self, parent, retiro):
        super().__init__(parent)
        self.retiro = retiro
        self.parent = parent
        
        self.title(f"Detalle del Retiro #{retiro['id']}")
        self.geometry("550x450")
        self.resizable(False, False)
        self.configure(bg=C_WHITE)
        self.grab_set()
        self._centrar(550, 450)
        self._build()

    def _format_fecha(self, fecha_str):
        """Formatea la fecha para mostrar solo hasta segundos (2 dígitos)."""
        if not fecha_str:
            return "N/A"
        
        if isinstance(fecha_str, str):
            try:
                if '.' in fecha_str:
                    fecha_str = fecha_str.split('.')[0]
                return fecha_str
            except:
                return fecha_str[:19] if len(fecha_str) > 19 else fecha_str
        
        try:
            return fecha_str.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return str(fecha_str)

    def _build(self):
        canvas = tk.Canvas(self, bg=C_WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=C_WHITE)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frm = scrollable_frame
        frm.configure(padx=25, pady=20)

        tk.Label(frm, text=f"📋 Detalle del Retiro #{self.retiro['id']}",
                font=("Arial", 14, "bold"), bg=C_WHITE, fg=C_ACCENT).pack(anchor="w", pady=(0, 15))

        tk.Frame(frm, bg="#E0E0E0", height=2).pack(fill="x", pady=(0, 15))

        fecha_retiro = self._format_fecha(self.retiro.get('fecha_retiro', 'N/A'))

        info = [
            ("ID:", str(self.retiro.get('id', 'N/A'))),
            ("Fecha y Hora:", fecha_retiro),
            ("Caja:", f"{self.retiro.get('nombre_caja', 'N/A')} (N° {self.retiro.get('numero_caja', 'N/A')})"),
            ("Usuario:", self.retiro.get('nombre_usuario', self.retiro.get('username', 'N/A'))),
            ("Monto:", f"${self.retiro.get('monto', 0):,.2f}"),
            ("Motivo:", self.retiro.get('motivo', '') or "(sin motivo)"),
            ("Observaciones:", self.retiro.get('observaciones', '') or "(sin observaciones)")
        ]

        for i, (label, valor) in enumerate(info):
            frm_fila = tk.Frame(frm, bg=C_WHITE)
            frm_fila.pack(fill="x", pady=6)

            lbl_label = tk.Label(frm_fila, text=label, font=("Arial", 10, "bold"),
                                bg=C_WHITE, fg=C_TEXT, width=12, anchor="w")
            lbl_label.pack(side="left")

            lbl_valor = tk.Label(frm_fila, text=valor, font=("Arial", 10),
                                bg=C_WHITE, fg=C_TEXT, wraplength=320, justify="left")
            lbl_valor.pack(side="left", fill="x", expand=True, padx=(5, 0))

        tk.Frame(frm, bg="#E0E0E0", height=1).pack(fill="x", pady=(15, 10))

        btn_cerrar = tk.Button(frm, text="Cerrar", command=self.destroy,
                 bg=C_ACCENT, fg=C_WHITE, font=("Arial", 10, "bold"),
                 relief="flat", cursor="hand2", padx=30, pady=8)
        btn_cerrar.pack(pady=(10, 0))

        self.bind("<Escape>", lambda e: self.destroy())

    def _centrar(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")