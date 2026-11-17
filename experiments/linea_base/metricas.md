# Métricas de la línea base (sin RAG)

Generado: 2026-11-16T22:56:53

- Archivo de respuestas: `/home/moises/Documents/utb2026-2/ia/proyecto-final/chatutb/experiments/linea_base/respuestas_baseline.csv`
- Modelos usados: gemini-3.5-flash-lite
- Preguntas totales: 50
- Preguntas calificadas: 50 (100.0%)
- Errores de API: 0

## Métricas generales

| Métrica | Valor |
|---|---|
| Preguntas totales | 50 |
| Preguntas calificadas | 50 |
| Cobertura de calificación (%) | 100.0 |
| Errores de API | 0 |
| Sin respuesta generada | 0 |
| Exactitud media (0-3) | 1.18 |
| Exactitud sobre 100 | 39.33 |
| Exactitud plena (%) | 18.0 |
| Exactitud aceptable (>=2) (%) | 40.0 |
| Exactitud baja (<=1) (%) | 60.0 |
| Fidelidad media (0-3) | 1.08 |
| Fidelidad sobre 100 | 36.0 |
| Fidelidad plena (%) | 16.0 |
| Fidelidad baja (<=1) (%) | 62.0 |
| Alucinación media (0-2) | 1.3 |
| Sin alucinación (%) | 18.0 |
| Con alucinación (>=1) (%) | 82.0 |
| Alucinación grave (2) (%) | 48.0 |
| Respuesta ideal: exactitud 3 + fidelidad 3 + alucinación 0 (%) | 12.0 |

## Métricas por tipo de pregunta

| Tipo | n | Exact. media | Exact. plena | Fidel. media | Fidel. plena | Aluc. media | Con aluc. | Ideal |
|---|---|---|---|---|---|---|---|---|
| articulo_especifico | 10 | 1.50 | 30.0% | 1.50 | 40.0% | 1.00 | 60.0% | 30.0% |
| interpretacion_simple | 8 | 1.50 | 0.0% | 1.50 | 12.5% | 1.12 | 87.5% | 0.0% |
| multi_articulo | 8 | 1.75 | 37.5% | 1.62 | 25.0% | 1.12 | 75.0% | 25.0% |
| ambigua | 7 | 0.86 | 0.0% | 0.57 | 0.0% | 1.43 | 100.0% | 0.0% |
| dificil | 7 | 1.57 | 42.9% | 1.29 | 14.3% | 1.14 | 71.4% | 14.3% |
| fuera_de_alcance | 5 | 0.00 | 0.0% | 0.00 | 0.0% | 2.00 | 100.0% | 0.0% |
| conflicto_entre_documentos | 5 | 0.20 | 0.0% | 0.20 | 0.0% | 1.80 | 100.0% | 0.0% |

## Métricas por documento

| Documento | n | Exactitud | Fidelidad | Alucinación | Con aluc. |
|---|---|---|---|---|---|
| RE2026 | 25 | 1.48 | 1.40 | 1.04 | 68.0% |
| CJ2025 | 5 | 0.60 | 0.40 | 1.80 | 100.0% |
| RUTA2026 | 4 | 1.75 | 1.75 | 1.00 | 75.0% |
| TV | 3 | 0.33 | 0.33 | 1.67 | 100.0% |
| FOTO | 3 | 1.33 | 1.00 | 1.33 | 100.0% |
| SONIDO | 1 | 2.00 | 2.00 | 1.00 | 100.0% |
| SALA | 1 | 2.00 | 2.00 | 1.00 | 100.0% |
| PSICO | 4 | 0.75 | 0.50 | 1.75 | 100.0% |
| NO_APLICA | 4 | 0.00 | 0.00 | 2.00 | 100.0% |

## Preguntas de control vs. preguntas del corpus

## Lectura rápida

- Mejor exactitud media: **multi_articulo** (1.75/3).
- Peor exactitud media: **fuera_de_alcance** (0.00/3).
- Mayor tasa de alucinación: **conflicto_entre_documentos** (100.0% de respuestas con al menos una invención).
- La línea base sirve como referencia: si el RAG no supera estos valores, la recuperación no está aportando.

## Definiciones

- **Exactitud (0-3):** 0 = incorrecta; 1 = correcta en algo pero con errores importantes; 2 = parcialmente correcta u omite datos clave; 3 = correcta y completa frente a la respuesta esperada.
- **Fidelidad (0-3):** 0 = no se sustenta en las fuentes o las contradice; 1 = mezcla datos fieles con inventados; 2 = mayormente fiel con imprecisiones; 3 = todos los datos relevantes son verificables en las fuentes.
- **Alucinación (0-2):** 0 = no inventa; 1 = inventa un detalle menor (cifra, plazo, nombre, correo); 2 = inventa hechos centrales o contradice la fuente.
- **Respuesta ideal:** exactitud 3, fidelidad 3 y alucinación 0.
- **Abstención:** el modelo dice explícitamente que no tiene la información (esperado sobre todo en `fuera_de_alcance`).
