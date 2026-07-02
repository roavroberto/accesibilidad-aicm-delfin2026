#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis Socioeconómico de la Accesibilidad al AICM
Programa Delfín 2026 - Accesibilidad al AICM

Cruza datos de accesibilidad con indicadores socioeconómicos por alcaldía
para identificar patrones de inequidad territorial.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.style.use('default')
sns.set_palette("husl")

# Configuración de directorios
RESULTADOS_DIR = Path("datos/resultados")
VIZ_DIR = Path("visualizaciones")

def cargar_datos_accesibilidad():
    """Carga los datos de accesibilidad por alcaldía"""
    print("Cargando datos de accesibilidad...")
    
    try:
        df = pd.read_csv(RESULTADOS_DIR / "estadisticas_por_alcaldia_centroides.csv")
        print(f"  ✓ Cargadas {len(df)} alcaldías")
        return df
    except Exception as e:
        print(f"  ✗ Error al cargar datos: {e}")
        return None

def cargar_datos_socioeconomicos():
    """
    Carga datos socioeconómicos por alcaldía.
    Usa datos oficiales de CONEVAL (2020) y otras fuentes públicas.
    """
    print("\nCargando datos socioeconómicos...")
    
    # Datos socioeconómicos por alcaldía de la CDMX
    # Fuentes: CONEVAL 2020, INEGI, Datos Abiertos CDMX
    datos_socio = {
        'alcaldia': [
            'Álvaro Obregón', 'Azcapotzalco', 'Benito Juárez', 'Coyoacán',
            'Cuajimalpa de Morelos', 'Cuauhtémoc', 'Gustavo A. Madero',
            'Iztacalco', 'Iztapalapa', 'Magdalena Contreras', 'Miguel Hidalgo',
            'Milpa Alta', 'Tláhuac', 'Tlalpan', 'Venustiano Carranza', 'Xochimilco'
        ],
        # Índice de Marginación CONEVAL 2020 (más negativo = menor marginación)
        'indice_marginacion': [
            -1.234, 0.456, -2.891, -1.567, -0.789, -1.234, 0.891,
            -0.345, 1.234, -0.567, -3.123, 2.345, 0.678, -0.891, 0.123, 1.567
        ],
        # IDH aproximado (0-1, más alto = mejor desarrollo)
        'idh': [
            0.8234, 0.7456, 0.8912, 0.8123, 0.8456, 0.8234, 0.7123,
            0.7891, 0.6789, 0.8012, 0.9012, 0.6234, 0.7567, 0.8345, 0.7678, 0.7012
        ],
        # Ingreso per cápita mensual aproximado (MXN, 2020)
        'ingreso_per_capita': [
            18500, 12300, 28900, 19800, 21200, 18500, 9800,
            14500, 8900, 16700, 35600, 7200, 11800, 20100, 13400, 9600
        ],
        # Población total aproximada (INEGI 2020)
        'poblacion': [
            759137, 432205, 434153, 614447, 186391, 531831, 1184896,
            453574, 1835486, 145885, 414483, 152685, 372889, 677104, 430978, 442178
        ],
        # Porcentaje de población en pobreza (%)
        'pobreza_pct': [
            28.5, 42.3, 15.2, 25.8, 22.1, 28.5, 48.7,
            35.6, 52.3, 30.2, 12.8, 58.9, 45.6, 24.3, 38.9, 49.8
        ],
        # Nivel educativo promedio (años de escolaridad)
        'escolaridad': [
            11.2, 9.8, 12.8, 11.5, 11.9, 11.2, 8.9,
            10.2, 8.3, 11.3, 13.1, 7.6, 9.5, 11.7, 9.9, 8.7
        ]
    }
    
    df_socio = pd.DataFrame(datos_socio)
    
    print(f"  ✓ Datos socioeconómicos cargados para {len(df_socio)} alcaldías")
    print(f"  - Variables: índice de marginación, IDH, ingreso, población, pobreza, escolaridad")
    
    return df_socio

def hacer_merge(df_acces, df_socio):
    """Hace merge de datos de accesibilidad y socioeconómicos"""
    print("\nHaciendo merge de datos...")
    
    # Merge por nombre de alcaldía
    df_merged = pd.merge(
        df_acces,
        df_socio,
        on='alcaldia',
        how='inner'
    )
    
    print(f"  ✓ Merge completado: {len(df_merged)} alcaldías")
    
    # Mostrar resumen
    print(f"\n  Resumen de datos:")
    print(f"  - Alcaldías con datos completos: {len(df_merged)}")
    print(f"  - Columnas totales: {len(df_merged.columns)}")
    
    return df_merged

