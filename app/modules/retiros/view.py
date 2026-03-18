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
from app.ui.components import styled_button, make_treeview, page_header

# Paleta de colores (consistente con cajas)
C_BG     = "#F0F2F5"
C_WHITE  = "#FFFFFF"
C_TEXT   = "#212121"
C_ACCENT = "#1976D2"
C_DANGER = "#C62828"
C_SUCCESS = "#2E7D32"


class RetirosView(tk.Frame):
    """
    Vista del módulo de retiros.
    
    Proporciona interfaz para:
    - Registrar nuevos retiros
    - Consultar retiros por fecha/caja
    - Ver detalles de retiros
    """

    def __init__(self, parent):
        """
        Inicializa la vista de retiros.
        
        Args:
            parent: Widget padre (ventana principal).
        """
        super().__init__(parent, bg=C_BG)
        self.parent = parent
        self.tabla = None
        self.cajas_cache = []
        self._create_widgets()
        self._cargar_cajas()
        self._refresh_retiros()

    def _create_widgets(self):
        """
        Crea los componentes de la interfaz.
        
        Incluye:
        - Panel de filtros
        - Tabla de retiros
        - Botones de acciones
        """
        sesion = Session()

        # Encabezado
        page_header(self, "Registro de Retiros").pack(fill="x")

        # Panel superior con filtros y botón nuevo
        frm_superior = tk.Frame(self, bg=C_BG, pady=10, padx=16)
        frm_superior.pack(fill="x")

        # Botón Nuevo Retiro (disponible para todos)
        styled_button(frm_superior, "Nuevo Retiro",
                     self._on_nuevo_retiro, width=15).pack(side="left", padx=(0, 20))

        # Filtros
        frm_filtros = tk.Frame(frm_superior, bg=C_BG)
        frm_filtros.pack(side="left", fill="x", expand=True)

        tk.Label(frm_filtros, text="Fecha:", bg=C_BG, fg=C_TEXT,
                font=("Arial", 10)).pack(side="left", padx=(0, 5))
        
        self.filtro_fecha = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.entry_fecha = tk.Entry(frm_filtros, textvariable=self.filtro_fecha,
                                   width=12, font=("Arial", 10))
        self.entry_fecha.pack(side="left", padx=(0, 15))

        tk.Label(frm_filtros, text="Caja:", bg=C_BG, fg=C_TEXT,
                font=("Arial", 10)).pack(side="left", padx=(0, 5))
        
        self.filtro_caja = tk.StringVar(value="Todas")
        self.combo_caja = ttk.Combobox(frm_filtros, textvariable=self.filtro_caja,
                                      values=["Todas"], width=15, state="readonly")
        self.combo_caja.pack(side="left", padx=(0, 10))

        styled_button(frm_filtros, "Filtrar", self._on_filtrar, width=8).pack(side="left")

        # Panel de estadísticas rápidas
        frm_stats = tk.Frame(self, bg=C_WHITE, relief="solid", bd=1, padx=16, pady=8)
        frm_stats.pack(fill="x", padx=16, pady=5)

        tk.Label(frm_stats, text="Resumen del Día:", bg=C_WHITE, fg=C_TEXT,
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
        frm_tree, self.tabla = make_treeview(frm_tabla, columnas, anchos, height=18)
        frm_tree.pack(fill="both", expand=True)

        # Botón Eliminar (solo admin/gerente)
        if sesion.is_admin() or sesion.is_gerente():
            frm_inferior = tk.Frame(self, bg=C_BG, pady=10, padx=16)
            frm_inferior.pack(fill="x")
            styled_button(frm_inferior, "Eliminar Retiro Seleccionado",
                         self._on_eliminar_retiro, danger=True).pack(side="right")

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
        """
        Refresca la tabla de retiros con los datos actualizados.
        """
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)

            # Parsear fecha
            try:
                fecha_obj = datetime.strptime(self.filtro_fecha.get(), "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/AAAA", parent=self)
                return

            # Obtener retiros según filtro
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

            # Insertar retiros
            for i, r in enumerate(retiros):
                # Formatear fecha
                if isinstance(r['fecha_retiro'], str):
                    fecha_str = r['fecha_retiro'][:16].replace('T', ' ')
                else:
                    fecha_str = str(r['fecha_retiro'])

                self.tabla.insert("", "end",
                    iid=str(r["id"]),
                    values=(
                        r["id"],
                        fecha_str,
                        r.get("nombre_caja", "N/A"),
                        r.get("nombre_usuario", r.get("username", "N/A")),
                        f"${r['monto']:,.2f}",
                        r.get("motivo", "")[:50] + "..." if len(r.get("motivo", "")) > 50 else r.get("motivo", "")
                    )
                )

            # Actualizar estadísticas
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
        """
        Abre el diálogo para registrar un nuevo retiro.
        
        Captura:
        - Caja
        - Monto
        - Motivo
        - Observaciones
        """
        if not self.cajas_cache:
            messagebox.showerror("Error", "No hay cajas activas disponibles", parent=self)
            return

        dialogo = _DialogoRetiro(self, self.cajas_cache)
        self.wait_window(dialogo)
        
        if dialogo.resultado:
            sesion = Session()
            try:
                id_retiro = retiros_model.insertar_retiro(
                    id_usuario=sesion.get_id_usuario(),
                    id_caja=dialogo.resultado['id_caja'],
                    monto=dialogo.resultado['monto'],
                    motivo=dialogo.resultado['motivo'],
                    observaciones=dialogo.resultado['observaciones']
                )
                messagebox.showinfo("Éxito", f"Retiro #{id_retiro} registrado correctamente.", parent=self)
                self._refresh_retiros()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el retiro: {e}", parent=self)

    def _on_eliminar_retiro(self):
        """
        Elimina el retiro seleccionado (previa confirmación).
        """
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Selecciona un retiro para eliminar.", parent=self)
            return

        id_retiro = int(seleccion[0])
        
        if messagebox.askyesno("Confirmar",
                               f"¿Eliminar el retiro #{id_retiro}?\nEsta acción no se puede deshacer.",
                               parent=self):
            try:
                if retiros_model.eliminar_retiro(id_retiro):
                    messagebox.showinfo("Éxito", "Retiro eliminado correctamente.", parent=self)
                    self._refresh_retiros()
                else:
                    messagebox.showerror("Error", "El retiro no existe.", parent=self)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def _on_filtrar(self):
        """
        Filtra retiros según fecha y caja seleccionadas.
        """
        self._refresh_retiros()

    def _on_ver_detalle(self, event):
        """
        Muestra el detalle del retiro seleccionado (doble click).
        """
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        id_retiro = int(seleccion[0])
        retiro = retiros_model.obtener_retiro_por_id(id_retiro)
        
        if retiro:
            _DialogoDetalleRetiro(self, retiro)


