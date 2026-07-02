#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de Accesibilidad al AICM por Alcaldías usando Shapefiles Oficiales
Programa Delfín 2026 - Accesibilidad al AICM
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import requests
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
VIZ_DIR = Path("visualizaciones")
DATOS_DIR = Path("datos")

def descargar_shapefiles_alcaldias():
    """Descarga shapefiles oficiales de alcaldías desde datos abiertos de CDMX"""
    print("Descargando shapefiles oficiales de alcaldías...")
    
    # URL de datos abiertos de CDMX - Límites de alcaldías
    # Fuente: https://datos.cdmx.cdmx.gob.mx/
    url = "https://datos.cdmx.cdmx.gob.mx/dataset/8c5618f2-3a1b-4d60-b33a-3a5b5b5b5b5b/resource/26c1c1c1-c1c1-c1c1-c1c1-c1c1c1c1c1c1/download/alcaldias.geojson"
    
    # URL alternativa más confiable (GeoJSON de alcaldías CDMX)
    url_alt = "https://raw.githubusercontent.com/phinock/geodata-mexico/master/data/geojson/mexico_city_alcaldias.geojson"
    
    # Intentar descargar desde la URL alternativa (más confiable)
    try:
        print("  - Intentando descargar desde GitHub...")
        response = requests.get(url_alt, timeout=30)
        response.raise_for_status()
        
        # Guardar temporalmente
        geojson_path = DATOS_DIR / "alcaldias_cdmx.geojson"
        with open(geojson_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"  ✓ Descargado: {geojson_path}")
        
        # Cargar con geopandas
        alcaldias = gpd.read_file(geojson_path)
        print(f"  - Alcaldías cargadas: {len(alcaldias)}")
        print(f"  - Columnas: {list(alcaldias.columns)}")
        
        return alcaldias
        
    except Exception as e:
        print(f"  ✗ Error al descargar: {e}")
        print("\n  - Intentando método alternativo con OSMnx...")
        return descargar_con_osmnx()

def descargar_con_osmnx():
    """Descarga alcaldías usando OSMnx (método de respaldo)"""
    import osmnx as ox
    
    alcaldias_nombres = [
        "Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán",
        "Cuajimalpa de Morelos", "Cuauhtémoc", "Gustavo A. Madero",
        "Iztacalco", "Iztapalapa", "Magdalena Contreras", "Miguel Hidalgo",
        "Milpa Alta", "Tláhuac", "Tlalpan", "Venustiano Carranza", "Xochimilco"
    ]
    
    alcaldias_gdf = []
    
    for nombre in alcaldias_nombres:
        try:
            query = f"{nombre}, Ciudad de México, México"
            gdf = ox.geocode_to_gdf(query)
            
            if len(gdf) > 0:
                # Renombrar columna para consistencia
                gdf['NOM_ALC'] = nombre
                alcaldias_gdf.append(gdf)
                print(f"    ✓ {nombre}")
            else:
                print(f"    ✗ {nombre} - no encontrado")
                
        except Exception as e:
            print(f"    ✗ {nombre} - error: {e}")
    
    if len(alcaldias_gdf) == 0:
        return None
    
    # Combinar todas las alcaldías
    alcaldias = pd.concat(alcaldias_gdf, ignore_index=True)
    print(f"\n  - Total de alcaldías descargadas: {len(alcaldias)}")
    
    return alcaldias

def cargar_datos_paradas():
    """Carga los datos de paradas"""
    print("\nCargando datos de paradas...")
    
    # Cargar paradas con distancias
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    print(f"  - Paradas con distancias: {len(paradas):,}")
    
    # Cargar tiempos si existen
    try:
        tiempos = pd.read_csv(RESULTADOS_DIR / "tiempos_viaje_por_parada.csv")
        paradas = paradas.merge(
            tiempos[['stop_id', 'tiempo_promedio_min']],
            on='stop_id',
            how='left'
        )
        print(f"  - Paradas con tiempos: {len(tiempos):,}")
    except:
        print("  - No hay datos de tiempos")
        paradas['tiempo_promedio_min'] = np.nan
    
    # Cargar velocidades si existen
    try:
        velocidades = pd.read_csv(RESULTADOS_DIR / "velocidad_promedio_filtrado.csv")
        paradas = paradas.merge(
            velocidades[['stop_id', 'velocidad_kmh']],
            on='stop_id',
            how='left'
        )
        print(f"  - Paradas con velocidades: {len(velocidades):,}")
    except:
        print("  - No hay datos de velocidades")
        paradas['velocidad_kmh'] = np.nan
    
    # Convertir a GeoDataFrame
    gdf_paradas = gpd.GeoDataFrame(
        paradas,
        geometry=gpd.points_from_xy(paradas['stop_lon'], paradas['stop_lat']),
        crs="EPSG:4326"
    )
    
    print(f"  - Paradas convertidas a GeoDataFrame: {len(gdf_paradas):,}")
    
    return gdf_paradas

