import tkinter as tk
from tkinter import ttk

def guardar_retiro():
    print("Guardando retiro...")
    print(f"Caja: {combo_caja.get()}")
    print(f"Importe: {entrada_importe.get()}")

# --- NUEVA FUNCIÓN DE VALIDACIÓN ---
def validar_importe(nuevo_valor):
    # 1. Permite que la caja esté vacía (por si el usuario borra todo para corregir)
    if nuevo_valor == "":
        return True
    # 2. Intenta convertir lo que escriben a un número decimal (float)
    try:
        float(nuevo_valor)
        return True
    except ValueError:
        # 3. Si no es un número (por ejemplo, una letra), lo rechaza y no lo escribe
        return False

# 1. Crear la ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Control de Retiros - Equipo 2")
ventana.geometry("450x550")
ventana.configure(bg="#F0F8FF")

# --- CONFIGURACIÓN DE ESTILOS ---
estilo = ttk.Style()
estilo.theme_use('clam')
estilo.configure('TLabel', background="#F0F8FF", foreground="#003366", font=("Segoe UI", 10))
estilo.configure('Titulo.TLabel', font=("Segoe UI", 18, "bold"), foreground="#001F3F", background="#F0F8FF")
estilo.configure('TButton', background="#0056b3", foreground="white", font=("Segoe UI", 10, "bold"), padding=6)
estilo.map('TButton', background=[('active', '#004080')])

# 2. Marco principal
marco = tk.Frame(ventana, bg="#F0F8FF", padx=30, pady=20)
marco.pack(fill="both", expand=True)

# 3. Título del formulario
titulo = ttk.Label(marco, text="Registro de Retiro", style="Titulo.TLabel")
titulo.grid(row=0, column=0, columnspan=2, pady=(0, 25))

# 4. Creación de los campos 

# Caja
ttk.Label(marco, text="Caja:").grid(row=1, column=0, sticky="e", pady=8, padx=5)
combo_caja = ttk.Combobox(marco, values=["Caja 1", "Caja 2", "Caja 3"], state="readonly", font=("Segoe UI", 10))
combo_caja.grid(row=1, column=1, sticky="w", pady=8)

# Número de Retiro
ttk.Label(marco, text="No. Retiro:").grid(row=2, column=0, sticky="e", pady=8, padx=5)
entrada_num_retiro = ttk.Entry(marco, font=("Segoe UI", 10))
entrada_num_retiro.grid(row=2, column=1, sticky="w", pady=8)

# Número de Transacción
ttk.Label(marco, text="No. Transacción:").grid(row=3, column=0, sticky="e", pady=8, padx=5)
entrada_transaccion = ttk.Entry(marco, font=("Segoe UI", 10))
entrada_transaccion.grid(row=3, column=1, sticky="w", pady=8)

# Hora de Retiro
ttk.Label(marco, text="Hora de Retiro (HH:MM):").grid(row=4, column=0, sticky="e", pady=8, padx=5)
entrada_hora_retiro = ttk.Entry(marco, font=("Segoe UI", 10))
entrada_hora_retiro.grid(row=4, column=1, sticky="w", pady=8)

# --- IMPORTE CON VALIDACIÓN ---
ttk.Label(marco, text="Importe ($):").grid(row=5, column=0, sticky="e", pady=8, padx=5)

# Registramos la función de validación en la ventana
validacion = ventana.register(validar_importe)

# Le decimos a la entrada que valide las teclas (key) usando nuestra función
entrada_importe = ttk.Entry(marco, font=("Segoe UI", 10), validate="key", validatecommand=(validacion, '%P'))
entrada_importe.grid(row=5, column=1, sticky="w", pady=8)
# ------------------------------

# Usuario Responsable
ttk.Label(marco, text="Usuario Responsable:").grid(row=6, column=0, sticky="e", pady=8, padx=5)
entrada_usuario = ttk.Entry(marco, font=("Segoe UI", 10))
entrada_usuario.grid(row=6, column=1, sticky="w", pady=8)

# Observaciones 
ttk.Label(marco, text="Observaciones:").grid(row=7, column=0, sticky="ne", pady=8, padx=5)
texto_obs = tk.Text(marco, height=4, width=28, font=("Segoe UI", 10), bg="#ffffff", bd=1, relief="solid")
texto_obs.grid(row=7, column=1, sticky="w", pady=8)

# 5. Botón de Guardar
boton_guardar = ttk.Button(marco, text="Guardar Retiro", command=guardar_retiro)
boton_guardar.grid(row=8, column=0, columnspan=2, pady=(30, 0))

# 6. Arrancar la aplicación
ventana.mainloop()