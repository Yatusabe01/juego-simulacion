"""Selector de dificultad para VS clásico."""

from __future__ import annotations

import pygame

from configuracion import ANCHO, COLORES, TAMANO_SUBTITULO, TAMANO_TITULO
from nucleo.ayudantes import ajustar_texto_centrado, cargar_fuente, dibujar_boton


class EscenaDificultadVs:
    """Permite elegir dificultad en VS clásico."""

    def __init__(self, entrada) -> None:
        self.entrada = entrada
        self.fuente_titulo = cargar_fuente(TAMANO_TITULO)
        self.fuente_subtitulo = cargar_fuente(TAMANO_SUBTITULO)
        self.opciones = ["facil", "medio", "dificil"]
        self.seleccion = 1

    def manejar_escape(self):
        return "escena_selector_vs"

    def actualizar(self, dt: float):
        if self.entrada.recien_presionada(pygame.K_LEFT):
            self.seleccion = max(0, self.seleccion - 1)
        if self.entrada.recien_presionada(pygame.K_RIGHT):
            self.seleccion = min(2, self.seleccion + 1)
        if self.entrada.recien_presionada(pygame.K_RETURN):
            return ("escena_iniciales", {"modo": "vs", "dificultad": self.opciones[self.seleccion], "cantidad_jugadores": 2})
        return None

    def renderizar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLORES["fondo"])
        ajustar_texto_centrado(pantalla, "VS - DIFICULTAD", self.fuente_titulo, COLORES["primario"], ANCHO // 2, 80)
        base_y = 220
        separacion = 220
        for indice, nombre in enumerate(self.opciones):
            rect = pygame.Rect(ANCHO // 2 - 90 + (indice - 1) * separacion, base_y, 180, 56)
            dibujar_boton(pantalla, rect, nombre.upper(), self.fuente_subtitulo, self.seleccion == indice)
