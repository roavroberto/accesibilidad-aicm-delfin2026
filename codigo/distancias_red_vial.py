#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo de Distancias en Red Vial (OSMnx)
Calcula la distancia real por carretera desde las paradas al AICM
Programa Delfín 2026 - Accesibilidad al AICM
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
VIZ_DIR = Path("visualizaciones")
AICM_LAT = 19.4361
AICM_LON = -99.0719
RADIO_RED = 5000  # Radio de 5km para descargar la red (en metros)

def descargar_red_vial():
    """Descarga la red vial de OpenStreetMap alrededor del AICM"""
    print(f"Descargando red vial desde OpenStreetMap (radio {RADIO_RED/1000} km)...")
    print("  (Esto puede tardar unos 10-20 segundos)")
    
    # Descargar red de calles para autos
    G = ox.graph_from_point(
        (AICM_LAT, AICM_LON), 
        dist=RADIO_RED, 
        network_type='drive',
        simplify=True
    )
    
    print(f"  - Nodos en la red: {len(G.nodes)}")
    print(f"  - Calles en la red: {len(G.edges)}")
    
    return G

def calcular_distancias_red(G, paradas):
    """Calcula la distancia real por carretera para cada parada"""
    print("\nCalculando distancias en red vial...")
    
    # Filtrar paradas dentro del radio de la red
    paradas_filtradas = paradas[paradas['distancia_km'] <= (RADIO_RED/1000)].copy()
    
    # Obtener nodo más cercano al AICM en la red
    aicm_node = ox.distance.nearest_nodes(G, AICM_LON, AICM_LAT)
    
    distancias_red = []
    
    # Calcular ruta más corta para cada parada
    for idx, row in paradas_filtradas.iterrows():
        try:
            # Obtener nodo más cercano a la parada
            stop_node = ox.distance.nearest_nodes(G, row['stop_lon'], row['stop_lat'])
            
            # Calcular distancia más corta (en metros)
            dist_metros = nx.shortest_path_length(G, stop_node, aicm_node, weight='length')
            distancias_red.append(dist_metros / 1000) # Convertir a km
            
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            # Si no hay ruta, usar distancia euclidiana
            distancias_red.append(row['distancia_km'])
            
        if idx % 100 == 0:
            print(f"  - Procesadas {idx} de {len(paradas_filtradas)} paradas...")
            
    paradas_filtradas['distancia_red_km'] = distancias_red
    
    # Calcular diferencia entre distancia euclidiana y en red
    paradas_filtradas['diferencia_km'] = paradas_filtradas['distancia_red_km'] - paradas_filtradas['distancia_km']
    paradas_filtradas['factor_desvio'] = paradas_filtradas['distancia_red_km'] / paradas_filtradas['distancia_km']
    
    print(f"  - Cálculo completado para {len(paradas_filtradas)} paradas.")
    
    return paradas_filtradas

def visualizar_rutas_ejemplo(G, paradas):
    """Visualiza la red vial y algunas rutas de ejemplo"""
    print("\nGenerando visualización de rutas...")
    
    # Seleccionar 5 paradas de ejemplo de diferentes rangos de distancia
    # 1 cercana (< 2km), 2 medias (2-3.5km), 2 lejanas (> 3.5km)
    cercanas = paradas[paradas['distancia_red_km'] < 2.0].nsmallest(1, 'distancia_red_km')
    medias_bajas = paradas[(paradas['distancia_red_km'] >= 2.0) & (paradas['distancia_red_km'] < 3.5)].sample(1, random_state=42)
    medias_altas = paradas[(paradas['distancia_red_km'] >= 3.5) & (paradas['distancia_red_km'] < 4.5)].sample(1, random_state=42)
    lejanas_cercanas = paradas[(paradas['distancia_red_km'] >= 4.5) & (paradas['distancia_red_km'] < 5.0)].sample(1, random_state=42)
    lejanas = paradas[paradas['distancia_red_km'] >= 5.0].nsmallest(1, 'distancia_red_km')

    ejemplos = pd.concat([cercanas, medias_bajas, medias_altas, lejanas_cercanas, lejanas])
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Graficar red vial
    ox.plot_graph(G, ax=ax, node_size=0, edge_color='lightgray', edge_linewidth=0.5, show=False, close=False)
    
    # Marcar AICM
    ax.plot(AICM_LON, AICM_LAT, 'r*', markersize=20, label='AICM', zorder=10)
    
    # Graficar rutas de ejemplo
    aicm_node = ox.distance.nearest_nodes(G, AICM_LON, AICM_LAT)
    colores = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    
    for i, (_, row) in enumerate(ejemplos.iterrows()):
        stop_node = ox.distance.nearest_nodes(G, row['stop_lon'], row['stop_lat'])
        
        try:
            ruta = nx.shortest_path(G, stop_node, aicm_node, weight='length')
            ruta_coords = [(G.nodes[n]['x'], G.nodes[n]['y']) for n in ruta]
            xs, ys = zip(*ruta_coords)
            
            ax.plot(xs, ys, color=colores[i], linewidth=2, alpha=0.8, 
                   label=f"Parada {i+1} ({row['distancia_red_km']:.2f} km)")
            ax.plot(row['stop_lon'], row['stop_lat'], 'o', color=colores[i], markersize=8)
        except:
            pass
            
    ax.set_title('Rutas Reales por Carretera hacia el AICM\n(Red Vial de OpenStreetMap)', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.set_xlim(AICM_LON - 0.04, AICM_LON + 0.04)
    ax.set_ylim(AICM_LAT - 0.04, AICM_LAT + 0.04)
    
    plt.tight_layout()
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "rutas_red_vial_aicm.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"  - Visualización guardada: {output_path}")
    plt.close()

def main():
    print("="*60)
    print("CÁLCULO DE DISTANCIAS EN RED VIAL (OSMnx)")
    print("="*60)
    
    # 1. Descargar red
    G = descargar_red_vial()
    
    # 2. Cargar paradas
    print("\nCargando paradas de transporte público...")
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    
    # 3. Calcular distancias en red
    paradas_con_red = calcular_distancias_red(G, paradas)
    
    # 4. Guardar resultados
    print("\nGuardando resultados actualizados...")
    paradas_con_red.to_csv(RESULTADOS_DIR / "paradas_con_distancia_red.csv", index=False)
    
    # Resumen estadístico
    print("\nResumen de Desviación (Red vs Euclidiana):")
    print(f"  - Factor de desvío promedio: {paradas_con_red['factor_desvio'].mean():.2f}x")
    print(f"  - Distancia euclidiana promedio: {paradas_con_red['distancia_km'].mean():.2f} km")
    print(f"  - Distancia en red promedio: {paradas_con_red['distancia_red_km'].mean():.2f} km")
    
    # 5. Visualizar
    visualizar_rutas_ejemplo(G, paradas_con_red)
    
    print("\n" + "="*60)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*60)

if __name__ == "__main__":
    main()
