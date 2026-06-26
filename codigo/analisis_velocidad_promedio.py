#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de Velocidad Promedio del Transporte Público al AICM - VERSIÓN CORREGIDA
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
    """Carga los datos de tiempos y distancias"""
    print("Cargando datos...")
    
    # Cargar tiempos de viaje
    tiempos = pd.read_csv(RESULTADOS_DIR / "tiempos_viaje_por_parada.csv")
    print(f"  - Paradas con tiempos: {len(tiempos):,}")
    
    # Cargar distancias
    distancias = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    print(f"  - Paradas con distancias: {len(distancias):,}")
    
    return tiempos, distancias

def calcular_velocidad(tiempos, distancias):
    """Calcula velocidad promedio cruzando tiempos y distancias"""
    print("\nCalculando velocidad promedio...")
    
    # Merge por stop_id
    merge = tiempos.merge(
        distancias[['stop_id', 'distancia_km']],
        on='stop_id',
        how='inner'
    )
    
    print(f"  - Paradas con tiempos Y distancias: {len(merge):,}")
    
    # Calcular velocidad en km/h
    merge['velocidad_kmh'] = merge['distancia_km'] / (merge['tiempo_promedio_min'] / 60)
    
    # FILTROS DE CALIDAD
    print("\nAplicando filtros de calidad...")
    
    # Filtro 1: Distancia mínima (paradas muy cercanas tienen tiempos no confiables)
    merge_filtrado = merge[merge['distancia_km'] >= 2.0].copy()
    print(f"  - Después de filtrar distancia < 2 km: {len(merge_filtrado):,} paradas")
    
    # Filtro 2: Velocidad máxima realista (transporte público no puede ir a más de 60 km/h)
    merge_filtrado = merge_filtrado[merge_filtrado['velocidad_kmh'] <= 60].copy()
    print(f"  - Después de filtrar velocidad > 60 km/h: {len(merge_filtrado):,} paradas")
    
    # Filtro 3: Velocidad mínima (al menos 5 km/h, menos que eso es caminar)
    merge_filtrado = merge_filtrado[merge_filtrado['velocidad_kmh'] >= 5].copy()
    print(f"  - Después de filtrar velocidad < 5 km/h: {len(merge_filtrado):,} paradas")
    
    return merge_filtrado, merge

def mostrar_estadisticas(merge_filtrado, merge_original):
    """Muestra estadísticas de velocidad"""
    print("\n" + "="*60)
    print("ESTADÍSTICAS DE VELOCIDAD PROMEDIO (FILTRADAS)")
    print("="*60)
    
    print(f"\nParadas originales: {len(merge_original):,}")
    print(f"Paradas después de filtros: {len(merge_filtrado):,}")
    print(f"Paradas descartadas: {len(merge_original) - len(merge_filtrado):,}")
    
    print(f"\nVelocidad promedio (km/h):")
    print(f"  - Mínimo: {merge_filtrado['velocidad_kmh'].min():.1f} km/h")
    print(f"  - Máximo: {merge_filtrado['velocidad_kmh'].max():.1f} km/h")
    print(f"  - Promedio: {merge_filtrado['velocidad_kmh'].mean():.1f} km/h")
    print(f"  - Mediana: {merge_filtrado['velocidad_kmh'].median():.1f} km/h")
    
    # Distribución por rangos de velocidad
    print("\nDistribución por rangos de velocidad:")
    bins = [0, 10, 15, 20, 25, 30, 40, 60]
    labels = ['<10 km/h', '10-15 km/h', '15-20 km/h', '20-25 km/h', 
              '25-30 km/h', '30-40 km/h', '40-60 km/h']
    merge_filtrado['rango_velocidad'] = pd.cut(merge_filtrado['velocidad_kmh'], 
                                               bins=bins, labels=labels, include_lowest=True)
    distribucion = merge_filtrado['rango_velocidad'].value_counts().sort_index()
    
    for rango, count in distribucion.items():
        porcentaje = count / len(merge_filtrado) * 100
        print(f"  - {rango}: {count} paradas ({porcentaje:.1f}%)")
    
    # Top 10 rutas más rápidas
    print("\nTop 10 rutas MÁS RÁPIDAS (mayor velocidad):")
    top_rapidas = merge_filtrado.nlargest(10, 'velocidad_kmh')
    for idx, row in top_rapidas.iterrows():
        print(f"  - {row['stop_name']}: {row['velocidad_kmh']:.1f} km/h "
              f"({row['distancia_km']:.1f} km en {row['tiempo_promedio_min']:.1f} min)")
    
    # Top 10 rutas más lentas
    print("\nTop 10 rutas MÁS LENTAS (menor velocidad):")
    top_lentas = merge_filtrado.nsmallest(10, 'velocidad_kmh')
    for idx, row in top_lentas.iterrows():
        print(f"  - {row['stop_name']}: {row['velocidad_kmh']:.1f} km/h "
              f"({row['distancia_km']:.1f} km en {row['tiempo_promedio_min']:.1f} min)")

