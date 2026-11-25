# Asistente RAG UTB

Asistente en español que responde preguntas sobre los reglamentos de la
Universidad Tecnológica de Bolívar (UTB). El proyecto descarga los PDF
institucionales, extrae y divide su texto, genera embeddings con Gemini y
compara las respuestas del modelo **sin** recuperación de documentos (línea
base) y **con** recuperación (RAG). Las respuestas y las métricas se guardan en
`experiments/`.

## Requisitos

- Windows y Python 3.11.9, la versión usada para validar el proyecto.
- Conexión a internet y una clave de Gemini API.

## Instalación y ejecución

Desde PowerShell, en la carpeta del proyecto, ejecuta estos **4 comandos** en
orden. Cada uno va en su propio bloque.

**1. Crear el entorno virtual**

```powershell
py -3.11 -m venv .venv
```

**2. Instalar las dependencias**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**3. Guardar tu clave de Gemini** (reemplaza `TU_CLAVE_DE_GEMINI`)

```powershell
.\.venv\Scripts\python.exe set_api_key.py TU_CLAVE_DE_GEMINI
```

**4. Ejecutar el flujo completo**

```powershell
.\.venv\Scripts\python.exe main.py
```

El último comando inicia todo el pipeline: descarga de PDF, extracción de texto,
creación de chunks y embeddings, generación de respuestas y evaluación manual
cuando corresponde. La descarga y las llamadas a Gemini requieren internet y
pueden consumir cuota.

No compartas ni subas `.env`; está excluido por Git.

## Ejecutar solo una etapa

El flujo se puede reanudar sin repetir todo. Usa `--etapa` con uno de estos
valores: `fetching`, `preprocesamiento`, `lineabase`, `procesamiento`,
`embedding` o `rag`. Por ejemplo, `--etapa rag` continúa desde la línea RAG y
`--etapa rag --only` ejecuta únicamente esa etapa.