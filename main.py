from src.fetching import fetching
from src.linea_base import linea_base
from src.linea_base import calcular_metricas
from src.extraccion_texto import extraccion_texto
from src.chunking import chunking
from src.embedding import embedding
import os

from dotenv import load_dotenv

ROOT = os.path.dirname(__file__)
load_dotenv(ROOT + "/.env")

from config import (
    CARPETA_TXT,
    CARPETA_PDF,
    CARPETA_CHUNKS,
    CARPETA_EMBEDDINGS,
    DIR_RESULTADOS_BASELINE,
    DIR_RESULTADOS_RAG,
    GEMINI_API_KEY,
    RUTA_RESPUESTAS_BASELINE
)

#Verificar si existen los directorios necesarios

def crear_si_no_existe(ruta):
    if not os.path.isdir(ruta):
        os.mkdir(ruta)

crear_si_no_existe(CARPETA_TXT)
crear_si_no_existe(CARPETA_PDF)
crear_si_no_existe(CARPETA_CHUNKS)
crear_si_no_existe(CARPETA_EMBEDDINGS)
crear_si_no_existe(DIR_RESULTADOS_BASELINE)
crear_si_no_existe(DIR_RESULTADOS_RAG)

# Verificar si existe la clave de Gemini API

if GEMINI_API_KEY == None:
    print("No se ha definido la clave GEMINI_API_KEY.")
    print("Ejecute 'python set_api_key.py SU_API_KEY'")
    exit(1)


print("\n              PIPELINE COMPLETO")

print("\n\n-----------------------------------------")
print("1. Fetching de PDFs institucionales")
print("-----------------------------------------\n")

fetching.main()

print("\n\n-----------------------------------------")
print("2. Extracción de texto y preprocesamiento de texto")
print("-----------------------------------------\n")

extraccion_texto.main()

print("\n\n-----------------------------------------")
print("3. Linea base: LLM sin RAG")
print("-----------------------------------------\n")

if os.path.exists(RUTA_RESPUESTAS_BASELINE):
    opcion = input(
        f"Ya existe la línea base en {RUTA_RESPUESTAS_BASELINE}.\n"
        "¿Quieres ver las respuestas ya generadas (v), regenerarlas (r) " +
        "o continuar generando las respuestas (c)? [v/r/c]: "
    ).strip().lower()

    if opcion == "v":
        linea_base.main(["--ver-existentes"])
    elif opcion == "r":
        linea_base.main(["--reemplazar"])
    elif opcion == "c":
        linea_base.main()
else:
    linea_base.main()

print("\n- EVALUACIÓN DE LA LÍNEA BASE\n")
print(f"Edita el archivo {RUTA_RESPUESTAS_BASELINE} para calificar exactitud, fidelidad y alucinación.")
print(f"Después, regresa y presiona ENTER...")

input()

while calcular_metricas.main() == 1:
    print("Termina la calificación y presiona ENTER para continuar...")
    input()

print("\n\n-----------------------------------------")
print("4. Procesamiento de texto: division en chunkings")
print("-----------------------------------------\n")

df = chunking.main()

print("\n\n-----------------------------------------")
print("5. Agregacion de embeddings")
print("-----------------------------------------\n")

df = embedding.main(df)
