import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import subprocess
from datetime import datetime
import pytz
from pathlib import Path

# Configuración de rutas
BASE_PATH = Path(__file__).parent.resolve()
BASE_PATH_INPUTS = BASE_PATH / "inputs"

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Completo - Jardines",
    page_icon="📊",
    layout="wide"
)

# BLOQUE DE CSS GLOBAL
st.markdown("""
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #eaefff;
        }
        .stApp {
            background-color: #eaefff;
        }
        h1, h2, h3 {
            font-family: 'DM Sans', sans-serif;
            color: black;
        }
        .header {
            background-color: #0C1461;
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            position: relative;
            margin-top: 50px;
        }
        .header h1 {
            color: white;
        }
        .kpi-container {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin: 20px 0;
            padding: 0;
            width: 100%;
        }
        .kpi {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border: 1px solid #e0e0e0;
        }
        .kpi:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .kpi h2 {
            color: #0C1461;
            font-size: 2.5em;
            margin: 0;
            font-family: 'DM Sans', sans-serif;
            font-weight: bold;
            line-height: 1.2;
        }
        .kpi p {
            color: #666;
            margin: 10px 0 0 0;
            font-size: 1em;
            font-weight: 500;
            line-height: 1.4;
            text-align: center;
        }
        .stDataFrame, .stTable {
            background: transparent !important;
            box-shadow: none !important;
            border-radius: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .stDataFrame table, .stTable table {
            background: transparent !important;
            border-radius: 10px !important;
            border-collapse: collapse !important;
            width: 100% !important;
        }
        .stDataFrame th, .stTable th {
            background-color: #5DDBDB !important;
            color: white !important;
            padding: 12px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 1.08em !important;
            border: 1px solid #BDC3C7 !important;
        }
        .stDataFrame td, .stTable td {
            background-color: white !important;
            color: #222 !important;
            padding: 12px !important;
            border: 1px solid #BDC3C7 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 1em !important;
        }
        .stDataFrame tr, .stTable tr {
            background: transparent !important;
        }
        .bar-row {
            margin-bottom: 12px;
        }
        .bar-label {
            display: block;
            font-weight: 500;
            margin-bottom: 4px;
        }
        .bar {
            width: 100%;
            background-color: #ddd;
            border-radius: 8px;
            height: 24px;
        }
        .bar-fill {
            background-color: #5DDBDB;
            height: 100%;
            border-radius: 8px;
        }

        /* Botones generales en calipso */
        .stButton > button {
            background-color: #5DDBDB !important;
            color: #0C1461 !important;
            border-radius: 8px;
            padding: 10px 20px;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            box-shadow: 0 4px 16px rgba(44, 62, 80, 0.15);
            transform: translateY(-2px) scale(1.04);
            color: #0C1461 !important;
            background-color: #5DDBDB !important;
        }

        /* Color base del texto general */
        body, .stApp, .markdown-text-container, .stMarkdown, p {
            color: #111 !important;
        }
        .header h1, .header h2, .header h3 {
            color: white !important;
        }

        /* Solo títulos y párrafos en negro */
        h1, h2, h3, p {
            color: #111 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Función para obtener la última hora de actualización desde Git
def obtener_ultima_actualizacion():
    fecha_a_mostrar = None
    mensaje_fecha = "Última Actualización:"

    # Intentar obtener la fecha del último commit de Git
    try:
        # Ruta del archivo relativa al repositorio
        file_path_relative_to_repo = Path("inputs") / "mongo_applicants_merged.csv"
        
        # Comando git log para obtener la fecha del último commit
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=iso-strict', str(file_path_relative_to_repo)],
            cwd=BASE_PATH,
            capture_output=True,
            text=True,
            check=True
        )
        
        git_date_str = result.stdout.strip()
        if git_date_str:
            # Parsear la fecha obtenida de git y convertir a zona horaria de Chile
            fecha_utc = datetime.fromisoformat(git_date_str)
            zona_horaria_chile = pytz.timezone('America/Santiago')
            fecha_a_mostrar = fecha_utc.astimezone(zona_horaria_chile)
            mensaje_fecha = "Última Actualización:"
        else:
            st.warning(f"Git log no retornó fecha para {file_path_relative_to_repo}.")
            
    except FileNotFoundError:
        st.warning("Error: Comando 'git' no encontrado en el servidor.")
        mensaje_fecha = "Última Actualización (Error Git - No encontrado):"
    except subprocess.CalledProcessError as e:
        st.warning(f"Error al ejecutar comando Git: {e}")
        mensaje_fecha = "Última Actualización (Error Git):"
    except Exception as e:
        st.warning(f"Error inesperado al obtener fecha de Git: {e}")
        mensaje_fecha = "Última Actualización (Error Inesperado):"

    # Si no se pudo obtener la fecha de Git, usar la fecha de modificación del archivo como respaldo
    if fecha_a_mostrar is None:
        try:
            archivo_mongo = BASE_PATH_INPUTS / "mongo_applicants_merged.csv"
            if archivo_mongo.exists():
                fecha_utc = datetime.fromtimestamp(archivo_mongo.stat().st_mtime, tz=pytz.utc)
                zona_horaria_chile = pytz.timezone('America/Santiago')
                fecha_a_mostrar = fecha_utc.astimezone(zona_horaria_chile)
                mensaje_fecha = "Última Actualización (del archivo en Servidor - UTC):"
            else:
                mensaje_fecha = "Última Actualización: Archivo no encontrado"
        except Exception as e:
            st.warning(f"Error al obtener la fecha de última actualización del archivo: {e}")
            mensaje_fecha = "Última Actualización: Error Archivo"

    return fecha_a_mostrar, mensaje_fecha

# Header azul bonito
st.markdown("""
    <div class="header">
        <h1>📊 Seguimiento jardines Bogotá </h1>
    </div>
""", unsafe_allow_html=True)

# Título simple adicional
st.title('Notas')

# Agregar botón de actualización al principio
if st.button("Actualizar Datos"):
   st.cache_data.clear()

# Obtener y mostrar la última hora de actualización
fecha_a_mostrar, mensaje_fecha = obtener_ultima_actualizacion()
if fecha_a_mostrar:
    st.info(f"{mensaje_fecha} {fecha_a_mostrar.strftime('%d/%m/%Y %H:%M:%S')}")
else:
    st.info(mensaje_fecha)

# Leer el archivo
file_path = 'inputs/mongo_applicants_merged.csv'
df = pd.read_csv(file_path)

# Filtrar solo las filas que tienen email (excluir None, NaN, vacíos)
df_con_email = df.dropna(subset=['email'])

# Contadores
usuarios_unicos = df_con_email['user'].nunique()
total_notas = len(df_con_email)

# Mostrar contadores en la parte superior
col1, col2 = st.columns(2)
with col1:
    st.metric("Usuarios únicos", usuarios_unicos)
with col2:
    st.metric("Total de notas", total_notas)

# Renombrar columnas para mostrar
df_mostrar = df_con_email[['timestamp','user', 'email', 'data', 'campus_name', 'campusId']].copy()
df_mostrar = df_mostrar.rename(columns={
    'campus_name': 'Nombre sede',
    'campusId': 'campus_code',
    'user': 'Usuario', 
    'email': 'Correo',
    'data': 'Nota',
    'timestamp': 'Fecha'
})

# Ordenar por fecha (más reciente primero)
df_mostrar = df_mostrar.sort_values('Fecha', ascending=False)

# Filtro por usuario
usuarios_unicos = sorted(df_mostrar['Correo'].dropna().unique())
usuario_seleccionado = st.selectbox(
    "Filtrar por usuario:",
    ["Todos los usuarios"] + usuarios_unicos
)

# Aplicar filtro si se selecciona un usuario específico
if usuario_seleccionado != "Todos los usuarios":
    df_filtrado = df_mostrar[df_mostrar['Correo'] == usuario_seleccionado]
else:
    df_filtrado = df_mostrar

# Mostrar tabla con columnas renombradas (sin índice)
st.dataframe(df_filtrado, hide_index=True)
