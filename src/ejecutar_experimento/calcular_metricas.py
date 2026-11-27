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

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    CODIFICACION_CSV,
    DELIMITADOR,
    DESCRIPCION_TIPOS,
    ESCALA_ALUCINACION,
    ESCALA_EXACTITUD,
    ESCALA_FIDELIDAD,
    TIPOS,
    ROOT
)

def redondear_si_numero(valor, decimales):
    if type(valor) in [float,int]:
        return round(valor, decimales)
    else:
        return valor



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
        "%cobertura": (n / n_total * 100) if n_total else np.nan,
    }
    if n == 0:
        for k in [
            "%exactitud",
            "%fidelidad",
            "tasa_alucinacion",

            "%exactitud_plena",
            "%exactitud_aceptable",
            "%exactitud_baja",
            "%fidelidad_plena",
            "%fidelidad_baja",
            "%sin_alucinacion",
            "%alucinacion_grave",
            "%respuesta_perfecta",
        ]:
            out[k] = np.nan
        return out

    # ----------------------------------
    # Métricas principales
    # ----------------------------------
    
    # Porcentaje de exactitud y de fidelidad: como están en una escala de 0 a 3, se
    # promedia, se divide entre 3 y se multiplica por 100%
    out["%exactitud"] = ev["exactitud"].mean() / ESCALA_EXACTITUD[1] * 100
    out["%fidelidad"] = ev["fidelidad"].mean() / ESCALA_FIDELIDAD[1] * 100
    out["tasa_alucinacion"] = (ev["alucinacion"] >= 1).mean() * 100

    # ----------------------------------
    # Otras metricas
    # ----------------------------------

    # Porcentaje de exactitud y fidelidad plena: respuestas que obtuvieron exactamente
    # 3 de exactitud o de fidelidad
    out["%exactitud_plena"] = (ev["exactitud"] == ESCALA_EXACTITUD[1]).mean() * 100
    out["%fidelidad_plena"] = (ev["fidelidad"] == ESCALA_FIDELIDAD[1]).mean() * 100
    
    out["%exactitud_aceptable"] = (ev["exactitud"] >= 2).mean() * 100

    out["%exactitud_baja"] = (ev["exactitud"] <= 1).mean() * 100
    out["%fidelidad_baja"] = (ev["fidelidad"] <= 1).mean() * 100

    out["%sin_alucinacion"] = (ev["alucinacion"] == 0).mean() * 100
    out["%alucinacion_grave"] = (ev["alucinacion"] == ESCALA_ALUCINACION[1]).mean() * 100

    # Porcentaje de respuestas perfectas: aquellas que obtuvieron 3 en exactitud,
    # 3 en fidelidad y 0 en alucinacion
    out["%respuesta_perfecta"] = (
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
            if c.startswith("%"):
                celdas.append(fmt_pct(v))
            elif isinstance(v, (int, float, np.integer, np.floating)):
                celdas.append(fmt_num(v) if c not in ("n_total", "n_evaluadas") else str(int(v)))
            else:
                celdas.append(str(v))
        lineas.append("| " + " | ".join(celdas) + " |")
    return "\n".join(lineas)


def main(ruta_respuestas, dir_resultados, titulo):
    archivo = Path(ruta_respuestas)
    salida = Path(dir_resultados)
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

    # En la linea base no aplica fidelidad ni % respuestas perfectas
    linea_base = titulo == "Métricas de la línea base (sin RAG)"

    if linea_base:
        general["%fidelidad"] = "N/A"
        general["%fidelidad_plena"] = "N/A"
        general["%fidelidad_baja"] = "N/A"
        general["%respuesta_perfecta"] = "N/A"

    general_df = pd.DataFrame(
        [
            ("Preguntas totales", n_total),
            ("Preguntas calificadas", n_evaluadas),
            ("Cobertura de calificación (%)", round(general["%cobertura"], 2)),
            ("Errores de API", n_errores),
            ("Sin respuesta generada", n_sin_respuesta),
            
            # Métricas principales
            ("Exactitud (%)", round(general["%exactitud"], 2)),
            ("Fidelidad (%)", redondear_si_numero(general["%fidelidad"], 2)),
            ("Tasa de alucinación (%)", round(general["tasa_alucinacion"], 2)),
            ("Respuesta perfecta (%)", redondear_si_numero(general["%respuesta_perfecta"], 2)),

            # Otras
            ("Exactitud plena (=3) (%)", round(general["%exactitud_plena"], 2)),
            ("Exactitud aceptable (>=2) (%)", round(general["%exactitud_aceptable"], 2)),
            ("Exactitud baja (<=1) (%)", round(general["%exactitud_baja"], 2)),
            
            ("Fidelidad plena (%)", redondear_si_numero(general["%fidelidad_plena"], 2)),
            ("Fidelidad baja (<=1) (%)", redondear_si_numero(general["%fidelidad_baja"], 2)),
            
            ("Sin alucinación (%)", round(general["%sin_alucinacion"], 2)),
            ("Alucinación grave (=2) (%)", round(general["%alucinacion_grave"], 2)),
            
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
    metricas_principales = [
        "Exactitud (%)",
        "Fidelidad (%)",
        "Tasa de alucinación (%)",
        "Respuesta perfecta (%)"
    ]

    columnas_tipo = [
        "tipo",
        "n_evaluadas",
        "%exactitud",
        "%fidelidad",
        "tasa_alucinacion",
        "%respuesta_perfecta",
    ]
    etiquetas_tipo = {
        "tipo": "Tipo",
        "n_evaluadas": "n",
        "%exactitud": "Porc. Exact.",
        "%fidelidad": "Porc. Fidel.",
        "tasa_alucinacion": "Tasa aluc.",
        "%respuesta_perfecta": "Porc. Resp. Perfectas",
    }

    columnas_doc = ["documento", "n_evaluadas", "%exactitud", "%fidelidad", "tasa_alucinacion", "%respuesta_perfecta"]
    etiquetas_doc = {
        "documento": "Documento",
        "n_evaluadas": "n",
        "%exactitud": "Porc. Exactitud",
        "%fidelidad": "Porc. Fidelidad",
        "tasa_alucinacion": "Tasa aluc.",
        "%respuesta_perfecta": "Porc. Resp. Perfectas",
    }

    # La fidelidad y % resp. perfectas no aplica en la linea base
    if linea_base:
        columnas_tipo.remove("%fidelidad")
        columnas_doc.remove("%fidelidad")
        del etiquetas_tipo["%fidelidad"]
        del etiquetas_doc["%fidelidad"]

        columnas_tipo.remove("%respuesta_perfecta")
        columnas_doc.remove("%respuesta_perfecta")
        del etiquetas_tipo["%respuesta_perfecta"]
        del etiquetas_doc["%respuesta_perfecta"]


    modelos = sorted(set(df["modelo"].dropna().astype(str))) if "modelo" in df.columns else []

    mejor_tipo = por_tipo.dropna(subset=["%exactitud"]).sort_values("%exactitud", ascending=False).head(1)
    peor_tipo = por_tipo.dropna(subset=["%exactitud"]).sort_values("%exactitud").head(1)
    mas_alucina = por_tipo.dropna(subset=["tasa_alucinacion"]).sort_values("tasa_alucinacion", ascending=False).head(1)

    # Calcular ruta relativa desde la raíz del proyecto
    ruta_relativa_archivo = archivo.relative_to(ROOT.absolute())

    # Crear contenido markdown
    lineas = []
    lineas.append(f"# {titulo}")
    lineas.append("")
    lineas.append(f"Generado: {datetime.now().isoformat(timespec='seconds')}")
    lineas.append("")
    lineas.append(f"- Archivo de respuestas: `ROOT/{ruta_relativa_archivo}`")
    lineas.append(f"- Modelos usados: {', '.join(modelos) if modelos else '—'}")
    lineas.append(f"- Preguntas totales: {n_total}")
    lineas.append(f"- Preguntas calificadas: {n_evaluadas} ({general['%cobertura']:.1f}%)")
    lineas.append(f"- Errores de API: {n_errores}")
    lineas.append("")

    lineas.append("## Métricas principales")
    lineas.append("")
    lineas.append("La fidelidad y porcentaje de respuestas perfectas no aplican en la línea base.")
    lineas.append("")
    lineas.append("| Métrica | Valor |")
    lineas.append("|---|---|")
    for _, r in general_df.iterrows():
        if r['metrica'] in metricas_principales:
            lineas.append(f"| {r['metrica']} | {r['valor']} |")
    lineas.append("")

    lineas.append("## Otras métricas")
    lineas.append("")
    lineas.append("| Métrica | Valor |")
    lineas.append("|---|---|")
    for _, r in general_df.iterrows():
        if r['metrica'] not in metricas_principales:
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
    lineas.append("## Resumen")
    lineas.append("")
    if not mejor_tipo.empty:
        r = mejor_tipo.iloc[0]
        lineas.append(f"- Mejor %exactitud: **{r['tipo']}** ({r['%exactitud']:.2f}/3).")
    if not peor_tipo.empty:
        r = peor_tipo.iloc[0]
        lineas.append(f"- Peor %exactitud: **{r['tipo']}** ({r['%exactitud']:.2f}/3).")
    if not mas_alucina.empty:
        r = mas_alucina.iloc[0]
        lineas.append(f"- Mayor tasa de alucinación: **{r['tipo']}** ({r['tasa_alucinacion']:.1f}% de respuestas con al menos una invención).")

    lineas.append("")
    lineas.append("## Definiciones")
    lineas.append("")
    lineas.append("- **Exactitud (0-3):** 0 = incorrecta; 1 = correcta en algo pero con errores importantes; 2 = parcialmente correcta u omite datos clave; 3 = correcta y completa frente a la respuesta esperada.")
    lineas.append("- **Fidelidad (0-3):** 0 = no se sustenta en las fuentes o las contradice; 1 = mezcla datos fieles con inventados; 2 = mayormente fiel con imprecisiones; 3 = todos los datos relevantes son verificables en las fuentes.")
    lineas.append("- **Alucinación (0-2):** 0 = no inventa; 1 = inventa un detalle menor (cifra, plazo, nombre, correo); 2 = inventa hechos centrales o contradice la fuente.")
    lineas.append("- **Respuesta perfecta:** exactitud 3, fidelidad 3 y alucinación 0.")
    lineas.append("")

    (salida / "metricas.md").write_text("\n".join(lineas), encoding="utf-8")

    # --- Consola ----------------------------------------------------------
    print("\nMÉTRICAS PRINCIPALES")
    for _, r in general_df.iterrows():
        if r['metrica'] in metricas_principales:
            print(f"  {r['metrica']}: {r['valor']}")

    print("\nOTRAS MÉTRICAS")
    for _, r in general_df.iterrows():
        if r['metrica'] not in metricas_principales:
            print(f"  {r['metrica']}: {r['valor']}")


    print("\nMÉTRICAS POR TIPO")

    lista_metricas = [
        "tipo",
        "n_evaluadas",
        "%exactitud",
        "%fidelidad",
        "tasa_alucinacion",
        "%respuesta_perfecta",
    ]

    if linea_base:
        lista_metricas.remove("%fidelidad")
        lista_metricas.remove("%respuesta_perfecta")

    print(
        por_tipo[lista_metricas].to_string(index=False)
    )
    print(f"\nReporte: {(salida / 'metricas.md').resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
