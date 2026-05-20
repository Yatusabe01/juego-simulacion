"""Funciones compartidas de recursos e interfaz para METEOR STRIKE."""

from __future__ import annotations

import os

import pygame

from configuracion import (
    COLORES,
    ESTRELLAS_POR_CAPA,
    FUENTE_FALLBACK,
    RUTA_FUENTE_RETRO,
    RUTA_SPRITE_NAVE,
    VELOCIDAD_ESTRELLAS,
    ANCHO,
    ALTO,
)
from matematicas.probabilidad import entero_uniforme, muestra_uniforme

RUTA_AUDIO = os.path.join(os.path.dirname(RUTA_SPRITE_NAVE), "audio")
_SONIDOS: dict[str, pygame.mixer.Sound] = {}
_MUSICA_ACTUAL = None


def cargar_fuente(tamano: int) -> pygame.font.Font:
    """Carga la fuente retro o una monoespaciada por defecto."""
    try:
        fuente = pygame.font.Font(RUTA_FUENTE_RETRO, tamano * 2)
        fuente.set_bold(False)
        return fuente
    except (FileNotFoundError, OSError):
        fuente = pygame.font.SysFont(FUENTE_FALLBACK, tamano * 2)
        fuente.set_bold(True)
        return fuente


def _crear_nave_base() -> pygame.Surface:
    superficie = pygame.Surface((64, 32), pygame.SRCALPHA)
    color = (240, 240, 240)
    pygame.draw.polygon(superficie, color, [(6, 8), (42, 8), (58, 16), (42, 24), (6, 24), (16, 16)])
    pygame.draw.polygon(superficie, (170, 170, 170), [(16, 11), (36, 11), (46, 16), (36, 21), (16, 21), (22, 16)])
    pygame.draw.circle(superficie, (95, 200, 255), (28, 16), 4)
    pygame.draw.rect(superficie, (120, 120, 120), pygame.Rect(2, 13, 10, 6))
    return superficie


def cargar_sprite_nave() -> pygame.Surface:
    """Carga el sprite de la nave con fallback generado."""
    if os.path.exists(RUTA_SPRITE_NAVE):
        imagen = pygame.image.load(RUTA_SPRITE_NAVE).convert_alpha()
        return pygame.transform.smoothscale(imagen, (64, 32))
    return _crear_nave_base()


def _ruta_audio(nombre_base: str) -> str | None:
    for extension in (".ogg", ".mp3", ".wav"):
        ruta = os.path.join(RUTA_AUDIO, f"{nombre_base}{extension}")
        if os.path.exists(ruta):
            return ruta
    return None


def cargar_sonido(nombre_base: str) -> pygame.mixer.Sound | None:
    if not pygame.mixer.get_init():
        return None
    sonido = _SONIDOS.get(nombre_base)
    if sonido is not None:
        return sonido
    ruta = _ruta_audio(nombre_base)
    if ruta is None:
        return None
    try:
        sonido = pygame.mixer.Sound(ruta)
    except pygame.error:
        return None
    _SONIDOS[nombre_base] = sonido
    return sonido


def reproducir_sonido(nombre_base: str) -> None:
    sonido = cargar_sonido(nombre_base)
    if sonido is not None:
        if nombre_base == "sonido_bala":
            sonido.set_volume(0.35)
        else:
            sonido.set_volume(1.0)
        return sonido.play()


def crear_estrellas() -> list[dict[str, float | int]]:
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


def actualizar_estrellas(estrellas: list[dict[str, float | int]], dt: float) -> None:
    for estrella in estrellas:
        estrella["x"] = float(estrella["x"]) - float(estrella["velocidad"]) * dt
        if float(estrella["x"]) < 0:
            estrella["x"] = ANCHO + muestra_uniforme(0, 40)
            estrella["y"] = muestra_uniforme(0, ALTO)
            estrella["tamano"] = entero_uniforme(1, 2)


