#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapa de Calor de Vialidades: Accesibilidad al AICM desde cada calle
Programa Delfín 2026 - Accesibilidad al AICM
"""

import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
VIZ_DIR = Path("visualizaciones")
AICM_LAT = 19.4361
AICM_LON = -99.0719
CDMX_CENTER_LAT = 19.4326
CDMX_CENTER_LON = -99.1332
RADIO_CDMX = 20000  # 20 km

def descargar_red_y_calcular_distancias():
    """Descarga la red vial y calcula distancias desde el AICM"""
    print(f"Descargando red vial de CDMX (radio {RADIO_CDMX/1000} km)...")
    print("  (Esto puede tardar 2-5 minutos)")
    
    G = ox.graph_from_point(
        (CDMX_CENTER_LAT, CDMX_CENTER_LON), 
        dist=RADIO_CDMX, 
        network_type='drive',
        simplify=True
    )
    
    print(f"  - Nodos: {len(G.nodes):,}")
    print(f"  - Calles: {len(G.edges):,}")
    
    print("\nCalculando distancias desde el AICM a toda la red...")
    aicm_node = ox.distance.nearest_nodes(G, AICM_LON, AICM_LAT)
    distancias = nx.single_source_dijkstra_path_length(G, aicm_node, weight='length')
    
    print(f"  - Nodos alcanzables: {len(distancias):,}")
    
    return G, distancias

def asignar_colores_a_calles(G, distancias):
    """Asigna un color a cada calle basado en la distancia promedio de sus nodos"""
    print("\nAsignando colores a calles...")
    
    colores_calles = []
    distancias_calles = []
    
    for u, v, key in G.edges(keys=True):
        # Obtener distancias de ambos nodos extremos
        dist_u = distancias.get(u, np.nan)
        dist_v = distancias.get(v, np.nan)
        
        # Calcular distancia promedio de la calle
        if not np.isnan(dist_u) and not np.isnan(dist_v):
            dist_promedio = (dist_u + dist_v) / 2 / 1000  # Convertir a km
            distancias_calles.append(dist_promedio)
        else:
            distancias_calles.append(np.nan)
    
    print(f"  - Calles con distancia válida: {sum(1 for d in distancias_calles if not np.isnan(d)):,}")
    
    return distancias_calles

def generar_mapa_calor_vialidades(G, distancias_calles):
    """Genera el mapa de calor de vialidades"""
    print("\nGenerando mapa de calor de vialidades...")
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Convertir distancias a array para normalización
    distancias_array = np.array(distancias_calles)
    distancias_validas = distancias_array[~np.isnan(distancias_array)]
    
    # Usar los mismos límites que el mapa de paradas para comparabilidad
    vmin = np.nanmin(distancias_validas)
    vmax = np.nanmax(distancias_validas)
    
    # Graficar cada calle con su color
    for idx, (u, v, key) in enumerate(G.edges(keys=True)):
        dist_km = distancias_calles[idx]
        
        if not np.isnan(dist_km):
            # Normalizar distancia a [0, 1] para el colormap
            norm_dist = (dist_km - vmin) / (vmax - vmin)
            
            # Usar RdYlGn_r (rojo=lejos, verde=cerca) - igual que mapa de paradas
            color = plt.cm.RdYlGn_r(norm_dist)
            
            # Obtener coordenadas de la calle
            x_coords = [G.nodes[u]['x'], G.nodes[v]['x']]
            y_coords = [G.nodes[u]['y'], G.nodes[v]['y']]
            
            # Dibujar la calle
            ax.plot(x_coords, y_coords, color=color, linewidth=0.5, alpha=0.7)
    
    # Marcar AICM
    ax.scatter(AICM_LON, AICM_LAT, c='blue', s=200, marker='*', 
              edgecolors='white', linewidths=2, zorder=10, label='AICM')
    
    # Configurar gráfico
    ax.set_xlabel('Longitud', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitud', fontsize=12, fontweight='bold')
    ax.set_title('Mapa de Calor de Vialidades: Accesibilidad al AICM\n(Distancia real por carretera en km)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Colorbar con la misma escala
    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn_r, 
                                norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.8)
    cbar.set_label('Distancia real al AICM (km)', fontsize=11, fontweight='bold')
    
    # Leyenda y límites (mismos que mapa de paradas)
    ax.legend(loc='upper right', fontsize=11)
    ax.set_xlim(-99.35, -98.90)
    ax.set_ylim(19.25, 19.60)
    
    plt.tight_layout()
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "mapa_calor_vialidades_aicm.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"  - Mapa guardado: {output_path}")
    plt.close()
    
    # Estadísticas
    print("\nEstadísticas de accesibilidad vial:")
    print(f"  - Distancia mínima: {np.nanmin(distancias_validas):.2f} km")
    print(f"  - Distancia máxima: {np.nanmax(distancias_validas):.2f} km")
    print(f"  - Distancia promedio: {np.nanmean(distancias_validas):.2f} km")
    print(f"  - Mediana: {np.nanmedian(distancias_validas):.2f} km")

def main():
    print("="*60)
    print("MAPA DE CALOR DE VIALIDADES: ACCESIBILIDAD AL AICM")
    print("="*60)
    
    # 1. Descargar red y calcular distancias
    G, distancias = descargar_red_y_calcular_distancias()
    
    # 2. Asignar colores a calles
    distancias_calles = asignar_colores_a_calles(G, distancias)
    
    # 3. Generar mapa
    generar_mapa_calor_vialidades(G, distancias_calles)
    
    print("\n" + "="*60)
    print("MAPA GENERADO EXITOSAMENTE")
    print("="*60)

if __name__ == "__main__":
    main()
