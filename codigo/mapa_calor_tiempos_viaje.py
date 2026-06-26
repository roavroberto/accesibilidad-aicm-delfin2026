#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapa de Calor de Tiempos de Viaje al AICM
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
    """Carga los datos de tiempos de viaje"""
    print("Cargando datos...")
    
    # Cargar tiempos de viaje por parada (ya tiene coordenadas)
    tiempos = pd.read_csv(RESULTADOS_DIR / "tiempos_viaje_por_parada.csv")
    print(f"  - Paradas con tiempos de viaje: {len(tiempos):,}")
    
    # Verificar que tenga coordenadas
    print(f"  - Columnas: {list(tiempos.columns)}")
    
    return tiempos

def generar_mapa_calor_tiempos(tiempos):
    """Genera el mapa de calor de tiempos de viaje"""
    print("\nGenerando mapa de calor de tiempos de viaje...")
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Crear mapa de calor
    scatter = ax.scatter(
        tiempos['stop_lon'],
        tiempos['stop_lat'],
        c=tiempos['tiempo_promedio_min'],
        cmap='RdYlGn_r',  # Rojo (lento) a Verde (rápido)
        s=20,
        alpha=0.7,
        edgecolors='none'
    )
    
    # Marcar AICM (Terminal 1 y Terminal 2)
    ax.scatter(-99.08367, 19.43531, c='blue', s=200, marker='*', 
              edgecolors='white', linewidths=2, zorder=10, label='Terminal 1')
    ax.scatter(-99.07725, 19.42148, c='red', s=200, marker='*', 
              edgecolors='white', linewidths=2, zorder=10, label='Terminal 2')
    
    # Configurar gráfico
    ax.set_xlabel('Longitud', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitud', fontsize=12, fontweight='bold')
    ax.set_title('Mapa de Calor: Tiempos de Viaje al AICM\n(Tiempo promedio en minutos)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
    cbar.set_label('Tiempo promedio al AICM (minutos)', fontsize=11, fontweight='bold')
    
    # Leyenda y límites (mismos que otros mapas)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_xlim(-99.35, -98.90)
    ax.set_ylim(19.25, 19.60)
    
    plt.tight_layout()
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "mapa_calor_tiempos_viaje_aicm.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"  - Mapa guardado: {output_path}")
    plt.close()

def mostrar_estadisticas(tiempos):
    """Muestra estadísticas de los tiempos"""
    print("\n" + "="*60)
    print("ESTADÍSTICAS DE TIEMPOS DE VIAJE")
    print("="*60)
    
    print(f"\nParadas con tiempos de viaje: {len(tiempos):,}")
    print(f"\nTiempo de viaje (minutos):")
    print(f"  - Mínimo: {tiempos['tiempo_promedio_min'].min():.1f} min")
    print(f"  - Máximo: {tiempos['tiempo_promedio_min'].max():.1f} min")
    print(f"  - Promedio: {tiempos['tiempo_promedio_min'].mean():.1f} min")
    print(f"  - Mediana: {tiempos['tiempo_promedio_min'].median():.1f} min")
    
    # Distribución por rangos
    print("\nDistribución por rangos de tiempo:")
    bins = [0, 10, 20, 30, 40, 50, 60, 70]
    labels = ['0-10 min', '10-20 min', '20-30 min', '30-40 min', '40-50 min', '50-60 min', '60+ min']
    tiempos['rango'] = pd.cut(tiempos['tiempo_promedio_min'], bins=bins, labels=labels, include_lowest=True)
    distribucion = tiempos['rango'].value_counts().sort_index()
    
    for rango, count in distribucion.items():
        print(f"  - {rango}: {count} paradas")

def main():
    print("="*60)
    print("MAPA DE CALOR DE TIEMPOS DE VIAJE AL AICM")
    print("="*60)
    
    # 1. Cargar datos
    tiempos = cargar_datos()
    
    if len(tiempos) == 0:
        print("\nERROR: No hay datos para graficar")
        return
    
    # 2. Generar mapa
    generar_mapa_calor_tiempos(tiempos)
    
    # 3. Mostrar estadísticas
    mostrar_estadisticas(tiempos)
    
    print("\n" + "="*60)
    print("MAPA GENERADO EXITOSAMENTE")
    print("="*60)

if __name__ == "__main__":
    main()
