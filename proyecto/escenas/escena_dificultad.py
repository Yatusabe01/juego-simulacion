"""Escena de selección de dificultad para la campaña."""

from __future__ import annotations

import pygame

from configuracion import ANCHO, ALTO, COLORES, TAMANO_SUBTITULO, TAMANO_TITULO
from nucleo.ayudantes import ajustar_texto_centrado, cargar_fuente, dibujar_boton, dibujar_texto_ajustado


class EscenaDificultad:
    """Permite elegir entre fácil, medio y difícil."""

    def __init__(self, entrada) -> None:
        self.entrada = entrada
        self.fuente_titulo = cargar_fuente(TAMANO_TITULO)
        self.fuente_subtitulo = cargar_fuente(TAMANO_SUBTITULO)
        self.opciones = ["facil", "medio", "dificil"]
        self.seleccion = 1

    def manejar_escape(self):
        return "escena_menu"

    def actualizar(self, dt: float):
        if self.entrada.recien_presionada(pygame.K_LEFT):
            self.seleccion = max(0, self.seleccion - 1)
        if self.entrada.recien_presionada(pygame.K_RIGHT):
            self.seleccion = min(len(self.opciones) - 1, self.seleccion + 1)
        if self.entrada.recien_presionada(pygame.K_RETURN):
            return ("escena_iniciales", {"modo": "campana", "dificultad": self.opciones[self.seleccion], "cantidad_jugadores": 1})
        return None

    def renderizar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLORES["fondo"])
        dibujar_texto_ajustado(pantalla, "ELIGE DIFICULTAD", 24, COLORES["primario"], (ANCHO // 2, 58), ANCHO - 60)

        base_y = 170
        separacion = 220
        for indice, nombre in enumerate(self.opciones):
            rect = pygame.Rect(ANCHO // 2 - 90 + (indice - 1) * separacion, base_y, 180, 56)
            dibujar_boton(pantalla, rect, nombre.upper(), self.fuente_subtitulo, self.seleccion == indice)
            if nombre == "facil":
                descripcion = "Lentos, 1 disparo"
            elif nombre == "medio":
                descripcion = "Media, 2 disparos"
            else:
                descripcion = "Rapidos, 3 disparos"
            dibujar_texto_ajustado(pantalla, descripcion, 10, COLORES["neutro_claro"], (rect.centerx, rect.bottom + 22), 180)

        dibujar_texto_ajustado(pantalla, "ESC <- MENÚ", 10, COLORES["neutro_medio"], (ANCHO // 2, 430), 160)