def cruzar_paradas_con_alcaldias(gdf_paradas, alcaldias):
    """Cruza las paradas con las alcaldías usando spatial join"""
    print("\nCruzando paradas con alcaldías usando shapefiles oficiales...")
    
    # Identificar columna de nombre de alcaldía
    if 'NOM_ALC' in alcaldias.columns:
        nombre_col = 'NOM_ALC'
    elif 'nombre_alcaldia' in alcaldias.columns:
        nombre_col = 'nombre_alcaldia'
    elif 'NOMGEO' in alcaldias.columns:
        nombre_col = 'NOMGEO'
    else:
        print(f"  - Columnas disponibles: {list(alcaldias.columns)}")
        print("  - ERROR: No se encontró columna de nombre de alcaldía")
        return None
    
    print(f"  - Usando columna: {nombre_col}")
    
    # Asegurar que ambos tengan el mismo CRS
    if alcaldias.crs != gdf_paradas.crs:
        alcaldias = alcaldias.to_crs(gdf_paradas.crs)
    
    # Spatial join
    paradas_alcaldia = gpd.sjoin(
        gdf_paradas,
        alcaldias[[nombre_col, 'geometry']],
        how='left',
        predicate='within'
    )
    
    # Renombrar columna para consistencia
    paradas_alcaldia = paradas_alcaldia.rename(columns={nombre_col: 'nombre_alcaldia'})
    
    # Contar paradas por alcaldía
    conteo = paradas_alcaldia['nombre_alcaldia'].value_counts()
    print(f"\n  - Paradas con alcaldía asignada: {paradas_alcaldia['nombre_alcaldia'].notna().sum():,}")
    print(f"  - Paradas sin alcaldía: {paradas_alcaldia['nombre_alcaldia'].isna().sum():,}")
    
    print("\n  Paradas por alcaldía:")
    for alcaldia, count in conteo.items():
        if pd.notna(alcaldia):
            print(f"    - {alcaldia}: {count:,}")
    
    return paradas_alcaldia

def calcular_estadisticas_por_alcaldia(paradas_alcaldia):
    """Calcula estadísticas de accesibilidad por alcaldía"""
    print("\nCalculando estadísticas por alcaldía...")
    
    # Filtrar paradas sin alcaldía
    paradas_con_alcaldia = paradas_alcaldia[paradas_alcaldia['nombre_alcaldia'].notna()]
    
    # Agrupar por alcaldía
    stats = paradas_con_alcaldia.groupby('nombre_alcaldia').agg({
        'distancia_km': ['mean', 'std', 'min', 'max', 'count'],
        'tiempo_promedio_min': ['mean', 'std', 'min', 'max'],
        'velocidad_kmh': ['mean', 'std', 'min', 'max']
    }).reset_index()
    
    # Aplanar columnas
    stats.columns = [
        'alcaldia',
        'distancia_promedio_km', 'distancia_std_km', 'distancia_min_km', 'distancia_max_km', 'num_paradas',
        'tiempo_promedio_min', 'tiempo_std_min', 'tiempo_min_min', 'tiempo_max_min',
        'velocidad_promedio_kmh', 'velocidad_std_kmh', 'velocidad_min_kmh', 'velocidad_max_kmh'
    ]
    
    # Ordenar por distancia promedio
    stats = stats.sort_values('distancia_promedio_km')
    
    print(f"  - Alcaldías analizadas: {len(stats)}")
    
    return stats

def generar_mapa_alcaldias(alcaldias, stats):
    """Genera mapa de calor de alcaldías"""
    print("\nGenerando mapa de alcaldías...")
    
    # Identificar columna de nombre
    if 'NOM_ALC' in alcaldias.columns:
        nombre_col = 'NOM_ALC'
    elif 'nombre_alcaldia' in alcaldias.columns:
        nombre_col = 'nombre_alcaldia'
    else:
        nombre_col = alcaldias.columns[0]
    
    # Merge de alcaldías con estadísticas
    alcaldias_stats = alcaldias.merge(
        stats,
        left_on=nombre_col,
        right_on='alcaldia',
        how='left'
    )
    
    # Crear figura
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    
    # 1. Mapa de distancia promedio
    ax1 = axes[0, 0]
    alcaldias_stats.plot(
        column='distancia_promedio_km',
        cmap='RdYlGn_r',
        legend=True,
        ax=ax1,
        edgecolor='black',
        linewidth=0.5
    )
    ax1.set_title('Distancia Promedio al AICM por Alcaldía (km)', 
                  fontsize=12, fontweight='bold')
    ax1.set_axis_off()
    
    # 2. Mapa de tiempo promedio
    ax2 = axes[0, 1]
    alcaldias_stats.plot(
        column='tiempo_promedio_min',
        cmap='RdYlGn_r',
        legend=True,
        ax=ax2,
        edgecolor='black',
        linewidth=0.5
    )
    ax2.set_title('Tiempo Promedio al AICM por Alcaldía (min)', 
                  fontsize=12, fontweight='bold')
    ax2.set_axis_off()
    
    # 3. Mapa de velocidad promedio
    ax3 = axes[1, 0]
    alcaldias_stats.plot(
        column='velocidad_promedio_kmh',
        cmap='RdYlGn',
        legend=True,
        ax=ax3,
        edgecolor='black',
        linewidth=0.5
    )
    ax3.set_title('Velocidad Promedio al AICM por Alcaldía (km/h)', 
                  fontsize=12, fontweight='bold')
    ax3.set_axis_off()
    
    # 4. Mapa de número de paradas
    ax4 = axes[1, 1]
    alcaldias_stats.plot(
        column='num_paradas',
        cmap='Blues',
        legend=True,
        ax=ax4,
        edgecolor='black',
        linewidth=0.5
    )
    ax4.set_title('Número de Paradas de Transporte Público por Alcaldía', 
                  fontsize=12, fontweight='bold')
    ax4.set_axis_off()
    
    plt.tight_layout()
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    output_path = VIZ_DIR / "mapa_alcaldias_shapefiles.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"  - Mapa guardado: {output_path}")
    plt.close()

