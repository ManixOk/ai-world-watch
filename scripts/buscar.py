"""Paso 1, cada día: la IA busca señales nuevas en fuentes oficiales
y las deja como "candidatos" en GitHub para que una persona las revise.
Nada de lo que encuentra este paso se publica solo."""
import json, re, sys
from datetime import date, timedelta
from pathlib import Path

import anthropic
import config, github

RAIZ = Path(__file__).resolve().parent.parent
HOY = date.today()

ESCALA = """
1 Zona estable: la IA avanza y las personas la supervisan bien.
2 Zona de aceleración: la IA avanza más rápido de lo que se regula.
3 Zona de alerta: incidentes reales o advertencias serias, pero se detectan y se contienen.
4 Zona de crisis: un sistema de IA causó un daño serio y no se lo pudo frenar a tiempo.
"""

INSTRUCCIONES = f"""Sos el equipo de monitoreo de AI World Watch, un indicador público de cuánto control humano
tenemos sobre la inteligencia artificial. Hoy es {HOY.isoformat()}.

Buscá hechos publicados entre {(HOY - timedelta(days=7)).isoformat()} y hoy sobre:
incidentes de seguridad con sistemas de IA, comportamientos no autorizados de modelos o agentes,
saltos de capacidad relevantes, uso de IA en defensa o infraestructura crítica,
advertencias públicas de laboratorios o investigadores, y leyes o acuerdos que refuercen o debiliten el control.

Escala del indicador:{ESCALA}

Reglas estrictas:
- Solo hechos que aparezcan en la fuente original (el laboratorio, el organismo o los investigadores).
- Nada de opiniones, predicciones ni especulación. Nada de citas textuales.
- Si no encontrás nada que cumpla, devolvé una lista vacía. Es mejor no reportar que inventar.
- La url debe ser exactamente la de un resultado de búsqueda que hayas visto.
- No repitas estas urls ya registradas: {{ya_vistas}}

Respondé al final SOLO con un bloque <json>[...]</json>, una lista de objetos con:
fecha (AAAA-MM-DD de publicación), titulo (español, máximo 120 caracteres, descriptivo y sin adjetivos),
resumen (español, 1 o 2 oraciones con lo que dice la fuente), fuente (organización y tipo de documento),
url, nivel (1 a 4 según la escala), efecto ("suma" si aumenta el riesgo, "resta" si lo reduce),
eje (capacidad, autonomía, uso militar e infraestructura, alertas de expertos o regulación).
"""


def urls_registradas():
    vistas = set()
    senales = json.loads((RAIZ / "data/senales.json").read_text(encoding="utf-8"))
    vistas |= {s["url"] for s in senales}
    for etiqueta in ("candidato", "aprobado", "rechazado"):
        for i in github.issues(etiqueta):
            s = github.leer_senal(i.get("body"))
            if s and s.get("url"):
                vistas.add(s["url"])
    return vistas


def consultar_claude(ya_vistas):
    cliente = anthropic.Anthropic()  # usa la variable ANTHROPIC_API_KEY
    mensajes = [{"role": "user", "content": INSTRUCCIONES.replace("{ya_vistas}", ", ".join(sorted(ya_vistas)) or "ninguna")}]
    herramienta = {"type": "web_search_20250305", "name": "web_search", "max_uses": 8,
                   "allowed_domains": config.DOMINIOS_OFICIALES}
    urls_vistas, texto = set(), ""
    for _ in range(4):  # la búsqueda puede pausarse y continuar
        r = cliente.messages.create(model=config.MODELO, max_tokens=4000,
                                    messages=mensajes, tools=[herramienta])
        for b in r.content:
            if b.type == "web_search_tool_result" and isinstance(b.content, list):
                urls_vistas |= {x.url for x in b.content if getattr(x, "url", None)}
            if b.type == "text":
                texto += b.text
        if r.stop_reason != "pause_turn":
            break
        mensajes += [{"role": "assistant", "content": r.content}]
    return texto, urls_vistas


def main():
    github.asegurar_etiquetas()
    ya_vistas = urls_registradas()
    texto, urls_vistas = consultar_claude(ya_vistas)

    m = re.search(r"<json>\s*(\[.*?\])\s*</json>", texto, re.S)
    if not m:
        print("La IA no devolvió resultados en el formato esperado. No se crea nada.")
        return
    candidatos = json.loads(m.group(1))

    creados = 0
    for c in candidatos:
        url = c.get("url", "")
        motivo = None
        if url in ya_vistas:
            motivo = "ya registrada"
        elif not config.dominio_permitido(url):
            motivo = "dominio no oficial"
        elif url not in urls_vistas:
            motivo = "la url no apareció en la búsqueda (posible invención)"
        elif c.get("nivel") not in (1, 2, 3, 4) or c.get("efecto") not in ("suma", "resta"):
            motivo = "nivel o efecto inválido"
        if motivo:
            print(f"Descartada ({motivo}): {url}")
            continue

        cuerpo = (
            f"**{c['titulo']}**\n\n{c.get('resumen','')}\n\n"
            f"Fuente: [{c.get('fuente','')}]({url})\n\n"
            "### Para revisar\n"
            "1. Abrí la fuente y confirmá que dice exactamente esto.\n"
            "2. Si hace falta, editá el bloque de abajo (título, nivel, efecto).\n"
            "3. Poné la etiqueta **aprobado** para publicarla, o **rechazado** para descartarla.\n\n"
            f"```json\n{json.dumps(c, ensure_ascii=False, indent=2)}\n```"
        )
        github.crear_issue(f"[Candidato] {c['titulo']}", cuerpo, ["candidato"])
        ya_vistas.add(url)
        creados += 1
    print(f"Candidatos nuevos para revisar: {creados}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # que un error de búsqueda no frene la publicación
        print(f"Error en la búsqueda: {e}", file=sys.stderr)
        sys.exit(0)