def generar_visualizacion(merge_filtrado):
    """Genera visualización de velocidad vs distancia"""
    print("\nGenerando visualización...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Scatter: Velocidad vs Distancia
    ax1 = axes[0, 0]
    scatter1 = ax1.scatter(merge_filtrado['distancia_km'], merge_filtrado['velocidad_kmh'], 
                          c=merge_filtrado['velocidad_kmh'], cmap='RdYlGn', 
                          s=30, alpha=0.6, edgecolors='none')
    ax1.set_xlabel('Distancia al AICM (km)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Velocidad Promedio (km/h)', fontsize=11, fontweight='bold')
    ax1.set_title('Velocidad vs Distancia (Datos Filtrados)', fontsize=12, fontweight='bold')
    ax1.grid(alpha=0.3)
    plt.colorbar(scatter1, ax=ax1, label='Velocidad (km/h)')
    
    # 2. Histograma de velocidades
    ax2 = axes[0, 1]
    ax2.hist(merge_filtrado['velocidad_kmh'], bins=20, color='steelblue', alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Velocidad Promedio (km/h)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Número de Paradas', fontsize=11, fontweight='bold')
    ax2.set_title('Distribución de Velocidades', fontsize=12, fontweight='bold')
    ax2.axvline(merge_filtrado['velocidad_kmh'].mean(), color='red', linestyle='--', 
               linewidth=2, label=f'Promedio: {merge_filtrado["velocidad_kmh"].mean():.1f} km/h')
    ax2.legend()
    ax2.grid(alpha=0.3, axis='y')
    
    # 3. Scatter: Tiempo vs Distancia
    ax3 = axes[1, 0]
    scatter3 = ax3.scatter(merge_filtrado['distancia_km'], merge_filtrado['tiempo_promedio_min'], 
                          c=merge_filtrado['velocidad_kmh'], cmap='RdYlGn_r', 
                          s=30, alpha=0.6, edgecolors='none')
    ax3.set_xlabel('Distancia al AICM (km)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Tiempo de Viaje (min)', fontsize=11, fontweight='bold')
    ax3.set_title('Tiempo vs Distancia (Datos Filtrados)', fontsize=12, fontweight='bold')
    ax3.grid(alpha=0.3)
    plt.colorbar(scatter3, ax=ax3, label='Velocidad (km/h)')
    
    # 4. Boxplot de velocidad por rangos de distancia
    ax4 = axes[1, 1]
    merge_filtrado['rango_distancia'] = pd.cut(merge_filtrado['distancia_km'], bins=5)
    data_to_plot = [merge_filtrado[merge_filtrado['rango_distancia'] == rango]['velocidad_kmh'].dropna().values 
                   for rango in merge_filtrado['rango_distancia'].cat.categories]
    
    bp = ax4.boxplot(data_to_plot, patch_artist=True, showmeans=True)
    ax4.set_xticklabels([f'{rango.left:.0f}-{rango.right:.0f}' for rango in merge_filtrado['rango_distancia'].cat.categories])
    
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
    
    ax4.set_xlabel('Distancia al AICM (km)', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Velocidad Promedio (km/h)', fontsize=11, fontweight='bold')
    ax4.set_title('Velocidad por Distancia', fontsize=12, fontweight='bold')
    ax4.grid(alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "analisis_velocidad_promedio_filtrado.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"  - Visualización guardada: {output_path}")
    plt.close()

def guardar_resultados(merge_filtrado):
    """Guarda los resultados en CSV"""
    print("\nGuardando resultados...")
    
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTADOS_DIR / "velocidad_promedio_filtrado.csv"
    merge_filtrado.to_csv(output_path, index=False)
    print(f"  - Resultados guardados: {output_path}")

def main():
    print("="*60)
    print("ANÁLISIS DE VELOCIDAD PROMEDIO - VERSIÓN CORREGIDA")
    print("="*60)
    
    # 1. Cargar datos
    tiempos, distancias = cargar_datos()
    
    # 2. Calcular velocidad con filtros
    merge_filtrado, merge_original = calcular_velocidad(tiempos, distancias)
    
    if len(merge_filtrado) == 0:
        print("\nERROR: No hay datos después de aplicar filtros")
        return
    
    # 3. Mostrar estadísticas
    mostrar_estadisticas(merge_filtrado, merge_original)
    
    # 4. Generar visualización
    generar_visualizacion(merge_filtrado)
    
    # 5. Guardar resultados
    guardar_resultados(merge_filtrado)
    
    print("\n" + "="*60)
    print("ANÁLISIS COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    main()
