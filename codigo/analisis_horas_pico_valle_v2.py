#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de Horas Pico vs. Horas Valle - Accesibilidad al AICM (Versión 2)
Programa Delfín 2026 - Accesibilidad al AICM

Usa frequencies.txt para calcular la frecuencia de servicio por período del día.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
GTFS_DIR = Path("datos/gtfs")
RESULTADOS_DIR = Path("datos/resultados")
VIZ_DIR = Path("visualizaciones")

def convertir_tiempo_a_horas(tiempo_str):
    """Convierte formato HH:MM:SS a horas decimales (maneja >24h)"""
    partes = str(tiempo_str).split(':')
    horas = int(partes[0])
    minutos = int(partes[1])
    segundos = int(partes[2])
    return horas + minutos/60 + segundos/3600

def clasificar_periodo(hora_inicio, hora_fin):
    """Calcula cuántas horas de servicio caen en cada período"""
    pico_manana = 0
    pico_tarde = 0
    valle = 0
    
    # Iterar por cada hora del intervalo
    hora_actual = hora_inicio
    while hora_actual < hora_fin:
        hora_int = int(hora_actual) % 24
        
        # Hora pico mañana (7-9)
        if 7 <= hora_int < 9:
            pico_manana += 1
        # Hora pico tarde (18-20)
        elif 18 <= hora_int < 20:
            pico_tarde += 1
        # Hora valle (10-16)
        elif 10 <= hora_int < 16:
            valle += 1
        
        hora_actual += 1
    
    return pico_manana, pico_tarde, valle

def cargar_datos_gtfs():
    """Carga los archivos GTFS necesarios"""
    print("Cargando datos GTFS...")
    
    stops = pd.read_csv(GTFS_DIR / "stops.txt")
    trips = pd.read_csv(GTFS_DIR / "trips.txt")
    stop_times = pd.read_csv(GTFS_DIR / "stop_times.txt")
    frequencies = pd.read_csv(GTFS_DIR / "frequencies.txt")
    
    print(f"  - Stops: {len(stops):,}")
    print(f"  - Trips: {len(trips):,}")
    print(f"  - Stop times: {len(stop_times):,}")
    print(f"  - Frequencies: {len(frequencies):,}")
    
    return stops, trips, stop_times, frequencies

def cargar_datos_accesibilidad():
    """Carga nuestros datos procesados de accesibilidad"""
    print("\nCargando datos de accesibilidad...")
    
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    
    # Agregar alcaldía si existe
    try:
        alcaldias = pd.read_csv(RESULTADOS_DIR / "paradas_con_alcaldia_centroides.csv")
        paradas = paradas.merge(alcaldias[['stop_id', 'nombre_alcaldia']], on='stop_id', how='left')
    except:
        pass
        
    print(f"  - Paradas con distancia: {len(paradas):,}")
    return paradas

