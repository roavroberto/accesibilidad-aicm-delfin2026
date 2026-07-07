#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de Eventos alrededor del AICM y su Impacto en la Movilidad
Programa Delfín 2026 - Accesibilidad al AICM

Analiza los principales venues de eventos cerca del AICM y evalúa
la capacidad del transporte público para atender la demanda durante eventos.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
EXTERNOS_DIR = Path("datos/externos")
EVENTOS_DIR = EXTERNOS_DIR / "eventos"
VIZ_DIR = Path("visualizaciones")

# Coordenadas del AICM
AICM_LAT = 19.43531
AICM_LON = -99.08367

def haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia en km entre dos puntos"""
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

def cargar_venues_eventos():
    """Carga los principales venues de eventos cerca del AICM"""
    print("="*80)
    print("PRINCIPALES VENUES DE EVENTOS CERCA DEL AICM")
    print("="*80)
    
    venues = pd.DataFrame({
        'nombre': [
            'Palacio de los Deportes',
            'Estadio GNP Seguros (Foro Sol)',
            'Arena CDMX',
            'Autódromo Hermanos Rodríguez',
            'Centro de Exposiciones Banamex'
        ],
        'latitud': [19.40528, 19.39472, 19.40361, 19.39167, 19.33889],
        'longitud': [-99.09972, -99.09333, -99.09639, -99.09833, -99.20667],
        'capacidad_max': [20000, 65000, 22500, 80000, 10000],
        'tipo_evento': [
            'Conciertos/Deportes',
            'Conciertos/Festival',
            'Conciertos/Deportes',
            'F1/Conciertos',
            'Exposiciones'
        ]
    })
    
    # Calcular distancia al AICM
    venues['distancia_aicm_km'] = venues.apply(
        lambda row: haversine(AICM_LAT, AICM_LON, row['latitud'], row['longitud']),
        axis=1
    )
    
    venues = venues.sort_values('distancia_aicm_km')
    
    print(f"\n✓ Total de venues identificados: {len(venues)}")
    print(f"\n{'Venue':<35} | {'Capacidad':<12} | {'Dist. AICM':<12} | {'Tipo'}")
    print("-"*80)
    
    for idx, row in venues.iterrows():
        print(f"{row['nombre']:<35} | {row['capacidad_max']:<12,} | {row['distancia_aicm_km']:<11.2f} km | {row['tipo_evento']}")
    
    return venues

def analizar_transporte_cercano_venues(venues, paradas_transporte):
    """Analiza el transporte público disponible cerca de cada venue"""
    print("\n" + "="*80)
    print("ANÁLISIS DE TRANSPORTE PÚBLICO CERCA DE VENUES")
    print("="*80)
    
    RADIO_ANALISIS_KM = 1.0  # Radio de 1 km alrededor de cada venue
    
    resultados = []
    
    for idx, venue in venues.iterrows():
        print(f"\nAnalizando: {venue['nombre']}")
        
        # Calcular distancia de cada parada al venue
        paradas_transporte['distancia_venue_km'] = paradas_transporte.apply(
            lambda row: haversine(venue['latitud'], venue['longitud'], 
                                 row['stop_lat'], row['stop_lon']),
            axis=1
        )
        
        # Filtrar paradas dentro del radio
        paradas_cercanas = paradas_transporte[
            paradas_transporte['distancia_venue_km'] <= RADIO_ANALISIS_KM
        ].copy()
        
        # Calcular estadísticas
        num_paradas = len(paradas_cercanas)
        
        # Frecuencia promedio (si está disponible)
        if 'Total_Pico' in paradas_cercanas.columns:
            freq_pico_prom = paradas_cercanas['Total_Pico'].mean() / 4.0  # Dividir entre 4 horas de pico
            freq_valle_prom = paradas_cercanas['Valle'].mean() / 6.0  # Dividir entre 6 horas de valle
        else:
            freq_pico_prom = np.nan
            freq_valle_prom = np.nan
        
        # Capacidad estimada (asumiendo 50 pasajeros por bus)
        PASAJEROS_POR_BUS = 50
        capacidad_pico = freq_pico_prom * PASAJEROS_POR_BUS if pd.notna(freq_pico_prom) else 0
        capacidad_valle = freq_valle_prom * PASAJEROS_POR_BUS if pd.notna(freq_valle_prom) else 0
        
        # Ratio de capacidad vs demanda del venue
        ratio_pico = (capacidad_pico * 60) / venue['capacidad_max'] if venue['capacidad_max'] > 0 else 0
        ratio_valle = (capacidad_valle * 60) / venue['capacidad_max'] if venue['capacidad_max'] > 0 else 0
        
        print(f"  - Paradas en radio de {RADIO_ANALISIS_KM} km: {num_paradas}")
        print(f"  - Frecuencia pico promedio: {freq_pico_prom:.1f} viajes/hora" if pd.notna(freq_pico_prom) else "  - Frecuencia pico: N/A")
        print(f"  - Capacidad estimada (pico): {capacidad_pico:.0f} pasajeros/hora")
        print(f"  - Ratio capacidad/demanda (pico): {ratio_pico:.2f}x")
        
        resultados.append({
            'venue': venue['nombre'],
            'latitud': venue['latitud'],
            'longitud': venue['longitud'],
            'capacidad_max': venue['capacidad_max'],
            'num_paradas_cercanas': num_paradas,
            'freq_pico_prom': freq_pico_prom,
            'freq_valle_prom': freq_valle_prom,
            'capacidad_pico_pasajeros_hora': capacidad_pico,
            'capacidad_valle_pasajeros_hora': capacidad_valle,
            'ratio_pico': ratio_pico,
            'ratio_valle': ratio_valle
        })
    
    df_resultados = pd.DataFrame(resultados)
    
    return df_resultados

def generar_visualizaciones(venues, resultados_transporte, paradas_transporte):
    """Genera visualizaciones del análisis de eventos"""
    print("\n" + "="*80)
    print("GENERACIÓN DE VISUALIZACIONES")
    print("="*80)
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Mapa de venues y paradas de transporte
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Plot del AICM
    ax.scatter([AICM_LON], [AICM_LAT], c='red', s=300, marker='*', 
               label='AICM', zorder=5, edgecolors='black', linewidth=2)
    
    # Plot de venues
    scatter_venues = ax.scatter(
        venues['longitud'],
        venues['latitud'],
        c=venues['capacidad_max'],
        cmap='YlOrRd',
        s=venues['capacidad_max'] / 500,
        alpha=0.7,
        edgecolors='black',
        linewidth=2,
        marker='s'
    )
    
    # Anotar venues
    for idx, row in venues.iterrows():
        ax.annotate(
            f"{row['nombre']}\n({row['capacidad_max']:,} cap.)",
            (row['longitud'], row['longitud']),
            fontsize=9,
            ha='center',
            va='bottom',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8)
        )
    
    # Plot de paradas de transporte (muestra solo una muestra)
    muestra_paradas = paradas_transporte.sample(min(2000, len(paradas_transporte)))
    ax.scatter(
        muestra_paradas['stop_lon'],
        muestra_paradas['stop_lat'],
        c='blue',
        s=10,
        alpha=0.3,
        label='Paradas de transporte'
    )
    
    plt.colorbar(scatter_venues, label='Capacidad del Venue (personas)')
    
    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    ax.set_title('Venues de Eventos y Transporte Público\nAlrededor del AICM', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "venues_eventos_transporte_aicm.png", dpi=200, bbox_inches='tight')
    print(f"✓ Mapa de venues guardado: {VIZ_DIR / 'venues_eventos_transporte_aicm.png'}")
    plt.close()
    
    # 2. Gráfico de capacidad de transporte vs demanda de venues
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(len(resultados_transporte))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, resultados_transporte['capacidad_pico_pasajeros_hora'], 
                   width, label='Capacidad Transporte (Pico)', color='#3498db')
    bars2 = ax.bar(x + width/2, resultados_transporte['capacidad_max'] / 60, 
                   width, label='Demanda Venue (por hora)', color='#e74c3c')
    
    ax.set_ylabel('Pasajeros por hora')
    ax.set_title('Capacidad de Transporte vs Demanda de Venues durante Eventos', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(resultados_transporte['venue'], rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "capacidad_transporte_vs_demanda_venues.png", dpi=200, bbox_inches='tight')
    print(f"✓ Gráfico de capacidad guardado: {VIZ_DIR / 'capacidad_transporte_vs_demanda_venues.png'}")
    plt.close()
    
    # 3. Tabla resumen
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('tight')
    ax.axis('off')
    
    tabla_data = resultados_transporte[['venue', 'num_paradas_cercanas', 
                                        'freq_pico_prom', 'capacidad_pico_pasajeros_hora',
                                        'ratio_pico']].copy()
    tabla_data.columns = ['Venue', 'Paradas Cercanas', 'Frec. Pico (viajes/h)', 
                          'Capacidad (pas/h)', 'Ratio Cap/Dem']
    
    table = ax.table(cellText=tabla_data.values, colLabels=tabla_data.columns,
                     cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Colorear celdas del ratio
    for i in range(1, len(tabla_data) + 1):
        ratio = tabla_data.iloc[i-1]['Ratio Cap/Dem']
        if ratio < 1:
            table[i, 4].set_facecolor('#ffcccc')  # Rojo claro
        elif ratio < 2:
            table[i, 4].set_facecolor('#ffffcc')  # Amarillo claro
        else:
            table[i, 4].set_facecolor('#ccffcc')  # Verde claro
    
    ax.set_title('Análisis de Capacidad de Transporte durante Eventos', 
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "tabla_analisis_eventos.png", dpi=200, bbox_inches='tight')
    print(f"✓ Tabla resumen guardada: {VIZ_DIR / 'tabla_analisis_eventos.png'}")
    plt.close()

def generar_reporte(resultados_transporte):
    """Genera un reporte del análisis de eventos"""
    print("\n" + "="*80)
    print("REPORTE: ANÁLISIS DE EVENTOS Y MOVILIDAD")
    print("="*80)
    
    print("\n📊 HALLAZGOS PRINCIPALES:")
    print("-"*80)
    
    # Identificar venues con mejor y peor acceso
    mejor_acceso = resultados_transporte.loc[resultados_transporte['ratio_pico'].idxmax()]
    peor_acceso = resultados_transporte.loc[resultados_transporte['ratio_pico'].idxmin()]
    
    print(f"\n✓ MEJOR ACCESO: {mejor_acceso['venue']}")
    print(f"  - Ratio capacidad/demanda: {mejor_acceso['ratio_pico']:.2f}x")
    print(f"  - {mejor_acceso['num_paradas_cercanas']:.0f} paradas cercanas")
    print(f"  - Capacidad: {mejor_acceso['capacidad_pico_pasajeros_hora']:.0f} pasajeros/hora")
    
    print(f"\n⚠️ PEOR ACCESO: {peor_acceso['venue']}")
    print(f"  - Ratio capacidad/demanda: {peor_acceso['ratio_pico']:.2f}x")
    print(f"  - {peor_acceso['num_paradas_cercanas']:.0f} paradas cercanas")
    print(f"  - Capacidad: {peor_acceso['capacidad_pico_pasajeros_hora']:.0f} pasajeros/hora")
    
    print("\n📋 INTERPRETACIÓN:")
    print("-"*80)
    print("• Ratio > 2x: Capacidad suficiente para evacuar el venue en 1 hora")
    print("• Ratio 1-2x: Capacidad adecuada, pero puede haber congestión")
    print("• Ratio < 1x: Capacidad insuficiente, se requiere transporte adicional")
    
    print("\n💡 RECOMENDACIONES:")
    print("-"*80)
    print("1. Venues con ratio < 1x necesitan rutas especiales durante eventos")
    print("2. Coordinar con operadores de transporte para aumentar frecuencia")
    print("3. Considerar servicios de buses lanzadera desde estaciones cercanas")
    print("4. Monitorear en tiempo real durante eventos masivos")

def guardar_resultados(venues, resultados_transporte):
    """Guarda los resultados del análisis"""
    print("\n" + "="*80)
    print("GUARDANDO RESULTADOS")
    print("="*80)
    
    EVENTOS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Guardar venues
    venues.to_csv(EVENTOS_DIR / "venues_eventos_aicm.csv", index=False)
    print(f"✓ Venues guardados: {EVENTOS_DIR / 'venues_eventos_aicm.csv'}")
    
    # Guardar resultados de transporte
    resultados_transporte.to_csv(RESULTADOS_DIR / "analisis_eventos_transporte.csv", index=False)
    print(f"✓ Resultados guardados: {RESULTADOS_DIR / 'analisis_eventos_transporte.csv'}")

def main():
    print("\n" + "="*80)
    print("ANÁLISIS DE EVENTOS ALREDEDOR DEL AICM Y SU IMPACTO EN LA MOVILIDAD")
    print("Programa Delfín 2026 - Roberto Rojas & Janine Flores")
    print("="*80)
    
    # 1. Cargar venues de eventos
    venues = cargar_venues_eventos()
    
    # 2. Cargar datos de transporte
    print("\nCargando datos de transporte público...")
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    print(f"✓ Paradas cargadas: {len(paradas):,}")

    # Cargar datos de frecuencia
    frecuencia = pd.read_csv(RESULTADOS_DIR / "frecuencia_pico_valle.csv")
    print(f"✓ Frecuencia cargada: {len(frecuencia):,} registros")

    # Merge con paradas
    paradas = paradas.merge(
        frecuencia[["stop_id", "Total_Pico", "Valle"]],
        on="stop_id",
        how="left"
    )
    print(f"✓ Datos mergeados. Paradas con frecuencia: {paradas["Total_Pico"].notna().sum():,}")
    print(f"✓ Total de paradas: {len(paradas):,}")

    # 3. Analizar transporte cerca de venues
    resultados_transporte = analizar_transporte_cercano_venues(venues, paradas)
    
    # 4. Generar visualizaciones
    generar_visualizaciones(venues, resultados_transporte, paradas)
    
    # 5. Generar reporte
    generar_reporte(resultados_transporte)
    
    # 6. Guardar resultados
    guardar_resultados(venues, resultados_transporte)
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()
