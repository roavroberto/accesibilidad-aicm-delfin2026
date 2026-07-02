#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrección de Duplicados en Análisis por Alcaldías
Programa Delfín 2026 - Accesibilidad al AICM
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
VIZ_DIR = Path("visualizaciones")

def cargar_datos():
    """Carga los datos de paradas con alcaldía"""
    print("Cargando datos...")
    
    # Cargar paradas con alcaldía (con duplicados)
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_con_alcaldia.csv")
    print(f"  - Paradas cargadas (con duplicados): {len(paradas):,}")
    
    # Cargar datos originales de paradas
    paradas_originales = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    print(f"  - Paradas originales: {len(paradas_originales):,}")
    
    return paradas, paradas_originales

def eliminar_duplicados(paradas):
    """Elimina duplicados manteniendo solo la primera asignación"""
    print("\nEliminando duplicados...")
    
    # Ordenar por stop_id y distancia para mantener la más cercana
    paradas_ordenadas = paradas.sort_values(['stop_id', 'distancia_km'])
    
    # Eliminar duplicados manteniendo el primero (más cercano)
    paradas_unicas = paradas_ordenadas.drop_duplicates(subset='stop_id', keep='first')
    
    print(f"  - Paradas después de eliminar duplicados: {len(paradas_unicas):,}")
    print(f"  - Duplicados eliminados: {len(paradas) - len(paradas_unicas):,}")
    
    return paradas_unicas

def calcular_estadisticas_corregidas(paradas_unicas):
    """Calcula estadísticas corregidas por alcaldía"""
    print("\nCalculando estadísticas corregidas...")
    
    # Agrupar por alcaldía
    stats = paradas_unicas.groupby('nombre_alcaldia').agg({
        'distancia_km': ['mean', 'std', 'min', 'max', 'count'],
        'tiempo_promedio_min': ['mean', 'std', 'min', 'max'],
        'velocidad_kmh': ['mean', 'std', 'min', 'max']
    }).reset_index()
    
    # Aplanar columnas
    stats.columns = [
        'alcaldia',
        'distancia_promedio_km', 'distancia_std_km', 'distancia_min_km', 'distancia_max_km', 'num_paradas',
        'tiempo_promedio_min', 'tiempo_std_min', 'tiempo_min_min', 'tiempo_max_min',
        'velocidad_promedio_kmh', 'velocidad_std_kmh', 'velocidad_min_kmh', 'velocidad_max_kmh'
    ]
    
    # Ordenar por distancia promedio
    stats = stats.sort_values('distancia_promedio_km')
    
    print(f"  - Alcaldías analizadas: {len(stats)}")
    
    return stats

def generar_tabla_comparativa(stats):
    """Genera tabla comparativa corregida"""
    print("\n" + "="*80)
    print("TABLA COMPARATIVA CORREGIDA DE ALCALDÍAS")
    print("="*80)
    
    print("\nAlcaldías ORDENADAS por distancia promedio al AICM:\n")
    
    for idx, row in stats.iterrows():
        tiempo_str = f"{row['tiempo_promedio_min']:5.1f}" if pd.notna(row['tiempo_promedio_min']) else "  N/A"
        vel_str = f"{row['velocidad_promedio_kmh']:5.1f}" if pd.notna(row['velocidad_promedio_kmh']) else "  N/A"
        
        print(f"{row['alcaldia']:30s} | "
              f"Dist: {row['distancia_promedio_km']:5.1f} km | "
              f"Tiempo: {tiempo_str} min | "
              f"Vel: {vel_str} km/h | "
              f"Paradas: {int(row['num_paradas']):4d}")
    
    # Top 5 mejores y peores
    print("\n" + "="*80)
    print("TOP 5 ALCALDÍAS CON MEJOR ACCESIBILIDAD (menor distancia)")
    print("="*80)
    top_5_mejores = stats.head(5)
    for idx, row in top_5_mejores.iterrows():
        print(f"  {idx+1}. {row['alcaldia']}: {row['distancia_promedio_km']:.1f} km promedio")
    
    print("\n" + "="*80)
    print("TOP 5 ALCALDÍAS CON PEOR ACCESIBILIDAD (mayor distancia)")
    print("="*80)
    top_5_peores = stats.tail(5)
    for idx, row in top_5_peores.iterrows():
        print(f"  {idx+1}. {row['alcaldia']}: {row['distancia_promedio_km']:.1f} km promedio")

def generar_grafico_barras(stats):
    """Genera gráfico de barras comparativo"""
    print("\nGenerando gráfico de barras...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 10))
    
    # 1. Distancia promedio por alcaldía
    ax1 = axes[0]
    colors = ['#2ecc71' if d < 10 else '#f39c12' if d < 15 else '#e74c3c' 
              for d in stats['distancia_promedio_km']]
    
    bars1 = ax1.barh(stats['alcaldia'], stats['distancia_promedio_km'], color=colors)
    ax1.set_xlabel('Distancia Promedio al AICM (km)', fontsize=11, fontweight='bold')
    ax1.set_title('Distancia Promedio por Alcaldía', fontsize=12, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Agregar valores en las barras
    for i, (bar, val) in enumerate(zip(bars1, stats['distancia_promedio_km'])):
        ax1.text(val + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{val:.1f}', va='center', fontsize=9)
    
    # 2. Número de paradas por alcaldía
    ax2 = axes[1]
    bars2 = ax2.barh(stats['alcaldia'], stats['num_paradas'], color='steelblue')
    ax2.set_xlabel('Número de Paradas', fontsize=11, fontweight='bold')
    ax2.set_title('Paradas de Transporte Público por Alcaldía', fontsize=12, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    # Agregar valores en las barras
    for i, (bar, val) in enumerate(zip(bars2, stats['num_paradas'])):
        ax2.text(val + 100, bar.get_y() + bar.get_height()/2, 
                f'{int(val)}', va='center', fontsize=9)
    
    plt.tight_layout()
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "grafico_barras_alcaldias.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"  - Gráfico guardado: {output_path}")
    plt.close()

def guardar_resultados_corregidos(paradas_unicas, stats):
    """Guarda los resultados corregidos"""
    print("\nGuardando resultados corregidos...")
    
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Guardar paradas únicas con alcaldía
    paradas_path = RESULTADOS_DIR / "paradas_con_alcaldia_corregido.csv"
    paradas_unicas.to_csv(paradas_path, index=False)
    print(f"  - Paradas corregidas guardadas: {paradas_path}")
    
    # Guardar estadísticas corregidas
    stats_path = RESULTADOS_DIR / "estadisticas_por_alcaldia_corregido.csv"
    stats.to_csv(stats_path, index=False)
    print(f"  - Estadísticas corregidas guardadas: {stats_path}")

def main():
    print("="*80)
    print("CORRECCIÓN DE DUPLICADOS EN ANÁLISIS POR ALCALDÍAS")
    print("="*80)
    
    # 1. Cargar datos
    paradas, paradas_originales = cargar_datos()
    
    # 2. Eliminar duplicados
    paradas_unicas = eliminar_duplicados(paradas)
    
    # 3. Calcular estadísticas corregidas
    stats = calcular_estadisticas_corregidas(paradas_unicas)
    
    # 4. Generar tabla comparativa
    generar_tabla_comparativa(stats)
    
    # 5. Generar gráfico de barras
    generar_grafico_barras(stats)
    
    # 6. Guardar resultados corregidos
    guardar_resultados_corregidos(paradas_unicas, stats)
    
    print("\n" + "="*80)
    print("CORRECCIÓN COMPLETADA")
    print("="*80)

if __name__ == "__main__":
    main()
