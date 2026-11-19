import sys
from src.ejecutar_experimento import ejecutar_experimento
from config import (
    PLANTILLA_PROMPT_BASELINE,
    RUTA_RESPUESTAS_BASELINE
)

def construir_prompt(pregunta):
    return PLANTILLA_PROMPT_BASELINE.format(
        pregunta=pregunta["pregunta"].strip(),
    )

def main(*, ver_existentes=False, reemplazar=False):
    try:
        ejecutar_experimento.main(ruta_salida=RUTA_RESPUESTAS_BASELINE,
                                  construir_prompt=construir_prompt,
                                  ver_existentes=ver_existentes,
                                  reemplazar=reemplazar)
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario. Las respuestas guardadas se conservan.")
        sys.exit(130)
    