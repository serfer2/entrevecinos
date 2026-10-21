class EmailAlreadyRegistered(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"Email already registered: {email}")
        self.email = email


class EmailPendingVerification(Exception):
    """El correo pertenece a una cuenta registrada que aún no lo ha validado."""

    def __init__(self, email: str) -> None:
        super().__init__(f"Email pending verification: {email}")
        self.email = email


class InvalidCredentials(Exception):
    """Correo o contraseña incorrectos, o cuenta que no puede iniciar sesión."""


class NotAuthenticated(Exception):
    """Falta el token de acceso, no es válido o su usuario ya no puede autenticarse."""


class EmailNotVerified(Exception):
    """Credenciales correctas, pero la cuenta todavía no ha validado su correo."""


class VerificationInvalid(Exception):
    """El enlace de validación no existe: nunca se envió o ya se ha purgado."""


class EmailAlreadyVerified(Exception):
    """El enlace existe, pero la cuenta ya tiene el correo validado."""


class VerificationSuperseded(Exception):
    """Otro enlace más reciente sustituyó a este y la cuenta sigue pendiente de validación."""

    def __init__(self, email: str) -> None:
        super().__init__("Email verification superseded")
        self.email = email


class VerificationExpired(Exception):
    def __init__(self, email: str) -> None:
        super().__init__("Email verification expired")
        self.email = email
