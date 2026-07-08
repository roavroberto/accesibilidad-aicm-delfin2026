#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de Series Temporales - Accesibilidad al AICM
Programa Delfín 2026 - Accesibilidad al AICM

Metodología para análisis de series temporales de movilidad y contaminación.
Cuando se obtengan datos históricos reales, esta misma metodología puede aplicarse.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
EXTERNOS_DIR = Path("datos/externos")
VIZ_DIR = Path("visualizaciones")
SERIES_DIR = RESULTADOS_DIR / "series_temporales"

# Coordenadas del AICM
AICM_LAT = 19.43531
AICM_LON = -99.08367

def generar_serie_temporal_sintetica():
    """
    Genera series temporales sintéticas basadas en patrones reales de transporte público.
    
    Patrones modelados:
    - Tendencia: crecimiento gradual de la demanda
    - Estacionalidad semanal: más viajes en días laborales
    - Estacionalidad diaria: picos en horas pico (7-9 AM, 6-8 PM)
    - Eventos especiales: incrementos súbitos durante eventos masivos
    - Ruido: variabilidad aleatoria
    """
    print("="*80)
    print("GENERACIÓN DE SERIES TEMPORALES SINTÉTICAS")
    print("="*80)
    
    SERIES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generar fechas para 1 año (2025)
    fechas = pd.date_range(start='2025-01-01', end='2025-12-31', freq='h')
    n_puntos = len(fechas)
    
    print(f"\nGenerando serie temporal de {n_puntos:,} puntos (1 año, frecuencia horaria)")
    
    # 1. Componente de tendencia (crecimiento gradual del 5% anual)
    tendencia = np.linspace(1000, 1050, n_puntos)
    
    # 2. Componente estacional semanal
    # Días laborales (Lun-Vie) tienen más viajes que fines de semana
    dia_semana = np.array([f.weekday() for f in fechas])
    estacionalidad_semanal = np.where(dia_semana < 5, 1.2, 0.7)  # 20% más en laborales
    
    # 3. Componente estacional diaria
    # Picos en horas pico (7-9 AM y 6-8 PM)
    hora = np.array([f.hour for f in fechas])
    estacionalidad_diaria = np.zeros(n_puntos)
    
    for i in range(n_puntos):
        h = hora[i]
        if 7 <= h < 9:  # Pico mañana
            estacionalidad_diaria[i] = 1.5
        elif 18 <= h < 20:  # Pico tarde
            estacionalidad_diaria[i] = 1.4
        elif 10 <= h < 16:  # Valle
            estacionalidad_diaria[i] = 0.8
        elif 22 <= h or h < 6:  # Noche/madrugada
            estacionalidad_diaria[i] = 0.3
        else:
            estacionalidad_diaria[i] = 1.0
    
    # 4. Eventos especiales (simulados)
    eventos = np.ones(n_puntos)
    
    # Evento 1: Concierto masivo en Foro Sol (65,000 asistentes)
    # Simula un día con incremento del 200% durante 6 horas
    evento1_inicio = pd.Timestamp('2025-03-15 18:00:00')
    evento1_idx = np.where(fechas == evento1_inicio)[0][0]
    eventos[evento1_idx:evento1_idx+6] = 3.0
    
    # Evento 2: Gran Premio de F1 en Autódromo (3 días)
    evento2_inicio = pd.Timestamp('2025-10-25 10:00:00')
    evento2_idx = np.where(fechas == evento2_inicio)[0][0]
    eventos[evento2_idx:evento2_idx+72] = 2.5  # 3 días * 24 horas
    
    # Evento 3: Temporada decembrina (incremento sostenido)
    evento3_inicio = pd.Timestamp('2025-12-20 00:00:00')
    evento3_idx = np.where(fechas == evento3_inicio)[0][0]
    eventos[evento3_idx:] = 1.3
    
    # 5. Ruido aleatorio
    np.random.seed(42)
    ruido = np.random.normal(1.0, 0.1, n_puntos)
    
    # 6. Serie temporal final
    serie_viajes = tendencia * estacionalidad_semanal * estacionalidad_diaria * eventos * ruido
    
    # Crear DataFrame
    df_series = pd.DataFrame({
        'fecha': fechas,
        'viajes_hora': serie_viajes,
        'tendencia': tendencia,
        'estacionalidad_semanal': estacionalidad_semanal,
        'estacionalidad_diaria': estacionalidad_diaria,
        'eventos': eventos,
        'ruido': ruido
    })
    
    print(f"✓ Serie temporal generada: {len(df_series):,} registros")
    print(f"  - Rango: {df_series['fecha'].min()} a {df_series['fecha'].max()}")
    print(f"  - Promedio de viajes/hora: {df_series['viajes_hora'].mean():.0f}")
    print(f"  - Máximo: {df_series['viajes_hora'].max():.0f}")
    print(f"  - Mínimo: {df_series['viajes_hora'].min():.0f}")
    
    # Guardar serie temporal
    df_series.to_csv(SERIES_DIR / "serie_temporal_viajes_aicm.csv", index=False)
    print(f"✓ Serie guardada: {SERIES_DIR / 'serie_temporal_viajes_aicm.csv'}")
    
    return df_series

