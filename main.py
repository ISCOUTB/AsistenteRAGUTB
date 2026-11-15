from src.fetching import fetching
#from src.linea_base import linea_base
from src.extraccion_texto import extraccion_texto
from src.chunking import chunking
from src.embedding import embedding
import os
import getpass

ROOT = os.getcwd()

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




print("PIPELINE COMPLETO")

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

#linea_base.main(ROOT)

print("\n\n-----------------------------------------")
print("4. Procesamiento de texto: division en chunkings")
print("-----------------------------------------\n")


df = chunking.main(ROOT)

print("\n\n-----------------------------------------")
print("5. Agregacion de embeddings")
print("-----------------------------------------\n")

df = embedding.main(ROOT, df)
