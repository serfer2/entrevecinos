def normalize_email(email: str) -> str:
    """Forma canónica del correo: sin espacios alrededor y en minúsculas."""
    return email.strip().lower()
