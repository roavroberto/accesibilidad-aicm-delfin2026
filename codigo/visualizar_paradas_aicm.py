#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualización: Mapa de paradas cercanas al AICM
Programa Delfín 2026 - Accesibilidad al AICM
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
VIZ_DIR = Path("visualizaciones")
AICM_LAT = 19.4361
AICM_LON = -99.0719

def cargar_paradas_cercanas():
    """Carga las paradas cercanas al AICM"""
    print("Cargando datos de paradas cercanas...")
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_cercanas_aicm.csv")
    print(f"  - Paradas cargadas: {len(paradas):,}")
    return paradas

def crear_mapa_paradas(paradas):
    """Crea un mapa de las paradas cercanas al AICM"""
    print("\nGenerando mapa...")
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Graficar paradas (azul)
    scatter = ax.scatter(
        paradas['stop_lon'], 
        paradas['stop_lat'],
        c=paradas['distancia_km'],
        cmap='YlOrRd',
        s=50,
        alpha=0.7,
        edgecolors='black',
        linewidths=0.5
    )
    
    # Marcar el AICM (estrella roja grande)
    ax.scatter(
        AICM_LON, AICM_LAT,
        c='red',
        s=500,
        marker='*',
        edgecolors='darkred',
        linewidths=2,
        zorder=10,
        label='AICM'
    )
    
    # Configurar gráfico
    ax.set_xlabel('Longitud', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitud', fontsize=12, fontweight='bold')
    ax.set_title('Paradas de Transporte Público Cercanas al AICM\n(< 2 km)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Agregar colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
    cbar.set_label('Distancia al AICM (km)', fontsize=11, fontweight='bold')
    
    # Agregar leyenda
    ax.legend(loc='upper right', fontsize=11)
    
    # Agregar grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Agregar texto informativo
    texto = f'Total paradas: {len(paradas)}\nRadio: 2 km'
    ax.text(0.02, 0.98, texto, transform=ax.transAxes, 
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Ajustar límites para mejor visualización
    ax.set_xlim(paradas['stop_lon'].min() - 0.01, paradas['stop_lon'].max() + 0.01)
    ax.set_ylim(paradas['stop_lat'].min() - 0.01, paradas['stop_lat'].max() + 0.01)
    
    # Guardar figura
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "mapa_paradas_cercanas_aicm.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  - Mapa guardado: {output_path}")
    
    plt.close()

def crear_grafico_distribucion_distancias(paradas):
    """Crea un histograma de la distribución de distancias"""
    print("\nGenerando histograma de distancias...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Histograma
    ax.hist(paradas['distancia_km'], bins=20, color='steelblue', 
            edgecolor='black', alpha=0.7)
    
    # Configurar gráfico
    ax.set_xlabel('Distancia al AICM (km)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Número de Paradas', fontsize=12, fontweight='bold')
    ax.set_title('Distribución de Distancias: Paradas al AICM', 
                 fontsize=14, fontweight='bold', pad=15)
    
    # Agregar estadísticas
    stats_text = f'Media: {paradas["distancia_km"].mean():.2f} km\n'
    stats_text += f'Mediana: {paradas["distancia_km"].median():.2f} km\n'
    stats_text += f'Mín: {paradas["distancia_km"].min():.2f} km\n'
    stats_text += f'Máx: {paradas["distancia_km"].max():.2f} km'
    
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Guardar figura
    output_path = VIZ_DIR / "distribucion_distancias_aicm.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  - Histograma guardado: {output_path}")
    
    plt.close()

def main():
    """Función principal"""
    print("="*60)
    print("VISUALIZACIÓN: Paradas Cercanas al AICM")
    print("="*60)
    
    # Cargar datos
    paradas = cargar_paradas_cercanas()
    
    # Crear visualizaciones
    crear_mapa_paradas(paradas)
    crear_grafico_distribucion_distancias(paradas)
    
    print("\n" + "="*60)
    print("VISUALIZACIONES COMPLETADAS")
    print("="*60)
    print(f"\nArchivos generados en: {VIZ_DIR}/")

if __name__ == "__main__":
    main()
