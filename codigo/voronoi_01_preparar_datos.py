"""
voronoi_01_preparar_datos.py
Proyecto Verano Delfín 2026 - Accesibilidad al AICM
Autor: Roberto Rojas Avila | Co-investigadora: Janine Flores

Descripción: 
Carga los archivos GTFS, cruza la información para etiquetar cada parada 
con su modo de transporte, proyecta a UTM y guarda el resultado.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
GTFS_DIR = BASE_DIR / "datos" / "gtfs"
RESULTADOS_DIR = BASE_DIR / "datos" / "resultados"

# Asegurar que exista la carpeta de resultados
RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("VORONOI - SCRIPT 1: PREPARACIÓN DE DATOS")
print("=" * 60)
print(f"Directorio GTFS: {GTFS_DIR}")
print(f"Directorio resultados: {RESULTADOS_DIR}")

# ==========================================
# 2. CARGAR ARCHIVOS GTFS
# ==========================================
print("\n[1/5] Cargando archivos GTFS...")

# Cargar stops.txt
stops = pd.read_csv(GTFS_DIR / "stops.txt")
print(f"✓ stops.txt: {len(stops)} paradas")

# Cargar stop_times.txt
stop_times = pd.read_csv(GTFS_DIR / "stop_times.txt")
print(f"✓ stop_times.txt: {len(stop_times)} registros")

# Cargar trips.txt
trips = pd.read_csv(GTFS_DIR / "trips.txt")
print(f"✓ trips.txt: {len(trips)} viajes")

# Cargar routes.txt
routes = pd.read_csv(GTFS_DIR / "routes.txt")
print(f"✓ routes.txt: {len(routes)} rutas")

# ==========================================
# 3. CRUZAR DATOS PARA IDENTIFICAR MODOS
# ==========================================
print("\n[2/5] Cruzando datos para identificar modos de transporte...")

# Paso 1: Unir stop_times con trips (para obtener route_id de cada parada)
print("  → Uniendo stop_times con trips...")
paradas_con_rutas = stop_times.merge(
    trips[['trip_id', 'route_id']], 
    on='trip_id', 
    how='left'
)
print(f"    Resultado: {len(paradas_con_rutas)} registros")

# Paso 2: Unir con routes (para obtener route_type)
print("  → Uniendo con routes para obtener route_type...")
paradas_con_tipo = paradas_con_rutas.merge(
    routes[['route_id', 'route_type', 'route_short_name', 'route_long_name']], 
    on='route_id', 
    how='left'
)
print(f"    Resultado: {len(paradas_con_tipo)} registros")

# Paso 3: Obtener paradas únicas con su modo
print("  → Obteniendo paradas únicas con su modo...")
paradas_unicas = paradas_con_tipo.groupby('stop_id').agg({
    'route_type': lambda x: x.mode()[0] if len(x) > 0 else None,
    'route_short_name': lambda x: x.mode()[0] if len(x) > 0 else None
}).reset_index()

print(f"✓ {len(paradas_unicas)} paradas únicas identificadas")

# ==========================================
# 4. ETIQUETAR MODOS DE TRANSPORTE
# ==========================================
print("\n[3/5] Etiquetando modos de transporte...")

# Mapeo de route_type a nombres de modos (estándar GTFS)
mapeo_modos = {
    0: 'Tranvía/Ligero',
    1: 'Metro',
    2: 'Tren',
    3: 'Autobús/CC',
    4: 'Ferry',
    5: 'Teleférico',
    6: 'Góndola/Cablebús',
    7: 'Funicular',
    11: 'Trolebús'
}

paradas_unicas['modo_transporte'] = paradas_unicas['route_type'].map(mapeo_modos)
paradas_unicas['modo_transporte'] = paradas_unicas['modo_transporte'].fillna('Desconocido')

# Mostrar resumen
print("\nResumen de modos de transporte:")
resumen_modos = paradas_unicas['modo_transporte'].value_counts()
for modo, cantidad in resumen_modos.items():
    print(f"  • {modo}: {cantidad} paradas")

# ==========================================
# 5. UNIR CON DATOS COMPLETOS DE PARADAS
# ==========================================
print("\n[4/5] Uniendo con datos completos de paradas...")

# Unir con stops.txt original para obtener coordenadas y nombres
paradas_completas = stops.merge(
    paradas_unicas[['stop_id', 'modo_transporte', 'route_short_name']], 
    on='stop_id', 
    how='left'
)

print(f"✓ {len(paradas_completas)} paradas con modo de transporte")

# ==========================================
# 6. PROYECTAR A UTM
# ==========================================
print("\n[5/5] Proyectando a UTM (EPSG:32614)...")

# Crear GeoDataFrame
gdf = gpd.GeoDataFrame(
    paradas_completas,
    geometry=gpd.points_from_xy(paradas_completas.stop_lon, paradas_completas.stop_lat),
    crs="EPSG:4326"
)

# Proyectar a UTM
gdf_utm = gdf.to_crs(epsg=32614)
print(f"✓ Datos proyectados a UTM (metros)")

# ==========================================
# 7. GUARDAR RESULTADOS
# ==========================================
print("\n" + "=" * 60)
print("GUARDANDO RESULTADOS")
print("=" * 60)

# Guardar CSV con coordenadas UTM
output_csv = RESULTADOS_DIR / "paradas_con_modo_utm.csv"
gdf_utm.to_csv(output_csv, index=False)
print(f"✓ CSV guardado: {output_csv}")

# Guardar GeoJSON (útil para análisis espacial posterior)
output_geojson = RESULTADOS_DIR / "paradas_con_modo_utm.geojson"
gdf_utm.to_file(output_geojson, driver='GeoJSON')
print(f"✓ GeoJSON guardado: {output_geojson}")

# ==========================================
# 8. RESUMEN FINAL
# ==========================================
print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
print(f"Total de paradas: {len(gdf_utm)}")
print(f"Modos de transporte identificados: {gdf_utm['modo_transporte'].nunique()}")
print(f"\nDistribución:")
print(gdf_utm['modo_transporte'].value_counts())
print("\n✓ Script completado exitosamente")
print(f"✓ Archivos disponibles en: {RESULTADOS_DIR}")
