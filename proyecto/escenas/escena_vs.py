"""Escena versus con dos mundos independientes sincronizados."""

from __future__ import annotations

import math

import pygame

from configuracion import ALTO, ALTO_VISTA_VS, ANCHO, ANCHO_DIVISORIA_VS, ALPHA_OVERLAY, COLORES, PUNTOS_EMPATE, TAMANO_MINI_NAVE, TAMANO_NORMAL, TAMANO_PEQUENO, TAMANO_SUBTITULO, TAMANO_TITULO, ANCHO_BOTON_OPCIONES, ALTO_BOTON_OPCIONES, MARGEN_GENERAL, ANCHO_MODAL_OPCIONES, ALTO_MODAL_OPCIONES, SLIDER_ANCHO, SLIDER_ALTO, TAMANO_MANGO_SLIDER, ANCHO_BOTON_MODAL, ALTO_BOTON_MODAL
from entidades.bala import Bala
from entidades.explosion import Explosion
from entidades.meteorito import Meteorito
from entidades.nave import Nave
from nucleo.ayudantes import ajustar_texto_centrado, cargar_fuente, crear_miniatura_nave, dibujar_boton_pequeno, dibujar_texto, dibujar_texto_ajustado
from nucleo.generador_oleada import GeneradorOleada
from nucleo.manejador_colisiones import hay_colision
from nucleo.manejador_puntaje import formatear_puntaje, sumar_por_destruccion, sumar_por_esquivar


