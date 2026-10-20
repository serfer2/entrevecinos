import re

MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 160

# Letras y dígitos Unicode: el resto de caracteres (operadores de tsquery incluidos) se descarta.
_WORD = re.compile(r"[^\W_]+")


def search_words(text: str) -> list[str]:
    """Palabras de la búsqueda sin las de un carácter (como prefijo coincidirían con casi todo)."""
    return [word for word in _WORD.findall(text) if len(word) > 1]


def prefix_tsquery(text: str) -> str | None:
    """`bici rojo` → `bici:* & rojo:*`. `None` si no queda ninguna palabra válida.

    El texto del usuario nunca llega sin limpiar a `to_tsquery`: solo palabras y operadores propios.
    """
    words = search_words(text)
    return " & ".join(f"{word}:*" for word in words) if words else None
