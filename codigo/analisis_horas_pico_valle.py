#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de Horas Pico vs. Horas Valle - Accesibilidad al AICM
Programa Delfín 2026 - Accesibilidad al AICM
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

def clasificar_periodo(hora):
    """Clasifica la hora en Pico o Valle"""
    if 7 <= hora < 9:
        return 'Pico (7-9 AM)'
    elif 18 <= hora < 20:
        return 'Pico (6-8 PM)'
    elif 10 <= hora < 16:
        return 'Valle (10 AM - 4 PM)'
    else:
        return 'Fuera de análisis'

def cargar_datos_gtfs():
    """Carga los archivos GTFS necesarios"""
    print("Cargando datos GTFS...")
    
    stops = pd.read_csv(GTFS_DIR / "stops.txt")
    trips = pd.read_csv(GTFS_DIR / "trips.txt")
    stop_times = pd.read_csv(GTFS_DIR / "stop_times.txt")
    
    print(f"  - Stops: {len(stops)}")
    print(f"  - Trips: {len(trips)}")
    print(f"  - Stop times: {len(stop_times)}")
    
    return stops, trips, stop_times

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
        
    print(f"  - Paradas con distancia: {len(paradas)}")
    return paradas

def analizar_frecuencia(stop_times, trips, paradas_acces):
    """Calcula la frecuencia de viajes por período"""
    print("\nAnalizando frecuencia de viajes (Pico vs Valle)...")
    
    # Unir stop_times con trips para obtener route_id
    st = stop_times.merge(trips[['trip_id', 'route_id']], on='trip_id', how='left')
    
    # Extraer hora de arrival_time
    # GTFS usa formato HH:MM:SS, a veces > 24:00:00 para rutas nocturnas
    st['hora'] = st['arrival_time'].apply(lambda x: int(str(x).split(':')[0]) % 24)
    
    # Clasificar período
    st['periodo'] = st['hora'].apply(clasificar_periodo)
    
    # Filtrar solo los períodos de interés
    periodos_interes = ['Pico (7-9 AM)', 'Pico (6-8 PM)', 'Valle (10 AM - 4 PM)']
    st = st[st['periodo'].isin(periodos_interes)]
    
    # Contar viajes únicos por parada y período
    # (Un viaje = un trip_id único)
    frecuencia = st.groupby(['stop_id', 'periodo'])['trip_id'].nunique().reset_index()
    frecuencia.columns = ['stop_id', 'periodo', 'num_viajes']
    
    # Pivotar para tener columnas por período
    freq_pivot = frecuencia.pivot(index='stop_id', columns='periodo', values='num_viajes').fillna(0).astype(int)
    
    # Calcular totales y promedios
    freq_pivot['Total_Pico'] = freq_pivot.get('Pico (7-9 AM)', 0) + freq_pivot.get('Pico (6-8 PM)', 0)
    freq_pivot['Valle'] = freq_pivot.get('Valle (10 AM - 4 PM)', 0)
    
    # Merge con datos de accesibilidad
    analisis = paradas_acces.merge(freq_pivot, on='stop_id', how='left').fillna(0)
    
    print(f"  - Paradas analizadas: {len(analisis)}")
    print(f"  - Promedio viajes en hora pico: {analisis['Total_Pico'].mean():.1f}")
    print(f"  - Promedio viajes en hora valle: {analisis['Valle'].mean():.1f}")
    
    return analisis

