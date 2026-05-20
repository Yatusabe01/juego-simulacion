"""Escena final con resultado, puntaje y opciones de salida."""

from __future__ import annotations

import pygame

from configuracion import ALTO, ANCHO, COLORES, TAMANO_NORMAL, TAMANO_SUBTITULO, TAMANO_TITULO
from nucleo.historial_puntajes import agregar_registro
from nucleo.ayudantes import ajustar_texto_centrado, cargar_fuente, dibujar_boton


class EscenaFinJuego:
    """Resume la partida y permite reintentar o volver al menú."""

    def __init__(self, entrada, resultado: str, puntaje: int | None = None, puntaje_j1: int | None = None, puntaje_j2: int | None = None, modo: str = "campana", dificultad: str = "medio", iniciales: str = "AAA", iniciales_j1: str = "AAA", iniciales_j2: str = "BBB") -> None:
        self.entrada = entrada
        self.resultado = resultado
        self.puntaje = puntaje
        self.puntaje_j1 = puntaje_j1
        self.puntaje_j2 = puntaje_j2
        self.modo = modo
        self.dificultad = dificultad
        self.iniciales = (iniciales or "AAA")[:3].upper()
        self.iniciales_j1 = (iniciales_j1 or "AAA")[:3].upper()
        self.iniciales_j2 = (iniciales_j2 or "BBB")[:3].upper()
        self.fuente_titulo = cargar_fuente(TAMANO_TITULO)
        self.fuente_subtitulo = cargar_fuente(TAMANO_SUBTITULO)
        self.fuente_normal = cargar_fuente(TAMANO_NORMAL)
        self.seleccion = 0
        if self.modo == "campana" and self.puntaje is not None:
            agregar_registro(self.iniciales[:3], self.modo, self.resultado, self.puntaje, categoria="campana")
        elif self.modo == "vs":
            puntaje_j1 = self.puntaje_j1 or 0
            puntaje_j2 = self.puntaje_j2 or 0
            agregar_registro(self.iniciales_j1[:3], self.modo, self.resultado, puntaje_j1, categoria="vs")
            if self.iniciales_j2 != self.iniciales_j1 or puntaje_j2 != puntaje_j1:
                agregar_registro(self.iniciales_j2[:3], self.modo, self.resultado, puntaje_j2, categoria="vs")

    def manejar_escape(self):
        return "escena_menu"

    def actualizar(self, dt: float):
        if self.entrada.recien_presionada(pygame.K_LEFT):
            self.seleccion = max(0, self.seleccion - 1)
        if self.entrada.recien_presionada(pygame.K_RIGHT):
            self.seleccion = min(1, self.seleccion + 1)
        if self.entrada.recien_presionada(pygame.K_RETURN):
            if self.seleccion == 0:
                if self.modo == "campana":
                    dificultad_segura = self.dificultad if self.dificultad in ["facil", "medio", "dificil"] else "facil"
                    return ("escena_iniciales", {"modo": "campana", "dificultad": dificultad_segura, "cantidad_jugadores": 1})
                return ("escena_iniciales", {"modo": "vs", "cantidad_jugadores": 2})
            return ("escena_menu", {})
        return None

    def renderizar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLORES["fondo"])
        if self.resultado == "victoria":
            titulo = "VICTORIA"
            color = COLORES["primario"]
        elif self.resultado == "derrota":
            titulo = "DERROTA"
            color = COLORES["peligro"]
        elif self.resultado == "empate":
            titulo = "EMPATE"
            color = COLORES["acento"]
        elif self.resultado == "victoria_j1":
            titulo = "GANA JUGADOR 1"
            color = COLORES["primario"]
        else:
            titulo = "GANA JUGADOR 2"
            color = COLORES["secundario"]

        ajustar_texto_centrado(pantalla, titulo, self.fuente_titulo, color, ANCHO // 2, 112)
        if self.modo == "campana":
            ajustar_texto_centrado(pantalla, f"PUNTAJE {self.puntaje or 0}", self.fuente_subtitulo, COLORES["blanco"], ANCHO // 2, 170)
        else:
            ajustar_texto_centrado(pantalla, f"PUNTAJE J1 {self.puntaje_j1 or 0}", self.fuente_subtitulo, COLORES["primario"], ANCHO // 2, 164)
            ajustar_texto_centrado(pantalla, f"PUNTAJE J2 {self.puntaje_j2 or 0}", self.fuente_subtitulo, COLORES["secundario"], ANCHO // 2, 194)

        dibujar_texto_centrado = ajustar_texto_centrado
        dibujar_texto_centrado(pantalla, "ESC <- MENÚ", self.fuente_normal, COLORES["neutro_medio"], ANCHO // 2, 248)
        boton_reintentar = pygame.Rect(ANCHO // 2 - 182, 300, 170, 48)
        boton_menu = pygame.Rect(ANCHO // 2 + 12, 300, 170, 48)
        dibujar_boton(pantalla, boton_reintentar, "REINTENTAR", self.fuente_normal, self.seleccion == 0)
        dibujar_boton(pantalla, boton_menu, "MENÚ", self.fuente_normal, self.seleccion == 1)
