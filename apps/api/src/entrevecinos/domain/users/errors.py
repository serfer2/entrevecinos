class EmailAlreadyRegistered(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email already registered: {email}")
        self.email = email


class InvalidCredentials(Exception):
    """Correo o contraseña incorrectos, o cuenta que no puede iniciar sesión."""


class NotAuthenticated(Exception):
    """Falta el token de acceso, no es válido o su usuario ya no puede autenticarse."""


class EmailNotVerified(Exception):
    """Credenciales correctas, pero la cuenta todavía no ha validado su correo."""


class VerificationInvalid(Exception):
    """El enlace de validación no existe: nunca existió, ya se usó o lo sustituyó otro."""


class VerificationExpired(Exception):
    def __init__(self, email: str) -> None:
        super().__init__("Email verification expired")
        self.email = email
