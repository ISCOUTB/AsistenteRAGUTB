"""
Calcula las métricas de la línea base, en general y por tipo de pregunta.

Lee `resultados/respuestas_baseline.csv` (o el archivo que indiques) y genera:
  - resultados/metricas_generales.csv
  - resultados/metricas_por_tipo.csv
  - resultados/metricas_por_documento.csv
  - resultados/metricas_control.csv
  - resultados/metricas.md

Solo se incluyen en los cálculos las filas con exactitud, fidelidad y
alucinación diligenciadas y dentro de rango.

Uso:
  python calcular_metricas.py
  python calcular_metricas.py --archivo resultados/respuestas_baseline.csv
"""

import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    CODIFICACION_CSV,
    DELIMITADOR,
    DESCRIPCION_TIPOS,
    DIR_RESULTADOS_BASELINE,
    ESCALA_ALUCINACION,
    ESCALA_EXACTITUD,
    ESCALA_FIDELIDAD,
    RUTA_RESPUESTAS_BASELINE,
    TIPOS,
)


def normalizar_si_no(valor):
    if pd.isna(valor):
        return np.nan
    v = str(valor).strip().lower()
    if v in ("si", "sí", "s", "1", "true", "verdadero"):
        return "si"
    if v in ("no", "n", "0", "false", "falso"):
        return "no"
    return np.nan


