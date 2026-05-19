"""Meteorito irregular con vida, deriva y parpadeo de impacto."""

from __future__ import annotations

import math

import pygame

from configuracion import (
    ALTO,
    ANCHO,
    COLORES,
    FLASH_METEORITO,
    RADIO_METEORITO_MAX,
    RADIO_METEORITO_MIN,
    DERIVA_Y_METEORITO_MAX,
    DERIVA_Y_METEORITO_MIN,
    VERTICES_METEORITO_MAX,
    VERTICES_METEORITO_MIN,
    VARIACION_RADIO_VERTICE_MAX,
    VARIACION_RADIO_VERTICE_MIN,
)
from matematicas.probabilidad import entero_uniforme, muestra_uniforme


class Meteorito:
    """Roca espacial que cruza la pantalla hacia la izquierda."""

    def __init__(self, pos_x: float, pos_y: float, vel_x: float, vel_y: float, radio: int, hp: int) -> None:
        self.pos_x = float(pos_x)
        self.pos_y = float(pos_y)
        self.vel_x = float(vel_x)
        self.vel_y = float(vel_y)
        self.radio = int(radio)
        self.hp_maxima = int(hp)
        self.hp = int(hp)
        self.tiempo_flash = 0.0
        self.vertices = self._crear_vertices()
        self.rect = self._crear_rectangulo()

    def _crear_vertices(self) -> list[tuple[float, float]]:
        cantidad = entero_uniforme(VERTICES_METEORITO_MIN, VERTICES_METEORITO_MAX)
        vertices: list[tuple[float, float]] = []
        paso = (2 * math.pi) / cantidad
        for indice in range(cantidad):
            angulo = indice * paso + muestra_uniforme(-paso * 0.3, paso * 0.3)
            escala = muestra_uniforme(VARIACION_RADIO_VERTICE_MIN, VARIACION_RADIO_VERTICE_MAX)
            radio_local = self.radio * escala
            x = math.cos(angulo) * radio_local
            y = math.sin(angulo) * radio_local
            vertices.append((x, y))
        return vertices

    def _crear_rectangulo(self) -> pygame.Rect:
        puntos_x = [self.pos_x + x for x, _ in self.vertices]
        puntos_y = [self.pos_y + y for _, y in self.vertices]
        x_min = int(min(puntos_x))
        y_min = int(min(puntos_y))
        x_max = int(max(puntos_x))
        y_max = int(max(puntos_y))
        return pygame.Rect(x_min, y_min, max(1, x_max - x_min), max(1, y_max - y_min))

    def _color_actual(self) -> tuple[int, int, int]:
        if self.tiempo_flash > 0.0:
            return COLORES["blanco"]
        if self.hp >= self.hp_maxima:
            return COLORES["neutro_medio"]
        if self.hp == 1:
            return COLORES["peligro"]
        return COLORES["secundario_medio"]

    def actualizar(self, dt: float) -> None:
        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt
        self.tiempo_flash = max(0.0, self.tiempo_flash - dt)
        self.rect = self._crear_rectangulo()

    def renderizar(self, pantalla: pygame.Surface, desplazamiento_y: int = 0) -> None:
        color = self._color_actual()
        puntos = [(self.pos_x + x, self.pos_y + y + desplazamiento_y) for x, y in self.vertices]
        pygame.draw.polygon(pantalla, color, puntos)
        pygame.draw.polygon(pantalla, COLORES["neutro_oscuro"], puntos, 2)

    def recibir_impacto(self) -> bool:
        self.hp -= 1
        self.tiempo_flash = FLASH_METEORITO
        return self.hp <= 0

    def esta_fuera_de_pantalla(self) -> bool:
        return self.rect.right < 0 or self.rect.top > ALTO or self.rect.bottom < 0 or self.rect.left > ANCHO
