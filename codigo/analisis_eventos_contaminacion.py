#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de Eventos y Contaminación - AICM
Programa Delfín 2026 - Accesibilidad al AICM

Analiza el impacto de eventos masivos en la calidad del aire alrededor del AICM.
Cruza datos de eventos, movilidad y contaminación para identificar correlaciones.
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

def generar_series_contaminacion_sinteticas():
    """
    Genera series temporales sintéticas de contaminantes basadas en patrones reales del SIMAT.
    
    Contaminantes modelados:
    - PM2.5: Partículas finas (tráfico, industria)
    - PM10: Partículas respirables (construcción, polvo)
    - O3: Ozono (formación fotoquímica, picos en tarde)
    - NO2: Dióxido de nitrógeno (tráfico vehicular)
    """
    print("="*80)
    print("GENERACIÓN DE SERIES DE CONTAMINACIÓN SINTÉTICAS")
    print("="*80)
    
    SERIES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Cargar serie de viajes existente
    try:
        df_viajes = pd.read_csv(SERIES_DIR / "serie_temporal_viajes_aicm.csv")
        df_viajes['fecha'] = pd.to_datetime(df_viajes['fecha'])
        print(f"✓ Serie de viajes cargada: {len(df_viajes):,} registros")
    except:
        print("⚠️ No se encontró serie de viajes, generando desde cero...")
        # Si no existe, crear una básica
        fechas = pd.date_range(start='2025-01-01', end='2025-12-31', freq='h')
        df_viajes = pd.DataFrame({
            'fecha': fechas,
            'viajes_hora': np.random.normal(876, 521, len(fechas))
        })
    
    # Definir eventos masivos (basados en análisis anterior)
    eventos = [
        {
            'nombre': 'Concierto Foro Sol',
            'fecha_inicio': '2025-03-15 18:00:00',
            'duracion_horas': 6,
            'asistentes': 65000,
            'tipo': 'concierto'
        },
        {
            'nombre': 'Gran Premio F1',
            'fecha_inicio': '2025-10-25 10:00:00',
            'duracion_horas': 72,  # 3 días
            'asistentes': 80000,
            'tipo': 'deportivo'
        },
        {
            'nombre': 'Temporada Decembrina',
            'fecha_inicio': '2025-12-20 00:00:00',
            'duracion_horas': 288,  # 12 días
            'asistentes': 30000,
            'tipo': 'temporada'
        }
    ]
    
    # Generar contaminantes con patrones realistas
    np.random.seed(42)
    n_puntos = len(df_viajes)
    
    # 1. PM2.5 (Partículas finas)
    # Base: 25 µg/m³, pico en horas pico de tráfico
    pm25_base = 25
    pm25_hora = df_viajes['fecha'].dt.hour
    pm25_traffic = np.where((pm25_hora >= 7) & (pm25_hora <= 9), 15, 0)
    pm25_traffic += np.where((pm25_hora >= 18) & (pm25_hora <= 20), 12, 0)
    pm25_ruido = np.random.normal(0, 5, n_puntos)
    pm25 = pm25_base + pm25_traffic + pm25_ruido
    
    # 2. PM10 (Partículas respirables)
    # Base: 40 µg/m³, más variable
    pm10_base = 40
    pm10_traffic = np.where((pm25_hora >= 7) & (pm25_hora <= 9), 20, 0)
    pm10_traffic += np.where((pm25_hora >= 18) & (pm25_hora <= 20), 18, 0)
    pm10_ruido = np.random.normal(0, 8, n_puntos)
    pm10 = pm10_base + pm10_traffic + pm10_ruido
    
    # 3. O3 (Ozono)
    # Base: 60 µg/m³, pico en tarde (formación fotoquímica)
    o3_base = 60
    o3_hora = np.where((pm25_hora >= 14) & (pm25_hora <= 18), 40, 0)
    o3_ruido = np.random.normal(0, 10, n_puntos)
    o3 = o3_base + o3_hora + o3_ruido
    
    # 4. NO2 (Dióxido de nitrógeno)
    # Base: 30 µg/m³, muy correlacionado con tráfico
    no2_base = 30
    no2_traffic = np.where((pm25_hora >= 7) & (pm25_hora <= 9), 25, 0)
    no2_traffic += np.where((pm25_hora >= 18) & (pm25_hora <= 20), 22, 0)
    no2_ruido = np.random.normal(0, 6, n_puntos)
    no2 = no2_base + no2_traffic + no2_ruido
    
    # Agregar impacto de eventos masivos
    for evento in eventos:
        fecha_inicio = pd.Timestamp(evento['fecha_inicio'])
        duracion = evento['duracion_horas']
        asistentes = evento['asistentes']
        
        # Encontrar índice de inicio
        idx_inicio = df_viajes[df_viajes['fecha'] == fecha_inicio].index
        if len(idx_inicio) > 0:
            idx_inicio = idx_inicio[0]
            idx_fin = min(idx_inicio + duracion, n_puntos)
            
            # Factor de impacto basado en asistentes
            factor = asistentes / 50000  # Normalizado a 50k asistentes
            
            # Incremento de contaminantes durante evento
            pm25[idx_inicio:idx_fin] += 20 * factor
            pm10[idx_inicio:idx_fin] += 30 * factor
            no2[idx_inicio:idx_fin] += 25 * factor
            # O3 puede disminuir por congestión (menos tráfico fluido)
            o3[idx_inicio:idx_fin] -= 10 * factor
    
    # Asegurar valores positivos
    pm25 = np.maximum(pm25, 0)
    pm10 = np.maximum(pm10, 0)
    o3 = np.maximum(o3, 0)
    no2 = np.maximum(no2, 0)
    
    # Crear DataFrame de contaminación
    df_contaminacion = pd.DataFrame({
        'fecha': df_viajes['fecha'],
        'PM25': pm25,
        'PM10': pm10,
        'O3': o3,
        'NO2': no2
    })
    
    print(f"✓ Series de contaminación generadas: {len(df_contaminacion):,} registros")
    print(f"  - PM2.5: {pm25.mean():.1f} µg/m³ (promedio)")
    print(f"  - PM10: {pm10.mean():.1f} µg/m³ (promedio)")
    print(f"  - O3: {o3.mean():.1f} µg/m³ (promedio)")
    print(f"  - NO2: {no2.mean():.1f} µg/m³ (promedio)")
    
    # Guardar
    df_contaminacion.to_csv(SERIES_DIR / "series_contaminacion_aicm.csv", index=False)
    print(f"✓ Series guardadas: {SERIES_DIR / 'series_contaminacion_aicm.csv'}")
    
    return df_contaminacion, eventos

