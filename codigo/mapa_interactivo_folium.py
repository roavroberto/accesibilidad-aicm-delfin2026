#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapa Interactivo de Accesibilidad al AICM con Folium
Programa Delfín 2026 - Accesibilidad al AICM

Genera un mapa HTML interactivo con todas las paradas de transporte público
y sus métricas de accesibilidad al Aeropuerto Internacional de la Ciudad de México.
"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
VIZ_DIR = Path("visualizaciones")

# Coordenadas del AICM
AICM_T1 = {'lat': 19.43531, 'lon': -99.08367, 'nombre': 'Terminal 1'}
AICM_T2 = {'lat': 19.42148, 'lon': -99.07725, 'nombre': 'Terminal 2'}

def cargar_datos():
    """Carga los datos de paradas con métricas de accesibilidad"""
    print("Cargando datos de paradas...")
    
    # Cargar paradas con distancias
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    print(f"  ✓ Paradas con distancias: {len(paradas):,}")
    
    # Cargar tiempos si existen
    try:
        tiempos = pd.read_csv(RESULTADOS_DIR / "tiempos_viaje_por_parada.csv")
        paradas = paradas.merge(
            tiempos[['stop_id', 'tiempo_promedio_min', 'num_viajes']],
            on='stop_id',
            how='left'
        )
        print(f"  ✓ Paradas con tiempos: {len(tiempos):,}")
    except:
        print("  ⚠ No hay datos de tiempos")
        paradas['tiempo_promedio_min'] = np.nan
        paradas['num_viajes'] = np.nan
    
    # Cargar velocidades si existen
    try:
        velocidades = pd.read_csv(RESULTADOS_DIR / "velocidad_promedio_filtrado.csv")
        paradas = paradas.merge(
            velocidades[['stop_id', 'velocidad_kmh']],
            on='stop_id',
            how='left'
        )
        print(f"  ✓ Paradas con velocidades: {len(velocidades):,}")
    except:
        print("  ⚠ No hay datos de velocidades")
        paradas['velocidad_kmh'] = np.nan
    
    # Cargar alcaldías si existen
    try:
        alcaldias = pd.read_csv(RESULTADOS_DIR / "paradas_con_alcaldia_centroides.csv")
        paradas = paradas.merge(
            alcaldias[['stop_id', 'nombre_alcaldia']],
            on='stop_id',
            how='left'
        )
        print(f"  ✓ Paradas con alcaldía: {len(alcaldias):,}")
    except:
        print("  ⚠ No hay datos de alcaldías")
        paradas['nombre_alcaldia'] = np.nan
    
    print(f"  ✓ Total de paradas: {len(paradas):,}")
    
    return paradas

def crear_mapa_base():
    """Crea el mapa base centrado en CDMX"""
    print("\nCreando mapa base...")
    
    # Centro de CDMX
    centro_cdmx = [19.4326, -99.1332]
    
    # Crear mapa base con tile de OpenStreetMap
    mapa = folium.Map(
        location=centro_cdmx,
        zoom_start=11,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # Agregar tile alternativo (satélite)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri World Imagery',
        name='Satélite',
        overlay=False,
        control=True
    ).add_to(mapa)
    
    # Agregar tile de transporte
    folium.TileLayer(
        tiles='https://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=6170aad10dfd42a38d4d8c709a536f38',
        attr='Thunderforest Transport',
        name='Transporte',
        overlay=False,
        control=True
    ).add_to(mapa)
    
    print("  ✓ Mapa base creado")
    
    return mapa

def obtener_color_distancia(distancia):
    """Retorna color según distancia al AICM"""
    if pd.isna(distancia):
        return 'gray'
    elif distancia < 5:
        return 'green'
    elif distancia < 10:
        return 'lightgreen'
    elif distancia < 15:
        return 'yellow'
    elif distancia < 20:
        return 'orange'
    else:
        return 'red'

def obtener_color_tiempo(tiempo):
    """Retorna color según tiempo de viaje"""
    if pd.isna(tiempo):
        return 'gray'
    elif tiempo < 20:
        return 'green'
    elif tiempo < 40:
        return 'lightgreen'
    elif tiempo < 60:
        return 'yellow'
    elif tiempo < 80:
        return 'orange'
    else:
        return 'red'

def obtener_color_velocidad(velocidad):
    """Retorna color según velocidad promedio"""
    if pd.isna(velocidad):
        return 'gray'
    elif velocidad > 25:
        return 'green'
    elif velocidad > 20:
        return 'lightgreen'
    elif velocidad > 15:
        return 'yellow'
    elif velocidad > 10:
        return 'orange'
    else:
        return 'red'

