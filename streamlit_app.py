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

# Agregar botón de actualización al principio
if st.button("Actualizar Datos"):
   st.cache_data.clear()

# Obtener y mostrar la última hora de actualización
fecha_a_mostrar, mensaje_fecha = obtener_ultima_actualizacion()
if fecha_a_mostrar:
    st.info(f"{mensaje_fecha} {fecha_a_mostrar.strftime('%d/%m/%Y %H:%M:%S')}")
else:
    st.info(mensaje_fecha)

# Crear pestañas para organizar el contenido
tab1, tab2 = st.tabs(["📝 Notas de Usuarios", "📊 Estadísticas de Uso"])

with tab1:
    # Título simple adicional
    st.title('Notas')

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

with tab2:
    st.title('📊 Estadísticas de Uso de la Aplicación')
    
    # Leer datos de Mixpanel
    try:
        df_mixpanel = pd.read_csv('inputs/mixpanel_applicants_collapsed.csv')
        
        # Métricas principales
        st.subheader('📈 Métricas Principales')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_usuarios = df_mixpanel['user'].nunique()
            st.metric("Total Usuarios", total_usuarios)
            
        with col2:
            total_applicants = df_mixpanel['applicant_id'].nunique()
            st.metric("Total Applicants", total_applicants)
            
        with col3:
            total_interacciones = df_mixpanel[['click_dashboard_menu', 'click_reg_user-log-in_log-in-button', 
                                             'click_school_pin', 'open_school_profile', 'favorite_school_from_list']].sum().sum()
            st.metric("Total Interacciones", f"{total_interacciones:,}")
            
        with col4:
            avg_interacciones = total_interacciones / total_usuarios if total_usuarios > 0 else 0
            st.metric("Promedio Interacciones/Usuario", f"{avg_interacciones:.1f}")
        
        # Análisis de comportamiento
        st.subheader('🎯 Análisis de Comportamiento')
        
        # Calcular métricas de comportamiento
        comportamiento_metrics = {
            'Clicks Dashboard Menu': df_mixpanel['click_dashboard_menu'].sum(),
            'Clicks Login Button': df_mixpanel['click_reg_user-log-in_log-in-button'].sum(),
            'Clicks School Pin': df_mixpanel['click_school_pin'].sum(),
            'Perfiles Abiertos': df_mixpanel['open_school_profile'].sum(),
            'Perfiles Cerrados': df_mixpanel['close_school_profile'].sum(),
            'Favoritos Agregados': df_mixpanel['favorite_school_from_list'].sum(),
            'Favoritos Removidos': df_mixpanel['remove_favorite_school_from_list'].sum(),
            'Logins': df_mixpanel['login'].sum(),
            'Filtros de Mapa': df_mixpanel['map_filter_click'].sum(),
            'Clicks en Grado': df_mixpanel['map_grade_click'].sum()
        }
        
        # Crear gráfico de barras para comportamiento
        fig_comportamiento = px.bar(
            x=list(comportamiento_metrics.keys()),
            y=list(comportamiento_metrics.values()),
            title="Interacciones por Tipo",
            color=list(comportamiento_metrics.values()),
            color_continuous_scale='Blues'
        )
        fig_comportamiento.update_layout(
            xaxis_title="Tipo de Interacción",
            yaxis_title="Cantidad",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_comportamiento, use_container_width=True)
        
        # Análisis de contenido visitado
        st.subheader('📚 Contenido Más Visitado')
        
        contenido_metrics = {
            'Liderazgo Escolar': df_mixpanel['sp_school_leadership'].sum(),
            'Rendimiento Escolar': df_mixpanel['sp_school_performance'].sum(),
            'Fotos Escolares': df_mixpanel['sp_school_photo'].sum(),
            'Precios': df_mixpanel['sp_school_price'].sum(),
            'Programas': df_mixpanel['sp_school_programs'].sum(),
            'Estudiantes': df_mixpanel['sp_school_students'].sum()
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_contenido = px.pie(
                values=list(contenido_metrics.values()),
                names=list(contenido_metrics.keys()),
                title="Distribución de Contenido Visitado"
            )
            st.plotly_chart(fig_contenido, use_container_width=True)
            
        with col2:
            # Top usuarios más activos
            st.subheader('👥 Usuarios Más Activos')
            df_usuarios_activos = df_mixpanel.groupby('email').agg({
                'click_dashboard_menu': 'sum',
                'click_school_pin': 'sum',
                'open_school_profile': 'sum',
                'favorite_school_from_list': 'sum'
            }).sum(axis=1).sort_values(ascending=False).head(10)
            
            fig_usuarios = px.bar(
                x=df_usuarios_activos.values,
                y=df_usuarios_activos.index,
                orientation='h',
                title="Top 10 Usuarios Más Activos"
            )
            fig_usuarios.update_layout(height=400)
            st.plotly_chart(fig_usuarios, use_container_width=True)
        
        # Análisis geográfico
        st.subheader('🗺️ Análisis Geográfico')
        
        # Crear mapa de calor de actividad
        if 'lat' in df_mixpanel.columns and 'lng' in df_mixpanel.columns:
            # Calcular actividad total por ubicación
            df_mixpanel['actividad_total'] = df_mixpanel[['click_dashboard_menu', 'click_school_pin', 
                                                         'open_school_profile', 'favorite_school_from_list']].sum(axis=1)
            
            fig_mapa = px.scatter_mapbox(
                df_mixpanel,
                lat='lat',
                lon='lng',
                size='actividad_total',
                color='actividad_total',
                hover_name='formatted_address',
                zoom=10,
                title="Mapa de Actividad de Usuarios",
                color_continuous_scale='Blues'
            )
            fig_mapa.update_layout(
                mapbox_style="open-street-map",
                height=500
            )
            st.plotly_chart(fig_mapa, use_container_width=True)
        
        # Estadísticas por área
        if 'area_id' in df_mixpanel.columns:
            st.subheader('🏘️ Actividad por Área')
            actividad_por_area = df_mixpanel.groupby('area_id').agg({
                'click_dashboard_menu': 'sum',
                'click_school_pin': 'sum',
                'open_school_profile': 'sum',
                'favorite_school_from_list': 'sum'
            }).sum(axis=1).sort_values(ascending=False)
            
            fig_area = px.bar(
                x=actividad_por_area.index,
                y=actividad_por_area.values,
                title="Actividad por Área ID"
            )
            st.plotly_chart(fig_area, use_container_width=True)
            
    except FileNotFoundError:
        st.error("No se encontró el archivo mixpanel_applicants_collapsed.csv")
    except Exception as e:
        st.error(f"Error al procesar los datos de Mixpanel: {e}")
