# Asistente RAG UTB

Asistente en español que responde preguntas sobre reglamentos de la
Universidad Tecnológica de Bolívar. Descarga los PDF institucionales, extrae y
divide su texto, genera embeddings con Gemini y compara respuestas del modelo
con y sin recuperación de documentos (RAG). Las respuestas y métricas se
guardan en `experiments/`.

## Requisitos

- Windows y Python 3.11.9, la versión usada para validar el proyecto.
- Acceso a internet y una clave de Gemini API.

## Instalación y ejecución

Desde PowerShell, en la carpeta del proyecto, ejecuta estos **3 comandos**:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Antes del tercer comando, crea o edita `.env` en la raíz y agrega tu clave:

```dotenv
GEMINI_API_KEY=TU_CLAVE_DE_GEMINI
```

No compartas ni subas `.env`; está excluido por Git. El comando de ejecución
inicia el flujo completo: descarga PDF, extrae texto, crea chunks y embeddings,
genera respuestas y solicita la evaluación manual cuando corresponde. La
descarga y las llamadas a Gemini requieren conexión a internet y pueden
consumir cuota.

## Archivos que puedes modificar

- `config.py`: URL de los PDF, modelos, prompts y parámetros del flujo.
- `data/preguntas/preguntas.csv`: preguntas y criterios de evaluación.
- `src/chunking/chunking.py`: reglas de división del texto en fragmentos.
- `src/linea_rag/linea_rag.py`: recuperación de documentos y contexto RAG.
- `.env`: clave privada de Gemini.