# ── Diálogo para nuevo/editar retiro ─────────────────────────────────────────

class _DialogoRetiro(tk.Toplevel):
    """
    Diálogo para registrar un nuevo retiro.
    """

    def __init__(self, parent, cajas, retiro=None):
        super().__init__(parent)
        self.parent = parent
        self.cajas = cajas
        self.retiro = retiro
        self.resultado = None
        
        self.title("Nuevo Retiro" if not retiro else "Editar Retiro")
        self.resizable(False, False)
        self.configure(bg=C_WHITE)
        self.grab_set()
        self._centrar(450, 500)
        self._build(retiro)

    def _build(self, retiro):
        frm = tk.Frame(self, bg=C_WHITE, padx=28, pady=24)
        frm.pack(fill="both", expand=True)

        # Título
        tk.Label(frm, text=self.title(), bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 12, "bold")).grid(
                    row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        # Caja
        tk.Label(frm, text="Caja *", bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 10)).grid(row=1, column=0, columnspan=2, sticky="w")
        
        cajas_nombres = [c["nombre"] for c in self.cajas]
        self.var_caja = tk.StringVar()
        self.combo_caja = ttk.Combobox(frm, textvariable=self.var_caja,
                                      values=cajas_nombres, state="readonly",
                                      font=("Arial", 11), width=30)
        self.combo_caja.grid(row=2, column=0, columnspan=2, sticky="ew", ipady=5, pady=(3, 12))
        if cajas_nombres:
            self.combo_caja.current(0)

        # Monto
        tk.Label(frm, text="Monto ($) *", bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 10)).grid(row=3, column=0, columnspan=2, sticky="w")
        
        vcmd = (self.register(self._validar_monto), '%P')
        self.var_monto = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_monto, font=("Arial", 11),
                validate="key", validatecommand=vcmd,
                relief="solid", bd=1).grid(
                    row=4, column=0, columnspan=2, sticky="ew",
                    ipady=5, pady=(3, 12))

        # Motivo
        tk.Label(frm, text="Motivo", bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 10)).grid(row=5, column=0, columnspan=2, sticky="w")
        
        self.var_motivo = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_motivo, font=("Arial", 11),
                relief="solid", bd=1).grid(
                    row=6, column=0, columnspan=2, sticky="ew",
                    ipady=5, pady=(3, 12))

        # Observaciones
        tk.Label(frm, text="Observaciones", bg=C_WHITE, fg=C_TEXT,
                font=("Arial", 10)).grid(row=7, column=0, columnspan=2, sticky="w")
        
        self.text_observaciones = tk.Text(frm, height=4, width=30, font=("Arial", 11),
                                         relief="solid", bd=1)
        self.text_observaciones.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(3, 18))

        # Botones
        frm_btns = tk.Frame(frm, bg=C_WHITE)
        frm_btns.grid(row=9, column=0, columnspan=2, sticky="e")

        tk.Button(frm_btns, text="Cancelar", command=self.destroy,
                 bg="#ECEFF1", fg=C_TEXT, relief="flat", cursor="hand2",
                 font=("Arial", 10), padx=12, pady=6).pack(
                     side="left", padx=(0, 8))
        
        tk.Button(frm_btns, text="Guardar", command=self._guardar,
                 bg=C_ACCENT, fg=C_WHITE, activebackground="#1565C0",
                 activeforeground=C_WHITE, relief="flat", cursor="hand2",
                 font=("Arial", 10, "bold"), padx=14, pady=6).pack(side="left")

        # Configurar grid
        frm.columnconfigure(0, weight=1)

        # Bindings
        self.bind("<Return>", lambda e: self._guardar())
        self.bind("<Escape>", lambda e: self.destroy())

    def _validar_monto(self, valor):
        """Valida que el monto sea un número válido"""
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

        # Obtener ID de la caja seleccionada
        caja_seleccionada = next(
            (c for c in self.cajas if c["nombre"] == self.var_caja.get()),
            None
        )
        if not caja_seleccionada:
            messagebox.showerror("Error", "Caja no válida.", parent=self)
            return

        self.resultado = {
            'id_caja': caja_seleccionada["id"],
            'monto': monto,
            'motivo': self.var_motivo.get().strip(),
            'observaciones': self.text_observaciones.get("1.0", "end-1c").strip()
        }
        self.destroy()

    def _centrar(self, ancho, alto):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")


