import streamlit as st
from openai import OpenAI
import datetime

# Configura tu clave de OpenAI desde los secretos de Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Base de conocimiento local (Cádiz)
zonas_locales = {
    "Cádiz": {
        "viento_tipico": "Levante o Poniente con influencia térmica en horas centrales.",
        "efectos_locales": "Roles frecuentes hacia la derecha con térmico, corriente leve bajando en bajamar, ola corta de 0.5-0.8 m."
    }
}

# Título de la app
st.title("Parte Meteorológico Táctico para Regatas Inshore")

# Formulario de entrada
with st.form("formulario"):
    zona = st.selectbox("Zona de regata", list(zonas_locales.keys()))
    fecha = st.date_input("Fecha de la regata", datetime.date.today())
    hora_inicio = st.time_input("Hora inicio", datetime.time(13, 0))
    hora_fin = st.time_input("Hora fin", datetime.time(16, 0))
    modelo = st.selectbox("Modelo meteorológico preferido", ["AROME", "ECMWF", "Otro"])
    incluir_consejos = st.checkbox("Incluir consejos tácticos", value=True)
    parte_manual = st.text_area("Parte meteorológico base (manual, opcional)",
                                 "Viento del ESE 14-17 nudos, cielo despejado, mar en calma, corriente bajando")
    enviado = st.form_submit_button("Generar parte")

# Cuando se envía el formulario
def generar_prompt(zona, fecha, hora_inicio, hora_fin, modelo, incluir_consejos, parte_manual):
    local = zonas_locales.get(zona, {})
    prompt = f"""
Genera un parte meteorológico profesional para una regata olímpica inshore.

Zona: {zona}
Fecha: {fecha.strftime('%d/%m/%Y')}
Horario: {hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}
Modelo meteorológico: {modelo}

Parte base:
{parte_manual}

Análisis local:
- Viento típico: {local.get('viento_tipico', '')}
- Efectos locales: {local.get('efectos_locales', '')}
"""
    if incluir_consejos:
        prompt += "\nIncluye consejos tácticos por tramo de regata."
    return prompt

if enviado:
    prompt = generar_prompt(zona, fecha, hora_inicio, hora_fin, modelo, incluir_consejos, parte_manual)

    with st.spinner("Generando parte táctico..."):
        respuesta = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un meteorólogo experto en regatas inshore."},
                {"role": "user", "content": prompt}
            ]
        )
        texto_generado = respuesta.choices[0].message.content
        st.subheader("📄 Parte generado")
        st.write(texto_generado)
        st.download_button("Descargar parte como .txt", data=texto_generado, file_name="parte_regata.txt")