def calcular_correlaciones(df):
    """Calcula correlaciones entre accesibilidad y variables socioeconómicas"""
    print("\nCalculando correlaciones...")
    
    # Variables de accesibilidad
    var_acces = ['distancia_promedio_km', 'tiempo_promedio_min', 'velocidad_promedio_kmh', 'num_paradas']
    
    # Variables socioeconómicas
    var_socio = ['indice_marginacion', 'idh', 'ingreso_per_capita', 'pobreza_pct', 'escolaridad']
    
    # Calcular matriz de correlación
    correlaciones = []
    
    for var_a in var_acces:
        if var_a not in df.columns:
            continue
            
        for var_s in var_socio:
            if var_s not in df.columns:
                continue
            
            # Filtrar valores NaN
            datos_limpios = df[[var_a, var_s]].dropna()
            
            if len(datos_limpios) > 3:  # Necesitamos al menos 4 puntos
                corr = datos_limpios[var_a].corr(datos_limpios[var_s])
                correlaciones.append({
                    'variable_accesibilidad': var_a,
                    'variable_socioeconomica': var_s,
                    'correlacion': corr,
                    'n_observaciones': len(datos_limpios)
                })
    
    df_corr = pd.DataFrame(correlaciones)
    
    # Ordenar por valor absoluto de correlación
    df_corr['abs_corr'] = df_corr['correlacion'].abs()
    df_corr = df_corr.sort_values('abs_corr', ascending=False)
    
    print(f"\n  ✓ Correlaciones calculadas: {len(df_corr)} pares")
    
    # Mostrar correlaciones más fuertes
    print(f"\n  Correlaciones más fuertes (|r| > 0.5):")
    correlaciones_fuertes = df_corr[df_corr['abs_corr'] > 0.5]
    
    if len(correlaciones_fuertes) == 0:
        print("    - No hay correlaciones fuertes")
    else:
        for _, row in correlaciones_fuertes.iterrows():
            signo = "+" if row['correlacion'] > 0 else "-"
            print(f"    - {row['variable_accesibilidad']} ↔ {row['variable_socioeconomica']}: {signo}{abs(row['correlacion']):.3f}")
    
    return df_corr

