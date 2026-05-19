"""Animación de explosión por partículas en cuatro etapas."""

from __future__ import annotations

import math

import pygame

from configuracion import COLORES, FRAMES_EXPLOSION, RADIO_PARTICULA_EXPLOSION, TAMANO_EXPLOSION, TIEMPO_FRAME_EXPLOSION


class Explosion:
    """Explosión breve con partículas preconfiguradas por frame."""

    def __init__(self, pos_x: float, pos_y: float) -> None:
        self.pos_x = float(pos_x)
        self.pos_y = float(pos_y)
        self.tiempo = 0.0
        self.frames = self._crear_frames()

    def _crear_frame(self, direcciones: list[tuple[int, int]], radio: int, color: tuple[int, int, int]) -> pygame.Surface:
        superficie = pygame.Surface((TAMANO_EXPLOSION, TAMANO_EXPLOSION), pygame.SRCALPHA)
        centro = TAMANO_EXPLOSION // 2
        for indice, (dx, dy) in enumerate(direcciones):
            distancia = radio if len(direcciones) < 8 else radio - (indice % 3)
            x = centro + dx * distancia
            y = centro + dy * distancia
            pygame.draw.circle(superficie, color, (int(x), int(y)), RADIO_PARTICULA_EXPLOSION)
        return superficie

    def _crear_frames(self) -> list[pygame.Surface]:
        return [
            self._crear_frame([(1, 0), (-1, 0), (0, 1), (0, -1)], 6, COLORES["acento"]),
            self._crear_frame([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)], 12, COLORES["acento"]),
            self._crear_frame([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)], 18, COLORES["secundario"]),
            self._crear_frame([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)], 24, COLORES["peligro"]),
        ]

    def actualizar(self, dt: float) -> None:
        self.tiempo += dt

    def renderizar(self, pantalla: pygame.Surface, desplazamiento_y: int = 0) -> None:
        indice = min(int(self.tiempo / TIEMPO_FRAME_EXPLOSION), FRAMES_EXPLOSION - 1)
        rect = self.frames[indice].get_rect(center=(int(self.pos_x), int(self.pos_y + desplazamiento_y)))
        pantalla.blit(self.frames[indice], rect)

    def termino(self) -> bool:
        return self.tiempo >= FRAMES_EXPLOSION * TIEMPO_FRAME_EXPLOSION