def agregar_capa_distancias(mapa, paradas):
    """Agrega capa de paradas coloreadas por distancia"""
    print("\nAgregando capa de distancias...")
    
    # Crear grupo de características
    grupo = folium.FeatureGroup(name='Distancia al AICM', overlay=True, control=True)
    
    # Agregar marcadores
    for idx, row in paradas.iterrows():
        if pd.isna(row['stop_lat']) or pd.isna(row['stop_lon']):
            continue
        
        color = obtener_color_distancia(row['distancia_km'])
        
        # Crear popup con información
        popup_html = f"""
        <div style="font-family: Arial; font-size: 11px; min-width: 200px;">
            <b style="font-size: 13px;">{row['stop_name']}</b><br>
            <hr style="margin: 5px 0;">
            <b>ID:</b> {row['stop_id']}<br>
            <b>Distancia:</b> {row['distancia_km']:.2f} km<br>
            <b>Coordenadas:</b> {row['stop_lat']:.5f}, {row['stop_lon']:.5f}<br>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=5,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=1
        ).add_to(grupo)
    
    grupo.add_to(mapa)
    print(f"  ✓ {len(paradas):,} paradas agregadas")

def agregar_capa_tiempos(mapa, paradas):
    """Agrega capa de paradas coloreadas por tiempo de viaje"""
    print("\nAgregando capa de tiempos...")
    
    # Filtrar paradas con tiempos
    paradas_con_tiempo = paradas[paradas['tiempo_promedio_min'].notna()].copy()
    
    if len(paradas_con_tiempo) == 0:
        print("  ⚠ No hay paradas con datos de tiempo")
        return
    
    # Crear grupo de características
    grupo = folium.FeatureGroup(name='Tiempo de Viaje', overlay=True, control=True)
    
    # Agregar marcadores
    for idx, row in paradas_con_tiempo.iterrows():
        color = obtener_color_tiempo(row['tiempo_promedio_min'])
        
        # Crear popup con información
        popup_html = f"""
        <div style="font-family: Arial; font-size: 11px; min-width: 200px;">
            <b style="font-size: 13px;">{row['stop_name']}</b><br>
            <hr style="margin: 5px 0;">
            <b>Distancia:</b> {row['distancia_km']:.2f} km<br>
            <b>Tiempo promedio:</b> {row['tiempo_promedio_min']:.1f} min<br>
            <b>Viajes observados:</b> {int(row['num_viajes']) if pd.notna(row['num_viajes']) else 'N/A'}<br>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=6,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            weight=1
        ).add_to(grupo)
    
    grupo.add_to(mapa)
    print(f"  ✓ {len(paradas_con_tiempo):,} paradas con tiempos agregadas")

def agregar_capa_velocidades(mapa, paradas):
    """Agrega capa de paradas coloreadas por velocidad"""
    print("\nAgregando capa de velocidades...")
    
    # Filtrar paradas con velocidades
    paradas_con_vel = paradas[paradas['velocidad_kmh'].notna()].copy()
    
    if len(paradas_con_vel) == 0:
        print("  ⚠ No hay paradas con datos de velocidad")
        return
    
    # Crear grupo de características
    grupo = folium.FeatureGroup(name='Velocidad Promedio', overlay=True, control=True)
    
    # Agregar marcadores
    for idx, row in paradas_con_vel.iterrows():
        color = obtener_color_velocidad(row['velocidad_kmh'])
        
        # Crear popup con información
        popup_html = f"""
        <div style="font-family: Arial; font-size: 11px; min-width: 200px;">
            <b style="font-size: 13px;">{row['stop_name']}</b><br>
            <hr style="margin: 5px 0;">
            <b>Distancia:</b> {row['distancia_km']:.2f} km<br>
            <b>Tiempo:</b> {row['tiempo_promedio_min']:.1f} min<br>
            <b>Velocidad:</b> {row['velocidad_kmh']:.1f} km/h<br>
            <b>Alcaldía:</b> {row['nombre_alcaldia'] if pd.notna(row['nombre_alcaldia']) else 'N/A'}<br>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['stop_lat'], row['stop_lon']],
            radius=7,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            weight=2
        ).add_to(grupo)
    
    grupo.add_to(mapa)
    print(f"  ✓ {len(paradas_con_vel):,} paradas con velocidades agregadas")

def agregar_marcadores_aicm(mapa):
    """Agrega marcadores especiales para las terminales del AICM"""
    print("\nAgregando marcadores del AICM...")
    
    # Terminal 1
    folium.Marker(
        location=[AICM_T1['lat'], AICM_T1['lon']],
        popup=folium.Popup(f"<b>{AICM_T1['nombre']}</b><br>Aeropuerto Internacional de la Ciudad de México", 
                          max_width=200),
        icon=folium.Icon(color='red', icon='plane', prefix='fa'),
        tooltip=AICM_T1['nombre']
    ).add_to(mapa)
    
    # Terminal 2
    folium.Marker(
        location=[AICM_T2['lat'], AICM_T2['lon']],
        popup=folium.Popup(f"<b>{AICM_T2['nombre']}</b><br>Aeropuerto Internacional de la Ciudad de México", 
                          max_width=200),
        icon=folium.Icon(color='blue', icon='plane', prefix='fa'),
        tooltip=AICM_T2['nombre']
    ).add_to(mapa)
    
    print("  ✓ Terminales T1 y T2 agregadas")

def agregar_leyenda(mapa):
    """Agrega leyenda explicativa al mapa"""
    leyenda_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 250px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 10px;
                ">
    <b style="font-size:14px;">Leyenda de Colores</b><br>
    <hr style="margin: 5px 0;">
    
    <b>Distancia:</b><br>
    <i class="fa fa-circle" style="color:green"></i> < 5 km<br>
    <i class="fa fa-circle" style="color:lightgreen"></i> 5-10 km<br>
    <i class="fa fa-circle" style="color:yellow"></i> 10-15 km<br>
    <i class="fa fa-circle" style="color:orange"></i> 15-20 km<br>
    <i class="fa fa-circle" style="color:red"></i> > 20 km<br>
    
    <hr style="margin: 5px 0;">
    
    <b>Tiempo de viaje:</b><br>
    <i class="fa fa-circle" style="color:green"></i> < 20 min<br>
    <i class="fa fa-circle" style="color:lightgreen"></i> 20-40 min<br>
    <i class="fa fa-circle" style="color:yellow"></i> 40-60 min<br>
    <i class="fa fa-circle" style="color:orange"></i> 60-80 min<br>
    <i class="fa fa-circle" style="color:red"></i> > 80 min<br>
    
    <hr style="margin: 5px 0;">
    
    <b>Velocidad:</b><br>
    <i class="fa fa-circle" style="color:green"></i> > 25 km/h<br>
    <i class="fa fa-circle" style="color:lightgreen"></i> 20-25 km/h<br>
    <i class="fa fa-circle" style="color:yellow"></i> 15-20 km/h<br>
    <i class="fa fa-circle" style="color:orange"></i> 10-15 km/h<br>
    <i class="fa fa-circle" style="color:red"></i> < 10 km/h<br>
    </div>
    """
    
    mapa.get_root().html.add_child(folium.Element(leyenda_html))

