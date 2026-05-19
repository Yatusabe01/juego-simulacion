"""Bucle principal con delta time y transición entre escenas."""

from __future__ import annotations

import pygame

from configuracion import ALTO, ANCHO, DT_MAXIMO, FPS
from escenas.escena_campana import EscenaCampana
from escenas.escena_dificultad import EscenaDificultad
from escenas.escena_dificultad_vs import EscenaDificultadVs
from escenas.escena_fin_juego import EscenaFinJuego
from escenas.escena_informacion import EscenaInformacion
from escenas.escena_iniciales import EscenaIniciales
from escenas.escena_menu import EscenaMenu
from escenas.escena_selector_vs import EscenaSelectorVs
from escenas.escena_vs import EscenaVs
from nucleo.manejador_entrada import ManejadorEntrada


class BucleJuego:
    """Administra eventos, actualización, render y cambios de escena."""

    def __init__(self) -> None:
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
        pygame.display.set_caption("METEOR STRIKE")
        self.reloj = pygame.time.Clock()
        self.entrada = ManejadorEntrada()
        self.es_pantalla_completa = False
        self.escena_activa = EscenaMenu(self.entrada)
        self.activo = True
        self.resolucion_base = (ANCHO, ALTO)
        self.superficie_base = pygame.Surface(self.resolucion_base)
        self.tamano_ventana = self.resolucion_base

    def _crear_escena(self, nombre: str, datos: dict[str, object] | None = None):
        datos = datos or {}
        if nombre == "escena_menu":
            return EscenaMenu(self.entrada)
        if nombre == "escena_dificultad":
            return EscenaDificultad(self.entrada)
        if nombre == "escena_informacion":
            return EscenaInformacion(self.entrada)
        if nombre == "escena_selector_vs":
            return EscenaSelectorVs(self.entrada)
        if nombre == "escena_dificultad_vs":
            return EscenaDificultadVs(self.entrada)
        if nombre == "escena_iniciales":
            if str(datos.get("modo", "campana")) == "vs_infinito":
                return EscenaIniciales(self.entrada, "vs_infinito", None, int(datos.get("cantidad_jugadores", 2)))
            return EscenaIniciales(self.entrada, str(datos.get("modo", "campana")), str(datos.get("dificultad", "medio")), int(datos.get("cantidad_jugadores", 1)))
        if nombre == "escena_campana":
            return EscenaCampana(self.entrada, str(datos.get("dificultad", "medio")), str(datos.get("iniciales", "AAA")))
        if nombre == "escena_vs":
            return EscenaVs(self.entrada, str(datos.get("iniciales_j1", "AAA")), str(datos.get("iniciales_j2", "BBB")), str(datos.get("modo_vs", "clasico")))
        if nombre == "escena_fin_juego":
            return EscenaFinJuego(self.entrada, **datos)
        return EscenaMenu(self.entrada)

    def _alternar_pantalla_completa(self) -> None:
        self.es_pantalla_completa = not self.es_pantalla_completa
        bandera = pygame.FULLSCREEN if self.es_pantalla_completa else 0
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO), bandera | pygame.RESIZABLE if not self.es_pantalla_completa else bandera)
        self.tamano_ventana = self.pantalla.get_size()

    def _presentar(self) -> None:
        if self.tamano_ventana == self.resolucion_base:
            self.pantalla.blit(self.superficie_base, (0, 0))
        else:
            escalada = pygame.transform.scale(self.superficie_base, self.tamano_ventana)
            self.pantalla.blit(escalada, (0, 0))
        pygame.display.flip()

    def correr(self) -> None:
        while self.activo:
            dt = min(self.reloj.tick(FPS) / 1000.0, DT_MAXIMO)
            eventos = pygame.event.get()
            self.entrada.actualizar(eventos)

            for evento in eventos:
                if evento.type == pygame.QUIT:
                    self.activo = False
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                    self._alternar_pantalla_completa()
                elif evento.type == pygame.VIDEORESIZE and not self.es_pantalla_completa:
                    self.pantalla = pygame.display.set_mode(evento.size, pygame.RESIZABLE)
                    self.tamano_ventana = evento.size

            if self.entrada.recien_presionada(pygame.K_ESCAPE):
                if hasattr(self.escena_activa, "manejar_escape"):
                    resultado_escape = self.escena_activa.manejar_escape()
                    if resultado_escape == "salir":
                        self.activo = False
                    elif isinstance(resultado_escape, tuple):
                        nombre, datos = resultado_escape
                        self.escena_activa = self._crear_escena(nombre, datos)
                    elif isinstance(resultado_escape, str):
                        self.escena_activa = self._crear_escena(resultado_escape)

            transicion = self.escena_activa.actualizar(dt)
            if isinstance(transicion, tuple):
                nombre, datos = transicion
                self.escena_activa = self._crear_escena(nombre, datos)
            elif isinstance(transicion, str):
                if transicion == "salir":
                    self.activo = False
                else:
                    self.escena_activa = self._crear_escena(transicion)

            self.superficie_base.fill((0, 0, 0))
            self.escena_activa.renderizar(self.superficie_base)
            self._presentar()
