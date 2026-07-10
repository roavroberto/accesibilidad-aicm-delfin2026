"""
voronoi_02_generar_poligonos.py
Proyecto Verano Delfín 2026 - Accesibilidad al AICM
Autor: Roberto Rojas Avila | Co-investigadora: Janine Flores

Descripción: 
Genera diagramas de Voronoi para cada modo de transporte y un análisis multimodal.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.spatial import Voronoi
from geovoronoi import voronoi_regions_from_coords, points_to_coords
from shapely.geometry import box
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTADOS_DIR = BASE_DIR / "datos" / "resultados"

print("=" * 60)
print("VORONOI - SCRIPT 2: GENERACIÓN DE POLÍGONOS")
print("=" * 60)

# ==========================================
# 2. CARGAR DATOS
# ==========================================
print("\n[1/4] Cargando datos de paradas...")

archivo_entrada = RESULTADOS_DIR / "paradas_con_modo_utm.geojson"
gdf_paradas = gpd.read_file(archivo_entrada)
print(f"✓ Cargadas {len(gdf_paradas)} paradas")

# ==========================================
# 3. DEFINIR ÁREA DE ESTUDIO
# ==========================================
print("\n[2/4] Definiendo área de estudio...")

# Coordenadas UTM (EPSG:32614) basadas en los datos reales
minx, miny = 425000, 2115000  # Suroeste
maxx, maxy = 505000, 2175000  # Noreste
area_estudio = box(minx, miny, maxx, maxy)

print(f"✓ Área de estudio creada: {area_estudio.bounds}")

# ==========================================
# 4. FUNCIÓN PARA GENERAR VORONOI
# ==========================================
def generar_voronoi_modo(gdf_modo, nombre_modo, area_limite):
    """
    Genera diagrama de Voronoi para un modo de transporte específico
    """
    print(f"\n  Procesando {nombre_modo}...")
    
    # Filtrar paradas dentro del área de estudio
    gdf_filtrado = gdf_modo[gdf_modo.within(area_limite)].copy()
    
    # RESETEAR ÍNDICE PARA COINCIDIR CON LOS ÍNDICES DE VORONOI
    gdf_filtrado = gdf_filtrado.reset_index(drop=True)
    
    if len(gdf_filtrado) < 3:
        print(f"    ⚠ Muy pocas paradas ({len(gdf_filtrado)}), omitiendo...")
        return None
    
    # Extraer coordenadas
    coords = points_to_coords(gdf_filtrado.geometry)
    
    # Generar regiones de Voronoi
    try:
        region_polys, region_pts = voronoi_regions_from_coords(coords, area_limite)
        
        # Crear GeoDataFrame con las regiones
        voronoi_gdf = gpd.GeoDataFrame({
            'idx': list(region_polys.keys()),
            'geometry': list(region_polys.values()),
            'modo_transporte': nombre_modo
        }, crs=gdf_filtrado.crs)
        
        # Asignar índice para unir con los datos originales
        voronoi_gdf = voronoi_gdf.set_index('idx')
        
        # Añadir columnas del gdf_filtrado directamente por índice
        columnas_a_unir = [c for c in gdf_filtrado.columns if c != 'geometry']
        for col in columnas_a_unir:
            voronoi_gdf[col] = gdf_filtrado[col]
            
        # Calcular métricas básicas
        voronoi_gdf['area_km2'] = voronoi_gdf.geometry.area / 1e6
        
        print(f"    ✓ {len(voronoi_gdf)} regiones generadas")
        print(f"    ✓ Área promedio: {voronoi_gdf['area_km2'].mean():.2f} km²")
        
        return voronoi_gdf
        
    except Exception as e:
        print(f"    ✗ Error generando Voronoi: {e}")
        return None

# ==========================================
# 5. GENERAR VORONOI POR MODO
# ==========================================
print("\n[3/4] Generando diagramas de Voronoi por modo...")

modos_interes = ['Metro', 'Autobús/CC', 'Góndola/Cablebús', 'Tranvía/Ligero', 'Tren']
resultados_voronoi = {}

for modo in modos_interes:
    gdf_modo = gdf_paradas[gdf_paradas['modo_transporte'] == modo].copy()
    
    if len(gdf_modo) > 0:
        voronoi = generar_voronoi_modo(gdf_modo, modo, area_estudio)
        if voronoi is not None:
            resultados_voronoi[modo] = voronoi

# ==========================================
# 6. GENERAR VORONOI MULTIMODAL
# ==========================================
print("\n[4/4] Generando diagrama multimodal (todos los modos)...")

# Combinar todos los modos para análisis multimodal
gdf_todos = gdf_paradas[gdf_paradas['modo_transporte'].isin(modos_interes)].copy()
voronoi_multimodal = generar_voronoi_modo(gdf_todos, 'Multimodal', area_estudio)

if voronoi_multimodal is not None:
    resultados_voronoi['Multimodal'] = voronoi_multimodal

# ==========================================
# 7. GUARDAR RESULTADOS
# ==========================================
print("\n" + "=" * 60)
print("GUARDANDO RESULTADOS")
print("=" * 60)

for modo, voronoi_gdf in resultados_voronoi.items():
    # Nombre de archivo seguro
    nombre_seguro = modo.replace('/', '_').replace(' ', '_')
    
    # Guardar GeoJSON
    archivo_salida = RESULTADOS_DIR / f"voronoi_{nombre_seguro}.geojson"
    voronoi_gdf.to_file(archivo_salida, driver='GeoJSON')
    print(f"✓ {modo}: {archivo_salida.name}")

# ==========================================
# 8. RESUMEN FINAL
# ==========================================
print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)

for modo, voronoi_gdf in resultados_voronoi.items():
    print(f"\n{modo}:")
    print(f"  • Regiones: {len(voronoi_gdf)}")
    print(f"  • Área total: {voronoi_gdf['area_km2'].sum():.2f} km²")
    print(f"  • Área promedio: {voronoi_gdf['area_km2'].mean():.2f} km²")
    print(f"  • Área mínima: {voronoi_gdf['area_km2'].min():.2f} km²")
    print(f"  • Área máxima: {voronoi_gdf['area_km2'].max():.2f} km²")

print("\n✓ Script completado exitosamente")
