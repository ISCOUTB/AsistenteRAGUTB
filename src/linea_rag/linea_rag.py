import sys
from src.ejecutar_experimento import ejecutar_experimento
import numpy as np

from config import (
    PLANTILLA_PROMPT_RAG,
    RUTA_RESPUESTAS_RAG,
    crear_cliente,
    crear_embedding
)

def find_top_k_passages(client, query, df_embeddings, k=5):
    query_embedding = crear_embedding(client, query)

    scores = np.dot(
        np.stack(df_embeddings["embeddings"]),
        query_embedding
    )

    top_k_idx = np.argsort(scores)[-k:][::-1]

    results = df_embeddings.iloc[top_k_idx].copy()
    results["score"] = scores[top_k_idx]

    return results


def preparar_texto(results):
    lista_docs = []
    for fila in results.iloc:
        texto = f"\n - DOCUMENTO: {fila["documento"]}"
        texto += f"\n - CAPITULO: {fila["capitulo"].replace("\n", " ")}"
        texto += f"\n - SCORE: {fila["score"]}"
        texto += f"\n - TEXTO: «{fila["chunk"].strip()}»"
        texto += "\n\n--------------------------------------------------\n"
        lista_docs.append(texto)

    return lista_docs

def crear_funcion_prompt_rag(df_embeddings, k=5):
    cliente = crear_cliente()

    def construir_prompt(pregunta):
        results = find_top_k_passages(
            cliente,
            pregunta.strip(),
            df_embeddings,
            k
        )
        lista_docs = preparar_texto(results)
        docs = "".join(lista_docs)

        prompt = PLANTILLA_PROMPT_RAG.format(
            pregunta=pregunta.strip(),
            docs=docs,
        )

        metadatos = {}
        for i in range(len(lista_docs)):
            metadatos[f"doc_enviado_{i}"] = lista_docs[i]
        
        return prompt, metadatos

    return construir_prompt


def main(df_embeddings, *, ver_existentes=False, reemplazar=False):

    construir_prompt = crear_funcion_prompt_rag(df_embeddings)

    try:
        ejecutar_experimento.main(
            ruta_salida=RUTA_RESPUESTAS_RAG,
            construir_prompt=construir_prompt,
            ver_existentes=ver_existentes,
            reemplazar=reemplazar,
        )
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario. Las respuestas guardadas se conservan.")
        sys.exit(130)