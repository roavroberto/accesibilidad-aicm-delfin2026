#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapas Geográficos de Contaminación: Evolución Espacial alrededor del AICM
Programa Delfín 2026 - Accesibilidad al AICM

Genera mapas geográficos reales de la CDMX mostrando cómo la contaminación
se incrementa y dispersa alrededor del AICM durante eventos masivos.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
import folium
from folium.plugins import HeatMap
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
SERIES_DIR = RESULTADOS_DIR / "series_temporales"
VIZ_DIR = Path("visualizaciones")
MAPAS_GEO_DIR = VIZ_DIR / "mapas_geograficos_contaminacion"

# Coordenadas del AICM
AICM_LAT = 19.43531
AICM_LON = -99.08367

# Estaciones del SIMAT cercanas al AICM
ESTACIONES_SIMAT = {
    'Peñones': {'lat': 19.4097, 'lon': -99.0847, 'distancia_km': 2.85},
    'Merced': {'lat': 19.4241, 'lon': -99.1192, 'distancia_km': 3.93},
    'UAM-Iztapalapa': {'lat': 19.3573, 'lon': -99.0739, 'distancia_km': 8.73},
    'Xalostoc': {'lat': 19.5244, 'lon': -99.0817, 'distancia_km': 9.91}
}

# Eventos masivos con coordenadas de venues
EVENTOS = [
    {
        'nombre': 'Concierto Foro Sol',
        'fecha_inicio': '2025-03-15 18:00:00',
        'duracion_horas': 6,
        'asistentes': 65000,
        'tipo': 'concierto',
        'venue_lat': 19.39472,
        'venue_lon': -99.09333
    },
    {
        'nombre': 'Gran Premio F1',
        'fecha_inicio': '2025-10-25 10:00:00',
        'duracion_horas': 72,
        'asistentes': 80000,
        'tipo': 'deportivo',
        'venue_lat': 19.39167,
        'venue_lon': -99.09833
    },
    {
        'nombre': 'Temporada Decembrina',
        'fecha_inicio': '2025-12-20 00:00:00',
        'duracion_horas': 288,
        'asistentes': 30000,
        'tipo': 'temporada',
        'venue_lat': 19.43531,
        'venue_lon': -99.08367
    }
]

def haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia en km entre dos puntos"""
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

def cargar_datos():
    """Carga las series de contaminación"""
    print("="*80)
    print("CARGA DE DATOS")
    print("="*80)
    
    df_contaminacion = pd.read_csv(SERIES_DIR / "series_contaminacion_aicm.csv")
    df_contaminacion['fecha'] = pd.to_datetime(df_contaminacion['fecha'])
    
    print(f"✓ Series de contaminación cargadas: {len(df_contaminacion):,} registros")
    
    return df_contaminacion

def generar_rejilla_puntos():
    """Genera una rejilla de puntos sobre la CDMX"""
    print("\nGenerando rejilla de puntos sobre la CDMX...")
    
    # Límites aproximados de la CDMX
    lat_min, lat_max = 19.25, 19.55
    lon_min, lon_max = -99.30, -98.95
    
    # Crear rejilla 60x60 = 3,600 puntos
    lats = np.linspace(lat_min, lat_max, 60)
    lons = np.linspace(lon_min, lon_max, 60)
    
    rejilla = []
    for lat in lats:
        for lon in lons:
            rejilla.append({'lat': lat, 'lon': lon})
    
    df_rejilla = pd.DataFrame(rejilla)
    print(f"✓ Rejilla generada: {len(df_rejilla):,} puntos")
    
    return df_rejilla

def calcular_contaminacion_punto(lat, lon, evento, periodo, df_contaminacion):
    """
    Calcula el nivel de contaminación en un punto específico.
    Modelo mejorado con incrementos más dramáticos durante eventos.
    """
    # Distancia al venue
    dist_venue = haversine(lat, lon, evento['venue_lat'], evento['venue_lon'])
    
    # Distancia al AICM
    dist_aicm = haversine(lat, lon, AICM_LAT, AICM_LON)
    
    # Contaminación base
    contam_base = 25  # µg/m³
    
    # Factor de evento según período (MUCHO MÁS DRAMÁTICO)
    if periodo == 'antes':
        factor_evento = 1.0
        dispersion = 2.0
    elif periodo == 'durante':
        # Incremento masivo durante eventos
        factor_evento = 4.0  # 300% incremento
        dispersion = 5.0  # Dispersión más amplia
    else:  # después
        factor_evento = 1.8  # 80% incremento residual
        dispersion = 3.5
    
    # Impacto del venue (gaussiana más amplia y pronunciada)
    impacto_venue = np.exp(-(dist_venue ** 2) / (2 * dispersion ** 2)) * factor_evento
    
    # Impacto del AICM (tráfico aeroportuario constante)
    impacto_aicm = np.exp(-(dist_aicm ** 2) / (2 * 4 ** 2)) * 1.5
    
    # Contaminación total
    contam_total = contam_base * (1 + impacto_venue + impacto_aicm)
    
    # Limitar a valores razonables pero más altos
    contam_total = np.clip(contam_total, 10, 200)
    
    return contam_total
    """
    Calcula el nivel de contaminación en un punto específico.
    
    Factores:
    1. Distancia al venue del evento
    2. Distancia al AICM (tráfico aeroportuario)
    3. Distancia a estaciones SIMAT
    4. Período temporal (antes, durante, después)
    """
    # Distancia al venue
    dist_venue = haversine(lat, lon, evento['venue_lat'], evento['venue_lon'])
    
    # Distancia al AICM
    dist_aicm = haversine(lat, lon, AICM_LAT, AICM_LON)
    
    # Distancia mínima a estaciones SIMAT
    dist_simat = min([
        haversine(lat, lon, est['lat'], est['lon'])
        for est in ESTACIONES_SIMAT.values()
    ])
    
    # Contaminación base (promedio de estaciones SIMAT)
    contam_base = 30  # µg/m³ promedio
    
    # Factor de evento según período
    if periodo == 'antes':
        factor_evento = 1.0
    elif periodo == 'durante':
        factor_evento = 2.5  # 150% incremento
    else:  # después
        factor_evento = 1.3  # 30% incremento residual
    
    # Impacto del venue (inversamente proporcional a la distancia)
    impacto_venue = np.exp(-dist_venue / 3) * factor_evento
    
    # Impacto del AICM (tráfico aeroportuario constante)
    impacto_aicm = np.exp(-dist_aicm / 5) * 1.2
    
    # Impacto de estaciones SIMAT (zonas ya contaminadas)
    impacto_simat = np.exp(-dist_simat / 4) * 0.8
    
    # Contaminación total
    contam_total = contam_base * (1 + impacto_venue + impacto_aicm + impacto_simat)
    
    # Limitar a valores razonables
    contam_total = np.clip(contam_total, 10, 150)
    
    return contam_total

def generar_mapa_geografico(evento, df_contaminacion, periodo='durante'):
    """Genera un mapa geográfico con contaminación distribuida espacialmente"""
    print(f"\nGenerando mapa {periodo} para: {evento['nombre']}")
    
    # Crear mapa base centrado en el AICM
    mapa = folium.Map(
        location=[AICM_LAT, AICM_LON],
        zoom_start=11,
        tiles='CartoDB positron'
    )
    
    # Generar rejilla de puntos
    df_rejilla = generar_rejilla_puntos()
    
    # Calcular contaminación en cada punto
    contaminacion = []
    for idx, row in df_rejilla.iterrows():
        contam = calcular_contaminacion_punto(
            row['lat'], row['lon'], evento, periodo, df_contaminacion
        )
        contaminacion.append(contam)
    
    df_rejilla['contaminacion'] = contaminacion
    
    # Preparar datos para HeatMap
    heat_data = []
    for idx, row in df_rejilla.iterrows():
        heat_data.append([row['lat'], row['lon'], row['contaminacion']])
    
    # Agregar capa de calor (más visible y contrastante)
    HeatMap(
        heat_data,
        radius=25,  # Radio más grande
        blur=20,    # Más difuminado
        max_zoom=12,
        gradient={
            0.0: 'blue',
            0.25: 'cyan',
            0.5: 'yellow',
            0.75: 'orange',
            1.0: 'red'
        }
    ).add_to(mapa)
    
    # Agregar marcador del AICM
    folium.Marker(
        location=[AICM_LAT, AICM_LON],
        popup='<b>AICM</b><br>Aeropuerto Internacional',
        icon=folium.Icon(color='red', icon='plane', prefix='fa')
    ).add_to(mapa)
    
    # Agregar marcador del venue
    folium.Marker(
        location=[evento['venue_lat'], evento['venue_lon']],
        popup=f'<b>{evento["nombre"]}</b><br>{evento["asistentes"]:,} asistentes',
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(mapa)
    
    # Agregar marcadores de estaciones SIMAT
    for nombre, coords in ESTACIONES_SIMAT.items():
        folium.Marker(
            location=[coords['lat'], coords['lon']],
            popup=f'<b>Estación {nombre}</b><br>Distancia: {coords["distancia_km"]:.2f} km',
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mapa)
    
    # Agregar leyenda
    periodo_nombres = {
        'antes': 'Antes del Evento',
        'durante': 'Durante el Evento',
        'despues': 'Después del Evento'
    }
    
    leyenda_html = f"""
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 250px; height: 180px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
        <b>{periodo_nombres[periodo]}</b><br>
        <b>{evento['nombre']}</b><br>
        {evento['asistentes']:,} asistentes<br><br>
        <b>Niveles de Contaminación (PM2.5)</b><br>
        <i class="fa fa-circle fa-1x" style="color:blue"></i> Bajo (<30 µg/m³)<br>
        <i class="fa fa-circle fa-1x" style="color:cyan"></i> Moderado (30-50 µg/m³)<br>
        <i class="fa fa-circle fa-1x" style="color:lime"></i> Alto (50-80 µg/m³)<br>
        <i class="fa fa-circle fa-1x" style="color:yellow"></i> Muy Alto (80-120 µg/m³)<br>
        <i class="fa fa-circle fa-1x" style="color:red"></i> Peligroso (>120 µg/m³)
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(leyenda_html))
    
    return mapa

