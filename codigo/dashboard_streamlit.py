#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Interactivo de Accesibilidad al AICM con Streamlit
Programa Delfín 2026 - Accesibilidad al AICM
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Accesibilidad al AICM", page_icon="🚌", layout="wide")

RESULTADOS_DIR = Path("datos/resultados")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

@st.cache_data
def cargar_datos():
    datos = {}
    try:
        datos['paradas'] = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    except:
        return None
    
    try:
        tiempos = pd.read_csv(RESULTADOS_DIR / "tiempos_viaje_por_parada.csv")
        datos['paradas'] = datos['paradas'].merge(tiempos[['stop_id', 'tiempo_promedio_min']], on='stop_id', how='left')
    except:
        datos['paradas']['tiempo_promedio_min'] = np.nan
        
    try:
        velocidades = pd.read_csv(RESULTADOS_DIR / "velocidad_promedio_filtrado.csv")
        datos['paradas'] = datos['paradas'].merge(velocidades[['stop_id', 'velocidad_kmh']], on='stop_id', how='left')
    except:
        datos['paradas']['velocidad_kmh'] = np.nan
        
    try:
        alcaldias = pd.read_csv(RESULTADOS_DIR / "paradas_con_alcaldia_centroides.csv")
        datos['paradas'] = datos['paradas'].merge(alcaldias[['stop_id', 'nombre_alcaldia']], on='stop_id', how='left')
    except:
        datos['paradas']['nombre_alcaldia'] = np.nan
        
    try:
        datos['stats_alcaldias'] = pd.read_csv(RESULTADOS_DIR / "estadisticas_por_alcaldia_centroides.csv")
    except:
        datos['stats_alcaldias'] = None
        
    return datos

datos = cargar_datos()
if datos is None:
    st.error("Error al cargar datos.")
    st.stop()

st.title("🚌 Dashboard de Accesibilidad al AICM")
st.markdown("### Programa Delfín 2026 - Roberto Rojas & Janine")
st.markdown("---")

st.sidebar.header("🔍 Filtros")

alcaldias_disponibles = sorted(datos['paradas']['nombre_alcaldia'].dropna().unique())
alcaldia_seleccionada = st.sidebar.multiselect("Selecciona alcaldías (vacío = todas):", options=alcaldias_disponibles, default=[])

radio_km = st.sidebar.slider("Radio desde alcaldía (km):", 0, 50, 10)
distancia_max = st.sidebar.slider("Distancia máxima al AICM (km):", 0, 40, 40)

df_filtrado = datos['paradas'].copy()

if alcaldia_seleccionada:
    centroides = df_filtrado[df_filtrado['nombre_alcaldia'].isin(alcaldia_seleccionada)].groupby('nombre_alcaldia').agg({'stop_lat': 'mean', 'stop_lon': 'mean'}).reset_index()
    
    distancias = []
    for _, row in df_filtrado.iterrows():
        dists = haversine(row['stop_lat'], row['stop_lon'], centroides['stop_lat'].values, centroides['stop_lon'].values)
        distancias.append(np.min(dists))
    
    df_filtrado['distancia_a_alcaldia'] = distancias
    df_filtrado = df_filtrado[df_filtrado['distancia_a_alcaldia'] <= radio_km]
    st.sidebar.info(f"Filtrando por {len(alcaldia_seleccionada)} alcaldía(s) con radio de {radio_km} km")
else:
    st.sidebar.info("Mostrando TODAS las paradas")

df_filtrado = df_filtrado[df_filtrado['distancia_km'] <= distancia_max]

st.sidebar.metric("Paradas visibles", f"{len(df_filtrado):,}")

tab1, tab2, tab3 = st.tabs(["📍 Mapa", "📈 Análisis", "🚀 Accesibilidad por Alcaldía"])