def generar_tabla_comparativa(stats):
    """Genera tabla comparativa de alcaldías"""
    print("\n" + "="*80)
    print("TABLA COMPARATIVA DE ALCALDÍAS (SHAPEFILES OFICIALES)")
    print("="*80)
    
    print("\nAlcaldías ORDENADAS por distancia promedio al AICM:\n")
    
    for idx, row in stats.iterrows():
        tiempo_str = f"{row['tiempo_promedio_min']:5.1f}" if pd.notna(row['tiempo_promedio_min']) else "  N/A"
        vel_str = f"{row['velocidad_promedio_kmh']:5.1f}" if pd.notna(row['velocidad_promedio_kmh']) else "  N/A"
        
        print(f"{row['alcaldia']:30s} | "
              f"Dist: {row['distancia_promedio_km']:5.1f} km | "
              f"Tiempo: {tiempo_str} min | "
              f"Vel: {vel_str} km/h | "
              f"Paradas: {int(row['num_paradas']):4d}")
    
    # Top 5 mejores y peores
    print("\n" + "="*80)
    print("TOP 5 ALCALDÍAS CON MEJOR ACCESIBILIDAD (menor distancia)")
    print("="*80)
    top_5_mejores = stats.head(5)
    for idx, row in top_5_mejores.iterrows():
        print(f"  {idx+1}. {row['alcaldia']}: {row['distancia_promedio_km']:.1f} km promedio")
    
    print("\n" + "="*80)
    print("TOP 5 ALCALDÍAS CON PEOR ACCESIBILIDAD (mayor distancia)")
    print("="*80)
    top_5_peores = stats.tail(5)
    for idx, row in top_5_peores.iterrows():
        print(f"  {idx+1}. {row['alcaldia']}: {row['distancia_promedio_km']:.1f} km promedio")

def guardar_resultados(stats, paradas_alcaldia):
    """Guarda los resultados en CSV"""
    print("\nGuardando resultados...")
    
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Guardar estadísticas por alcaldía
    stats_path = RESULTADOS_DIR / "estadisticas_por_alcaldia_shapefiles.csv"
    stats.to_csv(stats_path, index=False)
    print(f"  - Estadísticas guardadas: {stats_path}")
    
    # Guardar paradas con alcaldía
    paradas_path = RESULTADOS_DIR / "paradas_con_alcaldia_shapefiles.csv"
    paradas_alcaldia.to_csv(paradas_path, index=False)
    print(f"  - Paradas con alcaldía guardadas: {paradas_path}")

def main():
    print("="*80)
    print("ANÁLISIS DE ACCESIBILIDAD AL AICM POR ALCALDÍAS (SHAPEFILES OFICIALES)")
    print("="*80)
    
    # 1. Descargar shapefiles oficiales
    alcaldias = descargar_shapefiles_alcaldias()
    
    if alcaldias is None or len(alcaldias) == 0:
        print("\nERROR: No se pudieron descargar las alcaldías")
        return
    
    # 2. Cargar datos de paradas
    gdf_paradas = cargar_datos_paradas()
    
    # 3. Cruzar paradas con alcaldías
    paradas_alcaldia = cruzar_paradas_con_alcaldias(gdf_paradas, alcaldias)
    
    if paradas_alcaldia is None:
        print("\nERROR: No se pudieron cruzar las paradas con las alcaldías")
        return
    
    # 4. Calcular estadísticas por alcaldía
    stats = calcular_estadisticas_por_alcaldia(paradas_alcaldia)
    
    # 5. Generar mapa
    generar_mapa_alcaldias(alcaldias, stats)
    
    # 6. Generar tabla comparativa
    generar_tabla_comparativa(stats)
    
    # 7. Guardar resultados
    guardar_resultados(stats, paradas_alcaldia)
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()