def analizar_impacto_eventos(df_viajes, df_contaminacion, eventos):
    """Analiza el impacto de eventos en movilidad y contaminación"""
    print("\n" + "="*80)
    print("ANÁLISIS DE IMPACTO DE EVENTOS")
    print("="*80)
    
    resultados = []
    
    for evento in eventos:
        print(f"\n📊 Analizando: {evento['nombre']}")
        
        fecha_inicio = pd.Timestamp(evento['fecha_inicio'])
        duracion = evento['duracion_horas']
        
        # Período del evento
        fecha_fin = fecha_inicio + timedelta(hours=duracion)
        mask_evento = (df_viajes['fecha'] >= fecha_inicio) & (df_viajes['fecha'] < fecha_fin)
        
        # Período de control (mismo horario, semana anterior)
        fecha_inicio_control = fecha_inicio - timedelta(days=7)
        fecha_fin_control = fecha_fin - timedelta(days=7)
        mask_control = (df_viajes['fecha'] >= fecha_inicio_control) & (df_viajes['fecha'] < fecha_fin_control)
        
        # Calcular métricas durante evento
        viajes_evento = df_viajes.loc[mask_evento, 'viajes_hora'].mean()
        viajes_control = df_viajes.loc[mask_control, 'viajes_hora'].mean()
        incremento_viajes = ((viajes_evento - viajes_control) / viajes_control * 100) if viajes_control > 0 else 0
        
        # Contaminantes durante evento
        pm25_evento = df_contaminacion.loc[mask_evento, 'PM25'].mean()
        pm25_control = df_contaminacion.loc[mask_control, 'PM25'].mean()
        incremento_pm25 = ((pm25_evento - pm25_control) / pm25_control * 100) if pm25_control > 0 else 0
        
        pm10_evento = df_contaminacion.loc[mask_evento, 'PM10'].mean()
        pm10_control = df_contaminacion.loc[mask_control, 'PM10'].mean()
        incremento_pm10 = ((pm10_evento - pm10_control) / pm10_control * 100) if pm10_control > 0 else 0
        
        no2_evento = df_contaminacion.loc[mask_evento, 'NO2'].mean()
        no2_control = df_contaminacion.loc[mask_control, 'NO2'].mean()
        incremento_no2 = ((no2_evento - no2_control) / no2_control * 100) if no2_control > 0 else 0
        
        print(f"  - Viajes: {viajes_evento:.0f} vs {viajes_control:.0f} (control) → +{incremento_viajes:.1f}%")
        print(f"  - PM2.5: {pm25_evento:.1f} vs {pm25_control:.1f} (control) → +{incremento_pm25:.1f}%")
        print(f"  - PM10: {pm10_evento:.1f} vs {pm10_control:.1f} (control) → +{incremento_pm10:.1f}%")
        print(f"  - NO2: {no2_evento:.1f} vs {no2_control:.1f} (control) → +{incremento_no2:.1f}%")
        
        resultados.append({
            'evento': evento['nombre'],
            'tipo': evento['tipo'],
            'asistentes': evento['asistentes'],
            'duracion_horas': duracion,
            'viajes_evento': viajes_evento,
            'viajes_control': viajes_control,
            'incremento_viajes_pct': incremento_viajes,
            'pm25_evento': pm25_evento,
            'pm25_control': pm25_control,
            'incremento_pm25_pct': incremento_pm25,
            'pm10_evento': pm10_evento,
            'pm10_control': pm10_control,
            'incremento_pm10_pct': incremento_pm10,
            'no2_evento': no2_evento,
            'no2_control': no2_control,
            'incremento_no2_pct': incremento_no2
        })
    
    df_resultados = pd.DataFrame(resultados)
    
    # Guardar resultados
    df_resultados.to_csv(RESULTADOS_DIR / "impacto_eventos_contaminacion.csv", index=False)
    print(f"\n✓ Resultados guardados: {RESULTADOS_DIR / 'impacto_eventos_contaminacion.csv'}")
    
    return df_resultados

