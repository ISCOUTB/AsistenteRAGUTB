from time import sleep
import requests
import os

def main(ROOT):
    CARPETA_PDF = ROOT + "/data/pdf"

    if not os.path.isdir(f"{ROOT}/pdf"): # Comprobar si no existe el directorio
        os.mkdir(f"{ROOT}/pdf")          # crear directorio


    # Descargar PDFs y guardar en data/pdf

    urls = (
        "https://www.utb.edu.co/wp-content/uploads/2026/10/Reglamento-Estudiantil-2026.pdf",
        "https://www.utb.edu.co/wp-content/uploads/2026/03/Reglamento-Ruta-de-autonomia.pdf",
        "https://www.utb.edu.co/wp-content/uploads/2025/09/reglamento-del-CJ-26-09-25.pdf",
        "https://www.utb.edu.co/wp-content/uploads/2021/04/reglamento_estudio_de_television_y_laboratorio_de_posproduccion_0_0.pdf",
        "https://www.utb.edu.co/wp-content/uploads/2021/04/reglamento_laboratorio_de_fotografia_0.pdf",
        "https://www.utb.edu.co/wp-content/uploads/2021/04/reglamento_laboratorio_de_sonido_0.pdf",
        "https://www.utb.edu.co/wp-content/uploads/2021/04/reglamento_sala_multimedia.pdf",
        "https://www.utb.edu.co/wp-content/uploads/2021/06/REGLAMENTO-DE-USO-DE-LOS-LABORATORIOS-DE-PSICOLOGIA.pdf"
    )

    for url in urls:
        nombre = url.split("/")[-1]
        
        resp = requests.get(url)
        with open(CARPETA_PDF + "/" + nombre, "wb") as f:
            f.write(resp.content)

        print(f"Documento guardado: {CARPETA_PDF}/{nombre}")
        
        sleep(1)

if __name__ == "__main__":
    main("../..")