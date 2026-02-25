"""
app/utils/helpers.py

Funciones auxiliares y utilidades generales.
"""

import hashlib
from datetime import datetime, timedelta


def hash_password(password):
    """
    Hashea una contraseña usando SHA-256.

    Args:
        password (str): Contraseña en texto plano.

    Returns:
        str: Hash SHA-256 de la contraseña (en hexadecimal).
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """
    Verifica que una contraseña coincida con su hash.

    Args:
        password (str): Contraseña en texto plano.
        password_hash (str): Hash SHA-256 almacenado.

    Returns:
        bool: True si coinciden, False si no.
    """
    return hash_password(password) == password_hash


def format_currency(valor):
    """
    Formatea un valor numérico como moneda.

    Args:
        valor (float): Cantidad a formatear.

    Returns:
        str: Cantidad formateada con símbolo $ y 2 decimales.
                Ejemplo: "$1,234.56"
    """
    pass


def format_date(fecha, formato="%d/%m/%Y"):
    """
    Formatea una fecha para visualización.

    Args:
        fecha (datetime.date o datetime.datetime): Fecha a formatear.
        formato (str): Formato desdeado. Default "%d/%m/%Y".

    Returns:
        str: Fecha formateada como string.
    """
    if isinstance(fecha, datetime):
        return fecha.strftime(formato)
    return fecha.strftime(formato) if hasattr(fecha, 'strftime') else str(fecha)


def validate_date(fecha_string, formato="%d/%m/%Y"):
    """
    Valida que un string sea una fecha válida.

    Args:
        fecha_string (str): String de fecha a validar.
        formato (str): Formato esperado. Default "%d/%m/%Y".

    Returns:
        tuple: (bool, datetime.date o None) - (Es válida, Objeto date si es válida).
    """
    pass


def get_fecha_inicio_semana(fecha=None):
    """
    Obtiene el primer día de la semana (lunes) para una fecha dada.

    Args:
        fecha (datetime.date): Fecha de referencia. Si None, usa hoy.

    Returns:
        datetime.date: Primer día de la semana.
    """
    if fecha is None:
        fecha = datetime.today().date()
    return fecha - timedelta(days=fecha.weekday())


def get_fecha_fin_semana(fecha=None):
    """
    Obtiene el último día de la semana (domingo) para una fecha dada.

    Args:
        fecha (datetime.date): Fecha de referencia. Si None, usa hoy.

    Returns:
        datetime.date: Último día de la semana.
    """
    if fecha is None:
        fecha = datetime.today().date()
    return fecha + timedelta(days=6 - fecha.weekday())


def get_fecha_inicio_mes(fecha=None):
    """
    Obtiene el primer día del mes para una fecha dada.

    Args:
        fecha (datetime.date): Fecha de referencia. Si None, usa hoy.

    Returns:
        datetime.date: Primer día del mes.
    """
    if fecha is None:
        fecha = datetime.today().date()
    return fecha.replace(day=1)


def get_fecha_fin_mes(fecha=None):
    """
    Obtiene el último día del mes para una fecha dada.

    Args:
        fecha (datetime.date): Fecha de referencia. Si None, usa hoy.

    Returns:
        datetime.date: Último día del mes.
    """
    if fecha is None:
        fecha = datetime.today().date()
    # Ir al primer día del próximo mes y restar un día
    if fecha.month == 12:
        return fecha.replace(year=fecha.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        return fecha.replace(month=fecha.month + 1, day=1) - timedelta(days=1)


def is_valid_email(email):
    """
    Valida que un string sea un email válido (validación básica).

    Args:
        email (str): Email a validar.

    Returns:
        bool: True si parece un email válido, False si no.
    """
    return "@" in email and "." in email.split("@")[1] if "@" in email else False


def is_valid_username(username):
    """
    Valida que un nombre de usuario sea válido.

    Requerimientos:
    - Mínimo 3 caracteres
    - Solo letras, números y guiones bajos

    Args:
        username (str): Nombre de usuario a validar.

    Returns:
        bool: True si es válido, False si no.
    """
    pass
