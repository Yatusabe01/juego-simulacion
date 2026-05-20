"""Escena principal con título, estrellas y selección de modo."""

from __future__ import annotations

import pygame

from configuracion import ANCHO, ALTO, COLORES, PARPADEO_TITULO, TAMANO_BOTON_MENU, TAMANO_TITULO, TAMANO_SUBTITULO, MARGEN_GENERAL
from nucleo.ayudantes import ajustar_texto_centrado, cargar_fuente, dibujar_boton, dibujar_estrellas, dibujar_texto_ajustado, reproducir_musica, crear_estrellas, actualizar_estrellas


class EscenaMenu:
    """Menú principal con dos opciones y fondo animado."""

    def __init__(self, entrada) -> None:
        self.entrada = entrada
        self.fuente_titulo = cargar_fuente(TAMANO_TITULO)
        self.fuente_subtitulo = cargar_fuente(TAMANO_SUBTITULO)
        self.seleccion = 0
        self.tiempo_parpadeo = 0.0
        self.estrellas = crear_estrellas()
        reproducir_musica("musica_menu", 0.55)

    def manejar_escape(self):
        return "salir"

    def actualizar(self, dt: float):
        self.tiempo_parpadeo += dt
        actualizar_estrellas(self.estrellas, dt)

        if self.entrada.recien_presionada(pygame.K_LEFT):
            self.seleccion = max(0, self.seleccion - 1)
        if self.entrada.recien_presionada(pygame.K_RIGHT):
            self.seleccion = min(2, self.seleccion + 1)
        if self.entrada.recien_presionada(pygame.K_RETURN):
            if self.seleccion == 0:
                return ("escena_dificultad", {})
            if self.seleccion == 1:
                return ("escena_selector_vs", {})
            return ("escena_informacion", {})
        return None

    def renderizar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLORES["fondo"])
        dibujar_estrellas(pantalla, self.estrellas)

        sombra_x = 2
        sombra_y = 2
        dibujar_texto_ajustado(pantalla, "METEOR", 34, COLORES["primario_oscuro"], (ANCHO // 2 + sombra_x, 118 + sombra_y), ANCHO - 60)
        dibujar_texto_ajustado(pantalla, "METEOR", 34, COLORES["primario"], (ANCHO // 2, 118), ANCHO - 60)
        dibujar_texto_ajustado(pantalla, "STRIKE", 34, COLORES["primario_oscuro"], (ANCHO // 2 + sombra_x, 164 + sombra_y), ANCHO - 60)
        dibujar_texto_ajustado(pantalla, "STRIKE", 34, COLORES["primario"], (ANCHO // 2, 164), ANCHO - 60)

        if int(self.tiempo_parpadeo * 1000 / PARPADEO_TITULO) % 2 == 0:
            dibujar_texto_ajustado(pantalla, "PRESIONA ENTER", 16, COLORES["acento"], (ANCHO // 2, 228), ANCHO - 80)

        boton_y = 304
        ancho_boton = TAMANO_BOTON_MENU
        alto_boton = 54
        separacion = 22
        total = ancho_boton * 3 + separacion * 2
        inicio_x = (ANCHO - total) // 2
        boton_cam = pygame.Rect(inicio_x, boton_y, ancho_boton, alto_boton)
        boton_vs = pygame.Rect(inicio_x + ancho_boton + separacion, boton_y, ancho_boton, alto_boton)
        boton_info = pygame.Rect(inicio_x + (ancho_boton + separacion) * 2, boton_y, ancho_boton, alto_boton)
        dibujar_boton(pantalla, boton_cam, "CAMPAÑA", self.fuente_subtitulo, self.seleccion == 0)
        dibujar_boton(pantalla, boton_vs, "VS", self.fuente_subtitulo, self.seleccion == 1)
        dibujar_boton(pantalla, boton_info, "INFO", self.fuente_subtitulo, self.seleccion == 2)