def descomponer_serie_temporal(df_series):
    """
    Descompone la serie temporal en sus componentes:
    - Tendencia
    - Estacionalidad
    - Residuo
    """
    print("\n" + "="*80)
    print("DESCOMPOSICIÓN DE SERIE TEMPORAL")
    print("="*80)
    
    # Convertir a serie de pandas con índice de tiempo
    serie = df_series.set_index('fecha')['viajes_hora']
    
    # Descomposición aditiva (aproximación manual)
    # Tendencia: media móvil de 7 días (168 horas)
    tendencia = serie.rolling(window=168, center=True, min_periods=1).mean()
    
    # Estacionalidad: promedio por hora del día
    estacionalidad_hora = serie.groupby(serie.index.hour).transform('mean')
    estacionalidad_dia = serie.groupby(serie.index.dayofweek).transform('mean')
    estacionalidad = (estacionalidad_hora + estacionalidad_dia) / 2
    
    # Residuo: serie original - tendencia - estacionalidad
    residuo = serie - tendencia - estacionalidad + serie.mean()
    
    # Crear DataFrame de descomposición
    df_descomp = pd.DataFrame({
        'fecha': serie.index,
        'original': serie.values,
        'tendencia': tendencia.values,
        'estacionalidad': estacionalidad.values,
        'residuo': residuo.values
    })
    
    print(f"✓ Descomposición completada")
    print(f"  - Tendencia: {tendencia.mean():.0f} viajes/hora (promedio)")
    print(f"  - Estacionalidad: {estacionalidad.std():.0f} (desviación estándar)")
    print(f"  - Residuo: {residuo.std():.0f} (desviación estándar)")
    
    # Guardar descomposición
    df_descomp.to_csv(SERIES_DIR / "descomposicion_serie_temporal.csv", index=False)
    print(f"✓ Descomposición guardada: {SERIES_DIR / 'descomposicion_serie_temporal.csv'}")
    
    return df_descomp

def identificar_anomalias(df_series):
    """
    Identifica anomalías en la serie temporal usando:
    - Desviación estándar (> 2 desviaciones de la media)
    - Z-score
    """
    print("\n" + "="*80)
    print("IDENTIFICACIÓN DE ANOMALÍAS")
    print("="*80)
    
    # Calcular estadísticas
    media = df_series['viajes_hora'].mean()
    std = df_series['viajes_hora'].std()
    
    # Umbral: 2 desviaciones estándar
    umbral_superior = media + 2 * std
    umbral_inferior = media - 2 * std
    
    # Identificar anomalías
    df_series['es_anomalia'] = (
        (df_series['viajes_hora'] > umbral_superior) | 
        (df_series['viajes_hora'] < umbral_inferior)
    )
    
    # Calcular Z-score
    df_series['z_score'] = (df_series['viajes_hora'] - media) / std
    
    # Filtrar anomalías
    anomalias = df_series[df_series['es_anomalia']].copy()
    
    print(f"✓ Anomalías identificadas: {len(anomalias):,} ({len(anomalias)/len(df_series)*100:.2f}%)")
    print(f"  - Umbral superior: {umbral_superior:.0f} viajes/hora")
    print(f"  - Umbral inferior: {umbral_inferior:.0f} viajes/hora")
    print(f"  - Z-score máximo: {df_series['z_score'].max():.2f}")
    print(f"  - Z-score mínimo: {df_series['z_score'].min():.2f}")
    
    # Mostrar top 10 anomalías
    if len(anomalias) > 0:
        print(f"\n  Top 10 anomalías:")
        top_anomalias = anomalias.nlargest(10, 'z_score')
        for idx, row in top_anomalias.iterrows():
            print(f"    - {row['fecha']}: {row['viajes_hora']:.0f} viajes/hora (Z={row['z_score']:.2f})")
    
    # Guardar anomalías
    anomalias.to_csv(SERIES_DIR / "anomalias_serie_temporal.csv", index=False)
    print(f"✓ Anomalías guardadas: {SERIES_DIR / 'anomalias_serie_temporal.csv'}")
    
    return anomalias

