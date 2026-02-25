"""
app/modules/cajas/model.py

Modelo de datos para el módulo de cajas.
Maneja todas las operaciones de BD relacionadas con cajas.
"""

from app.db.connection import get_conn


def obtener_cajas(solo_activas=True):
    """
    Obtiene la lista de cajas del sistema.

    Args:
        solo_activas (bool): Si True, solo retorna cajas activas.

    Returns:
        list: Lista de cajas como diccionarios.
    """
    pass


def obtener_caja_por_id(id_caja):
    """
    Obtiene los detalles de una caja específica.

    Args:
        id_caja (int): ID de la caja.

    Returns:
        dict: Datos de la caja o None si no existe.
    """
    pass


def insertar_caja(nombre, numero_caja, ubicacion=""):
    """
    Inserta una nueva caja en la base de datos.

    Args:
        nombre (str): Nombre descriptivo de la caja.
        numero_caja (str): Número identificador de la caja.
        ubicacion (str): Ubicación física de la caja.

    Returns:
        int: ID de la caja insertada.

    Raises:
        Exception: Si hay error en la BD o nombre duplicado.
    """
    pass


def actualizar_caja(id_caja, nombre, numero_caja, ubicacion):
    """
    Actualiza los datos de una caja.

    Args:
        id_caja (int): ID de la caja a actualizar.
        nombre (str): Nuevo nombre.
        numero_caja (str): Nuevo número.
        ubicacion (str): Nueva ubicación.

    Returns:
        bool: True si se actualizó exitosamente.

    Raises:
        Exception: Si hay error en la BD.
    """
    pass


def toggle_activa(id_caja):
    """
    Activa o desactiva una caja (invierte su estado).

    Args:
        id_caja (int): ID de la caja.

    Returns:
        bool: Nuevo estado (True=activa, False=inactiva).

    Raises:
        Exception: Si hay error en la BD.
    """
    pass


def eliminar_caja(id_caja):
    """
    Elimina una caja de la base de datos.

    Args:
        id_caja (int): ID de la caja a eliminar.

    Returns:
        bool: True si se eliminó exitosamente.

    Raises:
        Exception: Si hay error en la BD.
    """
    pass
