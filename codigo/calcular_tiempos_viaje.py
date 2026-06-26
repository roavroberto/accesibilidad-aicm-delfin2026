#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo de Tiempos de Viaje al AICM usando datos GTFS - VERSIÓN MEJORADA
Programa Delfín 2026 - Accesibilidad al AICM
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
GTFS_DIR = Path("datos/gtfs")
RESULTADOS_DIR = Path("datos/resultados")

# Paradas del aeropuerto (identificadas en stops.txt)
PARADAS_AICM_IDS = [
    'B_0300L4-AEROT1',  # Terminal 1
    'B_0300L4-AEROT2',  # Terminal 2
    'B_010Z4J01-METRAERO',  # Metro Aeropuerto
    'B_010C1101-EJ1NAEROTER2',  # Eje 1 Norte - Terminal 2
    'B_0500431-BLVDPTOAERO',  # Blvd Puerto Aéreo
    'B_0502000-CTOIAEROCIVIL'  # Circuito Interior - Aeropuerto Civil
]

def cargar_datos_gtfs():
    """Carga los archivos GTFS necesarios"""
    print("Cargando datos GTFS...")
    
    stops = pd.read_csv(GTFS_DIR / "stops.txt", encoding='utf-8')
    stop_times = pd.read_csv(GTFS_DIR / "stop_times.txt", encoding='utf-8')
    trips = pd.read_csv(GTFS_DIR / "trips.txt", encoding='utf-8')
    routes = pd.read_csv(GTFS_DIR / "routes.txt", encoding='utf-8')
    
    print(f"  - Paradas: {len(stops):,}")
    print(f"  - Horarios: {len(stop_times):,}")
    print(f"  - Viajes: {len(trips):,}")
    print(f"  - Rutas: {len(routes):,}")
    
    return stops, stop_times, trips, routes

def convertir_tiempo_a_minutos(time_str):
    """Convierte tiempo HH:MM:SS a minutos desde medianoche"""
    if pd.isna(time_str):
        return np.nan
    
    parts = str(time_str).split(':')
    if len(parts) != 3:
        return np.nan
    
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        return hours * 60 + minutes + seconds / 60
    except:
        return np.nan

def identificar_viajes_al_aeropuerto(stop_times, trips):
    """Identifica viajes que pasan por paradas del aeropuerto"""
    print("\nIdentificando viajes que pasan por el aeropuerto...")
    
    # Filtrar stop_times que incluyan paradas del aeropuerto
    stop_times_aero = stop_times[stop_times['stop_id'].isin(PARADAS_AICM_IDS)]
    print(f"  - Registros en paradas del aeropuerto: {len(stop_times_aero):,}")
    
    # Obtener trip_ids únicos que pasan por el aeropuerto
    trips_aero_ids = stop_times_aero['trip_id'].unique()
    print(f"  - Viajes que pasan por el aeropuerto: {len(trips_aero_ids):,}")
    
    # Filtrar todos los stop_times de estos viajes
    stop_times_viajes_aero = stop_times[stop_times['trip_id'].isin(trips_aero_ids)]
    print(f"  - Total de registros de estos viajes: {len(stop_times_viajes_aero):,}")
    
    return stop_times_viajes_aero, trips_aero_ids

def calcular_tiempos_desde_cada_parada(stop_times_viajes_aero, stops):
    """Calcula tiempos desde CUALQUIER parada hasta el aeropuerto"""
    print("\nCalculando tiempos desde cada parada al aeropuerto...")
    
    # Convertir tiempos a minutos
    stop_times_viajes_aero = stop_times_viajes_aero.copy()
    stop_times_viajes_aero['arrival_minutes'] = stop_times_viajes_aero['arrival_time'].apply(convertir_tiempo_a_minutos)
    
    tiempos_viaje = []
    
    # Agrupar por trip_id
    trips_grouped = stop_times_viajes_aero.groupby('trip_id')
    
    print(f"  - Procesando {len(trips_grouped)} viajes...")
    
    for trip_id, group in trips_grouped:
        if len(group) < 2:
            continue
        
        # Ordenar por secuencia
        group = group.sort_values('stop_sequence')
        
        # Encontrar la primera parada del aeropuerto en este viaje
        aero_stops = group[group['stop_id'].isin(PARADAS_AICM_IDS)]
        
        if len(aero_stops) == 0:
            continue
        
        # Primera parada del aeropuerto
        primera_aero = aero_stops.iloc[0]
        stop_aero = primera_aero['stop_id']
        tiempo_aero = primera_aero['arrival_minutes']
        
        # Para cada parada ANTES del aeropuerto en este viaje
        paradas_antes = group[group['stop_sequence'] < primera_aero['stop_sequence']]
        
        for idx, parada in paradas_antes.iterrows():
            stop_origen = parada['stop_id']
            tiempo_origen = parada['arrival_minutes']
            
            # Calcular tiempo de viaje
            tiempo_viaje_min = tiempo_aero - tiempo_origen
            
            if tiempo_viaje_min > 0 and tiempo_viaje_min < 300:  # Menos de 5 horas
                tiempos_viaje.append({
                    'trip_id': trip_id,
                    'stop_id_origen': stop_origen,
                    'stop_id_destino': stop_aero,
                    'tiempo_origen_min': tiempo_origen,
                    'tiempo_destino_min': tiempo_aero,
                    'tiempo_viaje_min': tiempo_viaje_min,
                    'hora_salida': tiempo_origen
                })
    
    df_tiempos = pd.DataFrame(tiempos_viaje)
    print(f"  - Tiempos de viaje calculados: {len(df_tiempos):,}")
    
    return df_tiempos

