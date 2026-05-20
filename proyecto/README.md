# METEOR STRIKE

Juego arcade en `pygame` donde una nave esquiva y destruye meteoritos.

## Modos

- `Campaña`: 3 dificultades y luego modo infinito.
- `VS`: dos jugadores en pantallas separadas.
- `VS infinito`: variante con spawn más agresivo.

## Controles

- `WASD` / `Flechas`: mover nave.
- `SPACE` / `.`: disparar.
- `ESC`: abrir/cerrar pausa o volver al menú.
- `F11`: pantalla completa.

## Audio

Coloca tus archivos en `assets/audio/`.

Archivos esperados:

- `musica_menu.mp3`
- `musica_campana.mp3`
- `musica_vs.mp3`
- `sonido_bala.mp3`
- `sonido_explosion.mp3`
- `sonido_victoria.mp3`
- `sonido_derrota.mp3`
- `sonido_dificultad.mp3`

La música se reproduce en loop. Los efectos sonoros se disparan por evento.

## Estructura

- `principal.py`: entrada del juego.
- `configuracion.py`: constantes globales.
- `entidades/`: nave, bala, meteorito, explosión.
- `escenas/`: menú, campaña, VS, información, fin de juego.
- `nucleo/`: ayuda compartida, entrada, puntaje, historial, generador.

## Notas

- Si falta un archivo de audio, el juego sigue funcionando.
- El historial de puntajes se guarda localmente en JSON.
