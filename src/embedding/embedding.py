from google import genai
import pandas as pd
import time

from config import (
    CARPETA_EMBEDDINGS,
    GEMINI_API_KEY
)

# Llamar a modelo de embeddings

def crear_embedding(client, model, contents):
    result = client.models.embed_content(model=model, contents=contents)
    return result.embeddings[0].values

def main(df_chunks):
    
    # Conectar a Gemini API

    client = genai.Client(api_key=GEMINI_API_KEY)

    # Crear los embeddings por cada chunk

    modelo = "gemini-embedding-2"
    embeddings = []
    cantidad = len(df_chunks)

    # El limite gratuito del modelo de embeddings de Gemini
    # es de 100 peticiones por minuto = 1.6667 peticiones por segundo

    #  60 segundos
    # -------------- = 0.6 segundos de espera por peticion
    # 100 peticiones

    # en el codigo se usan 0.61 segundos de espera para no exceder
    # la cuota gratuita

    espera = 0.61

    for i, chunk in enumerate(df_chunks["chunk"]):
        emb = crear_embedding(client, modelo, chunk)
        embeddings.append(emb)
        
        time.sleep(espera)
        if ( (i+1)%10 ) == 0:
            print(f"Progreso: {i+1} embeddings de {cantidad}")

    print(f"Progreso: completados {cantidad} embeddings")

    df_chunks["embeddings"] = embeddings

    print("Tamaño de vector:", len(df_chunks["embeddings"][0]))

    print("\nDataframe resultante:\n")
    print(df_chunks)

    # -------------- Guardar como csv y html ---------------- #

    df_chunks.to_csv(CARPETA_EMBEDDINGS + "/db.csv", index=False)
    df_chunks.to_html(CARPETA_EMBEDDINGS + "/db.html", index=False)

    print(f"Guardado en {CARPETA_EMBEDDINGS}/db.csv")
    print(f"Guardado en {CARPETA_EMBEDDINGS}/db.html")

    return df_chunks