def analizar_frecuencia(frequencies, stop_times, trips, paradas_acces):
    """Calcula la frecuencia de viajes por período usando frequencies.txt"""
    print("\nAnalizando frecuencia de viajes (Pico vs Valle)...")
    
    # 1. Calcular viajes por período para cada trip
    print("  Calculando viajes por período...")
    freq_data = []
    
    for idx, row in frequencies.iterrows():
        if idx % 200 == 0:
            print(f"    Procesando trip {idx}/{len(frequencies)}...")
        
        hora_inicio = convertir_tiempo_a_horas(row['start_time'])
        hora_fin = convertir_tiempo_a_horas(row['end_time'])
        headway = row['headway_secs'] / 60  # Convertir a minutos
        
        # Calcular duración en cada período
        pico_manana, pico_tarde, valle = clasificar_periodo(hora_inicio, hora_fin)
        
        # Calcular número de viajes en cada período
        # (duración en horas * 60 / headway en minutos)
        viajes_pico_manana = (pico_manana * 60) / headway if headway > 0 else 0
        viajes_pico_tarde = (pico_tarde * 60) / headway if headway > 0 else 0
        viajes_valle = (valle * 60) / headway if headway > 0 else 0
        
        freq_data.append({
            'trip_id': row['trip_id'],
            'viajes_pico_manana': viajes_pico_manana,
            'viajes_pico_tarde': viajes_pico_tarde,
            'viajes_valle': viajes_valle,
            'headway_min': headway
        })
    
    freq_df = pd.DataFrame(freq_data)
    print(f"  ✓ Procesados {len(freq_df):,} trips con frecuencias")
    
    # 2. Obtener paradas de cada trip
    print("  Obteniendo paradas de cada trip...")
    paradas_por_trip = stop_times.groupby('trip_id')['stop_id'].apply(list).reset_index()
    paradas_por_trip.columns = ['trip_id', 'stops_list']
    
    # 3. Merge con frecuencias
    print("  Combinando datos...")
    trips_freq = freq_df.merge(paradas_por_trip, on='trip_id', how='left')
    
    # 4. Expandir: cada parada recibe los viajes de su trip
    print("  Asignando viajes a paradas...")
    paradas_viajes = []
    
    for idx, row in trips_freq.iterrows():
        if isinstance(row['stops_list'], list) and len(row['stops_list']) > 0:
            for stop_id in row['stops_list']:
                paradas_viajes.append({
                    'stop_id': stop_id,
                    'viajes_pico_manana': row['viajes_pico_manana'],
                    'viajes_pico_tarde': row['viajes_pico_tarde'],
                    'viajes_valle': row['viajes_valle']
                })
    
    paradas_viajes_df = pd.DataFrame(paradas_viajes)
    
    # 5. Sumar viajes por parada
    print("  Sumando viajes por parada...")
    frecuencia_paradas = paradas_viajes_df.groupby('stop_id').agg({
        'viajes_pico_manana': 'sum',
        'viajes_pico_tarde': 'sum',
        'viajes_valle': 'sum'
    }).reset_index()
    
    # Calcular totales
    frecuencia_paradas['Total_Pico'] = (
        frecuencia_paradas['viajes_pico_manana'] + 
        frecuencia_paradas['viajes_pico_tarde']
    )
    frecuencia_paradas['Valle'] = frecuencia_paradas['viajes_valle']
    
    # Calcular frecuencia promedio por hora (para comparación justa)
    # Pico: 4 horas totales (2h mañana + 2h tarde)
    # Valle: 6 horas totales
    frecuencia_paradas['Frec_Pico_por_hora'] = frecuencia_paradas['Total_Pico'] / 4.0
    frecuencia_paradas['Frec_Valle_por_hora'] = frecuencia_paradas['Valle'] / 6.0
    
    print(f"  ✓ Paradas con datos de frecuencia: {len(frecuencia_paradas):,}")
    
    # 6. Merge con datos de accesibilidad
    print("  Combinando con datos de accesibilidad...")
    analisis = paradas_acces.merge(frecuencia_paradas, on='stop_id', how='left').fillna(0)
    
    print(f"\n  Estadísticas:")
    print(f"    - Promedio viajes en hora pico: {analisis['Total_Pico'].mean():.1f}")
    print(f"    - Promedio viajes en hora valle: {analisis['Valle'].mean():.1f}")
    print(f"    - Paradas con servicio pico: {(analisis['Total_Pico'] > 0).sum():,}")
    print(f"    - Paradas con servicio valle: {(analisis['Valle'] > 0).sum():,}")
    
    return analisis

