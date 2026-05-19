"""Escena con controles, descripcion e historial de puntajes."""

from __future__ import annotations

import pygame

from configuracion import ANCHO, ALTO, COLORES, TAMANO_NORMAL, TAMANO_PEQUENO, TAMANO_SUBTITULO, TAMANO_TITULO
from nucleo.ayudantes import ajustar_texto_centrado, cargar_fuente, dibujar_boton, dibujar_texto, dibujar_texto_ajustado
from nucleo.historial_puntajes import cargar_historial


class EscenaInformacion:
    """Muestra controles, reglas rapidas e historial."""

    def __init__(self, entrada) -> None:
        self.entrada = entrada
        self.fuente_titulo = cargar_fuente(TAMANO_TITULO)
        self.fuente_subtitulo = cargar_fuente(TAMANO_SUBTITULO)
        self.fuente_normal = cargar_fuente(TAMANO_NORMAL)
        self.fuente_pequena = cargar_fuente(TAMANO_PEQUENO)
        self.historial = cargar_historial()

    def manejar_escape(self):
        return "escena_menu"

    def actualizar(self, dt: float):
        if self.entrada.recien_presionada(pygame.K_RETURN) or self.entrada.recien_presionada(pygame.K_ESCAPE):
            return "escena_menu"
        return None

    def renderizar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLORES["fondo"])

        # 1. Títulos
        dibujar_texto_ajustado(pantalla, "INFORMACION", 24, COLORES["primario"], (ANCHO // 2, 40), ANCHO - 80)
        dibujar_texto_ajustado(pantalla, "CONTROLES Y HISTORIAL", 12, COLORES["neutro_claro"], (ANCHO // 2, 70), ANCHO - 80)

        # 2. Panel historial
        dibujar_texto_ajustado(pantalla, "HISTORIAL", 14, COLORES["acento"], (648, 100), 220, alineado_centro=True)
        panel = pygame.Rect(490, 120, 330, 240)
        pygame.draw.rect(pantalla, COLORES["fondo_panel"], panel)
        pygame.draw.rect(pantalla, COLORES["primario"], panel, 2)
        if not self.historial:
            ajustar_texto_centrado(pantalla, "SIN PARTIDAS", self.fuente_pequena, COLORES["neutro_medio"], panel.centerx, panel.centery)
        else:
            for indice, registro in enumerate(self.historial[:6]):
                categoria = str(registro.get("categoria", registro.get("modo", "campana")))
                texto = f"{str(registro.get('iniciales', 'AAA')):>3} {categoria[:7]:<7} {int(registro.get('puntaje', 0)):05d}"
                dibujar_texto_ajustado(pantalla, texto, 9, COLORES["blanco"], (504, 138 + indice * 34), 300, alineado_centro=False)

        # 3. Controles
        dibujar_texto_ajustado(pantalla, "CONTROLES", 14, COLORES["acento"], (52, 104), 440, alineado_centro=False)
        lineas = [
            "J1: W/S/A/D mover | ESPACIO disparar",
            "J2: FLECHAS mover | . disparar",
            "ESC: abrir opciones",
            "F11: pantalla completa",
        ]
        for indice, linea in enumerate(lineas):
            dibujar_texto_ajustado(pantalla, linea, 11, COLORES["blanco"], (52, 130 + indice * 26), 420, alineado_centro=False)

        # 4. Objetivo
        dibujar_texto_ajustado(pantalla, "OBJETIVO", 14, COLORES["acento"], (52, 242), 420, alineado_centro=False)
        texto_objetivo = [
            "Destruye meteoritos: +10 pts",
            "Esquiva sin impacto: +5 pts",
            "Cada nivel dura 60 segundos.",
            "Iniciales: 3 primeras letras.",
        ]
        for indice, linea in enumerate(texto_objetivo):
            dibujar_texto_ajustado(pantalla, linea, 9, COLORES["neutro_claro"], (52, 266 + indice * 20), 420, alineado_centro=False)

        # 5. Pie de página
        dibujar_texto_ajustado(pantalla, "ESC <- VOLVER", 10, COLORES["neutro_medio"], (ANCHO // 2, 438), 180)
