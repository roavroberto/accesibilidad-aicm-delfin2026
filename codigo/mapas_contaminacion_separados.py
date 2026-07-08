#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapas de Contaminación Separados por Período
Genera mapas individuales para antes, durante y después de cada evento
"""

import pandas as pd
import numpy as np
import folium
from folium import plugins
from pathlib import Path
from datetime import timedelta

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
SERIES_DIR = RESULTADOS_DIR / "series_temporales"
VIZ_DIR = Path("visualizaciones")
MAPAS_DIR = VIZ_DIR / "mapas_contaminacion"

# Coordenadas del AICM
AICM_LAT = 19.43531
AICM_LON = -99.08367

# Estaciones del SIMAT
ESTACIONES_SIMAT = {
    'Peñones': {'lat': 19.4097, 'lon': -99.0847, 'distancia_km': 2.85},
    'Merced': {'lat': 19.4241, 'lon': -99.1192, 'distancia_km': 3.93},
    'UAM-Iztapalapa': {'lat': 19.3573, 'lon': -99.0739, 'distancia_km': 8.73},
    'Xalostoc': {'lat': 19.5244, 'lon': -99.0817, 'distancia_km': 9.91}
}

# Eventos masivos
EVENTOS = [
    {
        'nombre': 'Concierto Foro Sol',
        'fecha_inicio': '2025-03-15 18:00:00',
        'duracion_horas': 6,
        'asistentes': 65000,
        'venue_lat': 19.39472,
        'venue_lon': -99.09333
    },
    {
        'nombre': 'Gran Premio F1',
        'fecha_inicio': '2025-10-25 10:00:00',
        'duracion_horas': 72,
        'asistentes': 80000,
        'venue_lat': 19.39167,
        'venue_lon': -99.09833
    },
    {
        'nombre': 'Temporada Decembrina',
        'fecha_inicio': '2025-12-20 00:00:00',
        'duracion_horas': 288,
        'asistentes': 30000,
        'venue_lat': 19.43531,
        'venue_lon': -99.08367
    }
]

def cargar_datos():
    """Carga las series de contaminación"""
    print("Cargando datos de contaminación...")
    df = pd.read_csv(SERIES_DIR / "series_contaminacion_aicm.csv")
    df['fecha'] = pd.to_datetime(df['fecha'])
    print(f"✓ {len(df):,} registros cargados")
    return df

def extraer_ventanas(df, evento):
    """Extrae ventanas temporales"""
    fecha_inicio = pd.Timestamp(evento['fecha_inicio'])
    duracion = timedelta(hours=evento['duracion_horas'])
    fecha_fin = fecha_inicio + duracion
    
    ventanas = {
        'antes': df[(df['fecha'] >= fecha_inicio - timedelta(days=7)) & (df['fecha'] < fecha_inicio)],
        'durante': df[(df['fecha'] >= fecha_inicio) & (df['fecha'] <= fecha_fin)],
        'despues': df[(df['fecha'] > fecha_fin) & (df['fecha'] <= fecha_fin + timedelta(days=7))]
    }
    return ventanas

def generar_mapa_periodo(evento, periodo, datos):
    """Genera mapa para un período específico"""
    print(f"  Generando: {periodo}")
    
    if len(datos) == 0:
        print(f"  ⚠️ Sin datos para {periodo}")
        return
    
    pm25_prom = datos['PM25'].mean()
    print(f"    PM2.5 promedio: {pm25_prom:.1f} µg/m³")
    
    # Crear mapa base
    mapa = folium.Map(
        location=[AICM_LAT, AICM_LON],
        zoom_start=12,
        tiles='CartoDB positron'
    )
    
    # Marcadores
    folium.Marker(
        location=[AICM_LAT, AICM_LON],
        popup='<b>AICM</b><br>Aeropuerto Internacional',
        icon=folium.Icon(color='red', icon='plane', prefix='fa')
    ).add_to(mapa)
    
    for nombre, coords in ESTACIONES_SIMAT.items():
        folium.Marker(
            location=[coords['lat'], coords['lon']],
            popup=f'<b>Estación {nombre}</b><br>{coords["distancia_km"]:.2f} km',
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mapa)
    
    folium.Marker(
        location=[evento['venue_lat'], evento['venue_lon']],
        popup=f'<b>{evento["nombre"]}</b><br>{evento["asistentes"]:,} asistentes',
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(mapa)
    
    # Generar puntos de calor
    heat_data = []
    for lat in np.linspace(AICM_LAT - 0.15, AICM_LAT + 0.15, 60):
        for lon in np.linspace(AICM_LON - 0.15, AICM_LON + 0.15, 60):
            dist_aicm = np.sqrt((lat - AICM_LAT)**2 + (lon - AICM_LON)**2)
            dist_venue = np.sqrt((lat - evento['venue_lat'])**2 + (lon - evento['venue_lon'])**2)
            
            # Intensidad basada en PM2.5 normalizado (0-150 µg/m³)
            intensidad_base = pm25_prom / 150.0
            
            # Distribución gaussiana
            intensidad = intensidad_base * (
                np.exp(-dist_aicm**2 / (2 * 0.06**2)) * 0.5 +
                np.exp(-dist_venue**2 / (2 * 0.04**2)) * 0.5
            )
            
            # Clip suave
            intensidad = min(intensidad, 0.95)
            
            if intensidad > 0.02:
                heat_data.append([lat, lon, intensidad])
    
    print(f"    {len(heat_data)} puntos generados")
    
    # Agregar HeatMap
    plugins.HeatMap(
        heat_data,
        radius=12,
        blur=8,
        max_zoom=13,
        gradient={
            0.0: 'blue',
            0.15: 'cyan',
            0.3: 'lime',
            0.5: 'yellow',
            0.7: 'orange',
            0.85: 'red',
            1.0: 'darkred'
        }
    ).add_to(mapa)
    
    # Leyenda específica del período
    periodos_info = {
        'antes': 'Antes del Evento (7 días previos)',
        'durante': 'Durante el Evento',
        'despues': 'Después del Evento (7 días posteriores)'
    }
    
    leyenda = f"""
    <div style="position: fixed; bottom: 50px; left: 50px; width: 280px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; padding: 10px">
        <b>{periodos_info[periodo]}</b><br>
        <b>{evento['nombre']}</b><br>
        PM2.5 promedio: {pm25_prom:.1f} µg/m³<br><br>
        <b>Escala de Contaminación:</b><br>
        <i class="fa fa-circle" style="color:blue"></i> Muy Bajo (0-20)<br>
        <i class="fa fa-circle" style="color:cyan"></i> Bajo (20-40)<br>
        <i class="fa fa-circle" style="color:lime"></i> Moderado (40-60)<br>
        <i class="fa fa-circle" style="color:yellow"></i> Alto (60-80)<br>
        <i class="fa fa-circle" style="color:orange"></i> Muy Alto (80-100)<br>
        <i class="fa fa-circle" style="color:red"></i> Peligroso (>100)
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(leyenda))
    
    # Guardar
    nombre = f"mapa_{evento['nombre'].replace(' ', '_')}_{periodo}.html"
    mapa.save(MAPAS_DIR / nombre)
    print(f"    ✓ Guardado: {nombre}")

def main():
    print("="*80)
    print("MAPAS DE CONTAMINACIÓN SEPARADOS POR PERÍODO")
    print("="*80)
    
    df = cargar_datos()
    
    for evento in EVENTOS:
        print(f"\n{'='*80}")
        print(f"Procesando: {evento['nombre']}")
        print(f"{'='*80}")
        
        ventanas = extraer_ventanas(df, evento)
        
        for periodo in ['antes', 'durante', 'despues']:
            generar_mapa_periodo(evento, periodo, ventanas[periodo])
    
    print("\n" + "="*80)
    print("PROCESO COMPLETADO")
    print("="*80)
    print(f"\n📁 Archivos generados en: {MAPAS_DIR}")
    print(f"  - 9 mapas separados (3 eventos × 3 períodos)")
    print(f"  - Cada mapa muestra un período específico sin saturación")

if __name__ == "__main__":
    main()
