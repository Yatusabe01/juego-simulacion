"""Generador uniforme de meteoritos para campaña y VS."""

from __future__ import annotations

from configuracion import DIFICULTAD, DERIVA_Y_METEORITO_MAX, DERIVA_Y_METEORITO_MIN, RADIO_METEORITO_MAX, RADIO_METEORITO_MIN
from matematicas.probabilidad import entero_uniforme, muestra_uniforme


class GeneradorOleada:
    """Produce datos de spawn usando distribución uniforme."""

    def __init__(self, nivel: str, ancho: int, alto: int) -> None:
        self.nivel = nivel
        self.ancho = ancho
        self.alto = alto
        self.tiempo_acumulado = 0.0
        self.siguiente_spawn = self._nueva_espera()

    def _nueva_espera(self) -> float:
        base = DIFICULTAD[self.nivel]["intervalo_spawn"]
        return muestra_uniforme(base * 0.75, base * 1.25)

    def _nuevo_dato(self) -> dict[str, float | int]:
        radio = entero_uniforme(RADIO_METEORITO_MIN, RADIO_METEORITO_MAX)
        vel_x = muestra_uniforme(*DIFICULTAD[self.nivel]["vel_meteorito"])
        vel_y = muestra_uniforme(DERIVA_Y_METEORITO_MIN, DERIVA_Y_METEORITO_MAX)
        y_relativo = muestra_uniforme(0.0, 1.0)
        return {
            "radio": radio,
            "vel_x": vel_x,
            "vel_y": vel_y,
            "y_relativo": y_relativo,
            "hp": DIFICULTAD[self.nivel]["hp_max"],
        }

    def actualizar(self, dt: float) -> list[dict[str, float | int]]:
        """Devuelve una lista de datos de spawn cuando corresponde."""
        self.tiempo_acumulado += dt
        datos: list[dict[str, float | int]] = []
        while self.tiempo_acumulado >= self.siguiente_spawn:
            self.tiempo_acumulado -= self.siguiente_spawn
            datos.append(self._nuevo_dato())
            self.siguiente_spawn = self._nueva_espera()
        return datos
