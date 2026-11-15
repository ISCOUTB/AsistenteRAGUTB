import pandas as pd
import os
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def extraer(texto, titulos):
    contenidos = []
    end = 0    # indice hasta donde copiar
    texto = "      " + texto  # Para evitar problemas al calcular end

    for t in titulos:
        if t in ("INFORMACIÓN PREVIA", ""): continue # Primer "título"
        end = texto.find(t,3)            # calculo indice hasta donde copiar
        contenidos.append(texto[:end]) # agrego el contenido a la lista
        texto = texto[end:]            # ahora el texto comenzará donde terminó

    contenidos.append(texto)   # agrego lo restante

    longitud = len(titulos)
    if longitud != len(set(titulos)): # si los titulos estan repetidos
        titulos = [str(i) for i in range(longitud)] # asignar un numero unico para que no se sobreescriba
    
    return dict(zip(titulos, contenidos))


def insertar_chunks_en_db(reglamento, name, titulos_cap, regex_articulos, df):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,   # Máximo 500 palabras por bloque
        chunk_overlap=0, # No solapamiento de palabras entre bloques
        length_function=lambda x: len(x.split()),  # Cuenta palabras separadas por espacios
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    # cuando se va a extraer, a la lista de capitulos se le añade uno llamado "INFORMACIÓN PREVIA"
    # para capturar el contenido anterior al primer capitulo y para que no
    # se descuadren los capitulos
    capitulos = extraer(reglamento, ["INFORMACIÓN PREVIA"] + titulos_cap)

    # si no hay informacion previa, quitar la clave-valor
    if capitulos["INFORMACIÓN PREVIA"].strip() == "":
        del capitulos["INFORMACIÓN PREVIA"]

    # Extraer articulos y poner todo en la base de datos
    for titulo in capitulos:
        # eliminar el titulo del capitulo del texto del capitulo y hacerle strip
        content_cap = capitulos[titulo].replace(titulo, '').strip()
        lista_art = regex_articulos.findall(content_cap) # lista de articulos

        # si el texto del capitulo no tiene articulos sino texto continuo,
        # dividir en chunks de 500 palabras
        if len(lista_art) == 0:
            docs =  [Document(content_cap)] # convertir a Document de langchain
            splits = text_splitter.split_documents(docs)  # llamar al splitter
            
            for split in splits: # agregar cada chunk
                chunk = split.page_content   # contenido del chunk
                if chunk.strip() == "": continue
                
                nuevafila = pd.DataFrame({
                    "chunk": [chunk],
                    "capitulo": [titulo],
                    "documento": [name]
                })
    
                df = pd.concat([df, nuevafila], ignore_index=True)

            continue # no ejecutar lo de abajo

        # si el texto del capítulo sí se puede dividir en artículos,
        # extraer diccionario con los articulos. A lista_art se le agrega un
        # titulo vacío "" para que no se descuadre el diccionario
        articulos = extraer(content_cap, [""] + lista_art)

        # por cada articulo, agregar un chunk
        for name_chunk, chunk in zip(articulos.keys(), articulos.values()):
            if chunk.strip() == "": continue
            nuevafila = pd.DataFrame({
                "chunk": [chunk],
                "capitulo": [titulo],
                "documento": [name]
            })

            df = pd.concat([df, nuevafila], ignore_index=True)

    return df