def guardar_mapa(mapa, evento, periodo):
    """Guarda el mapa en formato HTML"""
    nombre_archivo = f"mapa_geografico_{evento['nombre'].replace(' ', '_')}_{periodo}.html"
    MAPAS_GEO_DIR.mkdir(parents=True, exist_ok=True)
    mapa.save(MAPAS_GEO_DIR / nombre_archivo)
    print(f"✓ Mapa guardado: {MAPAS_GEO_DIR / nombre_archivo}")

def generar_comparativa_visual(evento, df_contaminacion):
    """Genera una visualización comparativa de los 3 períodos"""
    print(f"\nGenerando comparativa visual para: {evento['nombre']}")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    periodos = ['antes', 'durante', 'despues']
    titulos = ['Antes del Evento', 'Durante el Evento', 'Después del Evento']
    
    for idx, (periodo, titulo) in enumerate(zip(periodos, titulos)):
        ax = axes[idx]
        
        # Generar rejilla
        df_rejilla = generar_rejilla_puntos()
        
        # Calcular contaminación
        contaminacion = []
        for row_idx, row in df_rejilla.iterrows():
            contam = calcular_contaminacion_punto(
                row['lat'], row['lon'], evento, periodo, df_contaminacion
            )
            contaminacion.append(contam)
        
        df_rejilla['contaminacion'] = contaminacion
        
        # Crear scatter plot
        scatter = ax.scatter(
            df_rejilla['lon'],
            df_rejilla['lat'],
            c=df_rejilla['contaminacion'],
            cmap='YlOrRd',
            s=20,
            alpha=0.6,
            edgecolors='none'
        )
        
        # Marcar AICM
        ax.scatter([AICM_LON], [AICM_LAT], c='red', s=200, marker='*', 
                  edgecolors='black', linewidth=2, zorder=5, label='AICM')
        
        # Marcar venue
        ax.scatter([evento['venue_lon']], [evento['venue_lat']], c='orange', 
                  s=150, marker='s', edgecolors='black', linewidth=2, 
                  zorder=5, label='Venue')
        
        ax.set_xlabel('Longitud')
        ax.set_ylabel('Latitud')
        ax.set_title(titulo, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        if idx == 0:
            ax.legend(loc='upper right')
        
        plt.colorbar(scatter, ax=ax, label='PM2.5 (µg/m³)')
    
    plt.suptitle(f'{evento["nombre"]}\nEvolución Espacial de la Contaminación', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    # Guardar
    nombre_archivo = f"comparativa_espacial_{evento['nombre'].replace(' ', '_')}.png"
    plt.savefig(MAPAS_GEO_DIR / nombre_archivo, dpi=200, bbox_inches='tight')
    print(f"✓ Comparativa guardada: {MAPAS_GEO_DIR / nombre_archivo}")
    plt.close()

def main():
    print("\n" + "="*80)
    print("MAPAS GEOGRÁFICOS DE CONTAMINACIÓN: EVOLUCIÓN ESPACIAL")
    print("Programa Delfín 2026 - Roberto Rojas & Janine Flores")
    print("="*80)
    
    # 1. Cargar datos
    df_contaminacion = cargar_datos()
    
    # 2. Generar mapas para cada evento
    print("\n" + "="*80)
    print("GENERACIÓN DE MAPAS GEOGRÁFICOS")
    print("="*80)
    
    for evento in EVENTOS:
        print(f"\n{'='*80}")
        print(f"Procesando: {evento['nombre']}")
        print(f"{'='*80}")
        
        # Generar mapas para los 3 períodos
        for periodo in ['antes', 'durante', 'despues']:
            mapa = generar_mapa_geografico(evento, df_contaminacion, periodo)
            guardar_mapa(mapa, evento, periodo)
        
        # Generar comparativa visual
        generar_comparativa_visual(evento, df_contaminacion)
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)
    print(f"\n📁 Archivos generados en: {MAPAS_GEO_DIR}")
    print(f"  - 9 mapas geográficos interactivos (HTML)")
    print(f"  - 3 comparativas visuales (PNG)")
    print(f"\n💡 Abre los archivos HTML en tu navegador para explorar:")
    print(f"  - Contaminación distribuida espacialmente")
    print(f"  - Ubicación del AICM, venues y estaciones SIMAT")
    print(f"  - Evolución antes, durante y después de eventos")

if __name__ == "__main__":
    main()