class EscenaVs:
    """Muestra dos batallas paralelas con meteoritos sincronizados."""

    def __init__(self, entrada, iniciales_j1: str = "AAA", iniciales_j2: str = "BBB", modo_vs: str = "clasico") -> None:
        self.entrada = entrada
        self.iniciales_j1 = (iniciales_j1 or "AAA")[:3].upper()
        self.iniciales_j2 = (iniciales_j2 or "BBB")[:3].upper()
        self.modo_vs = modo_vs
        self.fuente_titulo = cargar_fuente(TAMANO_TITULO)
        self.fuente_subtitulo = cargar_fuente(TAMANO_SUBTITULO)
        self.fuente_normal = cargar_fuente(TAMANO_NORMAL)
        self.fuente_pequena = cargar_fuente(TAMANO_PEQUENO)
        self.nave_j1 = Nave(1, COLORES["primario"], 0, ALTO_VISTA_VS)
        self.nave_j2 = Nave(2, COLORES["secundario"], 0, ALTO_VISTA_VS)
        self.balas_j1: list[Bala] = []
        self.balas_j2: list[Bala] = []
        self.meteoritos_j1: list[Meteorito] = []
        self.meteoritos_j2: list[Meteorito] = []
        self.explosiones_j1: list[Explosion] = []
        self.explosiones_j2: list[Explosion] = []
        self.generador = GeneradorOleada("medio", ANCHO, ALTO_VISTA_VS)
        if self.modo_vs == "infinito":
            self.generador.siguiente_spawn = 0.30
        self.modo_pausa = False
        self.subestado_opciones = "normal"
        self.volumen = 100
        self.ignorar_escape_una_vez = False

    def manejar_escape(self):
        if self.modo_pausa and self.subestado_opciones == "confirmar":
            return ("escena_menu", {})
        self.modo_pausa = not self.modo_pausa
        self.subestado_opciones = "reanudar"
        self.ignorar_escape_una_vez = True
        return None

    def _crear_meteoritos_compartidos(self, datos: dict[str, float | int]) -> None:
        radio = int(datos["radio"])
        y_relativo = float(datos["y_relativo"])
        base_y = y_relativo * ALTO_VISTA_VS
        factor_velocidad = 1.4 if self.modo_vs == "infinito" else 1.0
        pos_x = ANCHO - radio
        velocidad = float(datos["vel_x"]) * factor_velocidad

        objetivo_x_j1, objetivo_y_j1 = self.nave_j1.rect.center
        dx_j1 = objetivo_x_j1 - pos_x
        dy_j1 = objetivo_y_j1 - base_y
        distancia_j1 = math.hypot(dx_j1, dy_j1)
        if distancia_j1 <= 0.0:
            vel_x_j1, vel_y_j1 = -velocidad, 0.0
        else:
            vel_x_j1 = (dx_j1 / distancia_j1) * velocidad
            vel_y_j1 = (dy_j1 / distancia_j1) * velocidad

        objetivo_x_j2, objetivo_y_j2 = self.nave_j2.rect.center
        dx_j2 = objetivo_x_j2 - pos_x
        dy_j2 = objetivo_y_j2 - base_y
        distancia_j2 = math.hypot(dx_j2, dy_j2)
        if distancia_j2 <= 0.0:
            vel_x_j2, vel_y_j2 = -velocidad, 0.0
        else:
            vel_x_j2 = (dx_j2 / distancia_j2) * velocidad
            vel_y_j2 = (dy_j2 / distancia_j2) * velocidad

        self.meteoritos_j1.append(Meteorito(pos_x, base_y, vel_x_j1, vel_y_j1, radio, int(datos["hp"])))
        self.meteoritos_j2.append(Meteorito(pos_x, base_y, vel_x_j2, vel_y_j2, radio, int(datos["hp"])))

    def _actualizar_mundo(self, nave: Nave, balas: list[Bala], meteoritos: list[Meteorito], explosiones: list[Explosion], dt: float, entrada) -> None:
        bala = nave.actualizar(dt, entrada)
        if bala is not None:
            balas.append(bala)

        for bala_activa in balas:
            bala_activa.actualizar(dt)
        for meteorito in meteoritos:
            meteorito.actualizar(dt)
        for explosion in explosiones:
            explosion.actualizar(dt)

    def _resolver_colisiones(self, nave: Nave, balas: list[Bala], meteoritos: list[Meteorito], explosiones: list[Explosion]) -> tuple[list[Bala], list[Meteorito], list[Explosion], bool]:
        nave_danio = False

        # Rastreamos qué meteoritos y balas participaron en una colisión
        meteoritos_golpeados: set[int] = set()
        balas_usadas: set[int] = set()

        for meteorito in meteoritos:
            for bala_activa in balas:
                if id(bala_activa) in balas_usadas:
                    continue
                if hay_colision(bala_activa.rect, meteorito.rect):
                    balas_usadas.add(id(bala_activa))
                    meteoritos_golpeados.add(id(meteorito))
                    if meteorito.recibir_impacto():
                        # Destruido: sumar puntos y crear explosión
                        nave.puntaje = sumar_por_destruccion(nave.puntaje)
                        explosiones.append(Explosion(meteorito.pos_x, meteorito.pos_y))
                    break  # una bala por meteorito por frame

        # Reconstruir lista de meteoritos
        meteoritos_restantes: list[Meteorito] = []
        for meteorito in meteoritos:
            fue_golpeado = id(meteorito) in meteoritos_golpeados
            if fue_golpeado and meteorito.hp <= 0:
                continue  # destruido, no agregar
            if fue_golpeado and meteorito.hp > 0:
                meteoritos_restantes.append(meteorito)  # dañado pero vivo
                continue
            if meteorito.esta_fuera_de_pantalla():
                # Salió sin ser golpeado: es un esquive
                nave.puntaje = sumar_por_esquivar(nave.puntaje)
            else:
                meteoritos_restantes.append(meteorito)

        # Balas que no impactaron nada y siguen en pantalla
        balas_restantes: list[Bala] = []
        for bala_activa in balas:
            if id(bala_activa) not in balas_usadas and not bala_activa.esta_fuera_de_pantalla():
                balas_restantes.append(bala_activa)

        # Colisión nave <-> meteorito
        for meteorito in list(meteoritos_restantes):
            if hay_colision(nave.rect, meteorito.rect) and not nave.es_invencible:
                nave.recibir_danio()
                explosiones.append(Explosion(meteorito.pos_x, meteorito.pos_y))
                meteoritos_restantes.remove(meteorito)
                nave_danio = True

        explosiones[:] = [explosion for explosion in explosiones if not explosion.termino()]
        return balas_restantes, meteoritos_restantes, explosiones, nave_danio

    def _actualizar_opciones(self):
        if self.ignorar_escape_una_vez:
            self.ignorar_escape_una_vez = False
            return None

        if self.subestado_opciones == "confirmar":
            if self.entrada.recien_presionada(pygame.K_ESCAPE) or self.entrada.recien_presionada(pygame.K_RETURN):
                return ("escena_menu", {})
            if self.entrada.recien_presionada(pygame.K_LEFT) or self.entrada.recien_presionada(pygame.K_RIGHT):
                self.subestado_opciones = "menu"
            return None

        if self.entrada.recien_presionada(pygame.K_ESCAPE):
            self.modo_pausa = False
            self.subestado_opciones = "normal"
            return None
        if self.entrada.recien_presionada(pygame.K_UP):
            self.subestado_opciones = "reanudar" if self.subestado_opciones == "menu" else "menu"
        if self.entrada.recien_presionada(pygame.K_DOWN):
            self.subestado_opciones = "menu" if self.subestado_opciones == "reanudar" else "reanudar"
        if self.entrada.esta_presionada(pygame.K_LEFT):
            self.volumen = max(0, self.volumen - 1)
        if self.entrada.esta_presionada(pygame.K_RIGHT):
            self.volumen = min(100, self.volumen + 1)
        if self.entrada.recien_presionada(pygame.K_RETURN):
            if self.subestado_opciones == "menu":
                self.subestado_opciones = "confirmar"
                return None
            self.modo_pausa = False
            self.subestado_opciones = "normal"
            return None
        if self.subestado_opciones == "confirmar" and self.entrada.recien_presionada(pygame.K_ESCAPE):
            return ("escena_menu", {})
        if pygame.mixer.get_init() is not None:
            pygame.mixer.music.set_volume(self.volumen / 100)
        return None

    def actualizar(self, dt: float):
        if self.modo_pausa:
            return self._actualizar_opciones()

        for dato in self.generador.actualizar(dt):
            self._crear_meteoritos_compartidos(dato)
        if self.modo_vs == "infinito":
            if self.generador.siguiente_spawn > 0.16:
                self.generador.siguiente_spawn = max(0.16, self.generador.siguiente_spawn * 0.995)

        self._actualizar_mundo(self.nave_j1, self.balas_j1, self.meteoritos_j1, self.explosiones_j1, dt, self.entrada)
        self._actualizar_mundo(self.nave_j2, self.balas_j2, self.meteoritos_j2, self.explosiones_j2, dt, self.entrada)

        self.balas_j1, self.meteoritos_j1, self.explosiones_j1, _ = self._resolver_colisiones(self.nave_j1, self.balas_j1, self.meteoritos_j1, self.explosiones_j1)
        self.balas_j2, self.meteoritos_j2, self.explosiones_j2, _ = self._resolver_colisiones(self.nave_j2, self.balas_j2, self.meteoritos_j2, self.explosiones_j2)

        if self.nave_j1.vidas <= 0 and self.nave_j2.vidas <= 0:
            return ("escena_fin_juego", {"resultado": "empate", "puntaje_j1": self.nave_j1.puntaje, "puntaje_j2": self.nave_j2.puntaje, "modo": "vs", "iniciales_j1": self.iniciales_j1, "iniciales_j2": self.iniciales_j2})
        if self.nave_j1.vidas <= 0:
            return ("escena_fin_juego", {"resultado": "victoria_j2", "puntaje_j1": self.nave_j1.puntaje, "puntaje_j2": self.nave_j2.puntaje, "modo": "vs", "iniciales_j1": self.iniciales_j1, "iniciales_j2": self.iniciales_j2})
        if self.nave_j2.vidas <= 0:
            return ("escena_fin_juego", {"resultado": "victoria_j1", "puntaje_j1": self.nave_j1.puntaje, "puntaje_j2": self.nave_j2.puntaje, "modo": "vs", "iniciales_j1": self.iniciales_j1, "iniciales_j2": self.iniciales_j2})

        if self.nave_j1.puntaje >= PUNTOS_EMPATE and self.nave_j2.puntaje >= PUNTOS_EMPATE:
            return ("escena_fin_juego", {"resultado": "empate", "puntaje_j1": self.nave_j1.puntaje, "puntaje_j2": self.nave_j2.puntaje, "modo": "vs", "iniciales_j1": self.iniciales_j1, "iniciales_j2": self.iniciales_j2})
        return None

    def _dibujar_mundo(self, vista: pygame.Surface, desplazamiento_y: int, nave: Nave, balas: list[Bala], meteoritos: list[Meteorito], explosiones: list[Explosion], etiqueta: str, color_nave: tuple[int, int, int]) -> None:
        vista.fill(COLORES["fondo"])
        for meteorito in meteoritos:
            meteorito.renderizar(vista)
        for bala in balas:
            bala.renderizar(vista)
        for explosion in explosiones:
            explosion.renderizar(vista)
        nave.renderizar(vista)
        dibujar_texto(vista, f"SCORE {formatear_puntaje(nave.puntaje)}", self.fuente_pequena, COLORES["blanco"], (MARGEN_GENERAL, MARGEN_GENERAL))
        mini = crear_miniatura_nave(color_nave)
        for indice in range(nave.vidas):
            vista.blit(mini, (MARGEN_GENERAL + indice * 24, vista.get_height() - 22))
        ajustar_texto_centrado(vista, etiqueta, self.fuente_pequena, COLORES["neutro_claro"], vista.get_width() // 2, 12)

    def renderizar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLORES["fondo"])
        vista_j1 = pantalla.subsurface(pygame.Rect(0, 0, ANCHO, ALTO_VISTA_VS))
        vista_j2 = pantalla.subsurface(pygame.Rect(0, ALTO_VISTA_VS, ANCHO, ALTO_VISTA_VS))
        self._dibujar_mundo(vista_j1, 0, self.nave_j1, self.balas_j1, self.meteoritos_j1, self.explosiones_j1, "JUGADOR 1", COLORES["primario"])
        self._dibujar_mundo(vista_j2, ALTO_VISTA_VS, self.nave_j2, self.balas_j2, self.meteoritos_j2, self.explosiones_j2, "JUGADOR 2", COLORES["secundario"])
        pygame.draw.rect(pantalla, COLORES["neutro_oscuro"], pygame.Rect(0, ALTO_VISTA_VS - 1, ANCHO, ANCHO_DIVISORIA_VS))
        panel_opciones = pygame.Rect(ANCHO - 180 - MARGEN_GENERAL, MARGEN_GENERAL, 180, ALTO_BOTON_OPCIONES)
        dibujar_boton_pequeno(pantalla, panel_opciones, "ESC OPCIONES", self.fuente_pequena, False)

        if self.modo_pausa:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((*COLORES["fondo_panel"], ALPHA_OVERLAY))
            pantalla.blit(overlay, (0, 0))
            rect_modal = pygame.Rect((ANCHO - ANCHO_MODAL_OPCIONES) // 2, (ALTO - ALTO_MODAL_OPCIONES) // 2, ANCHO_MODAL_OPCIONES, ALTO_MODAL_OPCIONES)
            pygame.draw.rect(pantalla, COLORES["fondo_panel"], rect_modal)
            pygame.draw.rect(pantalla, COLORES["primario"], rect_modal, 2)
            ajustar_texto_centrado(pantalla, "OPCIONES", self.fuente_subtitulo, COLORES["primario"], rect_modal.centerx, rect_modal.y + 26)
            dibujar_texto(pantalla, f"VOLUMEN {self.volumen}", self.fuente_pequena, COLORES["neutro_claro"], (rect_modal.x + 20, rect_modal.y + 102))
            barra = pygame.Rect(rect_modal.x + 82, rect_modal.y + 126, SLIDER_ANCHO, SLIDER_ALTO)
            pygame.draw.rect(pantalla, COLORES["neutro_oscuro"], barra)
            pygame.draw.rect(pantalla, COLORES["primario_medio"], pygame.Rect(barra.x, barra.y, int((self.volumen / 100) * SLIDER_ANCHO), SLIDER_ALTO))
            manga = pygame.Rect(barra.x + int((self.volumen / 100) * (SLIDER_ANCHO - TAMANO_MANGO_SLIDER)), barra.y - 4, TAMANO_MANGO_SLIDER, TAMANO_MANGO_SLIDER)
            pygame.draw.rect(pantalla, COLORES["acento"], manga)
            boton_reanudar = pygame.Rect(rect_modal.centerx - ANCHO_BOTON_MODAL - 8, rect_modal.bottom - 58, ANCHO_BOTON_MODAL, ALTO_BOTON_MODAL)
            boton_menu = pygame.Rect(rect_modal.centerx + 8, rect_modal.bottom - 58, ANCHO_BOTON_MODAL, ALTO_BOTON_MODAL)
            dibujar_boton_pequeno(pantalla, boton_reanudar, "REANUDAR", self.fuente_pequena, self.subestado_opciones == "reanudar")
            dibujar_boton_pequeno(pantalla, boton_menu, "ESC MENÚ", self.fuente_pequena, self.subestado_opciones == "menu")
            dibujar_texto_ajustado(pantalla, "IZQ/DER VOLUMEN | ESC CERRAR", 9, COLORES["neutro_medio"], (rect_modal.centerx, rect_modal.bottom - 16), 300)