def cargar(archivo):
    df = pd.read_csv(archivo, sep=DELIMITADOR, encoding=CODIFICACION_CSV, dtype=str)
    requeridas = ["id", "tipo", "pregunta", "respuesta_generada", "exactitud", "fidelidad", "alucinacion"]
    faltantes = [c for c in requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas en {archivo}: {faltantes}")

    for col in ["exactitud", "fidelidad", "alucinacion"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["error"] = df["error"].fillna("").astype(str).str.strip() if "error" in df.columns else ""
    df["respuesta_generada"] = df.get("respuesta_generada", "").fillna("").astype(str)

    # Validación de rangos
    valida = (
        df["exactitud"].between(*ESCALA_EXACTITUD)
        & df["fidelidad"].between(*ESCALA_FIDELIDAD)
        & df["alucinacion"].between(*ESCALA_ALUCINACION)
    )
    df["evaluada"] = valida & df["exactitud"].notna() & df["fidelidad"].notna() & df["alucinacion"].notna()

    invalidas = df[~df["evaluada"]]
    invalidas = invalidas[invalidas[["exactitud", "fidelidad", "alucinacion"]].notna().any(axis=1)]
    if not invalidas.empty:
        print("Advertencia: hay filas con calificaciones fuera de rango o incompletas; se excluyen:")
        print(invalidas[["id", "exactitud", "fidelidad", "alucinacion"]].to_string(index=False))
        print()

    return df


def metricas_grupo(g):
    n_total = len(g)
    ev = g[g["evaluada"]]
    n = len(ev)
    out = {
        "n_total": n_total,
        "n_evaluadas": n,
        "cobertura_pct": (n / n_total * 100) if n_total else np.nan,
    }
    if n == 0:
        for k in [
            "exactitud_media",
            "exactitud_sobre_100",
            "exactitud_plena_pct",
            "exactitud_aceptable_pct",
            "exactitud_baja_pct",
            "fidelidad_media",
            "fidelidad_sobre_100",
            "fidelidad_plena_pct",
            "fidelidad_baja_pct",
            "alucinacion_media",
            "sin_alucinacion_pct",
            "con_alucinacion_pct",
            "alucinacion_grave_pct",
            "respuesta_ideal_pct",
        ]:
            out[k] = np.nan
        return out

    out["exactitud_media"] = ev["exactitud"].mean()
    out["exactitud_sobre_100"] = ev["exactitud"].mean() / ESCALA_EXACTITUD[1] * 100
    out["exactitud_plena_pct"] = (ev["exactitud"] == ESCALA_EXACTITUD[1]).mean() * 100
    out["exactitud_aceptable_pct"] = (ev["exactitud"] >= 2).mean() * 100
    out["exactitud_baja_pct"] = (ev["exactitud"] <= 1).mean() * 100

    out["fidelidad_media"] = ev["fidelidad"].mean()
    out["fidelidad_sobre_100"] = ev["fidelidad"].mean() / ESCALA_FIDELIDAD[1] * 100
    out["fidelidad_plena_pct"] = (ev["fidelidad"] == ESCALA_FIDELIDAD[1]).mean() * 100
    out["fidelidad_baja_pct"] = (ev["fidelidad"] <= 1).mean() * 100

    out["alucinacion_media"] = ev["alucinacion"].mean()
    out["sin_alucinacion_pct"] = (ev["alucinacion"] == 0).mean() * 100
    out["con_alucinacion_pct"] = (ev["alucinacion"] >= 1).mean() * 100
    out["alucinacion_grave_pct"] = (ev["alucinacion"] == ESCALA_ALUCINACION[1]).mean() * 100

    out["respuesta_ideal_pct"] = (
        (ev["exactitud"] == ESCALA_EXACTITUD[1])
        & (ev["fidelidad"] == ESCALA_FIDELIDAD[1])
        & (ev["alucinacion"] == 0)
    ).mean() * 100
    return out


def tabla_por(df, columna, orden=None):
    filas = []
    for valor, grupo in df.groupby(columna, dropna=False, sort=False):
        fila = {columna: valor}
        fila.update(metricas_grupo(grupo))
        filas.append(fila)
    tabla = pd.DataFrame(filas)
    if orden:
        tabla["_orden"] = tabla[columna].map({v: i for i, v in enumerate(orden)}).fillna(999)
        tabla = tabla.sort_values("_orden").drop(columns="_orden")
    return tabla.reset_index(drop=True)


def fmt_pct(x):
    return "—" if pd.isna(x) else f"{x:.1f}%"


def fmt_num(x):
    return "—" if pd.isna(x) else f"{x:.2f}"


def tabla_markdown(df, columnas, etiquetas):
    encabezado = "| " + " | ".join(etiquetas.values()) + " |"
    separador = "|" + "|".join(["---"] * len(columnas)) + "|"
    lineas = [encabezado, separador]
    for _, fila in df.iterrows():
        celdas = []
        for c in columnas:
            v = fila[c]
            if c.endswith("_pct"):
                celdas.append(fmt_pct(v))
            elif isinstance(v, (int, float, np.integer, np.floating)):
                celdas.append(fmt_num(v) if c not in ("n_total", "n_evaluadas") else str(int(v)))
            else:
                celdas.append(str(v))
        lineas.append("| " + " | ".join(celdas) + " |")
    return "\n".join(lineas)


def main():
    parser = argparse.ArgumentParser(description="Calcula métricas de la línea base")
    parser.add_argument("--archivo", default=str(RUTA_RESPUESTAS_BASELINE), help="CSV de respuestas calificadas")
    parser.add_argument("--salida-dir", default=str(DIR_RESULTADOS_BASELINE), help="Carpeta de salida")
    args = parser.parse_args()

    archivo = Path(args.archivo)
    salida = Path(args.salida_dir)
    salida.mkdir(parents=True, exist_ok=True)

    df = cargar(archivo)
    n_total = len(df)
    n_evaluadas = int(df["evaluada"].sum())
    n_errores = int((df["error"] != "").sum())
    n_sin_respuesta = int((df["respuesta_generada"].str.strip() == "").sum())

    print(f"Archivo: {archivo}")
    print(f"Filas: {n_total} | Calificadas: {n_evaluadas} | Sin calificar: {n_total - n_evaluadas}")
    print(f"Errores de API: {n_errores} | Sin respuesta generada: {n_sin_respuesta}")

    if n_evaluadas < 50:
        print("\nCalificación no terminada. Llena exactitud, fidelidad y alucinación")
        print("en el CSV y vuelve a ejecutar este script.")
        return 1

    general = metricas_grupo(df)
    general_df = pd.DataFrame(
        [
            ("Preguntas totales", n_total),
            ("Preguntas calificadas", n_evaluadas),
            ("Cobertura de calificación (%)", round(general["cobertura_pct"], 2)),
            ("Errores de API", n_errores),
            ("Sin respuesta generada", n_sin_respuesta),
            ("Exactitud media (0-3)", round(general["exactitud_media"], 4)),
            ("Exactitud sobre 100", round(general["exactitud_sobre_100"], 2)),
            ("Exactitud plena (%)", round(general["exactitud_plena_pct"], 2)),
            ("Exactitud aceptable (>=2) (%)", round(general["exactitud_aceptable_pct"], 2)),
            ("Exactitud baja (<=1) (%)", round(general["exactitud_baja_pct"], 2)),
            ("Fidelidad media (0-3)", round(general["fidelidad_media"], 4)),
            ("Fidelidad sobre 100", round(general["fidelidad_sobre_100"], 2)),
            ("Fidelidad plena (%)", round(general["fidelidad_plena_pct"], 2)),
            ("Fidelidad baja (<=1) (%)", round(general["fidelidad_baja_pct"], 2)),
            ("Alucinación media (0-2)", round(general["alucinacion_media"], 4)),
            ("Sin alucinación (%)", round(general["sin_alucinacion_pct"], 2)),
            ("Con alucinación (>=1) (%)", round(general["con_alucinacion_pct"], 2)),
            ("Alucinación grave (2) (%)", round(general["alucinacion_grave_pct"], 2)),
            ("Respuesta ideal: exactitud 3 + fidelidad 3 + alucinación 0 (%)", round(general["respuesta_ideal_pct"], 2)),
        ],
        columns=["metrica", "valor"],
        dtype=object,
    )
    general_df.to_csv(salida / "metricas_generales.csv", sep=DELIMITADOR, encoding=CODIFICACION_CSV, index=False)

    por_tipo = tabla_por(df, "tipo", orden=TIPOS)
    por_tipo["descripcion"] = por_tipo["tipo"].map(DESCRIPCION_TIPOS).fillna("")
    por_tipo.to_csv(salida / "metricas_por_tipo.csv", sep=DELIMITADOR, encoding=CODIFICACION_CSV, index=False)

    por_doc = tabla_por(df, "documento", orden=None)
    por_doc.to_csv(salida / "metricas_por_documento.csv", sep=DELIMITADOR, encoding=CODIFICACION_CSV, index=False)


    # --- Reporte Markdown -------------------------------------------------
    columnas_tipo = [
        "tipo",
        "n_evaluadas",
        "exactitud_media",
        "exactitud_plena_pct",
        "fidelidad_media",
        "fidelidad_plena_pct",
        "alucinacion_media",
        "con_alucinacion_pct",
        "respuesta_ideal_pct",
    ]
    etiquetas_tipo = {
        "tipo": "Tipo",
        "n_evaluadas": "n",
        "exactitud_media": "Exact. media",
        "exactitud_plena_pct": "Exact. plena",
        "fidelidad_media": "Fidel. media",
        "fidelidad_plena_pct": "Fidel. plena",
        "alucinacion_media": "Aluc. media",
        "con_alucinacion_pct": "Con aluc.",
        "respuesta_ideal_pct": "Ideal",
    }

    columnas_doc = ["documento", "n_evaluadas", "exactitud_media", "fidelidad_media", "alucinacion_media", "con_alucinacion_pct"]
    etiquetas_doc = {
        "documento": "Documento",
        "n_evaluadas": "n",
        "exactitud_media": "Exactitud",
        "fidelidad_media": "Fidelidad",
        "alucinacion_media": "Alucinación",
        "con_alucinacion_pct": "Con aluc.",
    }

    columnas_control = [
        "grupo_control",
        "n_evaluadas",
        "exactitud_media",
        "fidelidad_media",
        "alucinacion_media",
        "con_alucinacion_pct",
    ]
    etiquetas_control = {
        "grupo_control": "Grupo",
        "n_evaluadas": "n",
        "exactitud_media": "Exactitud",
        "fidelidad_media": "Fidelidad",
        "alucinacion_media": "Alucinación",
        "con_alucinacion_pct": "Con aluc.",
    }

    modelos = sorted(set(df["modelo"].dropna().astype(str))) if "modelo" in df.columns else []
    tipos_ordenados = [t for t in TIPOS if t in set(df["tipo"])]

    mejor_tipo = por_tipo.dropna(subset=["exactitud_media"]).sort_values("exactitud_media", ascending=False).head(1)
    peor_tipo = por_tipo.dropna(subset=["exactitud_media"]).sort_values("exactitud_media").head(1)
    mas_alucina = por_tipo.dropna(subset=["con_alucinacion_pct"]).sort_values("con_alucinacion_pct", ascending=False).head(1)

    lineas = []
    lineas.append("# Métricas de la línea base (sin RAG)")
    lineas.append("")
    lineas.append(f"Generado: {datetime.now().isoformat(timespec='seconds')}")
    lineas.append("")
    lineas.append(f"- Archivo de respuestas: `{archivo}`")
    lineas.append(f"- Modelos usados: {', '.join(modelos) if modelos else '—'}")
    lineas.append(f"- Preguntas totales: {n_total}")
    lineas.append(f"- Preguntas calificadas: {n_evaluadas} ({general['cobertura_pct']:.1f}%)")
    lineas.append(f"- Errores de API: {n_errores}")
    lineas.append("")
    lineas.append("## Métricas generales")
    lineas.append("")
    lineas.append("| Métrica | Valor |")
    lineas.append("|---|---|")
    for _, r in general_df.iterrows():
        lineas.append(f"| {r['metrica']} | {r['valor']} |")
    lineas.append("")
    lineas.append("## Métricas por tipo de pregunta")
    lineas.append("")
    lineas.append(tabla_markdown(por_tipo, columnas_tipo, etiquetas_tipo))
    lineas.append("")
    lineas.append("## Métricas por documento")
    lineas.append("")
    lineas.append(tabla_markdown(por_doc, columnas_doc, etiquetas_doc))
    lineas.append("")
    lineas.append("## Preguntas de control vs. preguntas del corpus")
    lineas.append("")
    lineas.append("## Lectura rápida")
    lineas.append("")
    if not mejor_tipo.empty:
        r = mejor_tipo.iloc[0]
        lineas.append(f"- Mejor exactitud media: **{r['tipo']}** ({r['exactitud_media']:.2f}/3).")
    if not peor_tipo.empty:
        r = peor_tipo.iloc[0]
        lineas.append(f"- Peor exactitud media: **{r['tipo']}** ({r['exactitud_media']:.2f}/3).")
    if not mas_alucina.empty:
        r = mas_alucina.iloc[0]
        lineas.append(f"- Mayor tasa de alucinación: **{r['tipo']}** ({r['con_alucinacion_pct']:.1f}% de respuestas con al menos una invención).")
    lineas.append(
        "- La línea base sirve como referencia: si el RAG no supera estos valores, la recuperación no está aportando."
    )
    lineas.append("")
    lineas.append("## Definiciones")
    lineas.append("")
    lineas.append("- **Exactitud (0-3):** 0 = incorrecta; 1 = correcta en algo pero con errores importantes; 2 = parcialmente correcta u omite datos clave; 3 = correcta y completa frente a la respuesta esperada.")
    lineas.append("- **Fidelidad (0-3):** 0 = no se sustenta en las fuentes o las contradice; 1 = mezcla datos fieles con inventados; 2 = mayormente fiel con imprecisiones; 3 = todos los datos relevantes son verificables en las fuentes.")
    lineas.append("- **Alucinación (0-2):** 0 = no inventa; 1 = inventa un detalle menor (cifra, plazo, nombre, correo); 2 = inventa hechos centrales o contradice la fuente.")
    lineas.append("- **Respuesta ideal:** exactitud 3, fidelidad 3 y alucinación 0.")
    lineas.append("- **Abstención:** el modelo dice explícitamente que no tiene la información (esperado sobre todo en `fuera_de_alcance`).")
    lineas.append("")

    (salida / "metricas.md").write_text("\n".join(lineas), encoding="utf-8")

    # --- Consola ----------------------------------------------------------
    print("\nMÉTRICAS GENERALES")
    for _, r in general_df.iterrows():
        print(f"  {r['metrica']}: {r['valor']}")

    print("\nMÉTRICAS POR TIPO")
    print(
        por_tipo[
            [
                "tipo",
                "n_evaluadas",
                "exactitud_media",
                "fidelidad_media",
                "alucinacion_media",
                "con_alucinacion_pct",
                "respuesta_ideal_pct",
            ]
        ].to_string(index=False)
    )
    print(f"\nReporte: {(salida / 'metricas.md').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
