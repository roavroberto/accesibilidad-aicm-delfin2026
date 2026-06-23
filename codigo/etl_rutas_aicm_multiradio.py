#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL Mejorado: Análisis de accesibilidad al AICM con múltiples radios
Programa Delfín 2026 - Accesibilidad al AICM
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuración
DATOS_DIR = Path("datos/gtfs")
AICM_LAT = 19.4361
AICM_LON = -99.0719
RADIOS_KM = [0.5, 1.0, 2.0, 5.0]  # Radios de análisis en kilómetros

def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia entre dos puntos usando la fórmula de Haversine (en km)."""
    R = 6371
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

def calcular_distancias(stops):
    """Calcula la distancia de todas las paradas al AICM"""
    print("\nCalculando distancias al AICM...")
    stops['distancia_km'] = haversine(stops['stop_lat'], stops['stop_lon'], AICM_LAT, AICM_LON)
    return stops

def analizar_por_radio(stops, stop_times, trips, routes):
    """Analiza paradas y rutas para cada radio definido"""
    print("\nAnalizando accesibilidad por radios...")
    resultados = []
    
    for radio in RADIOS_KM:
        # 1. Filtrar paradas dentro del radio
        paradas_radio = stops[stops['distancia_km'] <= radio].copy()
        
        # 2. Identificar rutas que tocan esas paradas
        stop_ids = set(paradas_radio['stop_id'])
        trips_radio_ids = stop_times[stop_times['stop_id'].isin(stop_ids)]['trip_id'].unique()
        route_ids = trips[trips['trip_id'].isin(trips_radio_ids)]['route_id'].unique()
        rutas_radio = routes[routes['route_id'].isin(route_ids)]
        
        # 3. Guardar resultados
        resultados.append({
            'radio_km': radio,
            'paradas_cercanas': len(paradas_radio),
            'rutas_conectadas': len(rutas_radio),
            'porcentaje_paradas': (len(paradas_radio) / len(stops)) * 100,
            'porcentaje_rutas': (len(rutas_radio) / len(routes)) * 100
        })
        
        print(f"  - Radio {radio} km: {len(paradas_radio)} paradas, {len(rutas_radio)} rutas")
        
    return pd.DataFrame(resultados)

def guardar_resultados(stops, df_resultados):
    """Guarda los datos procesados"""
    print("\nGuardando resultados...")
    resultados_dir = Path("datos/resultados")
    resultados_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar todas las paradas con su distancia
    stops.to_csv(resultados_dir / "paradas_con_distancia_aicm.csv", index=False)
    print(f"  - Todas las paradas con distancias: {resultados_dir / 'paradas_con_distancia_aicm.csv'}")
    
    # Guardar resumen por radios
    df_resultados.to_csv(resultados_dir / "resumen_accesibilidad_radios.csv", index=False)
    print(f"  - Resumen por radios: {resultados_dir / 'resumen_accesibilidad_radios.csv'}")

def main():
    print("="*60)
    print("ETL MEJORADO: Accesibilidad al AICM (Múltiples Radios)")
    print("="*60)
    
    stops, stop_times, trips, routes = cargar_datos_gtfs()
    stops = calcular_distancias(stops)
    df_resultados = analizar_por_radio(stops, stop_times, trips, routes)
    guardar_resultados(stops, df_resultados)
    
    print("\n" + "="*60)
    print("ETL COMPLETADO EXITOSAMENTE")
    print("="*60)

if __name__ == "__main__":
    main()
