"""Bala horizontal que viaja hacia la derecha."""

from __future__ import annotations

import pygame

from configuracion import ANCHO, COLORES, TAMANO_BALA, VELOCIDAD_BALA


class Bala:
    """Proyectil simple disparado por una nave."""

    def __init__(self, pos_x: float, pos_y: float, color: tuple[int, int, int]) -> None:
        self.pos_x = float(pos_x)
        self.pos_y = float(pos_y)
        self.color = color
        self.rect = pygame.Rect(int(self.pos_x), int(self.pos_y), TAMANO_BALA[0], TAMANO_BALA[1])

    def actualizar(self, dt: float) -> None:
        self.pos_x += VELOCIDAD_BALA * dt
        self.rect.x = int(self.pos_x)

    def renderizar(self, pantalla: pygame.Surface, desplazamiento_y: int = 0) -> None:
        rect = self.rect.move(0, desplazamiento_y)
        pygame.draw.rect(pantalla, self.color, rect)
        punta = pygame.Rect(rect.right - 2, rect.top, 2, rect.height)
        pygame.draw.rect(pantalla, COLORES["blanco"], punta)

    def esta_fuera_de_pantalla(self) -> bool:
        return self.rect.left > ANCHO