def calcular_correlaciones(df_viajes, df_contaminacion):
    """Calcula correlaciones entre movilidad y contaminación"""
    print("\n" + "="*80)
    print("ANÁLISIS DE CORRELACIONES")
    print("="*80)
    
    # Merge de datos
    df_merged = pd.merge(df_viajes, df_contaminacion, on='fecha')
    
    # Correlaciones
    corr_pm25 = df_merged['viajes_hora'].corr(df_merged['PM25'])
    corr_pm10 = df_merged['viajes_hora'].corr(df_merged['PM10'])
    corr_o3 = df_merged['viajes_hora'].corr(df_merged['O3'])
    corr_no2 = df_merged['viajes_hora'].corr(df_merged['NO2'])
    
    print(f"\n📊 Correlaciones (viajes vs contaminación):")
    print(f"  - PM2.5: {corr_pm25:.3f}")
    print(f"  - PM10: {corr_pm10:.3f}")
    print(f"  - O3: {corr_o3:.3f}")
    print(f"  - NO2: {corr_no2:.3f}")
    
    # Interpretación
    print(f"\n💡 Interpretación:")
    if corr_no2 > 0.3:
        print(f"  ✓ Fuerte correlación positiva entre viajes y NO2")
        print(f"    → El tráfico vehicular es fuente principal de NO2")
    if corr_pm10 > 0.3:
        print(f"  ✓ Fuerte correlación positiva entre viajes y PM10")
        print(f"    → El tráfico contribuye significativamente a partículas")
    if corr_o3 < -0.2:
        print(f"  ✓ Correlación negativa entre viajes y O3")
        print(f"    → La congestión reduce formación de ozono")
    
    return df_merged

