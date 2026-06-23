#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exploración de Vialidades CDMX
Compara vialidades primarias vs. todas las vialidades
"""

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from pathlib import Path

# Configuración
VIALIDADES_DIR = Path("datos/vialidades")
VIZ_DIR = Path("visualizaciones")
AICM_LON = -99.0719
AICM_LAT = 19.4361

def cargar_y_explorar():
    print("Cargando datasets de vialidades...")
    
    # Cargar vialidades primarias
    print("  - Cargando vialidades primarias (5.7 MB)...")
    vialidades_primarias = gpd.read_file(VIALIDADES_DIR / "mapa-de-las-vialidades-primarias-de-la-ciudad-de-mxico-.json")
    print(f"    * Registros: {len(vialidades_primarias)}")
    print(f"    * Columnas: {list(vialidades_primarias.columns)}")
    
    # Cargar todas las vialidades
    print("  - Cargando todas las vialidades (79 MB)... (esto puede tardar unos segundos)")
    vialidades_todas = gpd.read_file(VIALIDADES_DIR / "vialidades-de-la-ciudad-de-mxico.json")
    print(f"    * Registros: {len(vialidades_todas)}")
    print(f"    * Columnas: {list(vialidades_todas.columns)}")
    
    return vialidades_primarias, vialidades_todas

def visualizar_comparacion(v_primarias, v_todas):
    print("\nGenerando mapa comparativo...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Punto del AICM
    aicm_point = Point(AICM_LON, AICM_LAT)
    
    # Gráfico 1: Vialidades Primarias
    v_primarias.plot(ax=axes[0], color='red', linewidth=0.5, alpha=0.7)
    axes[0].plot(AICM_LON, AICM_LAT, 'b*', markersize=15, label='AICM')
    axes[0].set_title('Vialidades Primarias CDMX', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].set_xlim(-99.4, -98.9)
    axes[0].set_ylim(19.2, 19.6)
    
    # Gráfico 2: Todas las Vialidades
    v_todas.plot(ax=axes[1], color='gray', linewidth=0.2, alpha=0.5)
    axes[1].plot(AICM_LON, AICM_LAT, 'b*', markersize=15, label='AICM')
    axes[1].set_title('Todas las Vialidades CDMX', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].set_xlim(-99.4, -98.9)
    axes[1].set_ylim(19.2, 19.6)
    
    plt.tight_layout()
    
    # Guardar
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "comparacion_vialidades.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  - Mapa guardado: {output_path}")
    plt.close()

def main():
    print("="*60)
    print("EXPLORACIÓN DE VIALIDADES CDMX")
    print("="*60)
    
    v_primarias, v_todas = cargar_y_explorar()
    visualizar_comparacion(v_primarias, v_todas)
    
    print("\n" + "="*60)
    print("EXPLORACIÓN COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    main()