def generar_visualizaciones(analisis):
    """Genera gráficos comparativos"""
    print("\nGenerando visualizaciones...")
    
    sns.set_theme(style="whitegrid")
    
    # 1. Comparación general Pico vs Valle
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Histograma de viajes
    datos_plot = analisis[['Total_Pico', 'Valle']].melt(var_name='Período', value_name='Viajes')
    sns.boxplot(data=datos_plot, x='Período', y='Viajes', ax=axes[0], palette=['#e74c3c', '#3498db'])
    axes[0].set_title('Distribución de Viajes por Parada\n(Pico vs Valle)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Número de viajes')
    
    # Relación Distancia vs Frecuencia en Valle
    # Filtramos para que sea más limpio
    datos_scatter = analisis[analisis['distancia_km'] < 30].copy()
    sns.scatterplot(data=datos_scatter, x='distancia_km', y='Valle', 
                    alpha=0.3, s=20, color='#2ecc71', ax=axes[1])
    
    # Línea de tendencia
    z = np.polyfit(datos_scatter['distancia_km'], datos_scatter['Valle'], 1)
    p = np.poly1d(z)
    axes[1].plot(datos_scatter['distancia_km'].sort_values(), 
                 p(datos_scatter['distancia_km'].sort_values()), 
                 "r--", alpha=0.8, linewidth=2, label='Tendencia')
    
    axes[1].set_title('Distancia al AICM vs Frecuencia en Hora Valle', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Distancia al AICM (km)')
    axes[1].set_ylabel('Viajes en hora valle (10 AM - 4 PM)')
    axes[1].legend()
    
    plt.tight_layout()
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(VIZ_DIR / "analisis_pico_vs_valle.png", dpi=200, bbox_inches='tight')
    print(f"  - Gráfico guardado: {VIZ_DIR / 'analisis_pico_vs_valle.png'}")
    plt.close()

    # 2. Análisis por Alcaldía (Top 10)
    if 'nombre_alcaldia' in analisis.columns:
        fig, ax = plt.subplots(figsize=(10, 8))
        
        stats_alc = analisis.groupby('nombre_alcaldia').agg({
            'Total_Pico': 'mean',
            'Valle': 'mean',
            'distancia_km': 'mean'
        }).sort_values('Valle', ascending=True).head(10)
        
        x = np.arange(len(stats_alc))
        width = 0.35
        
        bars1 = ax.barh(x - width/2, stats_alc['Total_Pico'], width, label='Hora Pico', color='#e74c3c')
        bars2 = ax.barh(x + width/2, stats_alc['Valle'], width, label='Hora Valle', color='#3498db')
        
        ax.set_yticks(x)
        ax.set_yticklabels(stats_alc.index, fontsize=10)
        ax.set_xlabel('Promedio de viajes por parada')
        ax.set_title('Top 10 Alcaldías: Frecuencia de Servicio Pico vs Valle', fontsize=12, fontweight='bold')
        ax.legend()
        ax.invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(VIZ_DIR / "alcaldias_pico_vs_valle.png", dpi=200, bbox_inches='tight')
        print(f"  - Gráfico de alcaldías guardado: {VIZ_DIR / 'alcaldias_pico_vs_valle.png'}")
        plt.close()

def generar_tabla_resumen(analisis):
    """Imprime tabla resumen en consola"""
    print("\n" + "="*80)
    print("RESUMEN: ACCESIBILIDAD EN HORAS PICO VS VALLE")
    print("="*80)
    
    print(f"\n{'Métrica':<30} | {'Hora Pico':<15} | {'Hora Valle':<15} | {'Diferencia':<15}")
    print("-" * 80)
    
    pico_mean = analisis['Total_Pico'].mean()
    valle_mean = analisis['Valle'].mean()
    diff = pico_mean - valle_mean
    pct = (diff / pico_mean) * 100 if pico_mean > 0 else 0
    
    print(f"{'Promedio viajes por parada':<30} | {pico_mean:<15.1f} | {valle_mean:<15.1f} | {pct:<14.1f}%")
    
    # Correlación con distancia
    corr_valle = analisis['distancia_km'].corr(analisis['Valle'])
    corr_pico = analisis['distancia_km'].corr(analisis['Total_Pico'])
    
    print(f"\nCorrelación Distancia vs Frecuencia Pico: {corr_pico:.3f}")
    print(f"Correlación Distancia vs Frecuencia Valle: {corr_valle:.3f}")
    
    print("\n" + "="*80)
    print("INTERPRETACIÓN:")
    print("="*80)
    if corr_valle < corr_pico and corr_valle < 0:
        print("️ La frecuencia del servicio en hora valle disminuye más rápidamente")
        print("   a medida que aumenta la distancia al aeropuerto.")
        print("   Esto indica una PENALIZACIÓN TEMPORAL para las zonas alejadas.")
    else:
        print("✓ La frecuencia del servicio se mantiene relativamente estable")
        print("  independientemente de la distancia al aeropuerto.")

def guardar_resultados(analisis):
    """Guarda los datos procesados"""
    print("\nGuardando resultados...")
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    
    cols_guardar = ['stop_id', 'stop_name', 'distancia_km', 'Total_Pico', 'Valle']
    if 'nombre_alcaldia' in analisis.columns:
        cols_guardar.append('nombre_alcaldia')
        
    analisis[cols_guardar].to_csv(RESULTADOS_DIR / "frecuencia_pico_valle.csv", index=False)
    print(f"  - Datos guardados: {RESULTADOS_DIR / 'frecuencia_pico_valle.csv'}")

def main():
    print("="*80)
    print("ANÁLISIS DE HORAS PICO VS HORAS VALLE - ACCESIBILIDAD AL AICM")
    print("="*80)
    
    # 1. Cargar datos
    stops, trips, stop_times = cargar_datos_gtfs()
    paradas_acces = cargar_datos_accesibilidad()
    
    # 2. Analizar frecuencia
    analisis = analizar_frecuencia(stop_times, trips, paradas_acces)
    
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
