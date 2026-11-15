from src.a_fetching import fetching
from src.b_extraccion_texto import extraccion_texto
from src.c_chunking import chunking
import os

ROOT = os.getcwd()


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
print("3. Procesamiento de texto: division en chunkings")
print("-----------------------------------------\n")

df = chunking.main(ROOT)