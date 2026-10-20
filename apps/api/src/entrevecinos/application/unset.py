from enum import Enum
from typing import Final


class _Unset(Enum):
    TOKEN = "UNSET"


UNSET: Final = _Unset.TOKEN
"""Campo no enviado: no se modifica (a diferencia de `None`, que borra el valor)."""

Unset = _Unset
