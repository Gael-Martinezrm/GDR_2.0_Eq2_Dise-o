"""
app/auth/session.py

Gestión de sesión del usuario activo.
Singleton simple para mantener datos de usuario en memoria.
"""


class Session:
    """
    Gestiona la sesión del usuario activo.

    Implementa patrón Singleton para garantizar una única
    instancia durante la ejecución de la aplicación.

    Atributos:
        usuario (dict): Datos del usuario autenticado.
        id_usuario (int): ID del usuario activo.
        rol (str): Rol del usuario (administrador, gerente, operador).
    """

    _instance = None

    def __new__(cls):
        """
        Crea una instancia única de Session.

        Returns:
            Session: Instancia única de la clase.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._usuario = None
            cls._instance._id_usuario = None
            cls._instance._rol = None
        return cls._instance

    def set_user(self, id_usuario, nombre, usuario, rol):
        """
        Establece el usuario activo en la sesión.

        Args:
            id_usuario (int): ID del usuario.
            nombre (str): Nombre completo del usuario.
            usuario (str): Nombre de usuario (login).
            rol (str): Rol del usuario.
        """
        self._id_usuario = id_usuario
        self._usuario = {
            "id": id_usuario,
            "nombre": nombre,
            "usuario": usuario,
            "rol": rol
        }
        self._rol = rol

    def get_user(self):
        """
        Obtiene los datos del usuario activo.

        Returns:
            dict: Datos del usuario o None si no hay sesión activa.
        """
        return self._usuario

    def get_id_usuario(self):
        """
        Obtiene el ID del usuario activo.

        Returns:
            int: ID del usuario o None.
        """
        return self._id_usuario

    def get_rol(self):
        """
        Obtiene el rol del usuario activo.

        Returns:
            str: Rol del usuario o None.
        """
        return self._rol

    def is_authenticated(self):
        """
        Verifica si hay una sesión activa.

        Returns:
            bool: True si hay usuario autenticado, False si no.
        """
        return self._usuario is not None

    def is_admin(self):
        """
        Verifica si el usuario actual es administrador.

        Returns:
            bool: True si es admin, False si no.
        """
        return self._rol == "administrador"

    def is_gerente(self):
        """
        Verifica si el usuario actual es gerente.

        Returns:
            bool: True si es gerente, False si no.
        """
        return self._rol == "gerente"

    def is_operador(self):
        """
        Verifica si el usuario actual es operador.

        Returns:
            bool: True si es operador, False si no.
        """
        return self._rol == "operador"

    def logout(self):
        """
        Cierra la sesión del usuario actual.

        Limpia todos los datos de la sesión.
        """
        self._usuario = None
        self._id_usuario = None
        self._rol = None
