"""Paso 2: toma las señales que una persona aprobó en GitHub,
las agrega a data/senales.json y recalcula la zona del reloj.

Regla pública de la zona: es el nivel más alto entre las señales que SUMAN riesgo
en los últimos 90 días. Si no hay ninguna, la zona es 1. Así la aguja también
puede bajar cuando las señales envejecen."""
import json, os
from datetime import date, timedelta
from pathlib import Path

import config

RAIZ = Path(__file__).resolve().parent.parent
F_SENALES = RAIZ / "data/senales.json"
F_ESTADO = RAIZ / "data/estado.json"
CAMPOS = ("fecha", "titulo", "resumen", "fuente", "url", "nivel", "efecto", "eje")


def calcular_estado(senales, hoy):
    desde = hoy - timedelta(days=config.VENTANA_DIAS)
    activas = [s for s in senales if s["efecto"] == "suma" and date.fromisoformat(s["fecha"]) >= desde]
    zona = max((s["nivel"] for s in activas), default=1)
    return {
        "zona": zona,
        "nombre": config.ZONAS[zona],
        "actualizado": hoy.isoformat(),
        "ventana_dias": config.VENTANA_DIAS,
        "senales_activas": len(activas),
    }


def main():
    senales = json.loads(F_SENALES.read_text(encoding="utf-8"))
    urls = {s["url"] for s in senales}

    if os.environ.get("GITHUB_TOKEN"):
        import github
        for issue in github.issues("aprobado"):
            s = github.leer_senal(issue.get("body"))
            if not s or s.get("url") in urls:
                continue
            if not config.dominio_permitido(s.get("url", "")):
                print(f"No se publica, dominio no oficial: {s.get('url')}")
                continue
            nueva = {k: s.get(k) for k in CAMPOS}
            nueva["verificado"] = True
            nueva["issue"] = issue["html_url"]
            senales.append(nueva)
            urls.add(nueva["url"])
            if issue["state"] == "open":
                github.comentar_y_cerrar(issue["number"], "Publicada en el reloj.")
            print(f"Publicada: {nueva['titulo']}")

    senales.sort(key=lambda s: s["fecha"], reverse=True)
    F_SENALES.write_text(json.dumps(senales, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    estado = calcular_estado(senales, date.today())
    F_ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Zona actual: {estado['nombre']}")


if __name__ == "__main__":
    main()