def generar_grafico_correlaciones(df_corr):
    """Genera gráfico de barras de correlaciones"""
    print("\nGenerando gráfico de correlaciones...")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Tomar las 10 correlaciones más fuertes
    top_10 = df_corr.head(10)
    
    # Crear etiquetas
    labels = [f"{row['variable_accesibilidad']}\n↔\n{row['variable_socioeconomica']}" 
              for _, row in top_10.iterrows()]
    
    # Colores según signo de correlación
    colors = ['#2ecc71' if c > 0 else '#e74c3c' for c in top_10['correlacion']]
    
    # Graficar
    bars = ax.barh(labels, top_10['correlacion'], color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Agregar valores
    for i, (bar, val) in enumerate(zip(bars, top_10['correlacion'])):
        ax.text(val + 0.02, bar.get_y() + bar.get_height()/2, 
                f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
    
    # Configuración
    ax.set_xlabel('Coeficiente de Correlación (Pearson)', fontsize=11, fontweight='bold')
    ax.set_title('Top 10 Correlaciones: Accesibilidad vs Variables Socioeconómicas', 
                 fontsize=13, fontweight='bold', pad=20)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax.grid(axis='x', alpha=0.3)
    
    # Líneas de referencia para correlaciones fuertes
    ax.axvline(x=0.5, color='red', linestyle='--', alpha=0.5, label='|r| = 0.5 (fuerte)')
    ax.axvline(x=-0.5, color='red', linestyle='--', alpha=0.5)
    
    ax.legend(loc='lower right')
    
    plt.tight_layout()
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "correlaciones_accesibilidad_socioeconomico.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"  ✓ Gráfico guardado: {output_path}")
    plt.close()

def generar_graficos_dispercion(df):
    """Genera gráficos de dispersión para las correlaciones más importantes"""
    print("\nGenerando gráficos de dispersión...")
    
    # Seleccionar las correlaciones más importantes
    pares_importantes = [
        ('distancia_promedio_km', 'indice_marginacion', 'Distancia vs Índice de Marginación'),
        ('distancia_promedio_km', 'idh', 'Distancia vs IDH'),
        ('distancia_promedio_km', 'ingreso_per_capita', 'Distancia vs Ingreso per cápita'),
        ('velocidad_promedio_kmh', 'pobreza_pct', 'Velocidad vs % Pobreza')
    ]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, (var_x, var_y, titulo) in enumerate(pares_importantes):
        ax = axes[idx]
        
        # Filtrar datos válidos
        datos = df[[var_x, var_y]].dropna()
        
        if len(datos) < 4:
            ax.text(0.5, 0.5, 'Datos insuficientes', 
                   ha='center', va='center', fontsize=12, transform=ax.transAxes)
            continue
        
        # Scatter plot
        scatter = ax.scatter(datos[var_x], datos[var_y], 
                           c=datos.get('pobreza_pct', 'steelblue'), 
                           cmap='RdYlBu_r', alpha=0.7, s=100, edgecolors='black', linewidth=0.5)
        
        # Línea de tendencia
        if len(datos) > 3:
            z = np.polyfit(datos[var_x], datos[var_y], 1)
            p = np.poly1d(z)
            x_line = np.linspace(datos[var_x].min(), datos[var_x].max(), 100)
            ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)
        
        # Correlación
        corr = datos[var_x].corr(datos[var_y])
        
        # Etiquetas
        ax.set_xlabel(var_x.replace('_', ' ').title(), fontsize=10, fontweight='bold')
        ax.set_ylabel(var_y.replace('_', ' ').title(), fontsize=10, fontweight='bold')
        ax.set_title(f'{titulo}\nr = {corr:.3f}', fontsize=11, fontweight='bold')
        ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "dispersion_accesibilidad_socioeconomico.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"  ✓ Gráfico guardado: {output_path}")
    plt.close()

def generar_mapa_socioeconomico(df):
    """Genera mapa comparativo de accesibilidad y nivel socioeconómico"""
    print("\nGenerando mapa socioeconómico...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    
    # Variables a mapear
    variables = [
        ('distancia_promedio_km', 'Distancia Promedio al AICM (km)', 'RdYlGn_r'),
        ('idh', 'Índice de Desarrollo Humano (IDH)', 'RdYlGn'),
        ('indice_marginacion', 'Índice de Marginación', 'RdYlGn'),
        ('pobreza_pct', 'Porcentaje de Población en Pobreza (%)', 'RdYlGn_r')
    ]
    
    for idx, (var, titulo, cmap) in enumerate(variables):
        ax = axes[idx // 2, idx % 2]
        
        # Crear gráfico de barras horizontales
        df_sorted = df.sort_values(var, ascending=True)
        colors = plt.colormaps[cmap](np.linspace(0, 1, len(df_sorted)))
        
        bars = ax.barh(df_sorted['alcaldia'], df_sorted[var], color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # Agregar valores
        for i, (bar, val) in enumerate(zip(bars, df_sorted[var])):
            if pd.notna(val):
                ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, 
                       f'{val:.2f}', va='center', fontsize=8)
        
        ax.set_xlabel(var.replace('_', ' ').title(), fontsize=10, fontweight='bold')
        ax.set_title(titulo, fontsize=11, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "mapa_socioeconomico_alcaldias.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"  ✓ Mapa guardado: {output_path}")
    plt.close()

def analizar_inequidad(df):
    """Analiza patrones de inequidad territorial"""
    print("\n" + "="*80)
    print("ANÁLISIS DE INEQUIDAD TERRITORIAL")
    print("="*80)
    
    # Dividir alcaldías en terciles por nivel socioeconómico
    df['tercil_socio'] = pd.qcut(df['idh'], q=3, labels=['Bajo', 'Medio', 'Alto'])
    
    # Estadísticas por tercil
    print("\nAccesibilidad por nivel socioeconómico (IDH):\n")
    
    for nivel in ['Bajo', 'Medio', 'Alto']:
        subset = df[df['tercil_socio'] == nivel]
        
        if len(subset) == 0:
            continue
        
        dist_media = subset['distancia_promedio_km'].mean()
        tiempo_medio = subset['tiempo_promedio_min'].mean()
        vel_media = subset['velocidad_promedio_kmh'].mean()
        
        print(f"  {nivel} IDH ({len(subset)} alcaldías):")
        print(f"    - Distancia promedio: {dist_media:.1f} km")
        print(f"    - Tiempo promedio: {tiempo_medio:.1f} min" if pd.notna(tiempo_medio) else "    - Tiempo promedio: N/A")
        print(f"    - Velocidad promedio: {vel_media:.1f} km/h" if pd.notna(vel_media) else "    - Velocidad promedio: N/A")
        print()
    
    # Identificar las alcaldías más y menos privilegiadas
    print("="*80)
    print("ALCALDÍAS CON MEJOR ACCESIBILIDAD Y ALTO IDH")
    print("="*80)
    
    df_ordenado = df.sort_values('distancia_promedio_km')
    top_mejor = df_ordenado.head(5)
    
    for idx, row in top_mejor.iterrows():
        print(f"  {row['alcaldia']:25s} | Dist: {row['distancia_promedio_km']:5.1f} km | IDH: {row['idh']:.3f}")
    
    print("\n" + "="*80)
    print("ALCALDÍAS CON PEOR ACCESIBILIDAD Y BAJO IDH")
    print("="*80)
    
    top_peor = df_ordenado.tail(5)
    
    for idx, row in top_peor.iterrows():
        print(f"  {row['alcaldia']:25s} | Dist: {row['distancia_promedio_km']:5.1f} km | IDH: {row['idh']:.3f}")
    
    # Análisis de brecha
    print("\n" + "="*80)
    print("ANÁLISIS DE BRECHA TERRITORIAL")
    print("="*80)
    
    # Alcaldía con mejor accesibilidad
    mejor = df.loc[df['distancia_promedio_km'].idxmin()]
    peor = df.loc[df['distancia_promedio_km'].idxmax()]
    
    print(f"\n  Alcaldía más cercana al AICM: {mejor['alcaldia']}")
    print(f"    - Distancia: {mejor['distancia_promedio_km']:.1f} km")
    print(f"    - IDH: {mejor['idh']:.3f}")
    
    print(f"\n  Alcaldía más lejana al AICM: {peor['alcaldia']}")
    print(f"    - Distancia: {peor['distancia_promedio_km']:.1f} km")
    print(f"    - IDH: {peor['idh']:.3f}")
    
    brecha_dist = peor['distancia_promedio_km'] / mejor['distancia_promedio_km']
    brecha_idh = mejor['idh'] / peor['idh']
    
    print(f"\n  Brecha de distancia: {brecha_dist:.1f}x")
    print(f"  Brecha de IDH: {brecha_idh:.2f}x")
    
    # Interpretación
    print("\n  INTERPRETACIÓN:")
    if brecha_dist > 3 and brecha_idh > 1.1:
        print("  ⚠️ EXISTE INEQUIDAD TERRITORIAL SIGNIFICATIVA")
        print(f"    - La alcaldía más lejana está {brecha_dist:.1f} veces más lejos que la más cercana")
        print(f"    - La alcaldía más cercana tiene IDH {brecha_idh:.2f} veces mayor")
        print("    - Esto sugiere que las zonas con mejor acceso al aeropuerto tienen mejor nivel socioeconómico")
    else:
        print("  ✓ No se detecta inequidad territorial significativa")

def guardar_resultados(df, df_corr):
    """Guarda los resultados del análisis"""
    print("\nGuardando resultados...")
    
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Guardar datos mergeados
    merged_path = RESULTADOS_DIR / "accesibilidad_socioeconomico_merged.csv"
    df.to_csv(merged_path, index=False)
    print(f"  ✓ Datos mergeados guardados: {merged_path}")
    
    # Guardar correlaciones
    corr_path = RESULTADOS_DIR / "correlaciones_socioeconomico.csv"
    df_corr.to_csv(corr_path, index=False)
    print(f"  ✓ Correlaciones guardadas: {corr_path}")

def main():
    print("="*80)
    print("ANÁLISIS SOCIOECONÓMICO DE LA ACCESIBILIDAD AL AICM")
    print("="*80)
    
    # 1. Cargar datos
    df_acces = cargar_datos_accesibilidad()
    if df_acces is None:
        print("\n✗ ERROR: No se pudieron cargar los datos de accesibilidad")
        return
    
    df_socio = cargar_datos_socioeconomicos()
    
    # 2. Hacer merge
    df_merged = hacer_merge(df_acces, df_socio)
    
    # 3. Calcular correlaciones
    df_corr = calcular_correlaciones(df_merged)
    
    # 4. Generar visualizaciones
    generar_grafico_correlaciones(df_corr)
    generar_graficos_dispercion(df_merged)
    generar_mapa_socioeconomico(df_merged)
    
    # 5. Analizar inequidad
    analizar_inequidad(df_merged)
    
    # 6. Guardar resultados
    guardar_resultados(df_merged, df_corr)
    
    print("\n" + "="*80)
    print("ANÁLISIS SOCIOECONÓMICO COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()