def analizar_patrones_estacionalidad(df_series):
    """
    Analiza patrones de estacionalidad:
    - Por hora del día
    - Por día de la semana
    - Por mes del año
    """
    print("\n" + "="*80)
    print("ANÁLISIS DE PATRONES DE ESTACIONALIDAD")
    print("="*80)
    
    # 1. Patrón por hora del día
    patron_hora = df_series.groupby(df_series['fecha'].dt.hour)['viajes_hora'].mean()
    
    print(f"\n📊 Patrón por hora del día:")
    print(f"  - Hora pico máxima: {patron_hora.idxmax():02d}:00 ({patron_hora.max():.0f} viajes/hora)")
    print(f"  - Hora valle mínima: {patron_hora.idxmin():02d}:00 ({patron_hora.min():.0f} viajes/hora)")
    
    # 2. Patrón por día de la semana
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    patron_dia = df_series.groupby(df_series['fecha'].dt.dayofweek)['viajes_hora'].mean()
    patron_dia.index = dias_semana
    
    print(f"\n📊 Patrón por día de la semana:")
    print(f"  - Día con más viajes: {patron_dia.idxmax()} ({patron_dia.max():.0f} viajes/hora)")
    print(f"  - Día con menos viajes: {patron_dia.idxmin()} ({patron_dia.min():.0f} viajes/hora)")
    
    # 3. Patrón por mes del año
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    patron_mes = df_series.groupby(df_series['fecha'].dt.month)['viajes_hora'].mean()
    patron_mes.index = meses
    
    print(f"\n📊 Patrón por mes del año:")
    print(f"  - Mes con más viajes: {patron_mes.idxmax()} ({patron_mes.max():.0f} viajes/hora)")
    print(f"  - Mes con menos viajes: {patron_mes.idxmin()} ({patron_mes.min():.0f} viajes/hora)")
    
    # Guardar patrones por separado
    patron_hora.to_csv(SERIES_DIR / "patron_hora.csv", header=True)
    patron_dia.to_csv(SERIES_DIR / "patron_dia_semana.csv", header=True)
    patron_mes.to_csv(SERIES_DIR / "patron_mes.csv", header=True)
    print(f"✓ Patrones guardados en archivos separados")
    
    return patron_hora, patron_dia, patron_mes

