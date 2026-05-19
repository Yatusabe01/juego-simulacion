"""Selector para elegir VS clásico o VS infinito."""

from __future__ import annotations

import pygame

from configuracion import ANCHO, COLORES, TAMANO_SUBTITULO, TAMANO_TITULO
from nucleo.ayudantes import ajustar_texto_centrado, cargar_fuente, dibujar_boton


class EscenaSelectorVs:
    """Permite escoger entre VS por dificultad o VS infinito."""

    def __init__(self, entrada) -> None:
        self.entrada = entrada
        self.fuente_titulo = cargar_fuente(TAMANO_TITULO)
        self.fuente_subtitulo = cargar_fuente(TAMANO_SUBTITULO)
        self.seleccion = 0

    def manejar_escape(self):
        return "escena_menu"

    def actualizar(self, dt: float):
        if self.entrada.recien_presionada(pygame.K_LEFT):
            self.seleccion = max(0, self.seleccion - 1)
        if self.entrada.recien_presionada(pygame.K_RIGHT):
            self.seleccion = min(1, self.seleccion + 1)
        if self.entrada.recien_presionada(pygame.K_RETURN):
            if self.seleccion == 0:
                return ("escena_dificultad_vs", {})
            return ("escena_iniciales", {"modo": "vs_infinito", "cantidad_jugadores": 2})
        return None

    def renderizar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLORES["fondo"])
        ajustar_texto_centrado(pantalla, "MODO VS", self.fuente_titulo, COLORES["primario"], ANCHO // 2, 80)
        ajustar_texto_centrado(pantalla, "ELIGE TIPO DE PARTIDA", self.fuente_subtitulo, COLORES["neutro_claro"], ANCHO // 2, 120)

        boton_1 = pygame.Rect(ANCHO // 2 - 200, 220, 180, 56)
        boton_2 = pygame.Rect(ANCHO // 2 + 20, 220, 180, 56)
        dibujar_boton(pantalla, boton_1, "DIFICULTAD", cargar_fuente(10), self.seleccion == 0)
        dibujar_boton(pantalla, boton_2, "INFINITO", cargar_fuente(10), self.seleccion == 1)
