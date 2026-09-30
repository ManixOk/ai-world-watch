"""Funciones mínimas para hablar con la API de GitHub."""
import json, os, re, requests

REPO = os.environ.get("GITHUB_REPOSITORY", "")   # lo completa GitHub Actions
TOKEN = os.environ.get("GITHUB_TOKEN", "")       # lo completa GitHub Actions
API = f"https://api.github.com/repos/{REPO}"
H = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}

ETIQUETAS = {
    "candidato": ("E0BE3E", "Señal propuesta por la IA, falta revisión humana"),
    "aprobado": ("3FA66B", "Revisada por una persona: se publica en el reloj"),
    "rechazado": ("D2434F", "Descartada en la revisión"),
}


def asegurar_etiquetas():
    for nombre, (color, desc) in ETIQUETAS.items():
        r = requests.get(f"{API}/labels/{nombre}", headers=H, timeout=30)
        if r.status_code == 404:
            requests.post(f"{API}/labels", headers=H, timeout=30,
                          json={"name": nombre, "color": color, "description": desc}).raise_for_status()


def issues(etiqueta: str):
    out, page = [], 1
    while True:
        r = requests.get(f"{API}/issues", headers=H, timeout=30,
                         params={"labels": etiqueta, "state": "all", "per_page": 100, "page": page})
        r.raise_for_status()
        datos = r.json()
        out += [i for i in datos if "pull_request" not in i]
        if len(datos) < 100:
            return out
        page += 1


def crear_issue(titulo, cuerpo, etiquetas):
    requests.post(f"{API}/issues", headers=H, timeout=30,
                  json={"title": titulo[:250], "body": cuerpo, "labels": etiquetas}).raise_for_status()


def comentar_y_cerrar(numero, texto):
    requests.post(f"{API}/issues/{numero}/comments", headers=H, timeout=30, json={"body": texto}).raise_for_status()
    requests.patch(f"{API}/issues/{numero}", headers=H, timeout=30, json={"state": "closed"}).raise_for_status()


def leer_senal(cuerpo: str):
    """Extrae el bloque ```json del texto de un issue."""
    m = re.search(r"```json\s*(\{.*?\})\s*```", cuerpo or "", re.S)
    return json.loads(m.group(1)) if m else None
