"""Nave del jugador con movimiento, disparo e invencibilidad."""

from __future__ import annotations

import pygame

from configuracion import (
    ALTO,
    ANCHO,
    COLORES,
    MARGEN_NAVE,
    PORCENTAJE_LIMITE_NAVE_X,
    TAMANO_MINI_NAVE,
    TAMANO_NAVE,
    TIEMPO_INVENCIBLE,
    VELOCIDAD_NAVE,
)
from entidades.bala import Bala
from nucleo.ayudantes import aplicar_tinte, cargar_sprite_nave, reproducir_sonido


class Nave:
    """Controla posición, vida, disparos e invulnerabilidad temporal."""

    def __init__(self, jugador: int, color: tuple[int, int, int], limite_superior: int, limite_inferior: int, ancho_ventana: int = ANCHO) -> None:
        self.jugador = jugador
        self.color = color
        self.ancho_ventana = ancho_ventana
        self.limite_superior = limite_superior
        self.limite_inferior = limite_inferior
        self.velocidad = VELOCIDAD_NAVE
        self.vidas = 3
        self.puntaje = 0
        self.ultimo_disparo = 0.0
        self.es_invencible = False
        self.tiempo_invencible = 0.0
        self.esta_activa = True
        self.pos_x = float(MARGEN_NAVE)
        self.pos_y = float((limite_superior + limite_inferior - TAMANO_NAVE[1]) / 2)
        self.base = pygame.transform.smoothscale(cargar_sprite_nave(), TAMANO_NAVE)
        self.imagen = aplicar_tinte(self.base, color)
        self.imagen_mini = pygame.transform.smoothscale(self.imagen, TAMANO_MINI_NAVE)
        self.rect = pygame.Rect(int(self.pos_x + 8), int(self.pos_y + 6), 48, 20)

    def _actualizar_rectangulo(self) -> None:
        self.rect.x = int(self.pos_x + 8)
        self.rect.y = int(self.pos_y + 6)

    def actualizar(self, dt: float, entrada) -> Bala | None:
        if not self.esta_activa:
            return None

        movimiento_x = 0.0
        movimiento_y = 0.0

        if self.jugador == 1:
            if entrada.esta_presionada(pygame.K_a):
                movimiento_x -= 1
            if entrada.esta_presionada(pygame.K_d):
                movimiento_x += 1
            if entrada.esta_presionada(pygame.K_w):
                movimiento_y -= 1
            if entrada.esta_presionada(pygame.K_s):
                movimiento_y += 1
        else:
            if entrada.esta_presionada(pygame.K_LEFT):
                movimiento_x -= 1
            if entrada.esta_presionada(pygame.K_RIGHT):
                movimiento_x += 1
            if entrada.esta_presionada(pygame.K_UP):
                movimiento_y -= 1
            if entrada.esta_presionada(pygame.K_DOWN):
                movimiento_y += 1

        self.pos_x += movimiento_x * self.velocidad * dt
        self.pos_y += movimiento_y * self.velocidad * dt

        limite_x = self.ancho_ventana * PORCENTAJE_LIMITE_NAVE_X
        self.pos_x = max(MARGEN_NAVE, min(self.pos_x, limite_x - TAMANO_NAVE[0] - MARGEN_NAVE))
        self.pos_y = max(self.limite_superior, min(self.pos_y, self.limite_inferior - TAMANO_NAVE[1]))

        self.ultimo_disparo = max(0.0, self.ultimo_disparo - dt)
        if self.es_invencible:
            self.tiempo_invencible = max(0.0, self.tiempo_invencible - dt)
            if self.tiempo_invencible <= 0:
                self.es_invencible = False

        self._actualizar_rectangulo()

        tecla_disparo = pygame.K_SPACE if self.jugador == 1 else pygame.K_PERIOD
        if entrada.recien_presionada(tecla_disparo):
            return self.disparar()
        return None

    def renderizar(self, pantalla: pygame.Surface, desplazamiento_y: int = 0) -> None:
        visible = True
        if self.es_invencible:
            visible = int(self.tiempo_invencible / 0.1) % 2 == 0
        if visible:
            pantalla.blit(self.imagen, (int(self.pos_x), int(self.pos_y + desplazamiento_y)))

    def disparar(self) -> Bala | None:
        if self.ultimo_disparo > 0 or not self.esta_activa:
            return None
        self.ultimo_disparo = 0.4 if self.jugador == 1 else 0.35
        reproducir_sonido("sonido_bala")
        salida_x = self.pos_x + TAMANO_NAVE[0] - 2
        salida_y = self.pos_y + TAMANO_NAVE[1] / 2 - 2
        return Bala(salida_x, salida_y, self.color)

    def recibir_danio(self) -> None:
        if self.es_invencible or not self.esta_activa:
            return
        self.vidas -= 1
        self.es_invencible = True
        self.tiempo_invencible = TIEMPO_INVENCIBLE
        if self.vidas <= 0:
            self.esta_activa = False

    def esta_fuera_de_pantalla(self) -> bool:
        return self.rect.right < 0 or self.rect.left > self.ancho_ventana or self.rect.bottom < self.limite_superior or self.rect.top > self.limite_inferior
