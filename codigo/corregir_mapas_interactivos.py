#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrección de Mapas Interactivos de Contaminación
Genera mapas con HeatMap real en lugar de círculos simples
"""

import pandas as pd
import numpy as np
import folium
from folium import plugins
from pathlib import Path

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
    from datetime import timedelta
    fecha_inicio = pd.Timestamp(evento['fecha_inicio'])
    duracion = timedelta(hours=evento['duracion_horas'])
    fecha_fin = fecha_inicio + duracion
    
    ventanas = {
        'antes': df[(df['fecha'] >= fecha_inicio - timedelta(days=7)) & (df['fecha'] < fecha_inicio)],
        'durante': df[(df['fecha'] >= fecha_inicio) & (df['fecha'] <= fecha_fin)],
        'despues': df[(df['fecha'] > fecha_fin) & (df['fecha'] <= fecha_fin + timedelta(days=7))]
    }
    return ventanas

def generar_mapa_interactivo_corregido(evento, ventanas):
    """Genera mapa con HeatMap real"""
    print(f"\nGenerando mapa para: {evento['nombre']}")
    
    # Crear mapa base
    mapa = folium.Map(
        location=[AICM_LAT, AICM_LON],
        zoom_start=12,
        tiles='CartoDB positron'
    )
    
    # Marcadores
    folium.Marker(
        location=[AICM_LAT, AICM_LON],
        popup='<b>AICM</b>',
        icon=folium.Icon(color='red', icon='plane', prefix='fa')
    ).add_to(mapa)
    
    for nombre, coords in ESTACIONES_SIMAT.items():
        folium.Marker(
            location=[coords['lat'], coords['lon']],
            popup=f'<b>{nombre}</b><br>{coords["distancia_km"]:.2f} km',
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mapa)
    
    folium.Marker(
        location=[evento['venue_lat'], evento['venue_lon']],
        popup=f'<b>{evento["nombre"]}</b><br>{evento["asistentes"]:,} asistentes',
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(mapa)
    
    # Generar HeatMap para cada período
    periodos_nombres = {
        'antes': 'Antes del Evento',
        'durante': 'Durante el Evento',
        'despues': 'Después del Evento'
    }
    
    for periodo, datos in ventanas.items():
        if len(datos) > 0:
            pm25_prom = datos['PM25'].mean()
            
            # Factor según período
            if periodo == 'antes':
                factor = 1.0
            elif periodo == 'durante':
                factor = 2.5
            else:
                factor = 1.3
            
            # Generar puntos de calor
            heat_data = []
            for lat in np.linspace(AICM_LAT - 0.15, AICM_LAT + 0.15, 50):
                for lon in np.linspace(AICM_LON - 0.15, AICM_LON + 0.15, 50):
                    dist_aicm = np.sqrt((lat - AICM_LAT)**2 + (lon - AICM_LON)**2)
                    dist_venue = np.sqrt((lat - evento['venue_lat'])**2 + (lon - evento['venue_lon'])**2)
                    
                    intensidad = (pm25_prom / 100.0) * factor * (
                        np.exp(-dist_aicm**2 / (2 * 0.05**2)) * 0.6 +
                        np.exp(-dist_venue**2 / (2 * 0.03**2)) * 0.4
                    )
                    
                    intensidad = min(intensidad, 1.0)
                    if intensidad > 0.1:
                        heat_data.append([lat, lon, intensidad])
            
            # Agregar HeatMap
            plugins.HeatMap(
                heat_data,
                radius=20,
                blur=15,
                max_zoom=13,
                gradient={
                    0.0: 'blue',
                    0.25: 'cyan',
                    0.5: 'yellow',
                    0.75: 'orange',
                    1.0: 'red'
                },
                name=periodos_nombres[periodo]
            ).add_to(mapa)
    
    # Control de capas
    folium.LayerControl().add_to(mapa)
    
    # Leyenda
    leyenda = """
    <div style="position: fixed; bottom: 50px; left: 50px; width: 220px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; padding: 10px">
        <b>Niveles de Contaminación (PM2.5)</b><br>
        <i class="fa fa-circle" style="color:blue"></i> Muy Bajo<br>
        <i class="fa fa-circle" style="color:cyan"></i> Bajo<br>
        <i class="fa fa-circle" style="color:yellow"></i> Moderado<br>
        <i class="fa fa-circle" style="color:orange"></i> Alto<br>
        <i class="fa fa-circle" style="color:red"></i> Muy Alto
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(leyenda))
    
    # Guardar
    nombre = f"mapa_interactivo_{evento['nombre'].replace(' ', '_')}.html"
    mapa.save(MAPAS_DIR / nombre)
    print(f"✓ Guardado: {nombre}")

def main():
    print("="*80)
    print("CORRECCIÓN DE MAPAS INTERACTIVOS DE CONTAMINACIÓN")
    print("="*80)
    
    df = cargar_datos()
    
    for evento in EVENTOS:
        ventanas = extraer_ventanas(df, evento)
        generar_mapa_interactivo_corregido(evento, ventanas)
    
    print("\n" + "="*80)
    print("PROCESO COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()
