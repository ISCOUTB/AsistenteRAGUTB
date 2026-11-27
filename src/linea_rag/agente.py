from config import (
    CARPETA_EMBEDDINGS,
    MODELO,
    TEMPERATURA,
    MAX_TOKENS_SALIDA,
    crear_cliente
)

from src.linea_rag.linea_rag import (
    crear_funcion_prompt_rag
)

from src.ejecutar_experimento.ejecutar_experimento import (
    llamar_modelo
)

import pandas as pd
import ast

def main(
        pregunta: str,
        *, 
        modelo = MODELO, 
        temperatura = TEMPERATURA,
        max_tokens=MAX_TOKENS_SALIDA,
        k=5
    ) -> dict:

    ruta_embeddings = CARPETA_EMBEDDINGS / "db.csv"
    if not ruta_embeddings.exists():
        print("No existe la base de embeddings. Ejecuta primero 'procesamiento' y 'embedding'.")
        return 1
    df = pd.read_csv(ruta_embeddings, converters={"embeddings": ast.literal_eval})

    construir_prompt = crear_funcion_prompt_rag(df, k)
    prompt, docs = construir_prompt(pregunta)

    client = crear_cliente()
    resp, error, latencia = llamar_modelo(
        client,
        prompt,
        modelo,
        temperatura,
        max_tokens,
    )

    return {'docs_recuperados': docs, 'contenido': resp,
            'error': error, 'latencia': latencia}

