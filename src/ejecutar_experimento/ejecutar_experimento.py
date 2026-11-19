"""
Lee `preguntas.csv`, envía cada pregunta al LLM y guarda
las respuestas en la ruta de salida especificada.

El CSV de salida incluye columnas vacías para calificar manualmente:
  exactitud (0-3), fidelidad (0-3), alucinacion (0-2),
   notas_evaluador y fecha_evaluacion.

"""

import csv
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from collections.abc import Callable

from config import (
    CODIFICACION_CSV,
    DELIMITADOR,
    MAX_TOKENS_SALIDA,
    MODELO,
    REINTENTOS,
    RUTA_PREGUNTAS,
    SEGUNDOS_ENTRE_LLAMADAS,
    TEMPERATURA,
    crear_cliente,
)

CAMPOS_ENTRADA = [
    "id",
    "tipo",
    "pregunta",
    "respuesta_esperada",
    "fuentes",
    "documento",
    "criterio_evaluacion",
]

CAMPOS_MANUALES = [
    "exactitud",
    "fidelidad",
    "alucinacion",
    "notas_evaluador",
    "fecha_evaluacion",
]

CAMPOS_SALIDA = CAMPOS_ENTRADA + [
    "respuesta_generada",
    "modelo",
    "fecha_hora",
    "error",
] + CAMPOS_MANUALES


def leer_preguntas(ruta):
    with open(ruta, "r", encoding=CODIFICACION_CSV, newline="") as f:
        reader = csv.DictReader(f, delimiter=DELIMITADOR)
        faltantes = [c for c in CAMPOS_ENTRADA if c not in (reader.fieldnames or [])]
        if faltantes:
            raise ValueError(f"Faltan columnas en {ruta}: {faltantes}")
        return [dict(row) for row in reader]


def leer_resultados(ruta):
    """Devuelve {id: fila} si el archivo existe."""
    ruta = Path(ruta)
    if not ruta.exists():
        return {}
    with open(ruta, "r", encoding=CODIFICACION_CSV, newline="") as f:
        reader = csv.DictReader(f, delimiter=DELIMITADOR)
        return {row["id"]: dict(row) for row in reader if row.get("id")}


def fila_vacia(pregunta):
    fila = {c: pregunta.get(c, "") for c in CAMPOS_ENTRADA}
    for c in CAMPOS_SALIDA:
        fila.setdefault(c, "")
    return fila


def limpiar_calificacion(fila):
    for c in CAMPOS_MANUALES:
        fila[c] = ""
    fila["notas_evaluador"] = "Respuesta regenerada; la calificación anterior quedó invalidada."


def extraer_retry_delay(exc):
    """Busca `retryDelay: '17s'` en el error 429 que devuelve la API."""
    candidatos = [str(exc)]
    for attr in ("details", "response_json", "message"):
        valor = getattr(exc, attr, None)
        if valor:
            candidatos.append(str(valor))
    for texto in candidatos:
        m = re.search(r"retryDelay['\"]?\s*[:=]\s*['\"]?(\d+(?:\.\d+)?)s", texto)
        if m:
            return float(m.group(1))
    return None


def es_error_de_cuota(exc):
    codigo = getattr(exc, "code", None)
    texto = str(exc)
    return codigo == 429 or "429" in texto or "RESOURCE_EXHAUSTED" in texto


def espera_reintento(exc, intento):
    """Segundos a esperar antes de reintentar, respetando el retryDelay de la API."""
    retry_delay = extraer_retry_delay(exc)
    if retry_delay is not None:
        return min(retry_delay + 1.0, 120.0)
    if es_error_de_cuota(exc):
        # Sin retryDelay explícito, esperamos bastante más que un backoff normal.
        return min(2 ** intento * 2, 60)
    return 2 ** intento


def llamar_modelo(cliente, prompt, modelo, temperatura, max_tokens):
    """Llama a Gemini con reintentos. Devuelve (texto, error, segundos)."""
    from google.genai import types

    ultimo_error = None
    inicio = time.perf_counter()
    for intento in range(1, REINTENTOS + 1):
        try:
            respuesta = cliente.models.generate_content(
                model=modelo,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperatura,
                    max_output_tokens=max_tokens,
                ),
            )
            texto = (respuesta.text or "").strip()
            if not texto:
                raise RuntimeError("La API devolvió una respuesta vacía.")
            return texto, "", round(time.perf_counter() - inicio, 2)
        except Exception as exc:  # noqa: BLE001 - queremos guardar cualquier error
            ultimo_error = f"{type(exc).__name__}: {exc}"
            if intento < REINTENTOS:
                espera = espera_reintento(exc, intento)
                print(f"    error (intento {intento}/{REINTENTOS}): {ultimo_error}")
                if es_error_de_cuota(exc):
                    print(f"    cuota agotada; se espera {espera:.1f}s según la API...")
                else:
                    print(f"    reintentando en {espera:.1f}s...")
                time.sleep(espera)
    return "", ultimo_error, round(time.perf_counter() - inicio, 2)


