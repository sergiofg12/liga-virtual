
import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import os
import re

DATA_FILE = 'stats.csv'

if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Nombre", "PJ", "Goles", "Asistencias", "CalificacionTotal"])
    df_init.to_csv(DATA_FILE, index=False)

def extract_stats_from_image(image):
    text = pytesseract.image_to_string(image, config='--oem 3 --psm 6')
    pattern = re.compile(r"([A-Za-z0-9_.-]+)\s+([6-9]\.\d|\d\.\d)\s+(\d+)\s+(\d+)")
    data = []
    for line in text.split('\n'):
        match = pattern.search(line)
        if match:
            nombre = match.group(1)
            calif = float(match.group(2))
            goles = int(match.group(3))
            asist = int(match.group(4))
            data.append({
                "Nombre": nombre,
                "PJ": 1,
                "Goles": goles,
                "Asistencias": asist,
                "CalificacionTotal": calif
            })
    return pd.DataFrame(data)

def update_stats(new_data):
    df = pd.read_csv(DATA_FILE)
    for _, row in new_data.iterrows():
        if row['Nombre'] in df['Nombre'].values:
            df.loc[df['Nombre'] == row['Nombre'], 'PJ'] += 1
            df.loc[df['Nombre'] == row['Nombre'], 'Goles'] += row['Goles']
            df.loc[df['Nombre'] == row['Nombre'], 'Asistencias'] += row['Asistencias']
            df.loc[df['Nombre'] == row['Nombre'], 'CalificacionTotal'] += row['CalificacionTotal']
        else:
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

st.title("⚽ Liga Virtual - Dashboard avanzado" )

uploaded_file = st.file_uploader("📤 Sube imagen de jornada (FIFA):", type=["png","jpg","jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen cargada", use_column_width=True)
    stats_df = extract_stats_from_image(image)
    if not stats_df.empty:
        update_stats(stats_df)
        st.success("¡Estadísticas actualizadas!")
    else:
        st.warning("No se reconocieron datos claros en la imagen (verifica la calidad o plantilla)." )

df = pd.read_csv(DATA_FILE)
if not df.empty:
    df['CalificacionProm'] = (df['CalificacionTotal'] / df['PJ']).round(2)
    st.header("📊 Estadísticas generales")
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Total Goles", int(df['Goles'].sum()))
    col2.metric("🅰️ Total Asistencias", int(df['Asistencias'].sum()))
    col3.metric("👥 Total Jugadores", df.shape[0])

    min_pj = st.slider("Filtra por mínimo partidos jugados", 1, int(df['PJ'].max()), 1)
    filtro_df = df[df['PJ'] >= min_pj]

    option = st.selectbox("¿Qué ranking quieres ver?", ["Ranking de Goleadores", "Ranking de Asistencias", "Ranking de MVP (Calificación Prom.)"])
    if option == "Ranking de Goleadores":
        st.subheader("🏆 Ranking Goleadores")
        st.dataframe(filtro_df[['Nombre', 'PJ', 'Goles']].sort_values(by='Goles', ascending=False))
    elif option == "Ranking de Asistencias":
        st.subheader("🅰️ Ranking Asistencias")
        st.dataframe(filtro_df[['Nombre', 'PJ', 'Asistencias']].sort_values(by='Asistencias', ascending=False))
    elif option == "Ranking de MVP (Calificación Prom.)":
        st.subheader("⭐ Ranking MVP (Calificación Prom.)")
        st.dataframe(filtro_df[['Nombre', 'PJ', 'CalificacionProm']].sort_values(by='CalificacionProm', ascending=False))
else:
    st.info("Sube primero una imagen o carga datos para empezar.")
