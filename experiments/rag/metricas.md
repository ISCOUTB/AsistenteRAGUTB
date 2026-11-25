# Métricas de la línea RAG (con RAG)

Generado: 2026-11-25T10:29:54

- Archivo de respuestas: `ROOT/experiments/rag/respuestas_rag.csv`
- Modelos usados: gemini-3.5-flash-lite
- Preguntas totales: 50
- Preguntas calificadas: 50 (100.0%)
- Errores de API: 0

## Métricas principales

La fidelidad y porcentaje de respuestas perfectas no aplican en la línea base.

| Métrica | Valor |
|---|---|
| Exactitud (%) | 89.33 |
| Fidelidad (%) | 86.66666666666667 |
| Tasa de alucinación (%) | 2.0 |
| Respuesta perfecta (%) | 78.0 |

## Otras métricas

| Métrica | Valor |
|---|---|
| Preguntas totales | 50 |
| Preguntas calificadas | 50 |
| Cobertura de calificación (%) | 100.0 |
| Errores de API | 0 |
| Sin respuesta generada | 0 |
| Exactitud plena (=3) (%) | 80.0 |
| Exactitud aceptable (>=2) (%) | 90.0 |
| Exactitud baja (<=1) (%) | 10.0 |
| Fidelidad plena (%) | 80.0 |
| Fidelidad baja (<=1) (%) | 12.0 |
| Sin alucinación (%) | 98.0 |
| Alucinación grave (=2) (%) | 0.0 |

## Métricas por tipo de pregunta

| Tipo | n | Porc. Exact. | Porc. Fidel. | Tasa aluc. | Porc. Resp. Perfectas |
|---|---|---|---|---|---|
| articulo_especifico | 10 | 90.0% | 90.0% | 10.00 | 90.0% |
| interpretacion_simple | 8 | 79.2% | 62.5% | 0.00 | 62.5% |
| multi_articulo | 8 | 95.8% | 91.7% | 0.00 | 75.0% |
| ambigua | 7 | 95.2% | 95.2% | 0.00 | 85.7% |
| dificil | 7 | 95.2% | 100.0% | 0.00 | 85.7% |
| fuera_de_alcance | 5 | 100.0% | 100.0% | 0.00 | 100.0% |
| conflicto_entre_documentos | 5 | 66.7% | 66.7% | 0.00 | 40.0% |

## Métricas por documento

| Documento | n | Porc. Exactitud | Porc. Fidelidad | Tasa aluc. | Porc. Resp. Perfectas |
|---|---|---|---|---|---|
| RE2026 | 25 | 97.3% | 96.0% | 0.00 | 92.0% |
| CJ2025 | 5 | 93.3% | 100.0% | 0.00 | 80.0% |
| RUTA2026 | 4 | 100.0% | 100.0% | 0.00 | 100.0% |
| TV | 3 | 88.9% | 88.9% | 0.00 | 66.7% |
| FOTO | 3 | 33.3% | 11.1% | 33.33 | 0.0% |
| SONIDO | 1 | 33.3% | 0.0% | 0.00 | 0.0% |
| SALA | 1 | 33.3% | 0.0% | 0.00 | 0.0% |
| PSICO | 4 | 83.3% | 83.3% | 0.00 | 50.0% |
| NO_APLICA | 4 | 100.0% | 100.0% | 0.00 | 100.0% |

## Resumen

- Mejor %exactitud: **fuera_de_alcance** (100.00/3).
- Peor %exactitud: **conflicto_entre_documentos** (66.67/3).
- Mayor tasa de alucinación: **articulo_especifico** (10.0% de respuestas con al menos una invención).

## Definiciones

- **Exactitud (0-3):** 0 = incorrecta; 1 = correcta en algo pero con errores importantes; 2 = parcialmente correcta u omite datos clave; 3 = correcta y completa frente a la respuesta esperada.
- **Fidelidad (0-3):** 0 = no se sustenta en las fuentes o las contradice; 1 = mezcla datos fieles con inventados; 2 = mayormente fiel con imprecisiones; 3 = todos los datos relevantes son verificables en las fuentes.
- **Alucinación (0-2):** 0 = no inventa; 1 = inventa un detalle menor (cifra, plazo, nombre, correo); 2 = inventa hechos centrales o contradice la fuente.
- **Respuesta perfecta:** exactitud 3, fidelidad 3 y alucinación 0.