def calcular_estadisticas_por_parada(df_tiempos, stops):
    """Calcula estadísticas de tiempo promedio por parada"""
    print("\nCalculando estadísticas por parada...")
    
    # Agrupar por parada de origen
    stats = df_tiempos.groupby('stop_id_origen').agg({
        'tiempo_viaje_min': ['mean', 'std', 'min', 'max', 'count']
    }).reset_index()
    
    stats.columns = ['stop_id', 'tiempo_promedio_min', 'tiempo_std_min', 
                     'tiempo_min_min', 'tiempo_max_min', 'num_viajes']
    
    # Merge con información de paradas
    stats = stats.merge(stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], 
                       on='stop_id', how='left')
    
    # Ordenar por tiempo promedio
    stats = stats.sort_values('tiempo_promedio_min')
    
    print(f"  - Paradas con tiempos calculados: {len(stats):,}")
    
    return stats

def calcular_frecuencias(df_tiempos):
    """Calcula frecuencias de servicio por hora"""
    print("\nCalculando frecuencias de servicio...")
    
    # Agrupar por hora del día
    df_tiempos = df_tiempos.copy()
    df_tiempos['hora'] = (df_tiempos['hora_salida'] / 60).astype(int)
    
    frecuencias = df_tiempos.groupby('hora').size().reset_index(name='num_viajes')
    
    print("  - Frecuencias por hora:")
    for _, row in frecuencias.iterrows():
        print(f"    {int(row['hora']):02d}:00 - {int(row['num_viajes'])} viajes")
    
    return frecuencias

def guardar_resultados(stats, frecuencias, df_tiempos):
    """Guarda los resultados en archivos CSV"""
    print("\nGuardando resultados...")
    
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Guardar estadísticas por parada
    stats_path = RESULTADOS_DIR / "tiempos_viaje_por_parada.csv"
    stats.to_csv(stats_path, index=False)
    print(f"  - Estadísticas guardadas: {stats_path}")
    
    # Guardar frecuencias
    freq_path = RESULTADOS_DIR / "frecuencias_servicio.csv"
    frecuencias.to_csv(freq_path, index=False)
    print(f"  - Frecuencias guardadas: {freq_path}")
    
    # Guardar todos los tiempos de viaje
    tiempos_path = RESULTADOS_DIR / "todos_los_tiempos_viaje.csv"
    df_tiempos.to_csv(tiempos_path, index=False)
    print(f"  - Todos los tiempos guardados: {tiempos_path}")

def mostrar_resumen(stats, df_tiempos):
    """Muestra un resumen de los resultados"""
    print("\n" + "="*60)
    print("RESUMEN DE TIEMPOS DE VIAJE AL AICM")
    print("="*60)
    
    print(f"\nTotal de tiempos de viaje calculados: {len(df_tiempos):,}")
    print(f"Paradas únicas analizadas: {len(stats):,}")
    
    print(f"\nTiempo de viaje (minutos):")
    print(f"  - Mínimo: {stats['tiempo_promedio_min'].min():.1f} min")
    print(f"  - Máximo: {stats['tiempo_promedio_min'].max():.1f} min")
    print(f"  - Promedio: {stats['tiempo_promedio_min'].mean():.1f} min")
    print(f"  - Mediana: {stats['tiempo_promedio_min'].median():.1f} min")
    
    print("\nTop 10 paradas con menor tiempo de viaje:")
    top_10 = stats.head(10)
    for idx, row in top_10.iterrows():
        print(f"  - {row['stop_name']}: {row['tiempo_promedio_min']:.1f} min ({int(row['num_viajes'])} viajes)")
    
    print("\nTop 10 paradas con mayor tiempo de viaje:")
    bottom_10 = stats.tail(10)
    for idx, row in bottom_10.iterrows():
        print(f"  - {row['stop_name']}: {row['tiempo_promedio_min']:.1f} min ({int(row['num_viajes'])} viajes)")

def main():
    print("="*60)
    print("CÁLCULO DE TIEMPOS DE VIAJE AL AICM - VERSIÓN MEJORADA")
    print("="*60)
    
    # 1. Cargar datos
    stops, stop_times, trips, routes = cargar_datos_gtfs()
    
    # 2. Identificar viajes al aeropuerto
    stop_times_viajes_aero, trips_aero_ids = identificar_viajes_al_aeropuerto(stop_times, trips)
    
    if len(trips_aero_ids) == 0:
        print("\nERROR: No se encontraron viajes al aeropuerto")
        return
    
    # 3. Calcular tiempos desde cada parada
    df_tiempos = calcular_tiempos_desde_cada_parada(stop_times_viajes_aero, stops)
    
    if len(df_tiempos) == 0:
        print("\nERROR: No se pudieron calcular tiempos de viaje")
        return
    
    # 4. Calcular estadísticas por parada
    stats = calcular_estadisticas_por_parada(df_tiempos, stops)
    
    # 5. Calcular frecuencias
    frecuencias = calcular_frecuencias(df_tiempos)
    
    # 6. Guardar resultados
    guardar_resultados(stats, frecuencias, df_tiempos)
    
    # 7. Mostrar resumen
    mostrar_resumen(stats, df_tiempos)
    
    print("\n" + "="*60)
    print("PROCESO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    main()
