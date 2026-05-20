"""Punto de entrada del juego METEOR STRIKE."""

import pygame

from nucleo.bucle_juego import BucleJuego


def main() -> None:
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass
    try:
        BucleJuego().correr()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
