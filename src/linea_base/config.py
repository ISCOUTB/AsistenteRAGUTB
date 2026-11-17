"""
Configuración compartida para los scripts de línea base.

La clave de Gemini es la que está en el notebook `asistente-rag-utb.ipynb`.
Se puede sobreescribir con la variable de entorno GEMINI_API_KEY sin tocar
este archivo.
"""

import os
from pathlib import Path

# --- Rutas del proyecto -----------------------------------------------------
RAIZ = Path(__file__).resolve().parent
RUTA_PREGUNTAS = RAIZ / "preguntas.csv"
DIR_RESULTADOS = RAIZ / "resultados"
RUTA_RESPUESTAS = DIR_RESULTADOS / "respuestas_baseline.csv"

# --- LLM --------------------------------------------------------------------
# Clave tomada del notebook. Para no dejarla escrita aquí:
#   PowerShell:  $env:GEMINI_API_KEY = "..."
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "GWMINI_API_KEY",
)
MODELO = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
TEMPERATURA = 0.0
MAX_TOKENS_SALIDA = 700

# Pausa entre llamadas para no golpear la cuota de la API.
# El nivel gratuito de Gemini permite ~15 solicitudes por minuto para este
# modelo; 4.5 s deja margen suficiente.
SEGUNDOS_ENTRE_LLAMADAS = 4.5
REINTENTOS = 3

# --- Prompt de la línea base ------------------------------------------------
# Importante: NO se incluye ningún fragmento de los reglamentos. El modelo
# responde solo con su conocimiento paramétrico.
PROMPT_SISTEMA = (
    "Eres un asistente académico que responde preguntas de estudiantes de la "
    "Universidad Tecnológica de Bolívar (UTB). Responde en español, de forma "
    "clara y concisa, en un máximo de 200 palabras."
)
PLANTILLA_PROMPT = "{sistema}\n\nPregunta: {pregunta}"

# --- Delimitador de los CSV -------------------------------------------------
# Se usa punto y coma para que Excel en configuración regional española abra
# el archivo con las columnas separadas. Todos los scripts leen con este valor.
DELIMITADOR = ";"
CODIFICACION_CSV = "utf-8-sig"

# --- Escalas de calificación manual ----------------------------------------
ESCALA_EXACTITUD = (0, 3)
ESCALA_FIDELIDAD = (0, 3)
ESCALA_ALUCINACION = (0, 2)

# Orden "oficial" de los tipos de pregunta. Sirve para que las tablas de
# métricas salgan siempre en el mismo orden.
TIPOS = [
    "articulo_especifico",
    "interpretacion_simple",
    "multi_articulo",
    "ambigua",
    "dificil",
    "fuera_de_alcance",
    "conflicto_entre_documentos",
]

DESCRIPCION_TIPOS = {
    "articulo_especifico": "La respuesta está contenida en un artículo o sección concreta.",
    "interpretacion_simple": "Aplicación directa de una sola regla a un caso sencillo.",
    "multi_articulo": "Requiere combinar dos o más artículos, secciones o documentos.",
    "ambigua": "La pregunta no precisa contexto; la buena respuesta debe desambiguar o pedir aclaración.",
    "dificil": "Requiere cálculo, excepciones, plazos encadenados o razonamiento sobre varios supuestos.",
    "fuera_de_alcance": "La respuesta no está en el corpus; lo correcto es abstenerse y no inventar.",
    "conflicto_entre_documentos": "Un mismo dato cambia según el documento o régimen aplicable.",
}


def crear_cliente():
    """Crea el cliente de Gemini con un error claro si falta la clave."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Falta GEMINI_API_KEY. Defínela como variable de entorno o edita config.py."
        )
    from google import genai

    return genai.Client(api_key=GEMINI_API_KEY)
