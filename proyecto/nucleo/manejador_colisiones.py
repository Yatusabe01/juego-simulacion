"""Funciones puras de colisión basadas en rectángulos."""

from __future__ import annotations

import pygame


def hay_colision(rectangulo_a: pygame.Rect, rectangulo_b: pygame.Rect) -> bool:
    """Indica si dos rectángulos se cruzan."""
    return rectangulo_a.colliderect(rectangulo_b)