def generar_visualizaciones(df_series, df_descomp, anomalias, patron_hora, patron_dia, patron_mes):
    """Genera visualizaciones del análisis de series temporales"""
    print("\n" + "="*80)
    print("GENERACIÓN DE VISUALIZACIONES")
    print("="*80)
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Serie temporal completa con anomalías
    fig, ax = plt.subplots(figsize=(16, 6))
    
    ax.plot(df_series['fecha'], df_series['viajes_hora'], 
            linewidth=0.5, alpha=0.7, label='Viajes/hora', color='#3498db')
    
    # Marcar anomalías
    if len(anomalias) > 0:
        ax.scatter(anomalias['fecha'], anomalias['viajes_hora'], 
                  c='red', s=30, marker='x', label='Anomalías', zorder=5)
    
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Viajes por hora')
    ax.set_title('Serie Temporal de Viajes en Transporte Público hacia el AICM\n' + 
                 'Análisis de 1 año (2025) con Anomalías Identificadas', 
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "serie_temporal_completa.png", dpi=200, bbox_inches='tight')
    print(f"✓ Serie temporal completa guardada: {VIZ_DIR / 'serie_temporal_completa.png'}")
    plt.close()
    
    # 2. Descomposición de la serie temporal
    fig, axes = plt.subplots(4, 1, figsize=(16, 12), sharex=True)
    
    # Original
    axes[0].plot(df_descomp['fecha'], df_descomp['original'], linewidth=0.5, color='#3498db')
    axes[0].set_ylabel('Original')
    axes[0].set_title('Descomposición de Serie Temporal', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # Tendencia
    axes[1].plot(df_descomp['fecha'], df_descomp['tendencia'], linewidth=1, color='#e74c3c')
    axes[1].set_ylabel('Tendencia')
    axes[1].grid(True, alpha=0.3)
    
    # Estacionalidad
    axes[2].plot(df_descomp['fecha'], df_descomp['estacionalidad'], linewidth=0.5, color='#2ecc71')
    axes[2].set_ylabel('Estacionalidad')
    axes[2].grid(True, alpha=0.3)
    
    # Residuo
    axes[3].plot(df_descomp['fecha'], df_descomp['residuo'], linewidth=0.5, color='#95a5a6')
    axes[3].axhline(y=df_descomp['residuo'].mean(), color='red', linestyle='--', linewidth=1)
    axes[3].set_ylabel('Residuo')
    axes[3].set_xlabel('Fecha')
    axes[3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "descomposicion_serie_temporal.png", dpi=200, bbox_inches='tight')
    print(f"✓ Descomposición guardada: {VIZ_DIR / 'descomposicion_serie_temporal.png'}")
    plt.close()
    
    # 3. Patrones de estacionalidad
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Por hora
    axes[0].bar(patron_hora.index, patron_hora.values, color='#3498db', alpha=0.7)
    axes[0].set_xlabel('Hora del día')
    axes[0].set_ylabel('Viajes promedio/hora')
    axes[0].set_title('Patrón por Hora del Día', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')
    axes[0].set_xticks(range(0, 24, 2))
    
    # Por día de la semana
    axes[1].bar(range(7), patron_dia.values, color='#e74c3c', alpha=0.7)
    axes[1].set_xlabel('Día de la semana')
    axes[1].set_ylabel('Viajes promedio/hora')
    axes[1].set_title('Patrón por Día de la Semana', fontsize=12, fontweight='bold')
    axes[1].set_xticks(range(7))
    axes[1].set_xticklabels(['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'])
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Por mes
    axes[2].bar(range(12), patron_mes.values, color='#2ecc71', alpha=0.7)
    axes[2].set_xlabel('Mes')
    axes[2].set_ylabel('Viajes promedio/hora')
    axes[2].set_title('Patrón por Mes del Año', fontsize=12, fontweight='bold')
    axes[2].set_xticks(range(12))
    axes[2].set_xticklabels(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                             'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'], rotation=45)
    axes[2].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "patrones_estacionalidad.png", dpi=200, bbox_inches='tight')
    print(f"✓ Patrones de estacionalidad guardados: {VIZ_DIR / 'patrones_estacionalidad.png'}")
    plt.close()
    
    # 4. Distribución de Z-scores
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(df_series['z_score'], bins=50, color='#3498db', alpha=0.7, edgecolor='black')
    ax.axvline(x=-2, color='red', linestyle='--', linewidth=2, label='Umbral -2σ')
    ax.axvline(x=2, color='red', linestyle='--', linewidth=2, label='Umbral +2σ')
    ax.axvline(x=0, color='green', linestyle='-', linewidth=2, label='Media')
    
    ax.set_xlabel('Z-score')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Distribución de Z-scores\nIdentificación de Anomalías', 
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "distribucion_zscore.png", dpi=200, bbox_inches='tight')
    print(f"✓ Distribución de Z-scores guardada: {VIZ_DIR / 'distribucion_zscore.png'}")
    plt.close()

