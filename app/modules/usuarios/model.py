"""
app/modules/usuarios/model.py

Modelo de datos para el módulo de usuarios.
Maneja todas las operaciones de BD relacionadas con usuarios.
"""

from app.db.connection import get_conn
from app.utils.helpers import hash_password


def obtener_usuarios(solo_activos=True):
    """
    Obtiene la lista de usuarios del sistema.

    Args:
        solo_activos (bool): Si True, solo retorna usuarios activos.

    Returns:
        list: Lista de usuarios como diccionarios.
    """
    pass


def obtener_usuario_por_id(id_usuario):
    """
    Obtiene los detalles de un usuario específico.

    Args:
        id_usuario (int): ID del usuario.

    Returns:
        dict: Datos del usuario o None si no existe.
    """
    pass


def obtener_usuario_por_username(usuario):
    """
    Obtiene un usuario por su nombre de usuario (login).

    Args:
        usuario (str): Nombre de usuario.

    Returns:
        dict: Datos del usuario o None si no existe.
    """
    pass


def insertar_usuario(nombre, usuario, password, rol):
    """
    Inserta un nuevo usuario en la base de datos.

    Args:
        nombre (str): Nombre completo del usuario.
        usuario (str): Nombre de usuario (login).
        password (str): Contraseña en texto plano (será hasheada).
        rol (str): Rol del usuario (administrador, gerente, operador).

    Returns:
        int: ID del usuario insertado.

    Raises:
        Exception: Si hay error en la BD o usuario duplicado.
    """
    pass


def actualizar_usuario(id_usuario, nombre, usuario, rol):
    """
    Actualiza los datos de un usuario (excepto contraseña).

    Args:
        id_usuario (int): ID del usuario a actualizar.
        nombre (str): Nuevo nombre.
        usuario (str): Nuevo nombre de usuario.
        rol (str): Nuevo rol.

    Returns:
        bool: True si se actualizó exitosamente.

    Raises:
        Exception: Si hay error en la BD.
    """
    pass


def cambiar_password(id_usuario, password_nueva):
    """
    Cambia la contraseña de un usuario.

    Args:
        id_usuario (int): ID del usuario.
        password_nueva (str): Nueva contraseña en texto plano.

    Returns:
        bool: True si se cambió exitosamente.

    Raises:
        Exception: Si hay error en la BD.
    """
    pass


def toggle_activo(id_usuario):
    """
    Activa o desactiva un usuario (invierte su estado).

    Args:
        id_usuario (int): ID del usuario.

    Returns:
        bool: Nuevo estado (True=activo, False=inactivo).

    Raises:
        Exception: Si hay error en la BD.
    """
    pass


def eliminar_usuario(id_usuario):
    """
    Elimina un usuario de la base de datos.

    Args:
        id_usuario (int): ID del usuario a eliminar.

    Returns:
        bool: True si se eliminó exitosamente.

    Raises:
        Exception: Si hay error en la BD.
    """
    pass


def verificar_password(id_usuario, password):
    """
    Verifica que la contraseña sea correcta para un usuario.

    Args:
        id_usuario (int): ID del usuario.
        password (str): Contraseña en texto plano a verificar.

    Returns:
        bool: True si es correcta, False si no.
    """
    pass
