import pymupdf

from config import (
    RUTAS_ARCHIVOS_PDF,
    RUTAS_ARCHIVOS_TXT
)

def main():
        
    reglamentos = []       # textos de los pdfs

    # -------------- Reglamento de autonomía y del consultorio jurídico ------ #

    for ruta in RUTAS_ARCHIVOS_PDF[0:2]:
            
        reglamento = ""   # aqui irá el texto completo del reglamento actual
        doc = pymupdf.open(ruta)  # leer el pdf

        for i, pagina in enumerate(doc):    # iterar por paginas
            texto = pagina.get_text().strip()

            reemplazo = "REGLAMENTO DE LA RUTA DE AUTONOMÍA Y ÉXITO PROFESIONALPARA ESTUDIANTES DE PREGRADO PRESENCIAL\n" + str(i+1) if ((i+1) % 2 != 0) else ""
            reemplazo = "UNIVERSIDAD TECNOLÓGICA DE BOLÍVAR\n" + str(i+1) if ((i+1) % 2 == 0) else reemplazo
            texto = texto.replace(reemplazo, "")  # quitar texto que se repite en todas las paginas
            texto = texto.replace("CAPITULO III", "CAPÍTULO III")  # corregir una I sin tilde
            texto += "\n"
            reglamento += texto
        
        reglamentos.append(reglamento)

    # --------------Reglamento estudiantil ------------------------------- #
    
    reglamento = ""
    ruta = RUTAS_ARCHIVOS_PDF[2]
    doc = pymupdf.open(ruta)
    reemplazo = """Reglamento Estudiantil
    Aprobado en Acta No. 03 del 17 de mayo de 2024 del Consejo Académico Resolución 
    No. 01 de 2024 y Modificado por la Resolución del Consejo Académico No. 01 de 2026"""

    for i, pagina in enumerate(doc):
        if (i+1) in [2,3,4]:   # omitir paginas de CONTENIDO
            continue
        texto = pagina.get_text().strip()
        impar = str(i+1) + '\n' if ((i+1) % 2 != 0) else ""
        par = '\n' + str(i+1) if ((i+1) % 2 == 0) else ""
        texto = texto.replace(f"{impar}{reemplazo}{par}", "")  # quitar texto que se repite en todas las paginas
        texto += "\n"
        reglamento += texto

    reglamentos.append(reglamento)
    
    # ------------ Otros reglamentos ------------------------------------- #

    for ruta in RUTAS_ARCHIVOS_PDF[3:]:
        reglamento = ""
        doc = pymupdf.open(ruta)

        for i, pagina in enumerate(doc):
            texto = pagina.get_text().strip()
            texto = texto.replace("\n", "-- ")  # Reemplazar viñeta
            texto = texto.replace("", "-- ") # Reemplazar viñeta
            texto += "\n"
            reglamento += texto
        
        reglamentos.append(reglamento)

    # -------------- Guardar en archivos txt --------------------------- #

    for reglamento, ruta in zip(reglamentos, RUTAS_ARCHIVOS_TXT):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(reglamento)

        print(f"Texto guardado: {ruta}")