def agregar_titulo(mapa):
    """Agrega título al mapa"""
    titulo_html = """
    <div style="position: fixed; 
                top: 10px; left: 50%; transform: translateX(-50%); 
                width: auto; 
                background-color: white; border:3px solid #333; z-index:9999; 
                font-size:16px; padding: 15px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
                ">
    <b style="font-size:18px;">🚌 Accesibilidad al AICM - Transporte Público CDMX</b><br>
    <span style="font-size:12px;">Programa Delfín 2026 | Roberto Rojas & Janine</span>
    </div>
    """
    
    mapa.get_root().html.add_child(folium.Element(titulo_html))

def guardar_mapa(mapa):
    """Guarda el mapa como archivo HTML"""
    print("\nGuardando mapa interactivo...")
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "mapa_interactivo_accesibilidad_aicm.html"
    
    mapa.save(output_path)
    
    print(f"  ✓ Mapa guardado: {output_path}")
    print(f"  ✓ Tamaño: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"\n  📌 Abre este archivo en tu navegador:")
    print(f"     {output_path.absolute()}")

def main():
    print("="*80)
    print("MAPA INTERACTIVO DE ACCESIBILIDAD AL AICM")
    print("="*80)
    
    # 1. Cargar datos
    paradas = cargar_datos()
    
    # 2. Crear mapa base
    mapa = crear_mapa_base()
    
    # 3. Agregar capas de datos
    agregar_capa_distancias(mapa, paradas)
    agregar_capa_tiempos(mapa, paradas)
    agregar_capa_velocidades(mapa, paradas)
    
    # 4. Agregar marcadores del AICM
    agregar_marcadores_aicm(mapa)
    
    # 5. Agregar elementos visuales
    agregar_leyenda(mapa)
    agregar_titulo(mapa)
    
    # 6. Guardar mapa
    guardar_mapa(mapa)
    
    print("\n" + "="*80)
    print("MAPA INTERACTIVO GENERADO EXITOSAMENTE")
    print("="*80)
    print("\n📋 Instrucciones:")
    print("  1. Abre el archivo HTML en tu navegador")
    print("  2. Usa las capas en la esquina superior derecha para cambiar entre:")
    print("     - Distancia al AICM")
    print("     - Tiempo de viaje")
    print("     - Velocidad promedio")
    print("  3. Haz clic en los marcadores para ver información detallada")
    print("  4. Usa zoom para explorar diferentes zonas de CDMX")
    print("  5. Puedes cambiar entre mapa callejero, satélite y transporte")
    print("\n💡 Este mapa es perfecto para tu presentación final del Programa Delfín")

if __name__ == "__main__":
    main()