def dibujar_estrellas(pantalla: pygame.Surface, estrellas: list[dict[str, float | int]], desplazamiento_y: int = 0, altura_visible: int | None = None) -> None:
    alto = altura_visible if altura_visible is not None else pantalla.get_height()
    for estrella in estrellas:
        y = int(estrella["y"])
        if desplazamiento_y and not (desplazamiento_y <= y < desplazamiento_y + alto):
            continue
        tamano = int(estrella["tamano"])
        brillo = COLORES["blanco"] if tamano == 2 else COLORES["neutro_claro"]
        pygame.draw.rect(pantalla, brillo, pygame.Rect(int(estrella["x"]), y - desplazamiento_y, tamano, tamano))


def reproducir_musica(nombre_base: str, volumen: float = 0.7) -> None:
    global _MUSICA_ACTUAL
    if not pygame.mixer.get_init():
        return
    ruta = _ruta_audio(nombre_base)
    if ruta is None or _MUSICA_ACTUAL == ruta:
        return
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play(-1)
        _MUSICA_ACTUAL = ruta
    except pygame.error:
        return


def detener_musica() -> None:
    global _MUSICA_ACTUAL
    if pygame.mixer.get_init() is not None:
        pygame.mixer.music.stop()
    _MUSICA_ACTUAL = None


def aplicar_tinte(superficie: pygame.Surface, color: tuple[int, int, int]) -> pygame.Surface:
    """Aplica un tinte de color a una superficie."""
    resultado = superficie.copy()
    resultado.fill((*color, 255), special_flags=pygame.BLEND_RGB_MULT)
    return resultado


def crear_miniatura_nave(color: tuple[int, int, int]) -> pygame.Surface:
    """Crea una miniatura de la nave para el HUD."""
    base = cargar_sprite_nave()
    tinte = aplicar_tinte(base, color)
    return pygame.transform.smoothscale(tinte, (20, 10))


def dibujar_texto(pantalla: pygame.Surface, texto: str, fuente: pygame.font.Font, color: tuple[int, int, int], posicion: tuple[int, int], centro: bool = False) -> pygame.Rect:
    """Dibuja texto y devuelve su rectángulo."""
    superficie_texto = fuente.render(texto, True, color)
    rect = superficie_texto.get_rect()
    if centro:
        rect.center = posicion
    else:
        rect.topleft = posicion
    pantalla.blit(superficie_texto, rect)
    return rect


def dibujar_texto_ajustado(pantalla: pygame.Surface, texto: str, tamano_maximo: int, color: tuple[int, int, int], centro: tuple[int, int], ancho_maximo: int, alineado_centro: bool = True) -> pygame.Rect:
    """Dibuja texto reduciendo el tamaño hasta que entre en el ancho indicado."""
    tamano = tamano_maximo
    fuente = cargar_fuente(tamano)
    superficie_texto = fuente.render(texto, True, color)
    while superficie_texto.get_width() > ancho_maximo and tamano > 8:
        tamano -= 1
        fuente = cargar_fuente(tamano)
        superficie_texto = fuente.render(texto, True, color)
    rect = superficie_texto.get_rect()
    if alineado_centro:
        rect.center = centro
    else:
        rect.topleft = centro
    pantalla.blit(superficie_texto, rect)
    return rect


def dibujar_boton(pantalla: pygame.Surface, rect: pygame.Rect, texto: str, fuente: pygame.font.Font, seleccionado: bool) -> None:
    """Dibuja un botón rectangular con borde y texto."""
    color_borde = COLORES["primario"] if seleccionado else COLORES["neutro_oscuro"]
    color_texto = COLORES["primario"] if seleccionado else COLORES["neutro_medio"]
    pygame.draw.rect(pantalla, COLORES["fondo_panel"], rect)
    pygame.draw.rect(pantalla, color_borde, rect, 2)
    dibujar_texto(pantalla, texto, fuente, color_texto, rect.center, centro=True)


def dibujar_boton_pequeno(pantalla: pygame.Surface, rect: pygame.Rect, texto: str, fuente: pygame.font.Font, seleccionado: bool) -> None:
    """Dibuja un botón pequeño para la interfaz."""
    dibujar_boton(pantalla, rect, texto, fuente, seleccionado)


def ajustar_texto_centrado(pantalla: pygame.Surface, texto: str, fuente: pygame.font.Font, color: tuple[int, int, int], x: int, y: int) -> pygame.Rect:
    """Dibuja texto centrado en una posición concreta."""
    return dibujar_texto(pantalla, texto, fuente, color, (x, y), centro=True)