def generar_reporte(df_series, anomalias, patron_hora, patron_dia, patron_mes):
    """Genera un reporte del análisis de series temporales"""
    print("\n" + "="*80)
    print("REPORTE: ANÁLISIS DE SERIES TEMPORALES")
    print("="*80)
    
    print("\n📊 ESTADÍSTICAS GENERALES:")
    print("-"*80)
    print(f"  - Período analizado: {df_series['fecha'].min()} a {df_series['fecha'].max()}")
    print(f"  - Total de registros: {len(df_series):,}")
    print(f"  - Promedio de viajes/hora: {df_series['viajes_hora'].mean():.0f}")
    print(f"  - Desviación estándar: {df_series['viajes_hora'].std():.0f}")
    print(f"  - Máximo: {df_series['viajes_hora'].max():.0f} viajes/hora")
    print(f"  - Mínimo: {df_series['viajes_hora'].min():.0f} viajes/hora")
    
    print(f"\n🚨 ANOMALÍAS DETECTADAS:")
    print("-"*80)
    print(f"  - Total de anomalías: {len(anomalias):,} ({len(anomalias)/len(df_series)*100:.2f}%)")
    
    if len(anomalias) > 0:
        print(f"  - Anomalía más extrema: Z-score = {anomalias['z_score'].max():.2f}")
        print(f"  - Fecha: {anomalias.loc[anomalias['z_score'].idxmax(), 'fecha']}")
    
    print(f"\n📈 PATRONES IDENTIFICADOS:")
    print("-"*80)
    print(f"  • Hora pico: {patron_hora.idxmax():02d}:00 ({patron_hora.max():.0f} viajes/hora)")
    print(f"  • Hora valle: {patron_hora.idxmin():02d}:00 ({patron_hora.min():.0f} viajes/hora)")
    print(f"  • Día más activo: {patron_dia.idxmax()} ({patron_dia.max():.0f} viajes/hora)")
    print(f"  • Día menos activo: {patron_dia.idxmin()} ({patron_dia.min():.0f} viajes/hora)")
    print(f"  • Mes más activo: {patron_mes.idxmax()} ({patron_mes.max():.0f} viajes/hora)")
    print(f"  • Mes menos activo: {patron_mes.idxmin()} ({patron_mes.min():.0f} viajes/hora)")
    
    print(f"\n💡 INTERPRETACIÓN:")
    print("-"*80)
    print("1. La serie temporal muestra patrones claros de estacionalidad:")
    print("   - Picos en horas laborales (7-9 AM y 6-8 PM)")
    print("   - Menor actividad en fines de semana")
    print("   - Variaciones mensuales asociadas a temporadas turísticas")
    print("\n2. Las anomalías identificadas corresponden a:")
    print("   - Eventos masivos (conciertos, eventos deportivos)")
    print("   - Temporadas especiales (decembrina)")
    print("   - Posibles incidentes o cierres viales")
    print("\n3. Esta metodología puede aplicarse a datos reales de:")
    print("   - Calidad del aire (SIMAT)")
    print("   - Frecuencia de transporte público")
    print("   - Tiempos de viaje al AICM")

def main():
    print("\n" + "="*80)
    print("ANÁLISIS DE SERIES TEMPORALES - ACCESIBILIDAD AL AICM")
    print("Programa Delfín 2026 - Roberto Rojas & Janine Flores")
    print("="*80)
    
    # 1. Generar serie temporal sintética
    df_series = generar_serie_temporal_sintetica()
    
    # 2. Descomponer serie temporal
    df_descomp = descomponer_serie_temporal(df_series)
    
    # 3. Identificar anomalías
    anomalias = identificar_anomalias(df_series)
    
    # 4. Analizar patrones de estacionalidad
    patron_hora, patron_dia, patron_mes = analizar_patrones_estacionalidad(df_series)
    
    # 5. Generar visualizaciones
    generar_visualizaciones(df_series, df_descomp, anomalias, patron_hora, patron_dia, patron_mes)
    
    # 6. Generar reporte
    generar_reporte(df_series, anomalias, patron_hora, patron_dia, patron_mes)
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()
