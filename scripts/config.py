"""Configuración compartida de AI World Watch."""
import os
from urllib.parse import urlparse

# Modelo de Claude que busca noticias. Se puede cambiar con la variable MODELO en GitHub.
MODELO = os.environ.get("MODELO") or "claude-sonnet-5-5"

# Solo se aceptan señales publicadas en estos dominios oficiales.
# Agregá o quitá dominios según tu criterio editorial.
DOMINIOS_OFICIALES = [
    # Laboratorios de IA
    "openai.com", "anthropic.com", "deepmind.google", "blog.google",
    "ai.meta.com", "x.ai", "mistral.ai", "microsoft.com",
    # Investigación independiente en seguridad
    "metr.org", "redwoodresearch.org", "apolloresearch.ai",
    # Gobiernos y organismos
    "aisi.gov.uk", "gov.uk", "nist.gov", "whitehouse.gov", "congress.gov",
    "federalregister.gov", "europa.eu", "oecd.ai", "oecd.org", "un.org", "gob.mx",
]

# La zona se calcula con las señales de los últimos N días.
VENTANA_DIAS = 90

ZONAS = {1: "Zona estable", 2: "Zona de aceleración", 3: "Zona de alerta", 4: "Zona de crisis"}


def dominio_permitido(url: str) -> bool:
    host = (urlparse(url or "").hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in DOMINIOS_OFICIALES)
