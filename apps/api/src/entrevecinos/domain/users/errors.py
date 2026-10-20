class EmailAlreadyRegistered(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email already registered: {email}")
        self.email = email


class InvalidCredentials(Exception):
    """Correo o contraseña incorrectos, o cuenta que no puede iniciar sesión."""


class NotAuthenticated(Exception):
    """Falta el token de acceso, no es válido o su usuario ya no puede autenticarse."""
