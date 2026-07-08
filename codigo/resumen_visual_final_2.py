#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Resumen Final - Accesibilidad al AICM
Programa Delfín 2026 - Roberto Rojas & Janine Flores

Genera una infografía / dashboard ejecutivo que resume los hallazgos
principales de las 5 semanas de investigación.
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from pathlib import Path

# Configuración
VIZ_DIR = Path("visualizaciones")
VIZ_DIR.mkdir(parents=True, exist_ok=True)

def crear_dashboard():
    print("="*80)
    print("GENERANDO DASHBOARD RESUMEN FINAL")
    print("="*80)
    
    # Crear figura con GridSpec (3 filas, 2 columnas)
    fig = plt.figure(figsize=(16, 11), facecolor='#f8f9fa')
    gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 0.8], hspace=0.5, wspace=0.3)
    
    # Título principal
    fig.suptitle('Accesibilidad al AICM: Resumen Ejecutivo', 
                 fontsize=24, fontweight='bold', y=0.98, color='#2c3e50')
    fig.text(0.5, 0.94, 'Programa Delfín 2026 | UPIITA IPN | Roberto Rojas & Janine Flores', 
             ha='center', fontsize=14, color='#7f8c8d', style='italic')

    # =========================================================================
    # GRÁFICO 1: Brecha de Velocidad (Inequidad Socioeconómica)
    # =========================================================================
    ax1 = fig.add_subplot(gs[0, 0])
    alcaldias = ['Alto IDH\n(Miguel Hidalgo)', 'Bajo IDH\n(Iztapalapa)']
    velocidades = [19.4, 10.3]
    colores_vel = ['#27ae60', '#e74c3c']
    
    bars1 = ax1.bar(alcaldias, velocidades, color=colores_vel, edgecolor='black', linewidth=1.5, width=0.5)
    ax1.set_ylabel('Velocidad Promedio (km/h)', fontsize=12, fontweight='bold')
    ax1.set_title('1. Inequidad: La brecha está en la velocidad', fontsize=14, fontweight='bold', color='#2c3e50')
    ax1.set_ylim(0, 25)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Agregar valores en las barras
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.8, f'{yval} km/h', 
                 ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax1.text(0.5, 0.9, '1.9x más lento en zonas marginadas', 
             transform=ax1.transAxes, ha='center', fontsize=12, 
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffeaa7', edgecolor='#fdcb6e', alpha=0.8))

    # =========================================================================
    # GRÁFICO 2: Equidad Temporal (Pico vs Valle)
    # =========================================================================
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis('off')  # Ocultar ejes para usar solo texto
    
    ax2.text(0.5, 0.7, '2. Equidad Temporal', ha='center', fontsize=14, fontweight='bold', color='#2c3e50', transform=ax2.transAxes)
    ax2.text(0.5, 0.4, 'Frecuencia Constante', ha='center', fontsize=18, color='#34495e', transform=ax2.transAxes)
    
    # Números grandes
    ax2.text(0.25, 0.15, '27.1', ha='center', fontsize=48, fontweight='bold', color='#3498db', transform=ax2.transAxes)
    ax2.text(0.25, 0.0, 'viajes/h\n(Hora Pico)', ha='center', fontsize=12, color='#7f8c8d', transform=ax2.transAxes)
    
    ax2.text(0.75, 0.15, '27.1', ha='center', fontsize=48, fontweight='bold', color='#9b59b6', transform=ax2.transAxes)
    ax2.text(0.75, 0.0, 'viajes/h\n(Hora Valle)', ha='center', fontsize=12, color='#7f8c8d', transform=ax2.transAxes)
    
    # Flecha de igualdad
    ax2.text(0.5, 0.15, '=', ha='center', fontsize=48, fontweight='bold', color='#2ecc71', transform=ax2.transAxes)

    # =========================================================================
    # GRÁFICO 3: Capacidad de Venues (Eventos Masivos)
    # =========================================================================
    ax3 = fig.add_subplot(gs[1, 0])
    venues = ['Banamex', 'Palacio Dep.', 'Arena CDMX', 'Foro Sol', 'Autódromo']
    ratios = [6.57, 6.02, 5.94, 1.78, 1.19]
    
    # Colores según criticidad
    colores_ratios = ['#27ae60' if r > 4 else '#f39c12' if r > 2 else '#e74c3c' for r in ratios]
    
    bars3 = ax3.barh(venues, ratios, color=colores_ratios, edgecolor='black', linewidth=1.2)
    ax3.set_xlabel('Ratio Capacidad / Demanda', fontsize=12, fontweight='bold')
    ax3.set_title('3. Venues Críticos durante Eventos', fontsize=14, fontweight='bold', color='#2c3e50')
    ax3.axvline(x=2.0, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Límite seguro (2.0x)')
    ax3.grid(axis='x', linestyle='--', alpha=0.6)
    ax3.legend(loc='lower right')
    
    for bar in bars3:
        width = bar.get_width()
        ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width:.2f}x', 
                 va='center', fontsize=11, fontweight='bold')

    # =========================================================================
    # GRÁFICO 4: Impacto en Contaminación (PM2.5)
    # =========================================================================
    ax4 = fig.add_subplot(gs[1, 1])
    eventos_cont = ['Temporada\nDecembrina', 'Concierto\nForo Sol', 'Gran Premio\nF1']
    incrementos = [43.0, 76.0, 109.1]
    colores_cont = ['#f1c40f', '#e67e22', '#c0392b']
    
    bars4 = ax4.bar(eventos_cont, incrementos, color=colores_cont, edgecolor='black', linewidth=1.5, width=0.5)
    ax4.set_ylabel('Incremento de PM2.5 (%)', fontsize=12, fontweight='bold')
    ax4.set_title('4. Eventos Masivos Duplican la Contaminación', fontsize=14, fontweight='bold', color='#2c3e50')
    ax4.set_ylim(0, 130)
    ax4.grid(axis='y', linestyle='--', alpha=0.6)
    ax4.axhline(y=100, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Incremento del 100%')
    ax4.legend(loc='upper left')
    
    for bar in bars4:
        yval = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2, yval + 2, f'+{yval:.0f}%', 
                 ha='center', va='bottom', fontsize=14, fontweight='bold', color='#2c3e50')

    # =========================================================================
    # GRÁFICO 5: Conclusión / Resiliencia del Transporte
    # =========================================================================
    ax5 = fig.add_subplot(gs[2, :])
    ax5.axis('off')
    
    # Caja de conclusión
    bbox_props = dict(boxstyle="round,pad=1", facecolor="#ecf0f1", edgecolor="#bdc3c7", alpha=0.9)
    
    texto_conclusion = (
        "CONCLUSIÓN PRINCIPAL: RESILIENCIA vs CONTAMINACIÓN\n\n"
        "Durante eventos masivos (ej. Gran Premio F1), la contaminación del aire (PM2.5) se dispara un +109%,\n"
        "mientras que los tiempos de viaje en transporte público solo aumentan un +8.3%.\n\n"
        "➤ El sistema de transporte público es ALTAMENTE RESILIENTE a la congestión vial,\n"
        "   pero la calidad del aire colapsa, requiriendo restricciones vehiculares obligatorias."
    )
    
    ax5.text(0.5, 0.5, texto_conclusion, ha='center', va='center', fontsize=14, 
             family='monospace', color='#2c3e50', bbox=bbox_props, transform=ax5.transAxes)

    # Guardar imagen
    archivo_salida = VIZ_DIR / "dashboard_resumen_final.png"
    plt.savefig(archivo_salida, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"✅ Dashboard guardado exitosamente: {archivo_salida}")
    plt.close()
    
    return archivo_salida

def main():
    print("\n" + "="*80)
    print("DASHBOARD RESUMEN FINAL - ACCESIBILIDAD AL AICM")
    print("="*80)
    
    archivo = crear_dashboard()
    
    print("\n" + "="*80)
    print("PROCESO COMPLETADO")
    print("="*80)
    print(f"\n💡 Abre la imagen con:")
    print(f"   xdg-open {archivo}")

if __name__ == "__main__":
    main()
