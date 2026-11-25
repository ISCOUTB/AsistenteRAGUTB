# Métricas de la línea base (sin RAG)

Generado: 2026-11-25T08:42:35

- Archivo de respuestas: `ROOT/experiments/linea_base/respuestas_baseline.csv`
- Modelos usados: gemini-3.5-flash-lite
- Preguntas totales: 50
- Preguntas calificadas: 50 (100.0%)
- Errores de API: 0

## Métricas principales

La fidelidad y porcentaje de respuestas perfectas no aplican en la línea base.

| Métrica | Valor |
|---|---|
| Exactitud (%) | 39.33 |
| Fidelidad (%) | N/A |
| Tasa de alucinación (%) | 82.0 |
| Respuesta perfecta (%) | N/A |

## Otras métricas

| Métrica | Valor |
|---|---|
| Preguntas totales | 50 |
| Preguntas calificadas | 50 |
| Cobertura de calificación (%) | 100.0 |
| Errores de API | 0 |
| Sin respuesta generada | 0 |
| Exactitud plena (=3) (%) | 18.0 |
| Exactitud aceptable (>=2) (%) | 40.0 |
| Exactitud baja (<=1) (%) | 60.0 |
| Fidelidad plena (%) | N/A |
| Fidelidad baja (<=1) (%) | N/A |
| Sin alucinación (%) | 18.0 |
| Alucinación grave (=2) (%) | 48.0 |

## Métricas por tipo de pregunta

| Tipo | n | Porc. Exact. | Tasa aluc. |
|---|---|---|---|
| articulo_especifico | 10 | 50.0% | 60.00 |
| interpretacion_simple | 8 | 50.0% | 87.50 |
| multi_articulo | 8 | 58.3% | 75.00 |
| ambigua | 7 | 28.6% | 100.00 |
| dificil | 7 | 52.4% | 71.43 |
| fuera_de_alcance | 5 | 0.0% | 100.00 |
| conflicto_entre_documentos | 5 | 6.7% | 100.00 |

## Métricas por documento

| Documento | n | Porc. Exactitud | Tasa aluc. |
|---|---|---|---|
| RE2026 | 25 | 49.3% | 68.00 |
| CJ2025 | 5 | 20.0% | 100.00 |
| RUTA2026 | 4 | 58.3% | 75.00 |
| TV | 3 | 11.1% | 100.00 |
| FOTO | 3 | 44.4% | 100.00 |
| SONIDO | 1 | 66.7% | 100.00 |
| SALA | 1 | 66.7% | 100.00 |
| PSICO | 4 | 25.0% | 100.00 |
| NO_APLICA | 4 | 0.0% | 100.00 |

## Resumen

- Mejor %exactitud: **multi_articulo** (58.33/3).
- Peor %exactitud: **fuera_de_alcance** (0.00/3).
- Mayor tasa de alucinación: **conflicto_entre_documentos** (100.0% de respuestas con al menos una invención).

## Definiciones

- **Exactitud (0-3):** 0 = incorrecta; 1 = correcta en algo pero con errores importantes; 2 = parcialmente correcta u omite datos clave; 3 = correcta y completa frente a la respuesta esperada.
- **Fidelidad (0-3):** 0 = no se sustenta en las fuentes o las contradice; 1 = mezcla datos fieles con inventados; 2 = mayormente fiel con imprecisiones; 3 = todos los datos relevantes son verificables en las fuentes.
- **Alucinación (0-2):** 0 = no inventa; 1 = inventa un detalle menor (cifra, plazo, nombre, correo); 2 = inventa hechos centrales o contradice la fuente.
- **Respuesta perfecta:** exactitud 3, fidelidad 3 y alucinación 0.
