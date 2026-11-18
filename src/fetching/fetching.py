from time import sleep
import requests

from config import (
    RUTAS_ARCHIVOS_PDF,
    URLS
)

def main():
    # Descargar PDFs y guardar en data/pdf

    for url, ruta in zip(URLS, RUTAS_ARCHIVOS_PDF):
        resp = requests.get(url)
        with open(ruta, "wb") as f:
            f.write(resp.content)

        print(f"Documento guardado: {ruta}")
        
        sleep(1)