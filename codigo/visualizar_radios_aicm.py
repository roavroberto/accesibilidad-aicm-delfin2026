#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualización Mejorada: Mapa de radios de accesibilidad al AICM
Programa Delfín 2026 - Accesibilidad al AICM
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import matplotlib.patches as patches

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
VIZ_DIR = Path("visualizaciones")
AICM_LAT = 19.4361
AICM_LON = -99.0719
RADIOS_KM = [0.5, 1.0, 2.0, 5.0]

def cargar_datos():
    """Carga los datos de paradas con distancias"""
    print("Cargando datos...")
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    resumen = pd.read_csv(RESULTADOS_DIR / "resumen_accesibilidad_radios.csv")
    print(f"  - Paradas cargadas: {len(paradas):,}")
    return paradas, resumen

def crear_mapa_radios(paradas, resumen):
    """Crea un mapa con anillos concéntricos de radios"""
    print("\nGenerando mapa de radios...")
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Colores para cada radio
    colores = ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1']
    labels = ['0.5 km', '1.0 km', '2.0 km', '5.0 km']
    
    # Dibujar anillos concéntricos (de mayor a menor)
    for i, (radio, color, label) in enumerate(zip(RADIOS_KM, colores, labels)):
        # Convertir km a grados aproximados (1 grado ≈ 111 km)
        radio_grados = radio / 111.0
        
        # Crear círculo
        circle = plt.Circle((AICM_LON, AICM_LAT), radio_grados, 
                           color=color, alpha=0.2, fill=True, 
                           label=f'{label}: {int(resumen.iloc[i]["paradas_cercanas"])} paradas, {int(resumen.iloc[i]["rutas_conectadas"])} rutas')
        ax.add_patch(circle)
        
        # Borde del círculo
        circle_border = plt.Circle((AICM_LON, AICM_LAT), radio_grados, 
                                   color=color, alpha=0.8, fill=False, linewidth=2)
        ax.add_patch(circle_border)
    
    # Filtrar paradas dentro de 5km para visualizar
    paradas_visibles = paradas[paradas['distancia_km'] <= 5.0].copy()
    
    # Asignar color según radio
    def asignar_color(distancia):
        if distancia <= 0.5:
            return colores[0]
        elif distancia <= 1.0:
            return colores[1]
        elif distancia <= 2.0:
            return colores[2]
        elif distancia <= 5.0:
            return colores[3]
        else:
            return 'gray'
    
    paradas_visibles['color'] = paradas_visibles['distancia_km'].apply(asignar_color)
    
    # Graficar paradas
    for color in colores:
        subset = paradas_visibles[paradas_visibles['color'] == color]
        if len(subset) > 0:
            ax.scatter(subset['stop_lon'], subset['stop_lat'], 
                      c=color, s=30, alpha=0.6, edgecolors='black', 
                      linewidths=0.3, zorder=5)
    
    # Marcar el AICM (estrella roja grande)
    ax.scatter(AICM_LON, AICM_LAT, c='red', s=800, marker='*', 
              edgecolors='darkred', linewidths=3, zorder=10, label='AICM')
    
    # Configurar gráfico
    ax.set_xlabel('Longitud', fontsize=13, fontweight='bold')
    ax.set_ylabel('Latitud', fontsize=13, fontweight='bold')
    ax.set_title('Análisis de Accesibilidad al AICM por Radios de Distancia\nAnillos Concéntricos: 0.5km, 1km, 2km, 5km', 
                 fontsize=15, fontweight='bold', pad=20)
    
    # Leyenda
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Texto informativo
    texto = f'Paradas totales: {len(paradas):,}\n'
    texto += f'Paradas <5km: {len(paradas_visibles):,}\n'
    texto += f'Radio máx mostrado: 5 km'
    
    ax.text(0.02, 0.98, texto, transform=ax.transAxes, 
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    # Ajustar límites
    ax.set_xlim(AICM_LON - 0.06, AICM_LON + 0.06)
    ax.set_ylim(AICM_LAT - 0.06, AICM_LAT + 0.06)
    
    # Guardar
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "mapa_radios_accesibilidad_aicm.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  - Mapa guardado: {output_path}")
    
    plt.close()

def crear_grafico_barras_comparativo(resumen):
    """Crea un gráfico de barras comparativo"""
    print("\nGenerando gráfico comparativo...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfico 1: Paradas
    bars1 = ax1.bar(resumen['radio_km'], resumen['paradas_cercanas'], 
                   color=['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1'],
                   edgecolor='black', linewidth=1.5)
    
    ax1.set_xlabel('Radio (km)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Número de Paradas', fontsize=12, fontweight='bold')
    ax1.set_title('Paradas de Transporte Público por Radio', 
                 fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Agregar valores en las barras
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', 
                fontsize=10, fontweight='bold')
    
    # Gráfico 2: Rutas
    bars2 = ax2.bar(resumen['radio_km'], resumen['rutas_conectadas'], 
                   color=['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1'],
                   edgecolor='black', linewidth=1.5)
    
    ax2.set_xlabel('Radio (km)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Número de Rutas', fontsize=12, fontweight='bold')
    ax2.set_title('Rutas de Transporte Público por Radio', 
                 fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Agregar valores en las barras
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', 
                fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    # Guardar
    output_path = VIZ_DIR / "grafico_comparativo_radios.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  - Gráfico guardado: {output_path}")
    
    plt.close()

def main():
    print("="*60)
    print("VISUALIZACIÓN MEJORADA: Radios de Accesibilidad al AICM")
    print("="*60)
    
    paradas, resumen = cargar_datos()
    crear_mapa_radios(paradas, resumen)
    crear_grafico_barras_comparativo(resumen)
    
    print("\n" + "="*60)
    print("VISUALIZACIONES COMPLETADAS")
    print("="*60)
    
    # Mostrar resumen
    print("\nResumen de accesibilidad:")
    for _, row in resumen.iterrows():
        print(f"  - Radio {row['radio_km']} km: {int(row['paradas_cercanas'])} paradas, {int(row['rutas_conectadas'])} rutas")

if __name__ == "__main__":
    main()
