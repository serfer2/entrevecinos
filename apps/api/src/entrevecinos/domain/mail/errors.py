class EmailQuotaExceeded(Exception):
    """No quedan correos en el periodo actual (TK-099): no se envía nada hasta el siguiente."""

    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__("Límite de correos del periodo alcanzado")
        self.retry_after_seconds = retry_after_seconds