def main(ROOT):
    CARPETA_TXT = ROOT + "/data/texto"
    
    reglamentos = []       # textos
    titulos_capitulos = [] # titulos de los capitulos de los reglamentos
    patrones = []          # patrones para encontrar los chunks o articulos
    nombres = []           # nombres de los reglamentos

    nombres_archivos = [
        "Reglamento-Ruta-de-autonomia.txt",
        "reglamento-del-CJ-26-09-25.txt",
        "Reglamento-Estudiantil-2026.txt",
        "REGLAMENTO-DE-USO-DE-LOS-LABORATORIOS-DE-PSICOLOGIA.txt",
        "reglamento_estudio_de_television_y_laboratorio_de_posproduccion_0_0.txt",
        "reglamento_laboratorio_de_fotografia_0.txt",
        "reglamento_laboratorio_de_sonido_0.txt",
        "reglamento_sala_multimedia.txt"
    ]

    # --------- Reglamento ruta de autonomia y consultorio juridico ------- #

    for nombre_archivo in nombres_archivos[:2]:
        with open(CARPETA_TXT + "/" + nombre_archivo, encoding="utf8") as f:
            reglamento = f.read()

        patron_cap = re.compile(r"(?s)(CAP[ÍI]TULO\s*.*?)\s*Art[íi]culo")
        patron_art = re.compile(r"Artículo .*?\.")

        reglamentos.append(reglamento)
        titulos_capitulos.append( patron_cap.findall(reglamento) )
        patrones.append(patron_art)
    
    nombres.append("Reglamento Ruta de Autonomía")
    nombres.append("Reglamento del Consultorio Jurídico")

    # --------------Reglamento estudiantil ------------------------------- #
    
    with open(CARPETA_TXT + "/" + nombres_archivos[2], encoding="utf8") as f:
        reglamento = f.read()

    patron_cap = re.compile(r"(?m)^[IVXLM]+\.(?!\s+(?:LENGUAS EXTRANJERAS|RECLAMOS))\s[\s\S]*?(?=\nARTÍCULO|\nA\.)")
    patron_art = re.compile(r"ARTÍCULO .*?:")

    titulos_capitulos.append( ["PRESENTACIÓN", "GLOSARIO"] + patron_cap.findall(reglamento) )
    patrones.append(patron_art)
    nombres.append("Reglamento Estudiantil")
    reglamentos.append(reglamento)

    
    # ------------ Otros reglamentos ------------------------------------- #

    cap_de_otros_reglamentos = [
        ["REGLAMENTO DE USO DE LOS LABORATORIOS DE PSICOLOGÍA \nLABPSIC"],
        
        ["REGLAMENTO ESTUDIO DE TELEVISIÓN Y LABORATORIO DE\nPOSPRODUCCIÓN.",
        "DISPOSICIONES GENERALES.", "Utilización de equipos al interior y fuera de la Universidad\nTecnológica de Bolívar.",
        "Son causales para perder el turno de prácticas\ny uso de equipos."],
        
        ["REGLAMENTO LABORATORIO DE FOTOGRAFÍA.", "DISPOSICIONES GENERALES.", 
        "Utilización de equipos al interior de la Universidad\nTecnológica de Bolívar",
        "Utilización de equipos fuera de la Universidad Tecnológica de\nBolívar.",
        "Son causales para perder el turno de\nprácticas."],
        
        ["REGLAMENTO LABORATORIO DE SONIDO", "DISPOSICIONES GENERALES.", "Son causales para perder el turno de\nprácticas."],
        
        ["REGLAMENTO SALA DE REDACCIÓN.", "DISPOSICIONES GENERALES."]
    ]

    for nombre_archivo, titulos_cap in zip(nombres_archivos[3:], cap_de_otros_reglamentos):
        with open(CARPETA_TXT + "/" + nombre_archivo, encoding="utf8") as f:
            reglamentos.append(f.read())

        if nombre_archivo == "REGLAMENTO-DE-USO-DE-LOS-LABORATORIOS-DE-PSICOLOGIA.txt":
            patron_art = re.compile(r"\d+\.")
        else:
            patron_art = re.compile("-- ")

        titulos_capitulos.append(titulos_cap)
        patrones.append(patron_art)
    
    nombres.append("Reglamento de uso de los laboratorios de psicología")
    nombres.append("Reglamento del estudio de televisión y laboratorio de posproducción")
    nombres.append("Reglamento del laboratorio de fotografía")
    nombres.append("Reglamento del laboratorio de sonido")
    nombres.append("Reglamento sala de redacción")

    # ------------------------ Guardar en csv y html ------------------ #

    df = pd.DataFrame({
        "chunk": [],
        "capitulo": [], 
        "documento": [],
        "embeddings": []
    })

    for i in range(len(reglamentos)):
        df = insertar_chunks_en_db(reglamentos[i], nombres[i], titulos_capitulos[i], patrones[i], df)

    print(f"{len(df)} registros agregados.")

    df["n_palabras"] = (
        df["chunk"].str.split().str.len()
    )

    print("\nDataframe resultante:\n")
    print(df)

    print("\nEstadisticas de longitud de chunks:\n")
    print(df["n_palabras"].describe())

    print("\nCantidad de chunks que exceden las 500 palabras: ", len(df[df["n_palabras"] > 500]))
    print()

    # -------------- Guardar como csv y html ---------------- #

    CARPETA_PROCESADO = ROOT + "/data/procesado"

    if not os.path.isdir(CARPETA_PROCESADO):
        os.mkdir(CARPETA_PROCESADO)

    df.to_html(CARPETA_PROCESADO + "/db.html", index=False)
    df.to_csv(CARPETA_PROCESADO + "/db.csv", index=False)

    print(f"Guardado en {ROOT}/data/procesado/")
    
    return df

if __name__ == "__main__":
    main("../..")