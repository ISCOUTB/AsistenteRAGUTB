# Asistente RAG UTB

Asistente en español basado en Retrieval-Augmented Generation (RAG) que responde preguntas sobre los reglamentos de la
Universidad Tecnológica de Bolívar (UTB). El proyecto descarga los PDF
institucionales, extrae y divide su texto, genera embeddings con Gemini y
compara las respuestas del modelo **sin** recuperación de documentos (línea
base) y **con** recuperación (RAG). Las respuestas y las métricas se guardan en
`experiments/`.

- Ruta de preguntas: `data/preguntas/preguntas.csv`
- Modelo utilizado: Gemini 3.5 Flash Lite
- Modelo de embeddings: Gemini Embedding 2

**Reglamentos del corpus:**

- Reglamento Estudiantil (RE2026)
- Reglamento Ruta de Autonomía (RUTA2026)
- Reglamento del Consultorio Jurídico (CJ2025)
- Reglamento de Psicología (PSICO)
- Reglamento de Fotografía (FOTO)
- Reglamento de Sonido (SONIDO)
- Reglamento de Televisión (TV)
- Reglamento Sala de Redacción (SALA)

## Nota para evaluación

El repositorio incluye:

- Los resultados experimentales utilizados en el informe.
- Un notebook con la ejecución de todo el flujo y las salidas de cada celda.
- El script `main.py`
- Una aplicación en Streamlit
- El archivo `data/embeddings/db.csv` con los embeddings precalculados.

Por lo tanto, no es necesario regenerar los embeddings ni volver a ejecutar el pipeline completo para revisar los resultados reportados.

## Flujo de ejecución

1. Descarga de reglamentos PDF.
2. Extracción y limpieza de texto.
3. Evaluación de la línea base (LLM sin RAG).
4. Segmentación en fragmentos.
5. Generación de embeddings.
6. Evaluación del sistema RAG.
7. Aplicación interactiva con Streamlit.

## Requisitos

- Python 3.11.9, la versión usada para validar el proyecto.
- Conexión a internet y una clave de Gemini API.

## Instalación

Se recomienda usar un entorno virtual.
En la carpeta del proyecto, ejecuta estos **3 comandos** en
orden para crear y activar el entorno virtual.

**1. Crear el entorno virtual**

```powershell
python -m venv .venv
```

**2. Activar el entorno**

En Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

En sistemas tipo UNIX o Linux:

```bash
source .venv/bin/activate
```

**3. Instalar paquetes requeridos**

```powershell
pip install -r requirements.txt
```

## Ejecución

**1. Configurar tu clave de Gemini API** (reemplaza `TU_CLAVE_DE_GEMINI`)

```powershell
python set_api_key.py TU_CLAVE_DE_GEMINI
```

**2. Ejecutar el flujo completo**

```powershell
python main.py
```

**3. Ejecutar la aplicación web:**

```powershell
streamlit run streamlit_app.py
```

El primer comando guarda en `.env` la clave de Gemini API, de manera que será cargada como variable de entorno al ejecutar los siguientes comandos.

El segundo comando inicia todo el pipeline: descarga de PDF, extracción de texto,
creación de chunks y embeddings, generación de respuestas y evaluación manual
cuando corresponde. La descarga y las llamadas a Gemini requieren internet y
pueden consumir cuota. Para embeddings, las claves con plan gratuito tienen un límite de 100
solicitudes por minuto y 30000 tokens por minuto.
El programa reintenta pasado el tiempo indicado por el mensaje de error.

La aplicación web en Streamlit muestra una interfaz de pregunta-respuesta y muestra detalles técnicos como:
- Latencia
- Documentos recuperados
- Si hubo errores o no

No compartas ni subas `.env`; está excluido por Git.

## Ejecutar solo una etapa

El flujo se puede reanudar sin repetir todo. 

**Ejecutar a partir de una etapa específica (se ejecutan también las siguientes):**

```powershell
main.py --etapa {fetching, preprocesamiento, lineabase, procesamiento, embedding, rag}
```

**Ejecutar SOLO una etapa específica**

```powershell
main.py --etapa {fetching, preprocesamiento, lineabase, procesamiento, embedding, rag} --only
```

Por ejemplo, `--etapa rag` continúa desde la línea RAG y
`--etapa rag --only` ejecuta únicamente esa etapa.

# Base de datos vectorial

El archivo `data/embeddings/db.csv` ya contiene los embeddings precalculados. La aplicación web puede ejecutarse directamente sin reprocesar los documentos ni regenerar los embeddings.