
from __future__ import annotations

import math

import pygame

from configuracion import ALTO, ANCHO, COLORES, ESTRELLAS_POR_CAPA, PUNTOS_DESTRUIR, PUNTOS_ESQUIVAR, TAMANO_SUBTITULO, TAMANO_NORMAL, TAMANO_PEQUENO, TAMANO_TITULO, ANCHO_BOTON_OPCIONES, ALTO_BOTON_OPCIONES, MARGEN_GENERAL, ANCHO_MODAL_OPCIONES, ALTO_MODAL_OPCIONES, ALPHA_OVERLAY, SLIDER_ANCHO, SLIDER_ALTO, TAMANO_MANGO_SLIDER, ANCHO_BOTON_MODAL, ALTO_BOTON_MODAL, VELOCIDAD_ESTRELLAS
from entidades.bala import Bala
from entidades.explosion import Explosion
from entidades.meteorito import Meteorito
from entidades.nave import Nave
from matematicas.probabilidad import entero_uniforme, muestra_uniforme
from nucleo.ayudantes import ajustar_texto_centrado, cargar_fuente, crear_miniatura_nave, dibujar_boton_pequeno, dibujar_texto, dibujar_texto_ajustado, detener_musica, reproducir_musica, reproducir_sonido
from nucleo.generador_oleada import GeneradorOleada
from nucleo.manejador_colisiones import hay_colision
from nucleo.manejador_puntaje import formatear_puntaje, sumar_por_destruccion, sumar_por_esquivar


