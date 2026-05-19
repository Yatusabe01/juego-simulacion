from __future__ import annotations

from math import floor
from random import random


def muestra_uniforme(a: float, b: float) -> float:
    """Devuelve una muestra uniforme continua en [a, b)."""
    return a + (b - a) * random()


def muestras_uniformes(n: int, a: float, b: float) -> list[float]:
    """Genera n muestras uniformes continuas."""
    return [muestra_uniforme(a, b) for _ in range(n)]


def entero_uniforme(a: int, b: int) -> int:
    """Devuelve un entero uniforme en [a, b]."""
    return floor(muestra_uniforme(a, b + 1))
