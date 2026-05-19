"""Manejador de teclado y estados recientes de entrada."""

from __future__ import annotations

import pygame


class ManejadorEntrada:
    """Registra teclas presionadas y teclas recién pulsadas."""

    def __init__(self) -> None:
        self.teclas_actuales: set[int] = set()
        self.teclas_previas: set[int] = set()
        self.eventos: list[pygame.event.Event] = []
        self.raton_posicion = (0, 0)
        self.raton_click_reciente = False

    def actualizar(self, eventos: list[pygame.event.Event]) -> None:
        self.teclas_previas = self.teclas_actuales.copy()
        self.eventos = eventos
        self.raton_click_reciente = False

        for evento in eventos:
            if evento.type == pygame.KEYDOWN:
                self.teclas_actuales.add(evento.key)
            elif evento.type == pygame.KEYUP:
                self.teclas_actuales.discard(evento.key)
            elif evento.type == pygame.MOUSEMOTION:
                self.raton_posicion = evento.pos
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                self.raton_posicion = evento.pos
                self.raton_click_reciente = True

    def esta_presionada(self, tecla: int) -> bool:
        return tecla in self.teclas_actuales

    def recien_presionada(self, tecla: int) -> bool:
        return tecla in self.teclas_actuales and tecla not in self.teclas_previas
