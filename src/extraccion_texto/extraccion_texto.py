import pymupdf, os

def main(ROOT):
        
    CARPETA_PDF = ROOT + "/data/pdf"
    reglamentos = []       # textos de los pdfs
    nombres = []           # nombres de los archivos

    # -------------- Reglamento de autonomía y del consultorio jurídico ------ #

    for name in ["Reglamento-Ruta-de-autonomia.pdf", "reglamento-del-CJ-26-09-25.pdf"]:
            
        reglamento = ""   # aqui irá el texto completo del reglamento actual
        doc = pymupdf.open(CARPETA_PDF + "/" + name)  # leer el pdf

        for i, pagina in enumerate(doc):    # iterar por paginas
            texto = pagina.get_text().strip()

            reemplazo = "REGLAMENTO DE LA RUTA DE AUTONOMÍA Y ÉXITO PROFESIONALPARA ESTUDIANTES DE PREGRADO PRESENCIAL\n" + str(i+1) if ((i+1) % 2 != 0) else ""
            reemplazo = "UNIVERSIDAD TECNOLÓGICA DE BOLÍVAR\n" + str(i+1) if ((i+1) % 2 == 0) else reemplazo
            texto = texto.replace(reemplazo, "")  # quitar texto que se repite en todas las paginas
            texto = texto.replace("CAPITULO III", "CAPÍTULO III")  # corregir una I sin tilde
            texto += "\n"
            reglamento += texto
        
        reglamentos.append(reglamento)
        nombres.append(name)

    # --------------Reglamento estudiantil ------------------------------- #
    
    reglamento = ""
    name = "Reglamento-Estudiantil-2026.pdf"
    doc = pymupdf.open(CARPETA_PDF + "/" + name)
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
    nombres.append(name)
    
    # ------------ Otros reglamentos ------------------------------------- #

    nombres_de_otros_reglamentos = [
        "REGLAMENTO-DE-USO-DE-LOS-LABORATORIOS-DE-PSICOLOGIA.pdf",
        "reglamento_estudio_de_television_y_laboratorio_de_posproduccion_0_0.pdf",
        "reglamento_laboratorio_de_fotografia_0.pdf",
        "reglamento_laboratorio_de_sonido_0.pdf",
        "reglamento_sala_multimedia.pdf"
    ]

    for name in nombres_de_otros_reglamentos:
        reglamento = ""
        doc = pymupdf.open(CARPETA_PDF + "/" + name)

        for i, pagina in enumerate(doc):
            texto = pagina.get_text().strip()
            texto = texto.replace("\n", "-- ")  # Reemplazar viñeta
            texto = texto.replace("", "-- ") # Reemplazar viñeta
            texto += "\n"
            reglamento += texto
        
        reglamentos.append(reglamento)
        nombres.append(name)

    # -------------- Guardar en archivos txt --------------------------- #

    CARPETA_TXT = ROOT + "/data/texto"

    if not os.path.isdir(CARPETA_TXT):
        os.mkdir(CARPETA_TXT)


    for reglamento, name in zip(reglamentos, nombres):
        name = name[:-4] + ".txt"
        with open(CARPETA_TXT + "/" + name, "w", encoding="utf-8") as f:
            f.write(reglamento)

        print(f"Texto guardado: {CARPETA_TXT}/{name}")

if __name__ == "__main__":
    main("../..")