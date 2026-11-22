from google import genai
from google.genai.errors import ClientError
import ast
import os
import pandas as pd
import re
import time

from config import (
    CARPETA_EMBEDDINGS,
    crear_cliente,
    crear_embedding
)


RUTA_CSV = CARPETA_EMBEDDINGS / "db.csv"
RUTA_HTML = CARPETA_EMBEDDINGS / "db.html"

# Margen prudente sobre el límite gratuito de 100 solicitudes por minuto.
ESPERA_ENTRE_SOLICITUDES = 0.65
# Estimación de aproximadamente 4 caracteres por token.
LIMITE_TOKENS_POR_MINUTO = 30000
CARACTERES_POR_TOKEN = 4


def convertir_embedding_guardado(valor):
    """Convierte el texto de la celda CSV a una lista de floats, si existe."""
    if valor is None:
        return None
    if isinstance(valor, list):
        return valor
    if isinstance(valor, float) and __import__("math").isnan(valor):
        return None

    try:
        convertido = ast.literal_eval(str(valor))
        return convertido if isinstance(convertido, list) else None
    except (SyntaxError, ValueError):
        return None


def cargar_progreso(df_chunks):
    """Carga embeddings anteriores y los incorpora a las filas coincidentes."""
    df_resultado = df_chunks.copy()

    # Pandas infiere float64 si la columna se inicia solo con None, y luego
    # no puede asignar una lista de valores numéricos a esa columna.
    df_resultado["embeddings"] = pd.Series(
        [None] * len(df_resultado),
        index=df_resultado.index,
        dtype="object",
    )

    if not RUTA_CSV.exists():
        return df_resultado

    try:
        df_guardado = __import__("pandas").read_csv(RUTA_CSV)
    except Exception as error:
        print(f"No se pudo leer el progreso previo: {error}")
        return df_resultado

    if "chunk" not in df_guardado.columns or "embeddings" not in df_guardado.columns:
        return df_resultado

    df_guardado["embeddings"] = df_guardado["embeddings"].apply(convertir_embedding_guardado)
    embeddings_por_chunk = dict(zip(df_guardado["chunk"], df_guardado["embeddings"]))

    recuperados = 0
    for indice, fila in df_resultado.iterrows():
        embedding = embeddings_por_chunk.get(fila["chunk"])
        if embedding:
            df_resultado.at[indice, "embeddings"] = embedding
            recuperados += 1

    print(f"Recuperadas {recuperados} filas con embeddings ya guardados")
    return df_resultado


def obtener_segundos_reintento(error):
    """Obtiene retryDelay o el tiempo indicado en el mensaje de una excepción 429."""
    texto = str(error)

    coincidencias = re.findall(r"retry(?:Delay)?['\"]?:?\s*['\"]?(\d+(?:\.\d+)?)s", texto, re.I)
    if coincidencias:
        return float(coincidencias[-1])

    coincidencias = re.findall(r"Please retry in ([\d.]+)s", texto, re.I)
    if coincidencias:
        return float(coincidencias[-1])

    return 60.0  # Devolver 60 segundos si no encuentra el tiempo de reintento


def guardar_progreso(df_chunks):
    """
    Guarda CSV y HTML en archivos temporales, para no sobreescribir 
    y arriesgarse a corromper los archivos principales.
    Reemplaza al terminar cada escritura."""
    CARPETA_EMBEDDINGS.mkdir(parents=True, exist_ok=True)

    csv_temporal = RUTA_CSV.with_suffix(".csv.tmp")
    html_temporal = RUTA_HTML.with_suffix(".html.tmp")

    df_chunks.to_csv(csv_temporal, index=False)
    df_chunks.to_html(html_temporal)
    os.replace(csv_temporal, RUTA_CSV)
    os.replace(html_temporal, RUTA_HTML)


def crear_embedding_con_reintentos(client, texto):
    """
    Reintenta al obtener error 429 esperando exactamente el tiempo
    indicado por la API.
    """
    intento = 0

    while True:
        try:
            return crear_embedding(client, texto)
        except ClientError as error:
            if getattr(error, "status_code", None) != 429:
                raise

            intento += 1
            espera = obtener_segundos_reintento(error)
            print(
                f"Límite alcanzado (Error 429). Esperando {espera:.1f} segundos "
                f"antes del reintento {intento}."
            )
            time.sleep(espera + 1.0)


def main(df_chunks):
    # Conectar a Gemini API

    client = crear_cliente()
    df_chunks = cargar_progreso(df_chunks)
    cantidad = len(df_chunks)

    # Lleva una ventana aproximada de consumo de tokens por 60 segundos.
    eventos_tokens = []
    creado = 0

    for i, fila in df_chunks.iterrows():
        embedding_actual = convertir_embedding_guardado(fila.get("embeddings"))
        if embedding_actual:
            continue

        ahora = time.monotonic()
        eventos_tokens = [(momento, tokens) for momento, tokens in eventos_tokens if ahora - momento < 60]
        tokens_estimados = max(1, len(str(fila["chunk"])) // CARACTERES_POR_TOKEN)
        tokens_en_minuto = sum(tokens for _, tokens in eventos_tokens)

        if tokens_en_minuto + tokens_estimados > LIMITE_TOKENS_POR_MINUTO:
            espera = 60 - (ahora - eventos_tokens[0][0])
            print(f"Límite aproximado de 30000 tokens por minuto. Esperando {espera:.1f} segundos.")
            time.sleep(max(1.0, espera + 1.0))
            eventos_tokens = []

        # Llamar al modelo de embeddings. Se le pasa informacion sobre el documento,
        # capitulo y el chunk. Asi el modelo de embeddings captura mejor el contexto
        # de cada fragmento
        texto = f"{fila['documento']}, {fila['capitulo']}\n\n{fila['chunk']}"
        embedding = crear_embedding_con_reintentos(client, texto)

        momento_envio = time.monotonic()
        eventos_tokens.append((momento_envio, tokens_estimados))
        df_chunks.at[i, "embeddings"] = embedding
        creado += 1

        # Persiste inmediatamente cada fila, no solo al terminar todo el proceso.
        guardar_progreso(df_chunks)

        if creado % 5 == 0:
            completados = sum(
                convertir_embedding_guardado(df_chunks.at[j, "embeddings"]) is not None
                for j in range(cantidad)
            )
            print(f"Progreso: {completados} embeddings de {cantidad}")

        time.sleep(ESPERA_ENTRE_SOLICITUDES)

    completados = sum(
        convertir_embedding_guardado(df_chunks.at[j, "embeddings"]) is not None
        for j in range(cantidad)
    )
    print(f"Progreso: completados {completados} embeddings")

    if completados:
        primer_embedding = next(
            valor for valor in df_chunks["embeddings"]
            if convertir_embedding_guardado(valor)
        )
        primer_embedding = convertir_embedding_guardado(primer_embedding)
        print("Tamaño de vector:", len(primer_embedding))

    guardar_progreso(df_chunks)
    print(f"Guardado en {RUTA_CSV}")
    print(f"Guardado en {RUTA_HTML}")

    return df_chunks