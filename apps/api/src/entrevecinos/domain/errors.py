class NotFoundError(Exception):
    """Base de los errores «no encontrado» de todas las áreas (la presentación responde 404)."""


class PermissionDenied(Exception):
    """El usuario no tiene permisos para la operación (la presentación responde 403)."""