class EscenaCampana:
    """Controla la campaña, niveles, HUD y opciones."""

    def __init__(self, entrada, dificultad: str = "medio", iniciales: str = "AAA") -> None:
        self.entrada = entrada
        self.niveles = ["facil", "medio", "dificil"]
        self.indice_nivel = self.niveles.index(dificultad) if dificultad in self.niveles else 0
        self.iniciales = (iniciales or "AAA")[:3].upper()
        self.fuente_titulo = cargar_fuente(TAMANO_TITULO)
        self.fuente_subtitulo = cargar_fuente(TAMANO_SUBTITULO)
        self.fuente_normal = cargar_fuente(TAMANO_NORMAL)
        self.fuente_pequena = cargar_fuente(TAMANO_PEQUENO)
        self.resultado_final = None
        self._inicializar_nivel()
        self.modo_pausa = False
        self.estado_transicion = None
        self.tiempo_transicion = 0.0
        self.duracion_transicion = 0.0
        self.mensaje_transicion = ""
        self.canal_victoria = None
        self.subestado_opciones = "normal"
        self.volumen = 100
        self.ignorar_escape_una_vez = False
        self.modo_accion = "destruir"
        self.enemigos_procesados = 0
        self.ultimo_cambio_modo = 0
        self.objetivo_nivel = 15
        self.modo_infinito = False
        self.oleada_infinita = 0
        self.meteoritos_generados = 0
        self.umbral_dificultad = 10000
        self.dificultad_extra = 0
        self.estrellas = self._crear_estrellas()
        self.tiempo_parpadeo = 0.0
        reproducir_musica("musica_campana", 0.55)

    def _crear_estrellas(self) -> list[dict[str, float | int]]:
        estrellas: list[dict[str, float | int]] = []
        for indice, cantidad in enumerate(ESTRELLAS_POR_CAPA):
            for _ in range(cantidad):
                estrellas.append({
                    "x": muestra_uniforme(0, ANCHO),
                    "y": muestra_uniforme(0, ALTO),
                    "tamano": entero_uniforme(1, 2),
                    "velocidad": VELOCIDAD_ESTRELLAS[indice],
                })
        return estrellas

    def _inicializar_nivel(self) -> None:
        puntaje_acumulado = getattr(self, "nave", None)
        puntaje_acumulado = puntaje_acumulado.puntaje if puntaje_acumulado else 0
        nivel = self.niveles[self.indice_nivel]
        self.nivel_actual = nivel
        self.nave = Nave(1, COLORES["primario"], 0, ALTO)
        self.nave.puntaje = puntaje_acumulado
        self.balas: list[Bala] = []
        self.meteoritos: list[Meteorito] = []
        self.explosiones: list[Explosion] = []
        self.generador = GeneradorOleada(nivel, ANCHO, ALTO)
        self.enemigos_procesados = 0
        self.ultimo_cambio_modo = 0
        self.modo_accion = "destruir"
        self.meteoritos_generados = 0
        self.umbral_dificultad = 10000
        self.dificultad_extra = 0

    def manejar_escape(self):
        if self.modo_pausa and self.subestado_opciones == "confirmar":
            return ("escena_menu", {})
        self.modo_pausa = not self.modo_pausa
        self.subestado_opciones = "reanudar"
        self.ignorar_escape_una_vez = True
        return None

    def _crear_meteorito(self, datos: dict[str, float | int]) -> Meteorito:
        radio = int(datos["radio"])
        factor_velocidad = 1.35 if self.modo_infinito else 1.0
        pos_x = ANCHO - radio
        pos_y = float(datos["y_relativo"]) * ALTO
        velocidad = float(datos["vel_x"]) * factor_velocidad
        objetivo_x, objetivo_y = self.nave.rect.center
        dx = objetivo_x - pos_x
        dy = objetivo_y - pos_y
        distancia = math.hypot(dx, dy)
        if distancia <= 0.0:
            vel_x, vel_y = -velocidad, 0.0
        else:
            vel_x = (dx / distancia) * velocidad
            vel_y = (dy / distancia) * velocidad
        return Meteorito(pos_x, pos_y, vel_x, vel_y, radio, int(datos["hp"]))

    def _actualizar_modo_accion(self) -> None:
        if self.enemigos_procesados > 0 and self.enemigos_procesados % 15 == 0 and self.enemigos_procesados != self.ultimo_cambio_modo:
            self.modo_accion = "esquivar" if self.modo_accion == "destruir" else "destruir"
            self.ultimo_cambio_modo = self.enemigos_procesados

    def _actualizar_dificultad_por_puntaje(self) -> None:
        while self.nave.puntaje >= self.umbral_dificultad and self.dificultad_extra < 9:
            self.dificultad_extra += 1
            self.umbral_dificultad += 10000
            if self.modo_infinito:
                self.generador.siguiente_spawn = max(0.10, self.generador.siguiente_spawn * 0.9)
            else:
                self.generador.siguiente_spawn = max(0.12, self.generador.siguiente_spawn * 0.92)

    def _avanzar_nivel_o_finalizar(self) -> str | tuple[str, dict[str, object]] | None:
        self.indice_nivel += 1
        if self.indice_nivel >= len(self.niveles):
            self.modo_infinito = True
            self.nivel_actual = "infinito"
            self.generador = GeneradorOleada("dificil", ANCHO, ALTO)
            self.generador.siguiente_spawn = 0.28
            self.objetivo_nivel = 999999
            return None
        self._inicializar_nivel()
        return None

    def _abrir_menu_salir(self):
        if self.subestado_opciones == "confirmar":
            return ("escena_menu", {})
        self.subestado_opciones = "confirmar"
        return None

    def _iniciar_transicion(self, estado: str, duracion: float, mensaje: str = "") -> None:
        self.estado_transicion = estado
        self.tiempo_transicion = 0.0
        self.duracion_transicion = duracion
        self.mensaje_transicion = mensaje
        self.modo_pausa = False
        self.subestado_opciones = "normal"

    def _actualizar_opciones(self) -> str | tuple[str, dict[str, object]] | None:
        eventos = self.entrada.eventos
        rect_modal = pygame.Rect((ANCHO - ANCHO_MODAL_OPCIONES) // 2, (ALTO - ALTO_MODAL_OPCIONES) // 2, ANCHO_MODAL_OPCIONES, ALTO_MODAL_OPCIONES)
        boton_reanudar = pygame.Rect(rect_modal.centerx - ANCHO_BOTON_MODAL - 8, rect_modal.bottom - 58, ANCHO_BOTON_MODAL, ALTO_BOTON_MODAL)
        boton_menu = pygame.Rect(rect_modal.centerx + 8, rect_modal.bottom - 58, ANCHO_BOTON_MODAL, ALTO_BOTON_MODAL)
        area_slider = pygame.Rect(rect_modal.x + 82, rect_modal.y + 126, SLIDER_ANCHO, SLIDER_ALTO)
        mango_x = area_slider.x + int((self.volumen / 100) * (SLIDER_ANCHO - TAMANO_MANGO_SLIDER))
        mango = pygame.Rect(mango_x, area_slider.y - 4, TAMANO_MANGO_SLIDER, TAMANO_MANGO_SLIDER)

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

        if self.entrada.raton_click_reciente:
            x, y = self.entrada.raton_posicion
            if boton_reanudar.collidepoint(x, y):
                self.modo_pausa = False
                self.subestado_opciones = "normal"
            elif boton_menu.collidepoint(x, y):
                return self._abrir_menu_salir()
            elif area_slider.collidepoint(x, y):
                self.volumen = int(max(0, min(100, ((x - area_slider.x) / max(1, (SLIDER_ANCHO - TAMANO_MANGO_SLIDER))) * 100)))

        for evento in eventos:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if mango.collidepoint(evento.pos):
                    self.volumen = int(max(0, min(100, ((evento.pos[0] - area_slider.x) / max(1, (SLIDER_ANCHO - TAMANO_MANGO_SLIDER))) * 100)))

        if pygame.mixer.get_init() is not None:
            pygame.mixer.music.set_volume(self.volumen / 100)
        return None

    def actualizar(self, dt: float):
        if self.estado_transicion is not None:
            if self.estado_transicion == "campana_completa" and self.entrada.recien_presionada(pygame.K_SPACE):
                if self.canal_victoria is not None:
                    self.canal_victoria.stop()
                    self.canal_victoria = None
                reproducir_musica("musica_campana", 0.55)
                self.tiempo_transicion = self.duracion_transicion
            self.tiempo_transicion += dt
            if self.tiempo_transicion >= self.duracion_transicion:
                estado = self.estado_transicion
                self.estado_transicion = None
                self.tiempo_transicion = 0.0
                self.duracion_transicion = 0.0
                mensaje = self.mensaje_transicion
                self.mensaje_transicion = ""
                if estado == "derrota":
                    return ("escena_fin_juego", {
                        "resultado": "derrota",
                        "puntaje": self.nave.puntaje,
                        "modo": "campana",
                        "dificultad": self.nivel_actual,
                        "iniciales": self.iniciales,
                    })
                if estado == "campana_completa":
                    reproducir_musica("musica_campana", 0.55)
                self._avanzar_nivel_o_finalizar()
            return None

        if self.modo_pausa:
            return self._actualizar_opciones()

        self.tiempo_parpadeo += dt
        for estrella in self.estrellas:
            estrella["x"] = float(estrella["x"]) - float(estrella["velocidad"]) * dt
            if float(estrella["x"]) < 0:
                estrella["x"] = ANCHO + muestra_uniforme(0, 40)
                estrella["y"] = muestra_uniforme(0, ALTO)
                estrella["tamano"] = entero_uniforme(1, 2)

        for dato in self.generador.actualizar(dt):
            self.meteoritos.append(self._crear_meteorito(dato))
        if self.modo_infinito:
            self.oleada_infinita += 1
            if self.oleada_infinita % 120 == 0:
                self.generador.siguiente_spawn = max(0.15, self.generador.siguiente_spawn * 0.88)

        bala = self.nave.actualizar(dt, self.entrada)
        if bala is not None:
            self.balas.append(bala)

        for bala_activa in self.balas:
            bala_activa.actualizar(dt)
        for meteorito in self.meteoritos:
            meteorito.actualizar(dt)
        for explosion in self.explosiones:
            explosion.actualizar(dt)

        # --- RESOLUCIÓN DE COLISIONES BALA <-> METEORITO ---
        # Rastreamos qué meteoritos fueron golpeados para no contar esquiva además
        meteoritos_golpeados: set[int] = set()
        balas_usadas: set[int] = set()

        for meteorito in self.meteoritos:
            for bala_activa in self.balas:
                if id(bala_activa) in balas_usadas:
                    continue
                if hay_colision(bala_activa.rect, meteorito.rect):
                    balas_usadas.add(id(bala_activa))
                    meteoritos_golpeados.add(id(meteorito))
                    if meteorito.recibir_impacto():
                        # Meteorito destruido: sumar puntos y explosión
                        self.nave.puntaje += PUNTOS_DESTRUIR
                        self.explosiones.append(Explosion(meteorito.pos_x, meteorito.pos_y))
                        reproducir_sonido("sonido_explosion")
                        self.enemigos_procesados += 1
                        self.meteoritos_generados += 1
                        self._actualizar_modo_accion()
                    break  # una bala por meteorito por frame

        # Reconstruir listas limpias
        meteoritos_restantes: list[Meteorito] = []
        for meteorito in self.meteoritos:
            fue_golpeado = id(meteorito) in meteoritos_golpeados
            if fue_golpeado and meteorito.hp <= 0:
                # Ya destruido, no agregar
                continue
            if fue_golpeado and meteorito.hp > 0:
                # Dañado pero no destruido, sigue en juego
                meteoritos_restantes.append(meteorito)
                continue
            if meteorito.esta_fuera_de_pantalla():
                # Salió sin ser golpeado: esquivado
                self.nave.puntaje += PUNTOS_ESQUIVAR
                self.enemigos_procesados += 1
                self.meteoritos_generados += 1
                self._actualizar_modo_accion()
            else:
                meteoritos_restantes.append(meteorito)

        balas_restantes: list[Bala] = []
        for bala_activa in self.balas:
            if id(bala_activa) not in balas_usadas and not bala_activa.esta_fuera_de_pantalla():
                balas_restantes.append(bala_activa)

        self.meteoritos = meteoritos_restantes
        self.balas = balas_restantes

        # --- COLISIÓN NAVE <-> METEORITO ---
        for meteorito in list(self.meteoritos):
            if hay_colision(self.nave.rect, meteorito.rect) and not self.nave.es_invencible:
                self.nave.recibir_danio()
                self.explosiones.append(Explosion(meteorito.pos_x, meteorito.pos_y))
                reproducir_sonido("sonido_explosion")
                self.meteoritos.remove(meteorito)
                self.enemigos_procesados += 1
                self.meteoritos_generados += 1
                self._actualizar_modo_accion()
                if self.nave.vidas <= 0:
                    reproducir_sonido("sonido_derrota")
                    self._iniciar_transicion("derrota", 1.35)
                    return None

        self.explosiones = [explosion for explosion in self.explosiones if not explosion.termino()]
        self._actualizar_dificultad_por_puntaje()
        if not self.modo_infinito and self.meteoritos_generados >= self.objetivo_nivel:
            if self.indice_nivel >= len(self.niveles) - 1:
                detener_musica()
                self.canal_victoria = reproducir_sonido("sonido_victoria")
                self._iniciar_transicion("campana_completa", 12.0, f"FELICIDADES {self.iniciales}")
            else:
                self._iniciar_transicion("nivel_completado", 0.9, "NIVEL COMPLETADO")
            return None
        return None

    def renderizar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLORES["fondo"])
        for estrella in self.estrellas:
            tamano = int(estrella["tamano"])
            brillo = COLORES["blanco"] if tamano == 2 else COLORES["neutro_claro"]
            pygame.draw.rect(pantalla, brillo, pygame.Rect(int(estrella["x"]), int(estrella["y"]), tamano, tamano))
        for meteorito in self.meteoritos:
            meteorito.renderizar(pantalla)
        for bala in self.balas:
            bala.renderizar(pantalla)
        for explosion in self.explosiones:
            explosion.renderizar(pantalla)
        self.nave.renderizar(pantalla)

        panel_opciones = pygame.Rect(ANCHO - 160 - MARGEN_GENERAL, MARGEN_GENERAL, 160, ALTO_BOTON_OPCIONES)
        dibujar_boton_pequeno(pantalla, panel_opciones, "OPCIONES", self.fuente_pequena, False)

        titulo_nivel = "MODO INFINITO" if self.modo_infinito else f"NIVEL {self.indice_nivel + 1}/3 - {self.nivel_actual.upper()}"
        dibujar_texto_ajustado(pantalla, titulo_nivel, 14, COLORES["neutro_claro"], (ANCHO // 2, MARGEN_GENERAL + 8), ANCHO - 180)
        if self.modo_infinito:
            dibujar_texto_ajustado(
                pantalla,
                f"DESTRUIR +{PUNTOS_DESTRUIR} | ESQUIVAR +{PUNTOS_ESQUIVAR}",
                10,
                COLORES["acento"],
                (ANCHO // 2, MARGEN_GENERAL + 34),
                ANCHO - 180,
            )
            dibujar_texto_ajustado(pantalla, f"DIFICULTAD {self.dificultad_extra}", 10, COLORES["neutro_claro"], (ANCHO // 2, MARGEN_GENERAL + 50), ANCHO - 180)
            dibujar_texto_ajustado(pantalla, f"OBJETIVO {self.modo_accion.upper()}", 11, COLORES["secundario"] if self.modo_accion == "destruir" else COLORES["primario"], (ANCHO // 2, MARGEN_GENERAL + 80), ANCHO - 180)
        else:
            dibujar_texto_ajustado(pantalla, f"PROGRESO {self.meteoritos_generados}/15", 14, COLORES["acento"], (ANCHO // 2, MARGEN_GENERAL + 32), ANCHO - 180)
            dibujar_texto_ajustado(pantalla, f"OBJETIVO {self.modo_accion.upper()}", 11, COLORES["secundario"] if self.modo_accion == "destruir" else COLORES["primario"], (ANCHO // 2, MARGEN_GENERAL + 58), ANCHO - 180)

        dibujar_texto(pantalla, f"SCORE {formatear_puntaje(self.nave.puntaje)}", self.fuente_normal, COLORES["blanco"], (MARGEN_GENERAL, MARGEN_GENERAL + 2))
        mini = crear_miniatura_nave(COLORES["primario"])
        for indice in range(self.nave.vidas):
            pantalla.blit(mini, (MARGEN_GENERAL + indice * 24, ALTO - 22))

        if self.estado_transicion is not None:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            pantalla.blit(overlay, (0, 0))
            if self.estado_transicion == "derrota":
                ajuste_y = 0
                color = COLORES["peligro"]
                mensaje = "DERROTA"
                submensaje = "EL METEORITO TE ALCANZO"
            elif self.estado_transicion == "campana_completa":
                ajuste_y = -8
                color = COLORES["acento"]
                mensaje = self.mensaje_transicion or f"FELICIDADES {self.iniciales}"
                submensaje = "PASASTE EL MODO CAMPANA"
            else:
                ajuste_y = 0
                color = COLORES["primario"]
                mensaje = self.mensaje_transicion or "NIVEL COMPLETADO"
                submensaje = "PREPARANDO SIGUIENTE NIVEL"
            ajustar_texto_centrado(pantalla, mensaje, self.fuente_titulo, color, ANCHO // 2, ALTO // 2 - 18 + ajuste_y)
            ajustar_texto_centrado(pantalla, submensaje, self.fuente_subtitulo, COLORES["blanco"], ANCHO // 2, ALTO // 2 + 24 + ajuste_y)
            if self.estado_transicion == "campana_completa":
                dibujar_texto_ajustado(pantalla, "ESPACIO PARA OMITIR", 10, COLORES["neutro_medio"], (ANCHO // 2, ALTO // 2 + 62), ANCHO - 120)

        if self.modo_pausa:
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((*COLORES["fondo_panel"], ALPHA_OVERLAY))
            pantalla.blit(overlay, (0, 0))
            rect_modal = pygame.Rect((ANCHO - ANCHO_MODAL_OPCIONES) // 2, (ALTO - ALTO_MODAL_OPCIONES) // 2, ANCHO_MODAL_OPCIONES, ALTO_MODAL_OPCIONES)
            pygame.draw.rect(pantalla, COLORES["fondo_panel"], rect_modal)
            pygame.draw.rect(pantalla, COLORES["primario"], rect_modal, 2)
            pygame.draw.rect(pantalla, COLORES["primario_oscuro"], rect_modal.inflate(-8, -8), 1)
            ajustar_texto_centrado(pantalla, "OPCIONES", self.fuente_subtitulo, COLORES["primario"], rect_modal.centerx, rect_modal.y + 26)
            dibujar_texto(pantalla, f"VOLUMEN {self.volumen}", self.fuente_pequena, COLORES["neutro_claro"], (rect_modal.x + 20, rect_modal.y + 102))
            barra = pygame.Rect(rect_modal.x + 82, rect_modal.y + 126, SLIDER_ANCHO, SLIDER_ALTO)
            pygame.draw.rect(pantalla, COLORES["neutro_oscuro"], barra)
            pygame.draw.rect(pantalla, COLORES["primario_medio"], pygame.Rect(barra.x, barra.y, int((self.volumen / 100) * SLIDER_ANCHO), SLIDER_ALTO))
            mango_x = barra.x + int((self.volumen / 100) * (SLIDER_ANCHO - TAMANO_MANGO_SLIDER))
            mango = pygame.Rect(mango_x, barra.y - 4, TAMANO_MANGO_SLIDER, TAMANO_MANGO_SLIDER)
            pygame.draw.rect(pantalla, COLORES["acento"], mango)
            boton_reanudar = pygame.Rect(rect_modal.centerx - ANCHO_BOTON_MODAL - 8, rect_modal.bottom - 58, ANCHO_BOTON_MODAL, ALTO_BOTON_MODAL)
            boton_menu = pygame.Rect(rect_modal.centerx + 8, rect_modal.bottom - 58, ANCHO_BOTON_MODAL, ALTO_BOTON_MODAL)
            dibujar_boton_pequeno(pantalla, boton_reanudar, "REANUDAR", self.fuente_pequena, self.subestado_opciones == "reanudar")
            dibujar_boton_pequeno(pantalla, boton_menu, "ESC MENÚ", self.fuente_pequena, self.subestado_opciones == "menu")
            if self.subestado_opciones == "confirmar":
                ajustar_texto_centrado(pantalla, "¿CONFIRMAR?", self.fuente_pequena, COLORES["peligro"], rect_modal.centerx, rect_modal.centery + 46)
            dibujar_texto_ajustado(pantalla, "IZQ/DER VOLUMEN | ESC CERRAR", 9, COLORES["neutro_medio"], (rect_modal.centerx, rect_modal.bottom - 16), 300)
