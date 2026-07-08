#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resumen Visual Final del Proyecto: Accesibilidad al AICM
Programa Delfín 2026 - Roberto Rojas & Janine Flores

Genera un dashboard/infografía de alta calidad que resume
todos los hallazgos clave del proyecto en una sola imagen.
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
VIZ_DIR = Path("visualizaciones")
VIZ_DIR.mkdir(parents=True, exist_ok=True)

def generar_resumen_visual():
    print("="*80)
    print("GENERANDO RESUMEN VISUAL FINAL DEL PROYECTO")
    print("="*80)
    
    # Configurar estilo general
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    
    # Crear figura de alta resolución (20x12 pulgadas)
    fig = plt.figure(figsize=(20, 12), facecolor='white')
    
    # Título principal
    fig.suptitle('RESUMEN EJECUTIVO: Accesibilidad al AICM y Impacto de Eventos Masivos', 
                 fontsize=24, fontweight='bold', y=0.98, color='#2c3e50')
    fig.text(0.5, 0.94, 'Programa Delfín 2026 | Laboratorio de IA Geoespacial - UPIITA IPN', 
             ha='center', fontsize=14, color='#7f8c8d')
    
    # Definir grid de 2 filas x 3 columnas
    # Fila 1: Brecha Social, Frecuencia Temporal, Capacidad en Eventos
    # Fila 2: Contaminación, Accesibilidad, Conclusiones
    
    # =====================================================================
    # PANEL 1: Brecha Socioeconómica (Velocidad vs IDH)
    # =====================================================================
    ax1 = plt.subplot2grid((2, 3), (0, 0))
    
    alcaldias = ['Alcaldías\nAlto IDH\n(M. Hidalgo)', 'Alcaldías\nBajo IDH\n(Iztapalapa)']
    velocidades = [19.4, 10.3]
    colores_vel = ['#2ecc71', '#e74c3c']
    
    bars1 = ax1.bar(alcaldias, velocidades, color=colores_vel, edgecolor='black', linewidth=1.2, width=0.6)
    ax1.set_ylabel('Velocidad Promedio (km/h)', fontweight='bold')
    ax1.set_title('1. La Inequidad está en la Velocidad', fontsize=14, fontweight='bold', color='#2c3e50')
    ax1.set_ylim(0, 25)
    ax1.grid(axis='y', alpha=0.3)
    
    for bar, val in zip(bars1, velocidades):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val} km/h', ha='center', fontweight='bold', fontsize=12)
        
    ax1.text(0.5, 0.9, 'Brecha de 1.9x', transform=ax1.transAxes, 
            ha='center', fontsize=16, fontweight='bold', color='#e74c3c',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#e74c3c', alpha=0.8))
    
    # =====================================================================
    # PANEL 2: Frecuencia Temporal (Pico vs Valle)
    # =====================================================================
    ax2 = plt.subplot2grid((2, 3), (0, 1))
    
    periodos = ['Hora Pico\n(7-9 AM, 6-8 PM)', 'Hora Valle\n(Resto del día)']
    frecuencias = [27.1, 27.1]
    
    bars2 = ax2.bar(periodos, frecuencias, color='#3498db', edgecolor='black', linewidth=1.2, width=0.6)
    ax2.set_ylabel('Frecuencia (viajes/hora)', fontweight='bold')
    ax2.set_title('2. Sistema Temporalmente Equitativo', fontsize=14, fontweight='bold', color='#2c3e50')
    ax2.set_ylim(0, 35)
    ax2.grid(axis='y', alpha=0.3)
    
    for bar, val in zip(bars2, frecuencias):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val}', ha='center', fontweight='bold', fontsize=14)
                
    ax2.text(0.5, 0.9, '0.0% Diferencia', transform=ax2.transAxes, 
            ha='center', fontsize=16, fontweight='bold', color='#3498db',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#3498db', alpha=0.8))
            
    # =====================================================================
    # PANEL 3: Capacidad de Transporte en Venues
    # =====================================================================
    ax3 = plt.subplot2grid((2, 3), (0, 2))
    
    venues = ['Palacio\nDeportes', 'Arena\nCDMX', 'Foro\nSol', 'Autódromo']
    ratios = [6.02, 5.94, 1.78, 1.19]
    colores_ratio = ['#2ecc71' if r >= 2 else '#f39c12' if r >= 1.5 else '#e74c3c' for r in ratios]
    
    bars3 = ax3.bar(venues, ratios, color=colores_ratio, edgecolor='black', linewidth=1.2, width=0.6)
    ax3.set_ylabel('Ratio Capacidad / Demanda', fontweight='bold')
    ax3.set_title('3. Venues Críticos en Eventos', fontsize=14, fontweight='bold', color='#2c3e50')
    ax3.set_ylim(0, 8)
    ax3.axhline(y=2.0, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Límite Seguro (2x)')
    ax3.grid(axis='y', alpha=0.3)
    ax3.legend(fontsize=9, loc='upper right')
    
    for bar, val in zip(bars3, ratios):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                f'{val}x', ha='center', fontweight='bold', fontsize=11)
                
    # =====================================================================
    # PANEL 4: Impacto en Contaminación
    # =====================================================================
    ax4 = plt.subplot2grid((2, 3), (1, 0))
    
    eventos = ['Concierto\nForo Sol', 'Gran Premio\nF1', 'Temporada\nDecembrina']
    pm25_inc = [87.6, 107.1, 43.0]
    no2_inc = [79.4, 111.5, 19.6]
    
    x = np.arange(len(eventos))
    width = 0.35
    
    bars4a = ax4.bar(x - width/2, pm25_inc, width, label='PM2.5', color='#e74c3c', edgecolor='black', linewidth=1)
    bars4b = ax4.bar(x + width/2, no2_inc, width, label='NO2', color='#9b59b6', edgecolor='black', linewidth=1)
    
    ax4.set_ylabel('Incremento respecto a base (%)', fontweight='bold')
    ax4.set_title('4. Eventos Duplican la Contaminación', fontsize=14, fontweight='bold', color='#2c3e50')
    ax4.set_xticks(x)
    ax4.set_xticklabels(eventos)
    ax4.set_ylim(0, 130)
    ax4.grid(axis='y', alpha=0.3)
    ax4.legend(fontsize=10, loc='upper left')
    
    for bars in [bars4a, bars4b]:
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'+{height:.0f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
                    
    # =====================================================================
    # PANEL 5: Impacto en Accesibilidad (Tiempos de Viaje)
    # =====================================================================
    ax5 = plt.subplot2grid((2, 3), (1, 1))
    
    acc_inc = [5.3, 8.3, 2.4]
    colores_acc = ['#f39c12', '#e74c3c', '#2ecc71']
    
    bars5 = ax5.bar(eventos, acc_inc, color=colores_acc, edgecolor='black', linewidth=1.2, width=0.6)
    ax5.set_ylabel('Incremento en Tiempo de Viaje (%)', fontweight='bold')
    ax5.set_title('5. Transporte Público es Resiliente', fontsize=14, fontweight='bold', color='#2c3e50')
    ax5.set_ylim(0, 12)
    ax5.grid(axis='y', alpha=0.3)
    
    for bar, val in zip(bars5, acc_inc):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                f'+{val}%', ha='center', fontweight='bold', fontsize=12)
                
    ax5.text(0.5, 0.85, 'Máximo +8.3%\n(vs +111% en aire)', transform=ax5.transAxes, 
            ha='center', fontsize=11, fontweight='bold', color='#34495e',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ecf0f1', edgecolor='#bdc3c7', alpha=0.9))
            
    # =====================================================================
    # PANEL 6: Conclusiones Clave
    # =====================================================================
    ax6 = plt.subplot2grid((2, 3), (1, 2))
    ax6.axis('off')
    
    conclusiones = (
        "🎯 HALLAZGOS PRINCIPALES:\n\n"
        "1️⃣ La inequidad no es de distancia, sino de velocidad (1.9x).\n\n"
        "2️⃣ El sistema mantiene frecuencia constante todo el día.\n\n"
        "3️⃣ Autódromo y Foro Sol operan al límite en eventos masivos.\n\n"
        "4️⃣ Los eventos disparan la contaminación (+107% PM2.5).\n\n"
        "5️⃣ El transporte público absorbe la congestión mejor que el aire."
    )
    
    ax6.text(0.05, 0.95, conclusiones, transform=ax6.transAxes, fontsize=13, 
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=1', facecolor='#ecf0f1', edgecolor='#2c3e50', linewidth=2))
             
    ax6.set_title('6. Conclusiones y Recomendaciones', fontsize=14, fontweight='bold', color='#2c3e50', pad=20)
    
    # Ajustar layout y guardar
    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    
    # Guardar
    archivo_salida = VIZ_DIR / "resumen_visual_final_proyecto.png"
    plt.savefig(archivo_salida, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ Dashboard guardado exitosamente: {archivo_salida}")
    
    plt.close()
    
    print("\n" + "="*80)
    print("RESUMEN VISUAL COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    generar_resumen_visual()
