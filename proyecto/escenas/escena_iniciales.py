"""Escena de captura de iniciales para una o dos personas."""

from __future__ import annotations

import pygame

from configuracion import ANCHO, ALTO, CANTIDAD_INICIALES, COLORES, TAMANO_NORMAL, TAMANO_SUBTITULO, TAMANO_TITULO
from nucleo.ayudantes import ajustar_texto_centrado, cargar_fuente, dibujar_boton, dibujar_texto, dibujar_texto_ajustado


class EscenaIniciales:
    """Permite escribir hasta tres letras por jugador."""

    def __init__(self, entrada, modo: str, dificultad: str | None = None, cantidad_jugadores: int = 1) -> None:
        self.entrada = entrada
        self.modo = modo
        self.dificultad = dificultad or "medio"
        self.cantidad_jugadores = cantidad_jugadores
        self.fuente_titulo = cargar_fuente(TAMANO_TITULO)
        self.fuente_subtitulo = cargar_fuente(TAMANO_SUBTITULO)
        self.fuente_normal = cargar_fuente(TAMANO_NORMAL)
        self.iniciales = ["", ""]
        self.indice_actual = 0

    def manejar_escape(self):
        return "escena_menu"

    def _inicial_actual(self) -> str:
        return self.iniciales[self.indice_actual]

    def _establecer_inicial(self, texto: str) -> None:
        self.iniciales[self.indice_actual] = texto[:CANTIDAD_INICIALES].upper()

    def actualizar(self, dt: float):
        for evento in self.entrada.eventos:
            if evento.type != pygame.KEYDOWN:
                continue
            if evento.key == pygame.K_BACKSPACE:
                self._establecer_inicial(self._inicial_actual()[:-1])
            elif evento.key == pygame.K_RETURN:
                if len(self._inicial_actual()) == CANTIDAD_INICIALES:
                    if self.indice_actual + 1 < self.cantidad_jugadores:
                        self.indice_actual += 1
                    else:
                        datos = {"modo": self.modo, "dificultad": self.dificultad, "iniciales": self.iniciales[0]}
                        if self.cantidad_jugadores > 1:
                            datos["iniciales_j1"] = self.iniciales[0]
                            datos["iniciales_j2"] = self.iniciales[1]
                        iniciales_unidas = {self.iniciales[0].upper(), self.iniciales[1].upper()}
                        if self.modo == "vs_imposible":
                            datos["modo_vs"] = "imposible"
                        if self.modo.startswith("vs"):
                            if "SIM" in iniciales_unidas or "ELF" in iniciales_unidas:
                                datos["modo_vs"] = "imposible"
                            datos["invencible_j1"] = self.iniciales[0].upper() in {"SIM", "ELF"}
                            datos["invencible_j2"] = self.iniciales[1].upper() in {"SIM", "ELF"}
                        if self.modo == "campana":
                            return ("escena_campana", datos)
                        if self.modo == "vs_infinito":
                            return ("escena_vs", {"iniciales_j1": self.iniciales[0], "iniciales_j2": self.iniciales[1], "modo_vs": "infinito"})
                        if self.modo == "vs_imposible":
                            return ("escena_vs", {
                                "iniciales_j1": self.iniciales[0],
                                "iniciales_j2": self.iniciales[1],
                                "modo_vs": "imposible",
                                "invencible_j1": datos.get("invencible_j1", False),
                                "invencible_j2": datos.get("invencible_j2", False),
                            })
                        return ("escena_vs", datos)
            else:
                letra = evento.unicode.upper()
                if letra.isalpha() and len(self._inicial_actual()) < CANTIDAD_INICIALES:
                    self._establecer_inicial(self._inicial_actual() + letra)
        return None

    def renderizar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLORES["fondo"])
        dibujar_texto_ajustado(pantalla, "INGRESA TUS INICIALES", 24, COLORES["primario"], (ANCHO // 2, 50), ANCHO - 70)
        subtitulo = f"{self.indice_actual + 1}/{self.cantidad_jugadores} - 3 LETRAS"
        dibujar_texto_ajustado(pantalla, subtitulo, 14, COLORES["acento"], (ANCHO // 2, 86), ANCHO - 90)

        panel = pygame.Rect(ANCHO // 2 - 130, 160, 260, 120)
        pygame.draw.rect(pantalla, COLORES["fondo_panel"], panel)
        pygame.draw.rect(pantalla, COLORES["primario"], panel, 2)
        etiqueta = f"JUGADOR {self.indice_actual + 1}"
        dibujar_texto_ajustado(pantalla, etiqueta, 14, COLORES["neutro_claro"], (panel.centerx, panel.y + 22), 220)
        texto = self._inicial_actual() or "_ _ _"
        dibujar_texto_ajustado(pantalla, texto, 24, COLORES["blanco"], (panel.centerx, panel.y + 62), 220)
        dibujar_texto_ajustado(pantalla, "ENTER PARA CONTINUAR", 9, COLORES["neutro_medio"], (panel.centerx, panel.bottom - 16), 220)
        dibujar_texto_ajustado(pantalla, "ESC <- MENÚ", 9, COLORES["neutro_medio"], (ANCHO // 2, 318), 160)
