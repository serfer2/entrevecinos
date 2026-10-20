from sqlalchemy import ColumnElement, func
from sqlalchemy.sql.elements import ColumnElement as Column


def escape_like(term: str) -> str:
    """Escapa los comodines de LIKE para que el texto del usuario se busque literalmente."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _normalized(value: Column[str] | str) -> ColumnElement[str]:
    # f_unaccent (migración 0003): unaccent inmutable, indexable en el futuro.
    return func.f_unaccent(func.lower(value))


def contains_text(column: Column[str], term: str) -> ColumnElement[bool]:
    """`column` contiene `term`, sin distinguir mayúsculas ni tildes."""
    return _normalized(column).like(_normalized(f"%{escape_like(term)}%"), escape="\\")


def starts_with_text(column: Column[str], term: str) -> ColumnElement[bool]:
    """`column` empieza por `term`, sin distinguir mayúsculas ni tildes."""
    return _normalized(column).like(_normalized(f"{escape_like(term)}%"), escape="\\")