def generar_visualizaciones(analisis):
    """Genera gráficos comparativos"""
    print("\nGenerando visualizaciones...")
    
    sns.set_theme(style="whitegrid")
    
    # Filtrar solo paradas con servicio
    analisis_servicio = analisis[analisis['Total_Pico'] > 0].copy()
    
    # 1. Comparación general Pico vs Valle
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Histograma de viajes
    datos_plot = analisis_servicio[['Total_Pico', 'Valle']].melt(var_name='Período', value_name='Viajes')
    sns.boxplot(data=datos_plot, x='Período', y='Viajes', ax=axes[0], 
                palette=['#e74c3c', '#3498db'], showfliers=False)
    axes[0].set_title('Distribución de Viajes por Parada\n(Pico vs Valle)', 
                      fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Número de viajes')
    axes[0].set_ylim(0, analisis_servicio['Total_Pico'].quantile(0.95))
    
    # Relación Distancia vs Frecuencia en Valle
    datos_scatter = analisis_servicio[analisis_servicio['distancia_km'] < 30].copy()
    sns.scatterplot(data=datos_scatter, x='distancia_km', y='Valle', 
                    alpha=0.3, s=20, color='#2ecc71', ax=axes[1])
    
    # Línea de tendencia
    if len(datos_scatter) > 0:
        z = np.polyfit(datos_scatter['distancia_km'], datos_scatter['Valle'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(datos_scatter['distancia_km'].min(), 
                             datos_scatter['distancia_km'].max(), 100)
        axes[1].plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, label='Tendencia')
    
    axes[1].set_title('Distancia al AICM vs Frecuencia en Hora Valle', 
                      fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Distancia al AICM (km)')
    axes[1].set_ylabel('Viajes en hora valle (10 AM - 4 PM)')
    axes[1].legend()
    
    plt.tight_layout()
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(VIZ_DIR / "analisis_pico_vs_valle_v2.png", dpi=200, bbox_inches='tight')
    print(f"  ✓ Gráfico guardado: {VIZ_DIR / 'analisis_pico_vs_valle_v2.png'}")
    plt.close()

    # 2. Análisis por Alcaldía (Top 10)
    if 'nombre_alcaldia' in analisis_servicio.columns:
        fig, ax = plt.subplots(figsize=(10, 8))
        
        stats_alc = analisis_servicio.groupby('nombre_alcaldia').agg({
            'Total_Pico': 'mean',
            'Valle': 'mean',
            'distancia_km': 'mean'
        }).sort_values('Valle', ascending=True).head(10)
        
        x = np.arange(len(stats_alc))
        width = 0.35
        
        bars1 = ax.barh(x - width/2, stats_alc['Total_Pico'], width, 
                        label='Hora Pico', color='#e74c3c')
        bars2 = ax.barh(x + width/2, stats_alc['Valle'], width, 
                        label='Hora Valle', color='#3498db')
        
        ax.set_yticks(x)
        ax.set_yticklabels(stats_alc.index, fontsize=10)
        ax.set_xlabel('Promedio de viajes por parada')
        ax.set_title('Top 10 Alcaldías: Frecuencia de Servicio Pico vs Valle', 
                     fontsize=12, fontweight='bold')
        ax.legend()
        ax.invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(VIZ_DIR / "alcaldias_pico_vs_valle_v2.png", dpi=200, bbox_inches='tight')
        print(f"  ✓ Gráfico de alcaldías guardado: {VIZ_DIR / 'alcaldias_pico_vs_valle_v2.png'}")
        plt.close()

def generar_tabla_resumen(analisis):
    """Imprime tabla resumen en consola"""
    print("\n" + "="*80)
    print("RESUMEN: ACCESIBILIDAD EN HORAS PICO VS VALLE")
    print("="*80)
    
    # Filtrar solo paradas con servicio
    analisis_servicio = analisis[analisis['Total_Pico'] > 0].copy()
    
    print(f"\n{'Métrica':<30} | {'Hora Pico':<15} | {'Hora Valle':<15} | {'Diferencia':<15}")
    print("-" * 80)
    
    pico_mean = analisis_servicio['Frec_Pico_por_hora'].mean()
    valle_mean = analisis_servicio['Frec_Valle_por_hora'].mean()
    diff = pico_mean - valle_mean
    pct = (diff / pico_mean) * 100 if pico_mean > 0 else 0
    
    print(f"{'Frecuencia por hora (viajes/hora)':<30} | {pico_mean:<15.1f} | {valle_mean:<15.1f} | {pct:<14.1f}%")
    
    # Correlación con distancia (usando frecuencia por hora)
    corr_valle = analisis_servicio['distancia_km'].corr(analisis_servicio['Frec_Valle_por_hora'])
    corr_pico = analisis_servicio['distancia_km'].corr(analisis_servicio['Frec_Pico_por_hora'])
    
    print(f"\nCorrelación Distancia vs Frecuencia Pico: {corr_pico:.3f}")
    print(f"Correlación Distancia vs Frecuencia Valle: {corr_valle:.3f}")
    
    # Brecha por distancia
    cerca = analisis_servicio[analisis_servicio['distancia_km'] < 10]
    lejos = analisis_servicio[analisis_servicio['distancia_km'] >= 20]
    
    print(f"\n{'Zona':<30} | {'Pico':<15} | {'Valle':<15} | {'Reducción':<15}")
    print("-" * 80)
    
    if len(cerca) > 0:
        pico_cerca = cerca['Frec_Pico_por_hora'].mean()
        valle_cerca = cerca['Frec_Valle_por_hora'].mean()
        red_cerca = ((pico_cerca - valle_cerca) / pico_cerca * 100) if pico_cerca > 0 else 0
        print(f"{'Cerca (<10 km)':<30} | {pico_cerca:<15.1f} | {valle_cerca:<15.1f} | {red_cerca:<14.1f}%")
    
    if len(lejos) > 0:
        pico_lejos = lejos['Frec_Pico_por_hora'].mean()
        valle_lejos = lejos['Frec_Valle_por_hora'].mean()
        red_lejos = ((pico_lejos - valle_lejos) / pico_lejos * 100) if pico_lejos > 0 else 0
        print(f"{'Lejos (>=20 km)':<30} | {pico_lejos:<15.1f} | {valle_lejos:<15.1f} | {red_lejos:<14.1f}%")
    
    print("\n" + "="*80)
    print("INTERPRETACIÓN:")
    print("="*80)
    
    if corr_valle < corr_pico and corr_valle < -0.3:
        print("⚠️  La frecuencia del servicio en hora valle disminuye más rápidamente")
        print("   a medida que aumenta la distancia al aeropuerto.")
        print("   Esto indica una PENALIZACIÓN TEMPORAL para las zonas alejadas.")
    elif abs(corr_valle - corr_pico) < 0.1:
        print("✓ La frecuencia del servicio se mantiene relativamente estable")
        print("  entre horas pico y valle, independientemente de la distancia.")
    else:
        print("📊 Patrón mixto: la frecuencia varía según la zona y el período.")

def guardar_resultados(analisis):
    """Guarda los datos procesados"""
    print("\nGuardando resultados...")
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    
    cols_guardar = ['stop_id', 'stop_name', 'distancia_km', 'Total_Pico', 'Valle']
    if 'nombre_alcaldia' in analisis.columns:
        cols_guardar.append('nombre_alcaldia')
        
    analisis[cols_guardar].to_csv(RESULTADOS_DIR / "frecuencia_pico_valle.csv", index=False)
    print(f"  ✓ Datos guardados: {RESULTADOS_DIR / 'frecuencia_pico_valle.csv'}")

def main():
    print("="*80)
    print("ANÁLISIS DE HORAS PICO VS HORAS VALLE - ACCESIBILIDAD AL AICM")
    print("="*80)
    
    # 1. Cargar datos
    stops, trips, stop_times, frequencies = cargar_datos_gtfs()
    paradas_acces = cargar_datos_accesibilidad()
    
    # 2. Analizar frecuencia
    analisis = analizar_frecuencia(frequencies, stop_times, trips, paradas_acces)
    
    # 3. Visualizar
    generar_visualizaciones(analisis)
    
    # 4. Resumen
    generar_tabla_resumen(analisis)
    
    # 5. Guardar
    guardar_resultados(analisis)
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()