def escribir_csv(ruta, filas):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_suffix(ruta.suffix + ".tmp")
    with open(tmp, "w", encoding=CODIFICACION_CSV, newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=CAMPOS_SALIDA,
            delimiter=DELIMITADOR,
            quoting=csv.QUOTE_MINIMAL,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(filas)
    os.replace(tmp, ruta)

def mostrar_respuestas_csv(ruta):
    ruta = Path(ruta)
    if not ruta.exists():
        print(f"No existe el archivo: {ruta}")
        return

    with open(ruta, "r", encoding=CODIFICACION_CSV, newline="") as f:
        reader = csv.DictReader(f, delimiter=DELIMITADOR)
        filas = list(reader)

    if not filas:
        print(f"El archivo {ruta} está vacío.")
        return

    print("=" * 80)
    print(f"RESPUESTAS YA GENERADAS: {ruta}")
    print("=" * 80)

    for fila in filas:
        print(f"ID: {fila.get('id', '')}")
        print(f"Pregunta: {fila.get('pregunta', '')[:200]}")
        print(f"Respuesta: {fila.get('respuesta_generada', '')[:500]}")
        print("-" * 80)


def main(*,
         ruta_salida: Path,
         construir_prompt: Callable[[str], str],
         ruta_preguntas=RUTA_PREGUNTAS,
         modelo=MODELO,
         temperatura=TEMPERATURA,
         max_tokens=MAX_TOKENS_SALIDA,
         delay=SEGUNDOS_ENTRE_LLAMADAS,
         limite=None,
         reemplazar=False,
         dry_run=False,
         silencioso=False,
         ver_existentes=False):
    
    '''       Argumentos:
- preguntas: Ruta que apunta al CSV de preguntas
- salida: Ruta donde se guardaran las respuestas del LLM
- modelo: Modelo de Gemini
- temperatura: valor entre 0 y 1; entre más cercano a 0, más determinístico será el modelo
- max-tokens: maximo número de tokens de salida
- delay: Segundos entre llamadas
- limite: Procesar solo las primeras N preguntas
- reemplazar: Regenerar respuestas ya existentes
- dry-run: Mostrar prompts sin llamar a la API
- silencioso: No imprimir cada prompt
- ver-existentes: Muestra las respuestas ya guardadas
'''

    # Para únicamente ver respuestas ya generadas
    if ver_existentes:
        mostrar_respuestas_csv(ruta_salida)
        return

    preguntas = leer_preguntas(ruta_preguntas)
    if limite:
        preguntas = preguntas[: limite]

    anteriores = leer_resultados(ruta_salida)
    filas = []
    for pregunta in preguntas:
        fila = fila_vacia(pregunta)
        anterior = anteriores.get(pregunta["id"])
        if anterior:
            for c in CAMPOS_SALIDA:
                if c in anterior:
                    fila[c] = anterior[c]
        filas.append(fila)

    # Conservar en el CSV final las preguntas que ya no se están procesando
    # (por ejemplo, si se usó --limite en una corrida posterior).
    ids_en_curso = {p["id"] for p in preguntas}
    for pid, anterior in anteriores.items():
        if pid not in ids_en_curso:
            fila = fila_vacia(anterior)
            for c in CAMPOS_SALIDA:
                fila[c] = anterior.get(c, "")
            filas.append(fila)

    if dry_run:
        for fila in filas:
            print("=" * 70)
            print(f"{fila['id']} [{fila['tipo']}]")
            print(construir_prompt(fila))
        print("=" * 70)
        print(f"Dry-run: {len(filas)} preguntas. No se llamó a la API.")
        return

    cliente = crear_cliente()
    total = len(filas)
    procesadas = 0
    errores = 0

    print(f"Modelo: {modelo}")
    print(f"Preguntas: {total}")
    print(f"Salida: {ruta_salida}")
    print("-" * 70)

    for i, fila in enumerate(filas, start=1):
        ya_respondida = bool(fila.get("respuesta_generada", "").strip()) and not fila.get("error", "").strip()
        if ya_respondida and not reemplazar:
            print(f"[{i}/{total}] {fila['id']} ya respondida; se omite.")
            continue

        if reemplazar and ya_respondida:
            limpiar_calificacion(fila)

        prompt = construir_prompt(fila)
        if not silencioso:
            print(f"[{i}/{total}] {fila['id']} [{fila['tipo']}] {fila['pregunta'][:90]}...")

        texto, error, latencia = llamar_modelo(
            cliente,
            prompt,
            modelo,
            temperatura,
            max_tokens,
        )
        fila["respuesta_generada"] = texto
        fila["modelo"] = modelo
        fila["fecha_hora"] = datetime.now().isoformat(timespec="seconds")
        fila["error"] = error
        if error:
            errores += 1
            print(f"    ERROR: {error}")
        else:
            procesadas += 1
            print(f"    OK ({latencia}s, {len(texto.split())} palabras)")

        escribir_csv(ruta_salida, filas)

        if i < total and delay > 0:
            time.sleep(delay)

    escribir_csv(ruta_salida, filas)

    print("-" * 70)
    print(f"Respuestas nuevas/actualizadas: {procesadas}")
    print(f"Errores: {errores}")
    print(f"Archivo: {Path(ruta_salida).resolve()}")
    if errores:
        print("Puedes volver a ejecutar el script: los errores se reintentan y las respuestas válidas se conservan.")
        sys.exit(1)