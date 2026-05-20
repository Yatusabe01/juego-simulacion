# METEOR STRIKE

Juego arcade en `pygame` donde una nave esquiva y destruye meteoritos.

## Arquitectura

- `principal.py`: inicia `pygame` y ejecuta el bucle principal.
- `nucleo/bucle_juego.py`: administra eventos, cambio de escenas, `dt` y render final.
- `nucleo/manejador_entrada.py`: captura teclas, mouse y pulsaciones recientes.
- `nucleo/ayudantes.py`: centraliza UI, fuentes, audio, estrellas y utilidades visuales.
- `entidades/`: contiene la lógica de objetos del juego.
- `escenas/`: implementa cada pantalla o estado del flujo.

## Flujo

- El juego comienza en `EscenaMenu`.
- Cada escena implementa `actualizar(dt)` y `renderizar(pantalla)`.
- `actualizar(dt)` devuelve `None`, un nombre de escena, o una tupla `(escena, datos)`.
- `bucle_juego.py` recibe esa transición y construye la siguiente escena.
- El estado visual y lógico se separa por escena para mantener el código modular.

## Responsabilidades

- `EscenaMenu`: menú, estrellas, navegación a campaña/VS/info.
- `EscenaDificultad`: selección de dificultad para campaña.
- `EscenaSelectorVs`: selección de VS clásico, imposible o infinito.
- `EscenaIniciales`: captura de iniciales por jugador.
- `EscenaCampana`: niveles, progresión, HUD, fin de campaña e infinito.
- `EscenaVs`: dos arenas sincronizadas con colisiones separadas.
- `EscenaFinJuego`: resultado final, reintento y retorno al menú.

## Sintaxis Usada

- `Clases`: cada pantalla y entidad está modelada con `class`.
- `Métodos`: la lógica se divide en funciones cortas como `actualizar`, `renderizar` y `_resolver_colisiones`.
- `Listas y diccionarios`: se usan para meteoritos, estrellas, datos de escena e historial.
- `Type hints`: se usa anotación como `list[Bala]`, `dict[str, object]`, `str | None`.
- `Match implícito`: la selección de escena se hace con `if`/`elif` en `bucle_juego.py`.
- `Guard clauses`: se usan retornos tempranos para pausa, confirmación y estados especiales.
- `pygame.Rect`: se usa para colisiones, botones y layout.
- `pygame.mixer`: se usa para música en loop y efectos por evento.

## Medidas

- Las medidas de la interfaz están en píxeles (`px`).
- Ejemplo: `60` significa `60 px` en posición, ancho o alto, según el contexto.
- Los tamaños de texto usan valores relativos al cargador de fuente, pero también se dibujan en pantalla como píxeles.
- `pygame.Rect(x, y, ancho, alto)` usa siempre coordenadas y tamaños en píxeles.
- Los valores como `dt` son de tiempo en segundos, no en píxeles.

## Distribucion

- Los meteoritos se generan con una espera base por dificultad y una variacion uniforme.
- La formula usada es: `espero = base * U(0.75, 1.25)`.
- `U(a, b)` representa una distribucion uniforme en el rango `[a, b]`.
- La altura de spawn tambien usa distribucion uniforme para repartir meteoritos en pantalla.
- El radio, la cantidad de vertices y la deriva vertical se toman con valores uniformes dentro de rangos definidos.
- En modo infinito e imposible se modifica la frecuencia de spawn con factores multiplicativos para aumentar la dificultad.

## Uso

- `WASD` o flechas: mover nave.
- `SPACE` o `.`: disparar.
- `ENTER`: confirmar y continuar.
- `ESC`: pausar, volver o salir.
- `F11`: pantalla completa.
- `SIM` o `ELF` en iniciales de VS: activa el modo especial.

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