with tab1:
    st.header("📍 Mapa Interactivo")
    if len(df_filtrado) > 0:
        centro = [df_filtrado['stop_lat'].mean(), df_filtrado['stop_lon'].mean()]
        mapa = folium.Map(location=centro, zoom_start=11)
        
        for idx, row in df_filtrado.iterrows():
            color = 'blue' if row['distancia_km'] < 10 else 'orange' if row['distancia_km'] < 20 else 'red'
            folium.CircleMarker(
                location=[row['stop_lat'], row['stop_lon']],
                radius=4,
                popup=f"<b>{row['stop_name']}</b><br>{row['distancia_km']:.1f} km al AICM",
                color=color, fill=True, fillColor=color, fillOpacity=0.7
            ).add_to(mapa)
            
        folium.Marker([19.43531, -99.08367], popup="AICM", icon=folium.Icon(color='red', icon='plane')).add_to(mapa)
        st_folium(mapa, width=None, height=600)
    else:
        st.warning("No hay paradas con estos filtros.")

with tab2:
    st.header("📈 Análisis General")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribución de Distancias")
        st.bar_chart(df_filtrado['distancia_km'].value_counts().sort_index())
    with col2:
        st.subheader("Estadísticas Rápidas")
        st.metric("Distancia Promedio", f"{df_filtrado['distancia_km'].mean():.1f} km")
        if df_filtrado['tiempo_promedio_min'].notna().any():
            st.metric("Tiempo Promedio", f"{df_filtrado['tiempo_promedio_min'].mean():.1f} min")
        if df_filtrado['velocidad_kmh'].notna().any():
            st.metric("Velocidad Promedio", f"{df_filtrado['velocidad_kmh'].mean():.1f} km/h")

with tab3:
    st.header("🚀 Accesibilidad desde Alcaldías")
    st.markdown("Selecciona una alcaldía para ver sus rutas más eficientes hacia el AICM.")
    
    if datos['stats_alcaldias'] is not None:
        alcaldia_ruta = st.selectbox("Selecciona una alcaldía:", sorted(datos['stats_alcaldias']['alcaldia'].unique()))
        
        stats_alc = datos['stats_alcaldias'][datos['stats_alcaldias']['alcaldia'] == alcaldia_ruta].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Distancia promedio", f"{stats_alc['distancia_promedio_km']:.1f} km")
        c2.metric("Tiempo promedio", f"{stats_alc['tiempo_promedio_min']:.1f} min" if pd.notna(stats_alc['tiempo_promedio_min']) else "N/A")
        c3.metric("Velocidad promedio", f"{stats_alc['velocidad_promedio_kmh']:.1f} km/h" if pd.notna(stats_alc['velocidad_promedio_kmh']) else "N/A")
        
        st.subheader("Top 10 Paradas más cercanas al AICM en esta alcaldía")
        paradas_alc = datos['paradas'][datos['paradas']['nombre_alcaldia'] == alcaldia_ruta].nsmallest(10, 'distancia_km')
        st.dataframe(paradas_alc[['stop_name', 'distancia_km', 'tiempo_promedio_min', 'velocidad_kmh']].rename(columns={'stop_name': 'Parada', 'distancia_km': 'Dist (km)', 'tiempo_promedio_min': 'Tiempo (min)', 'velocidad_kmh': 'Vel (km/h)'}), use_container_width=True)
        
        st.subheader("Mapa de rutas desde la alcaldía")
        centro_alc = [paradas_alc['stop_lat'].mean(), paradas_alc['stop_lon'].mean()]
        mapa_ruta = folium.Map(location=centro_alc, zoom_start=11)
        
        for idx, row in paradas_alc.head(10).iterrows():
            folium.CircleMarker([row['stop_lat'], row['stop_lon']], radius=8, color='blue', fill=True).add_to(mapa_ruta)
            folium.PolyLine([[row['stop_lat'], row['stop_lon']], [19.43531, -99.08367]], color='orange', weight=1, opacity=0.5).add_to(mapa_ruta)
            
        folium.Marker([19.43531, -99.08367], popup="AICM", icon=folium.Icon(color='red', icon='plane')).add_to(mapa_ruta)
        st_folium(mapa_ruta, width=None, height=500)
