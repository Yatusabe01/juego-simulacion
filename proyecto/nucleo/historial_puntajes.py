"""Lectura y escritura del historial persistente de puntajes."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from configuracion import MAX_HISTORIAL_PUNTAJES, RUTA_HISTORIAL_PUNTAJES


def cargar_historial() -> list[dict[str, object]]:
    ruta = Path(RUTA_HISTORIAL_PUNTAJES)
    if not ruta.exists():
        return []
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(datos, list):
        return []
    return [registro for registro in datos if isinstance(registro, dict)]


def guardar_historial(historial: list[dict[str, object]]) -> None:
    ruta = Path(RUTA_HISTORIAL_PUNTAJES)
    ruta.write_text(json.dumps(historial[:MAX_HISTORIAL_PUNTAJES], ensure_ascii=False, indent=2), encoding="utf-8")


def agregar_registro(iniciales: str, modo: str, resultado: str, puntaje: int, categoria: str | None = None) -> None:
    historial = cargar_historial()
    nuevo = {
        "iniciales": iniciales[:3].upper() or "AAA",
        "modo": modo,
        "categoria": categoria or modo,
        "resultado": resultado,
        "puntaje": int(puntaje),
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    historial.insert(0, nuevo)
    historial.sort(key=lambda r: int(r.get("puntaje", 0)), reverse=True)

    vistos = set()
    historial_limpio: list[dict[str, object]] = []
    for registro in historial:
        clave = (registro.get("iniciales"), registro.get("modo"), registro.get("puntaje"))
        if clave not in vistos:
            vistos.add(clave)
            historial_limpio.append(registro)

    guardar_historial(historial_limpio[:6])
