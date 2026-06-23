#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis Completo de Accesibilidad al AICM
Calcula rutas reales desde TODAS las paradas de la CDMX al aeropuerto
Programa Delfín 2026
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
VIZ_DIR = Path("visualizaciones")
AICM_LAT = 19.4361
AICM_LON = -99.0719
CDMX_CENTER_LAT = 19.4326
CDMX_CENTER_LON = -99.1332
RADIO_CDMX = 20000  # 20 km desde el centro para cubrir toda la CDMX

def descargar_red_cdmx():
    """Descarga la red vial completa de la CDMX"""
    print(f"Descargando red vial de CDMX (radio {RADIO_CDMX/1000} km)...")
    print("  (Esto puede tardar 2-5 minutos dependiendo de tu conexión)")
    
    G = ox.graph_from_point(
        (CDMX_CENTER_LAT, CDMX_CENTER_LON), 
        dist=RADIO_CDMX, 
        network_type='drive',
        simplify=True
    )
    
    # Añadir longitudes a las aristas (en metros)
    
    print(f"  - Nodos en la red: {len(G.nodes):,}")
    print(f"  - Calles en la red: {len(G.edges):,}")
    
    return G

def calcular_distancias_desde_aicm(G):
    """Calcula la distancia más corta desde el AICM a todos los nodos de la red"""
    print("\nCalculando distancias desde el AICM a toda la red vial...")
    print("  (Usando Dijkstra de fuente única - esto es muy rápido)")
    
    # Encontrar el nodo más cercano al AICM
    aicm_node = ox.distance.nearest_nodes(G, AICM_LON, AICM_LAT)
    
    # Calcular distancias desde el AICM a TODOS los nodos alcanzables
    distancias = nx.single_source_dijkstra_path_length(G, aicm_node, weight='length')
    
    print(f"  - Nodos alcanzables desde el AICM: {len(distancias):,}")
    
    return distancias, aicm_node

def mapear_paradas_a_red(paradas, G, distancias):
    """Asigna la distancia en red a cada parada de transporte público"""
    print("\nMapeando paradas de transporte público a la red vial...")
    
    paradas_resultado = paradas.copy()
    distancias_red = []
    nodos_cercanos = []
    
    for idx, row in paradas_resultado.iterrows():
        try:
            # Encontrar nodo más cercano a la parada
            stop_node = ox.distance.nearest_nodes(G, row['stop_lon'], row['stop_lat'])
            nodos_cercanos.append(stop_node)
            
            # Obtener distancia pre-calculada
            if stop_node in distancias:
                distancias_red.append(distancias[stop_node] / 1000) # Convertir a km
            else:
                distancias_red.append(np.nan) # No conectado
                
        except Exception:
            distancias_red.append(np.nan)
            nodos_cercanos.append(None)
            
        if idx % 1000 == 0:
            print(f"  - Procesadas {idx} de {len(paradas_resultado)} paradas...")
            
    paradas_resultado['distancia_red_completa_km'] = distancias_red
    paradas_resultado['nodo_red_cercano'] = nodos_cercanos
    
    # Estadísticas
    conectadas = paradas_resultado['distancia_red_completa_km'].notna().sum()
    print(f"  - Paradas conectadas a la red vial: {conectadas} de {len(paradas_resultado)}")
    
    return paradas_resultado

def generar_mapa_calor(paradas, G):
    """Genera un mapa de calor de accesibilidad"""
    print("\nGenerando mapa de calor de accesibilidad...")
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Graficar red vial de fondo (muy tenue)
    ox.plot_graph(G, ax=ax, node_size=0, edge_color='#cccccc', 
                  edge_linewidth=0.2, edge_alpha=0.3, show=False, close=False)
    
    # Filtrar paradas con distancia válida
    paradas_validas = paradas[paradas['distancia_red_completa_km'].notna()].copy()
    
    # Crear mapa de calor
    scatter = ax.scatter(
        paradas_validas['stop_lon'], 
        paradas_validas['stop_lat'],
        c=paradas_validas['distancia_red_completa_km'],
        cmap='RdYlGn_r', # Rojo (lejos) a Verde (cerca)
        s=15,
        alpha=0.6,
        edgecolors='none'
    )
    
    # Marcar AICM
    ax.scatter(AICM_LON, AICM_LAT, c='blue', s=200, marker='*', 
              edgecolors='white', linewidths=2, zorder=10, label='AICM')
    
    # Configurar gráfico
    ax.set_xlabel('Longitud', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitud', fontsize=12, fontweight='bold')
    ax.set_title('Mapa de Calor: Accesibilidad Real al AICM\n(Distancia por carretera en km)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.8)
    cbar.set_label('Distancia real al AICM (km)', fontsize=11, fontweight='bold')
    
    # Leyenda y límites
    ax.legend(loc='upper right', fontsize=11)
    ax.set_xlim(-99.35, -98.90)
    ax.set_ylim(19.25, 19.60)
    
    plt.tight_layout()
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "mapa_calor_accesibilidad_aicm.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"  - Mapa de calor guardado: {output_path}")
    plt.close()

def main():
    print("="*60)
    print("ANÁLISIS COMPLETO DE ACCESIBILIDAD AL AICM")
    print("="*60)
    
    # 1. Descargar red
    G = descargar_red_cdmx()
    
    # 2. Calcular distancias desde AICM
    distancias, aicm_node = calcular_distancias_desde_aicm(G)
    
    # 3. Cargar y mapear paradas
    print("\nCargando paradas de transporte público...")
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    paradas_completas = mapear_paradas_a_red(paradas, G, distancias)
    
    # 4. Guardar resultados
    print("\nGuardando resultados completos...")
    paradas_completas.to_csv(RESULTADOS_DIR / "paradas_accesibilidad_completa.csv", index=False)
    
    # Resumen
    print("\nResumen de Accesibilidad Real:")
    print(f"  - Distancia mínima: {paradas_completas['distancia_red_completa_km'].min():.2f} km")
    print(f"  - Distancia máxima: {paradas_completas['distancia_red_completa_km'].max():.2f} km")
    print(f"  - Distancia promedio: {paradas_completas['distancia_red_completa_km'].mean():.2f} km")
    print(f"  - Mediana: {paradas_completas['distancia_red_completa_km'].median():.2f} km")
    
    # 5. Visualizar
    generar_mapa_calor(paradas_completas, G)
    
    print("\n" + "="*60)
    print("ANÁLISIS COMPLETO FINALIZADO")
    print("="*60)

if __name__ == "__main__":
    main()
