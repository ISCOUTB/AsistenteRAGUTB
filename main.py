from src.fetching import fetching
from src.linea_base import linea_base
from src.linea_base import calcular_metricas
from src.extraccion_texto import extraccion_texto
from src.chunking import chunking
from src.embedding import embedding
import os
import getpass

ROOT = os.getcwd()
ruta_respuestas = os.path.join(ROOT, "experiments", "linea_base", "respuestas_baseline.csv")

# Verificar si existe la clave de Gemini API

try:
    key = os.environ["GEMINI_API_KEY"]
    print("Hay una clave GEMINI_API_KEY establecida.")
    r = input("Desea cambiarla (s/n)? ").lower()
    if r == "s":
        os.environ["GEMINI_API_KEY"] = getpass.getpass("Ingrese o pegue la api key (no se mostrará): ")

except:
    print("Clave GEMINI_API_KEY no establecida.")
    os.environ["GEMINI_API_KEY"] = getpass.getpass("Ingrese o pegue la api key (no se mostrará): ")




print("\n              PIPELINE COMPLETO")

print("\n\n-----------------------------------------")
print("1. Fetching de PDFs institucionales")
print("-----------------------------------------\n")

fetching.main(ROOT)

print("\n\n-----------------------------------------")
print("2. Extracción de texto y preprocesamiento de texto")
print("-----------------------------------------\n")

extraccion_texto.main(ROOT)

print("\n\n-----------------------------------------")
print("3. Linea base: LLM sin RAG")
print("-----------------------------------------\n")

if os.path.exists(ruta_respuestas):
    opcion = input(
        f"Ya existe la línea base en {ruta_respuestas}.\n"
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
print(f"Edita el archivo {ruta_respuestas} para calificar exactitud, fidelidad y alucinación.")
print(f"Después, regresa y presiona ENTER...")

input()

while calcular_metricas.main() == 1:
    input("Termina la calificación y presiona ENTER para continuar...")

print("\n\n-----------------------------------------")
print("4. Procesamiento de texto: division en chunkings")
print("-----------------------------------------\n")

df = chunking.main(ROOT)

print("\n\n-----------------------------------------")
print("5. Agregacion de embeddings")
print("-----------------------------------------\n")

df = embedding.main(ROOT, df)
