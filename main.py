# Cargar el contenido del .env antes de importar las librerias
import os
from dotenv import load_dotenv

ROOT = os.path.dirname(__file__)
load_dotenv(ROOT + "/.env")

import pandas as pd
import ast
import argparse
from src.fetching import fetching
from src.linea_base import linea_base
from src.extraccion_texto import extraccion_texto
from src.chunking import chunking
from src.embedding import embedding
from src.linea_rag import linea_rag
from src.ejecutar_experimento import calcular_metricas

from config import (
    CARPETA_TXT,
    CARPETA_PDF,
    CARPETA_CHUNKS,
    CARPETA_EMBEDDINGS,
    DIR_RESULTADOS_BASELINE,
    DIR_RESULTADOS_RAG,
    GEMINI_API_KEY,
    RUTA_RESPUESTAS_BASELINE,
    RUTA_RESPUESTAS_RAG
)

#Verificar si existe un directorio y si no, crearlo
def crear_si_no_existe(ruta):
    if not os.path.isdir(ruta):
        os.mkdir(ruta)


def main():
    parser = argparse.ArgumentParser(description="Asistente RAG UTB")
    parser.add_argument("--etapa",
                        help="Etapa a partir de la cual ejecutar.",
                        choices=["fetching", "preprocesamiento", "lineabase",
                                 "procesamiento", "embedding", "rag"])
    parser.add_argument("--only", action="store_true",
                        help="Ejecutar solo la etapa elegida. Sin esta opción, "
                             "se ejecutarán también las etapas siguientes.")
    args = parser.parse_args()

    if args.only and args.etapa is None:
        parser.error("--only requiere especificar --etapa")

    # Crear los directorios necesarios.
    directorios = [CARPETA_TXT, CARPETA_PDF, CARPETA_CHUNKS, CARPETA_EMBEDDINGS,
                   DIR_RESULTADOS_BASELINE, DIR_RESULTADOS_RAG]
    for directorio in directorios:
        crear_si_no_existe(directorio)

    if GEMINI_API_KEY is None:
        print("No se ha definido la clave GEMINI_API_KEY.")
        print("Ejecute 'python set_api_key.py SU_API_KEY'")
        return 1

    etapas = ["fetching", "preprocesamiento", "lineabase",
              "procesamiento", "embedding", "rag"]

    if args.etapa is None:
        indice_inicio = 0
        ejecutar_solo = False
    else:
        indice_inicio = etapas.index(args.etapa)
        ejecutar_solo = args.only

    etapas_a_ejecutar = (
        {args.etapa}
        if ejecutar_solo
        else set(etapas[indice_inicio:])
    )

    df = None

    print("\n              PIPELINE COMPLETO")

    if "fetching" in etapas_a_ejecutar:
        print("\n\n-----------------------------------------")
        print("1. Fetching de PDFs institucionales")
        print("-----------------------------------------\n")
        fetching.main()

    if "preprocesamiento" in etapas_a_ejecutar:
        print("\n\n-----------------------------------------")
        print("2. Extracción de texto y preprocesamiento de texto")
        print("-----------------------------------------\n")
        extraccion_texto.main()

    if "lineabase" in etapas_a_ejecutar:
        print("\n\n-----------------------------------------")
        print("3. Linea base: LLM sin RAG")
        print("-----------------------------------------\n")

        if os.path.exists(RUTA_RESPUESTAS_BASELINE):
            opcion = input(
                f"Ya existe la línea base en {RUTA_RESPUESTAS_BASELINE}.\n"
                "¿Quieres ver las respuestas ya generadas (v), regenerarlas (r) "
                "o continuar generando las respuestas (c)? [v/r/c]: "
            ).strip().lower()

            if opcion == "v":
                linea_base.main(ver_existentes=True)
            elif opcion == "r":
                linea_base.main(reemplazar=True)
            elif opcion == "c":
                linea_base.main()
        else:
            linea_base.main()

        print("\n- EVALUACIÓN DE LA LÍNEA BASE\n")
        print(f"Edita el archivo {RUTA_RESPUESTAS_BASELINE} para calificar exactitud, fidelidad y alucinación.")
        print("Después, regresa y presiona ENTER...")
        input()

        while calcular_metricas.main(
            RUTA_RESPUESTAS_BASELINE,
            DIR_RESULTADOS_BASELINE,
            "Métricas de la línea base (sin RAG)",
        ) == 1:
            print("\nTermina la calificación y presiona ENTER para continuar...")
            input()

    if "procesamiento" in etapas_a_ejecutar:
        print("\n\n-----------------------------------------")
        print("4. Procesamiento de texto: división en chunks")
        print("-----------------------------------------\n")
        df = chunking.main()

    if "embedding" in etapas_a_ejecutar:
        print("\n\n-----------------------------------------")
        print("5. Agregación de embeddings")
        print("-----------------------------------------\n")

        if not isinstance(df, pd.DataFrame):
            ruta_chunks = CARPETA_CHUNKS / "db.csv"
            if not ruta_chunks.exists():
                print("No existe la base de chunks. Ejecuta primero 'preprocesamiento' y 'procesamiento'.")
                return 1
            df = pd.read_csv(ruta_chunks)

        df = embedding.main(df)

    if "rag" in etapas_a_ejecutar:
        print("\n\n-----------------------------------------")
        print("6. Línea RAG: LLM + RAG")
        print("-----------------------------------------\n")

        if not isinstance(df, pd.DataFrame):
            ruta_embeddings = CARPETA_EMBEDDINGS / "db.csv"
            if not ruta_embeddings.exists():
                print("No existe la base de embeddings. Ejecuta primero 'procesamiento' y 'embedding'.")
                return 1
            df = pd.read_csv(ruta_embeddings, converters={"embeddings": ast.literal_eval})

        if os.path.exists(RUTA_RESPUESTAS_RAG):
            opcion = input(
                f"Ya existe la línea RAG en {RUTA_RESPUESTAS_RAG}.\n"
                "¿Quieres ver las respuestas ya generadas (v), regenerarlas (r) "
                "o continuar generando las respuestas (c)? [v/r/c]: "
            ).strip().lower()

            if opcion == "v":
                linea_rag.main(df, ver_existentes=True)
            elif opcion == "r":
                linea_rag.main(df, reemplazar=True)
            elif opcion == "c":
                linea_rag.main(df)
        else:
            linea_rag.main(df)

        print("\n- EVALUACIÓN DE LA LÍNEA RAG\n")
        print(f"Edita el archivo {RUTA_RESPUESTAS_RAG} para calificar exactitud, fidelidad y alucinación.")
        print("Después, regresa y presiona ENTER...")
        input()

        while calcular_metricas.main(
            RUTA_RESPUESTAS_RAG,
            DIR_RESULTADOS_RAG,
            "Métricas de la línea RAG (con RAG)",
        ) == 1:
            print("\nTermina la calificación y presiona ENTER para continuar...")
            input()

    return 0

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrumpido por el usuario. Puedes volver a ejecutar esta etapa con "
              "la opcion --etapa")