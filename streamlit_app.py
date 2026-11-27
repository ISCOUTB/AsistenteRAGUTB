# Cargar el contenido del .env antes de importar las librerias
import os

import streamlit as st
from dotenv import load_dotenv

ROOT = os.path.dirname(__file__)
load_dotenv(os.path.join(ROOT, ".env"))

from src.linea_rag import agente


st.set_page_config(
    page_title="Asistente RAG UTB",
    page_icon="🎓",
)

st.title("Asistente RAG UTB")
st.write("Haz una pregunta sobre la información disponible.")

with st.form("formulario_pregunta"):
    pregunta = st.text_input(
        "Pregunta",
        placeholder="Escribe tu pregunta aquí...",
    )
    enviar = st.form_submit_button("Preguntar", use_container_width=True)

if enviar:
    pregunta = pregunta.strip()

    if not pregunta:
        st.warning("Escribe una pregunta antes de continuar.")
    else:
        with st.spinner("Consultando el asistente..."):
            respuesta = agente.main(pregunta)

        st.subheader("Respuesta")

        contenido = respuesta.get("contenido", "")
        if contenido:
            st.write(contenido)
        else:
            st.info("No se generó una respuesta.")

        latencia = respuesta.get("latencia")
        if latencia is not None:
            st.caption(f"Tiempo: {latencia}")

        with st.expander("Detalles técnicos"):
            error = respuesta.get("error")
            st.markdown("**Mensaje de error**")
            st.write(error if error else "Sin errores.")

            st.markdown("**Documentos recuperados**")

            documentos = respuesta.get("docs_recuperados")

            if documentos:
                if isinstance(documentos, dict):
                    for nombre, contenido_documento in documentos.items():
                        st.write(contenido_documento)
                elif isinstance(documentos, (list, tuple)):
                    for documento in documentos:
                        st.write(documento)
                else:
                    st.write(documentos)
            else:
                st.write("No se recuperaron documentos.")