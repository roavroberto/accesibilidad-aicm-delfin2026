#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL Inicial: Filtrar rutas de transporte público que llegan al AICM
Programa Delfín 2026 - Accesibilidad al AICM
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuración
DATOS_DIR = Path("datos/gtfs")
AICM_LAT = 19.4361
AICM_LON = -99.0719
RADIO_KM = 2.0  # Radio de búsqueda en kilómetros

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos usando la fórmula de Haversine.
    Retorna distancia en kilómetros.
    """
    R = 6371  # Radio de la Tierra en km
    
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    
    a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c

def cargar_datos_gtfs():
    """Carga los archivos principales de GTFS"""
    print("Cargando datos GTFS...")
    
    stops = pd.read_csv(DATOS_DIR / "stops.txt")
    stop_times = pd.read_csv(DATOS_DIR / "stop_times.txt")
    trips = pd.read_csv(DATOS_DIR / "trips.txt")
    routes = pd.read_csv(DATOS_DIR / "routes.txt")
    
    print(f"  - Paradas: {len(stops):,}")
    print(f"  - Horarios: {len(stop_times):,}")
    print(f"  - Viajes: {len(trips):,}")
    print(f"  - Rutas: {len(routes):,}")
    
    return stops, stop_times, trips, routes

def filtrar_paradas_cercanas(stops):
    """Filtra paradas dentro del radio especificado del AICM"""
    print(f"\nFiltrando paradas a < {RADIO_KM} km del AICM...")
    
    # Calcular distancia de cada parada al AICM
    stops['distancia_km'] = haversine(
        stops['stop_lat'], 
        stops['stop_lon'], 
        AICM_LAT, 
        AICM_LON
    )
    
    # Filtrar paradas cercanas
    paradas_cercanas = stops[stops['distancia_km'] <= RADIO_KM].copy()
    
    print(f"  - Paradas encontradas: {len(paradas_cercanas):,}")
    print(f"  - Distancia mínima: {paradas_cercanas['distancia_km'].min():.2f} km")
    print(f"  - Distancia máxima: {paradas_cercanas['distancia_km'].max():.2f} km")
    
    return paradas_cercanas

def identificar_rutas_aicm(paradas_cercanas, stop_times, trips, routes):
    """Identifica qué rutas pasan por las paradas cercanas al AICM"""
    print("\nIdentificando rutas que llegan al AICM...")
    
    # Obtener IDs de paradas cercanas
    stop_ids_cercanos = set(paradas_cercanas['stop_id'])
    
    # Filtrar stop_times para solo paradas cercanas
    stop_times_cercanos = stop_times[stop_times['stop_id'].isin(stop_ids_cercanos)]
    
    # Obtener trip_ids únicos
    trip_ids = stop_times_cercanos['trip_id'].unique()
    
    # Filtrar trips para obtener route_ids
    trips_cercanos = trips[trips['trip_id'].isin(trip_ids)]
    route_ids = trips_cercanos['route_id'].unique()
    
    # Filtrar routes
    rutas_aicm = routes[routes['route_id'].isin(route_ids)].copy()
    
    print(f"  - Viajes que pasan por paradas cercanas: {len(trip_ids):,}")
    print(f"  - Rutas identificadas: {len(rutas_aicm):,}")
    
    return rutas_aicm, trips_cercanos

def guardar_resultados(paradas_cercanas, rutas_aicm, trips_cercanos):
    """Guarda los resultados en archivos CSV"""
    print("\nGuardando resultados...")
    
    # Crear directorio de resultados si no existe
    resultados_dir = Path("datos/resultados")
    resultados_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar paradas cercanas
    paradas_cercanas.to_csv(resultados_dir / "paradas_cercanas_aicm.csv", index=False)
    print(f"  - Paradas cercanas: {resultados_dir / 'paradas_cercanas_aicm.csv'}")
    
    # Guardar rutas
    rutas_aicm.to_csv(resultados_dir / "rutas_aicm.csv", index=False)
    print(f"  - Rutas al AICM: {resultados_dir / 'rutas_aicm.csv'}")
    
    # Guardar resumen
    resumen = {
        'metrica': ['Total paradas', 'Paradas cercanas (<2km)', 'Total rutas', 'Rutas al AICM'],
        'valor': [11362, len(paradas_cercanas), 301, len(rutas_aicm)]
    }
    pd.DataFrame(resumen).to_csv(resultados_dir / "resumen_etl.csv", index=False)
    print(f"  - Resumen: {resultados_dir / 'resumen_etl.csv'}")

def main():
    """Función principal del ETL"""
    print("="*60)
    print("ETL INICIAL: Rutas de Transporte Público al AICM")
    print("="*60)
    
    # Cargar datos
    stops, stop_times, trips, routes = cargar_datos_gtfs()
    
    # Filtrar paradas cercanas
    paradas_cercanas = filtrar_paradas_cercanas(stops)
    
    # Identificar rutas
    rutas_aicm, trips_cercanos = identificar_rutas_aicm(
        paradas_cercanas, stop_times, trips, routes
    )
    
    # Guardar resultados
    guardar_resultados(paradas_cercanas, rutas_aicm, trips_cercanos)
    
    print("\n" + "="*60)
    print("ETL COMPLETADO EXITOSAMENTE")
    print("="*60)
    
    # Mostrar resumen final
    print("\nResumen:")
    print(f"  - Paradas totales: {len(stops):,}")
    print(f"  - Paradas a <{RADIO_KM}km del AICM: {len(paradas_cercanas):,}")
    print(f"  - Rutas totales: {len(routes):,}")
    print(f"  - Rutas que llegan al AICM: {len(rutas_aicm):,}")
    print(f"\nResultados guardados en: datos/resultados/")

if __name__ == "__main__":
    main()
