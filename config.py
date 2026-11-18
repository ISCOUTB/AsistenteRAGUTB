from pathlib import Path
import os

# Ruta raiz desde los modulos en src
ROOT = Path(__file__).resolve().parent

# URLs y nombres de archivos
URLS = (
    "https://www.utb.edu.co/wp-content/uploads/2026/10/Reglamento-Estudiantil-2026.pdf",
    "https://www.utb.edu.co/wp-content/uploads/2026/03/Reglamento-Ruta-de-autonomia.pdf",
    "https://www.utb.edu.co/wp-content/uploads/2025/09/reglamento-del-CJ-26-09-25.pdf",
    "https://www.utb.edu.co/wp-content/uploads/2021/04/reglamento_estudio_de_television_y_laboratorio_de_posproduccion_0_0.pdf",
    "https://www.utb.edu.co/wp-content/uploads/2021/04/reglamento_laboratorio_de_fotografia_0.pdf",
    "https://www.utb.edu.co/wp-content/uploads/2021/04/reglamento_laboratorio_de_sonido_0.pdf",
    "https://www.utb.edu.co/wp-content/uploads/2021/04/reglamento_sala_multimedia.pdf",
    "https://www.utb.edu.co/wp-content/uploads/2021/06/REGLAMENTO-DE-USO-DE-LOS-LABORATORIOS-DE-PSICOLOGIA.pdf"
)

NOMBRES_ARCHIVOS = (
    "Reglamento-Ruta-de-autonomia",
    "reglamento-del-CJ-26-09-25",
    "Reglamento-Estudiantil-2026",
    "REGLAMENTO-DE-USO-DE-LOS-LABORATORIOS-DE-PSICOLOGIA",
    "reglamento_estudio_de_television_y_laboratorio_de_posproduccion_0_0",
    "reglamento_laboratorio_de_fotografia_0",
    "reglamento_laboratorio_de_sonido_0",
    "reglamento_sala_multimedia"
)

# Carpetas en data
CARPETA_TXT = ROOT / "data/texto"
CARPETA_PDF = ROOT / "data/pdf"
CARPETA_CHUNKS = ROOT / "data/chunks"
CARPETA_EMBEDDINGS = ROOT / "data/embeddings"

#Rutas archivos txt y pdf

RUTAS_ARCHIVOS_PDF = tuple([CARPETA_PDF / f"{nombre}.pdf" for nombre in NOMBRES_ARCHIVOS])
RUTAS_ARCHIVOS_TXT = tuple([CARPETA_TXT / f"{nombre}.txt" for nombre in NOMBRES_ARCHIVOS])

# Rutas de archivos csv 
RUTA_PREGUNTAS = ROOT / "data/preguntas/preguntas.csv"

DIR_RESULTADOS_BASELINE = ROOT / "experiments/linea_base"
DIR_RESULTADOS_RAG = ROOT / "experiments/rag"

RUTA_RESPUESTAS_BASELINE = DIR_RESULTADOS_BASELINE / "respuestas_baseline.csv"
RUTA_RESPUESTAS_RAG = DIR_RESULTADOS_RAG / "respuestas_rag.csv"

# --- LLM --------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
# Se usa punto y coma como delimitador. Se usa una codificación utf-8-sig
# que usa BOM (Byte Order Mark) lo que permite que Excel y otros programas
# puedan codificar correctamente el archivo.
DELIMITADOR = ";"
CODIFICACION_CSV = "utf-8-sig"

# --- Escalas de calificación manual ----------------------------------------
ESCALA_EXACTITUD = (0, 3)
ESCALA_FIDELIDAD = (0, 3)
ESCALA_ALUCINACION = (0, 2)

# Orden de los tipos de pregunta. Sirve para que las tablas de
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