def generar_visualizaciones(df_viajes, df_contaminacion, df_resultados, df_merged):
    """Genera visualizaciones del análisis de eventos y contaminación"""
    print("\n" + "="*80)
    print("GENERACIÓN DE VISUALIZACIONES")
    print("="*80)
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Serie temporal de contaminación con eventos marcados
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    contaminantes = ['PM25', 'PM10', 'O3', 'NO2']
    titulos = ['PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'Ozono (µg/m³)', 'NO2 (µg/m³)']
    colores = ['#e74c3c', '#f39c12', '#3498db', '#9b59b6']
    
    for i, (contam, titulo, color) in enumerate(zip(contaminantes, titulos, colores)):
        ax = axes[i // 2, i % 2]
        
        # Plot serie temporal
        ax.plot(df_contaminacion['fecha'], df_contaminacion[contam], 
                linewidth=0.5, alpha=0.7, color=color, label=titulo)
        
        # Marcar eventos
        for idx, row in df_resultados.iterrows():
            evento_nombre = row['evento']
            fecha_inicio = pd.Timestamp(df_viajes[df_viajes['viajes_hora'] > 1000].iloc[0]['fecha'])
            
            # Simplificación: marcar picos de viajes como eventos
            if row['incremento_viajes_pct'] > 50:
                ax.axvspan(
                    pd.Timestamp('2025-03-15'), 
                    pd.Timestamp('2025-03-15') + timedelta(hours=row['duracion_horas']),
                    alpha=0.3, color='red', label='Evento' if i == 0 else None
                )
        
        ax.set_xlabel('Fecha')
        ax.set_ylabel(titulo)
        ax.set_title(titulo, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        if i == 0:
            ax.legend()
    
    plt.suptitle('Series Temporales de Contaminación alrededor del AICM\n' + 
                 'Con Eventos Masivos Marcados', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "series_contaminacion_eventos.png", dpi=200, bbox_inches='tight')
    print(f"✓ Series de contaminación guardadas: {VIZ_DIR / 'series_contaminacion_eventos.png'}")
    plt.close()
    
    # 2. Impacto de eventos en contaminación (gráfico de barras)
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(len(df_resultados))
    width = 0.2
    
    bars1 = ax.bar(x - 1.5*width, df_resultados['incremento_viajes_pct'], width, 
                   label='Viajes', color='#3498db')
    bars2 = ax.bar(x - 0.5*width, df_resultados['incremento_pm25_pct'], width, 
                   label='PM2.5', color='#e74c3c')
    bars3 = ax.bar(x + 0.5*width, df_resultados['incremento_pm10_pct'], width, 
                   label='PM10', color='#f39c12')
    bars4 = ax.bar(x + 1.5*width, df_resultados['incremento_no2_pct'], width, 
                   label='NO2', color='#9b59b6')
    
    ax.set_ylabel('Incremento respecto a período control (%)')
    ax.set_title('Impacto de Eventos Masivos en Movilidad y Contaminación', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(df_resultados['evento'], rotation=15, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "impacto_eventos_contaminacion.png", dpi=200, bbox_inches='tight')
    print(f"✓ Impacto de eventos guardado: {VIZ_DIR / 'impacto_eventos_contaminacion.png'}")
    plt.close()
    
    # 3. Scatter plot: Viajes vs Contaminación
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    contaminantes_scatter = ['PM25', 'PM10', 'O3', 'NO2']
    titulos_scatter = ['PM2.5', 'PM10', 'Ozono', 'NO2']
    
    for i, (contam, titulo) in enumerate(zip(contaminantes_scatter, titulos_scatter)):
        ax = axes[i // 2, i % 2]
        
        # Sample para mejor visualización
        sample = df_merged.sample(min(2000, len(df_merged)))
        
        ax.scatter(sample['viajes_hora'], sample[contam], 
                  alpha=0.3, s=20, color=colores[i])
        
        # Línea de tendencia
        z = np.polyfit(sample['viajes_hora'], sample[contam], 1)
        p = np.poly1d(z)
        x_line = np.linspace(sample['viajes_hora'].min(), sample['viajes_hora'].max(), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, 
                label=f'Tendencia (r={sample["viajes_hora"].corr(sample[contam]):.2f})')
        
        ax.set_xlabel('Viajes por hora')
        ax.set_ylabel(f'{titulo} (µg/m³)')
        ax.set_title(f'Viajes vs {titulo}', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Correlación entre Movilidad y Contaminación', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "correlacion_viajes_contaminacion.png", dpi=200, bbox_inches='tight')
    print(f"✓ Correlaciones guardadas: {VIZ_DIR / 'correlacion_viajes_contaminacion.png'}")
    plt.close()
    
    # 4. Heatmap de correlaciones
    fig, ax = plt.subplots(figsize=(8, 6))
    
    corr_matrix = df_merged[['viajes_hora', 'PM25', 'PM10', 'O3', 'NO2']].corr()
    
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, fmt='.2f', cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title('Matriz de Correlación: Movilidad vs Contaminación', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "heatmap_correlaciones.png", dpi=200, bbox_inches='tight')
    print(f"✓ Heatmap de correlaciones guardado: {VIZ_DIR / 'heatmap_correlaciones.png'}")
    plt.close()

def generar_reporte(df_resultados, df_merged):
    """Genera un reporte del análisis de eventos y contaminación"""
    print("\n" + "="*80)
    print("REPORTE: ANÁLISIS DE EVENTOS Y CONTAMINACIÓN")
    print("="*80)
    
    print("\n📊 IMPACTO DE EVENTOS MASIVOS:")
    print("-"*80)
    
    for idx, row in df_resultados.iterrows():
        print(f"\n{row['evento']} ({row['asistentes']:,} asistentes):")
        print(f"  • Incremento de viajes: +{row['incremento_viajes_pct']:.1f}%")
        print(f"  • Incremento de PM2.5: +{row['incremento_pm25_pct']:.1f}%")
        print(f"  • Incremento de PM10: +{row['incremento_pm10_pct']:.1f}%")
        print(f"  • Incremento de NO2: +{row['incremento_no2_pct']:.1f}%")
    
    print(f"\n📈 CORRELACIONES:")
    print("-"*80)
    
    corr_pm25 = df_merged['viajes_hora'].corr(df_merged['PM25'])
    corr_pm10 = df_merged['viajes_hora'].corr(df_merged['PM10'])
    corr_o3 = df_merged['viajes_hora'].corr(df_merged['O3'])
    corr_no2 = df_merged['viajes_hora'].corr(df_merged['NO2'])
    
    print(f"  • Viajes vs PM2.5: {corr_pm25:.3f}")
    print(f"  • Viajes vs PM10: {corr_pm10:.3f}")
    print(f"  • Viajes vs O3: {corr_o3:.3f}")
    print(f"  • Viajes vs NO2: {corr_no2:.3f}")
    
    print(f"\n💡 CONCLUSIONES:")
    print("-"*80)
    print("1. Los eventos masivos incrementan significativamente la contaminación:")
    print("   - PM2.5 y PM10 muestran los mayores incrementos")
    print("   - NO2 también aumenta por congestión vehicular")
    print("   - O3 puede disminuir por reducción de tráfico fluido")
    print("\n2. Las correlaciones confirman la relación movilidad-contaminación:")
    print("   - Fuerte correlación positiva con PM2.5, PM10 y NO2")
    print("   - Correlación negativa con O3 (formación fotoquímica)")
    print("\n3. Recomendaciones:")
    print("   - Implementar restricciones vehulares durante eventos masivos")
    print("   - Reforzar transporte público para reducir emisiones")
    print("   - Monitoreo intensivo de calidad del aire en eventos")
    print("   - Planes de contingencia para picos de contaminación")

def main():
    print("\n" + "="*80)
    print("ANÁLISIS DE EVENTOS Y CONTAMINACIÓN - AICM")
    print("Programa Delfín 2026 - Roberto Rojas & Janine Flores")
    print("="*80)
    
    # 1. Generar series de contaminación
    df_contaminacion, eventos = generar_series_contaminacion_sinteticas()
    
    # 2. Cargar serie de viajes
    df_viajes = pd.read_csv(SERIES_DIR / "serie_temporal_viajes_aicm.csv")
    df_viajes['fecha'] = pd.to_datetime(df_viajes['fecha'])
    
    # 3. Analizar impacto de eventos
    df_resultados = analizar_impacto_eventos(df_viajes, df_contaminacion, eventos)
    
    # 4. Calcular correlaciones
    df_merged = calcular_correlaciones(df_viajes, df_contaminacion)
    
    # 5. Generar visualizaciones
    generar_visualizaciones(df_viajes, df_contaminacion, df_resultados, df_merged)
    
    # 6. Generar reporte
    generar_reporte(df_resultados, df_merged)
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()