# ── Diálogo para ver detalle ────────────────────────────────────────────────

class _DialogoDetalleRetiro(tk.Toplevel):
    """
    Diálogo para mostrar el detalle completo de un retiro.
    """

    def __init__(self, parent, retiro):
        super().__init__(parent)
        self.parent = parent
        self.retiro = retiro
        
        self.title(f"Detalle del Retiro #{retiro['id']}")
        self.resizable(False, False)
        self.configure(bg=C_WHITE)
        self.grab_set()
        self._centrar(400, 350)
        self._build()

    def _build(self):
        frm = tk.Frame(self, bg=C_WHITE, padx=25, pady=20)
        frm.pack(fill="both", expand=True)

        # Título
        tk.Label(frm, text=f"Detalle del Retiro #{self.retiro['id']}",
                font=("Arial", 12, "bold"), bg=C_WHITE, fg=C_ACCENT).pack(anchor="w", pady=(0, 15))

        # Información en grid
        info = [
            ("ID:", str(self.retiro['id'])),
            ("Fecha:", str(self.retiro['fecha_retiro'])),
            ("Caja:", f"{self.retiro.get('nombre_caja', 'N/A')} ({self.retiro.get('numero_caja', '')})"),
            ("Usuario:", self.retiro.get('nombre_usuario', self.retiro.get('username', 'N/A'))),
            ("Monto:", f"${self.retiro['monto']:,.2f}"),
            ("Motivo:", self.retiro.get('motivo', '') or "(sin motivo)"),
            ("Observaciones:", self.retiro.get('observaciones', '') or "(sin observaciones)"),
            ("Registrado:", self.retiro.get('fecha_registro', 'N/A'))
        ]

        for i, (label, valor) in enumerate(info):
            tk.Label(frm, text=label, font=("Arial", 10, "bold"),
                    bg=C_WHITE, fg=C_TEXT).grid(row=i, column=0, sticky="w", pady=2, padx=(0,10))
            
            if i >= 5:  # Motivo y Observaciones pueden ser largos
                tk.Label(frm, text=valor, font=("Arial", 10), wraplength=200,
                        bg=C_WHITE, fg=C_TEXT, justify="left").grid(row=i, column=1, sticky="w", pady=2)
            else:
                tk.Label(frm, text=valor, font=("Arial", 10),
                        bg=C_WHITE, fg=C_TEXT).grid(row=i, column=1, sticky="w", pady=2)

        # Botón Cerrar
        tk.Button(frm, text="Cerrar", command=self.destroy,
                 bg=C_ACCENT, fg=C_WHITE, font=("Arial", 10),
                 relief="flat", cursor="hand2", padx=20, pady=6).grid(
                     row=len(info), column=0, columnspan=2, pady=(15, 0))

        # Configurar grid
        frm.columnconfigure(1, weight=1)

        # Bind Escape
        self.bind("<Escape>", lambda e: self.destroy())

    def _centrar(self, ancho, alto):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")