"""Funciones puras para cálculo y formato de puntajes."""

from __future__ import annotations

from configuracion import PUNTOS_DESTRUIR, PUNTOS_ESQUIVAR


def sumar_por_destruccion(puntaje: int) -> int:
    return puntaje + PUNTOS_DESTRUIR


def sumar_por_esquivar(puntaje: int) -> int:
    return puntaje + PUNTOS_ESQUIVAR


def formatear_puntaje(valor: int) -> str:
    return str(max(0, valor)).zfill(5)
