"""
voronoi_04_desiertos_equidad.py
Proyecto Verano Delfín 2026 - Accesibilidad al AICM
Autor: Roberto Rojas Avila | Co-investigadora: Janine Flores

Descripción: 
Detecta desiertos de transporte y analiza equidad por alcaldía.
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTADOS_DIR = BASE_DIR / "datos" / "resultados"
VISUALIZACIONES_DIR = BASE_DIR / "visualizaciones"
VORONOI_DIR = VISUALIZACIONES_DIR / "voronoi"

VORONOI_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("VORONOI - SCRIPT 4: DESIERTOS Y EQUIDAD")
print("=" * 60)

# ==========================================
# 2. CARGAR DATOS
# ==========================================
print("\n[1/6] Cargando polígonos de Voronoi multimodal...")

archivo_voronoi = RESULTADOS_DIR / 'voronoi_Multimodal.geojson'
gdf_voronoi = gpd.read_file(archivo_voronoi)
print(f"✓ {len(gdf_voronoi)} polígonos cargados")

print("\n[2/6] Cargando datos de paradas...")
archivo_paradas = RESULTADOS_DIR / 'paradas_con_modo_utm.geojson'
gdf_paradas = gpd.read_file(archivo_paradas)
print(f"✓ {len(gdf_paradas)} paradas cargadas")

# ==========================================
# 3. DETECCIÓN DE DESIERTOS DE TRANSPORTE
# ==========================================
print("\n[3/6] Identificando desiertos de transporte...")

# Definir umbrales para desiertos
# Umbral 1: Área grande (mayor a 2 km² en zona urbana)
UMBRAL_AREA_GRANDE = 2.0  # km²

# Calcular percentiles para análisis más robusto
percentil_75 = gdf_voronoi['area_km2'].quantile(0.75)
percentil_90 = gdf_voronoi['area_km2'].quantile(0.90)
percentil_95 = gdf_voronoi['area_km2'].quantile(0.95)

print(f"  • Percentil 75: {percentil_75:.2f} km²")
print(f"  • Percentil 90: {percentil_90:.2f} km²")
print(f"  • Percentil 95: {percentil_95:.2f} km²")

# Clasificar polígonos por nivel de cobertura
gdf_voronoi['nivel_cobertura'] = pd.cut(
    gdf_voronoi['area_km2'],
    bins=[0, 0.5, 1.0, 2.0, 5.0, gdf_voronoi['area_km2'].max()],
    labels=['Excelente', 'Buena', 'Regular', 'Deficiente', 'Desierto'],
    include_lowest=True
)

# Identificar desiertos (área > 2 km²)
desiertos = gdf_voronoi[gdf_voronoi['area_km2'] >= UMBRAL_AREA_GRANDE].copy()
print(f"\n✓ Identificados {len(desiertos)} desiertos de transporte")
print(f"  • Área total de desiertos: {desiertos['area_km2'].sum():.2f} km²")
print(f"  • Esto representa {(desiertos['area_km2'].sum() / gdf_voronoi['area_km2'].sum() * 100):.1f}% del área de estudio")

# Guardar desiertos
archivo_desiertos = RESULTADOS_DIR / 'desiertos_transporte.geojson'
desiertos.to_file(archivo_desiertos, driver='GeoJSON')
print(f"✓ Desiertos guardados en: {archivo_desiertos.name}")

# ==========================================
# 4. ANÁLISIS POR ALCALDÍA
# ==========================================
print("\n[4/6] Analizando cobertura por alcaldía...")

# Cargar datos de paradas con alcaldía
archivo_alcaldias = RESULTADOS_DIR / 'paradas_con_alcaldia.csv'

if archivo_alcaldias.exists():
    df_alcaldias = pd.read_csv(archivo_alcaldias)
    
    # Identificar columnas de alcaldía
    col_alcaldia = None
    for col in df_alcaldias.columns:
        if 'alcaldia' in col.lower() or 'municipio' in col.lower() or 'delegacion' in col.lower():
            col_alcaldia = col
            break
    
    if col_alcaldia:
        print(f"  • Columna de alcaldía identificada: {col_alcaldia}")
        
        # Contar paradas por alcaldía
        paradas_por_alcaldia = df_alcaldias[col_alcaldia].value_counts().reset_index()
        paradas_por_alcaldia.columns = ['alcaldia', 'num_paradas']
        
        print(f"\n  Top 5 alcaldías con más paradas:")
        for _, row in paradas_por_alcaldia.head(5).iterrows():
            print(f"    • {row['alcaldia']}: {row['num_paradas']} paradas")
        
        # Guardar resumen por alcaldía
        archivo_resumen = RESULTADOS_DIR / 'cobertura_por_alcaldia.csv'
        paradas_por_alcaldia.to_csv(archivo_resumen, index=False)
        print(f"\n✓ Resumen por alcaldía guardado: {archivo_resumen.name}")
    else:
        print("  ⚠ No se encontró columna de alcaldía")
        paradas_por_alcaldia = None
else:
    print(f"  ⚠ Archivo {archivo_alcaldias.name} no encontrado")
    paradas_por_alcaldia = None

# ==========================================
# 5. MAPA DE DESIERTOS DE TRANSPORTE
# ==========================================
print("\n[5/6] Generando mapa de desiertos de transporte...")

fig, ax = plt.subplots(figsize=(14, 12))

# Mapa base: todos los polígonos en gris claro
gdf_voronoi.plot(
    ax=ax,
    color='lightgray',
    edgecolor='gray',
    linewidth=0.2,
    alpha=0.3
)

# Resaltar desiertos en rojo
desiertos.plot(
    ax=ax,
    color='red',
    edgecolor='darkred',
    linewidth=0.5,
    alpha=0.6,
    label=f'Desiertos de transporte ({len(desiertos)})'
)

# Marpar las paradas como puntos azules
gdf_paradas.plot(
    ax=ax,
    color='blue',
    markersize=1,
    alpha=0.3
)

ax.set_title(
    'Desiertos de Transporte Público en la CDMX\nÁreas con Cobertura Deficiente (>2 km² por parada)',
    fontsize=16,
    fontweight='bold',
    pad=20
)
ax.set_xlabel('Coordenada Este (m)', fontsize=12)
ax.set_ylabel('Coordenada Norte (m)', fontsize=12)
ax.legend(fontsize=12, loc='upper right')

# Agregar estadísticas
stats_text = f"Total de desiertos: {len(desiertos)}\n"
stats_text += f"Área afectada: {desiertos['area_km2'].sum():.1f} km²\n"
stats_text += f"Área promedio desierto: {desiertos['area_km2'].mean():.2f} km²"

ax.text(
    0.02, 0.02, stats_text,
    transform=ax.transAxes,
    fontsize=10,
    verticalalignment='bottom',
    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8)
)

plt.tight_layout()

ruta_desiertos_mapa = VORONOI_DIR / 'desiertos_transporte_mapa.png'
plt.savefig(ruta_desiertos_mapa, dpi=300, bbox_inches='tight')
plt.close()
print(f"✓ Mapa de desiertos creado: {ruta_desiertos_mapa.name}")

# ==========================================
# 6. MAPA DE EQUIDAD POR NIVEL DE COBERTURA
# ==========================================
print("\n[6/6] Generando mapa de equidad por nivel de cobertura...")

fig, ax = plt.subplots(figsize=(14, 12))

# Colormap personalizado: verde (excelente) a rojo (desierto)
colors = ['green', 'lightgreen', 'yellow', 'orange', 'red']
cmap = LinearSegmentedColormap.from_list('cobertura', colors, N=256)

gdf_voronoi.plot(
    column='nivel_cobertura',
    ax=ax,
    categorical=True,
    legend=True,
    cmap=cmap,
    edgecolor='black',
    linewidth=0.3,
    alpha=0.7,
    legend_kwds={
        'loc': 'upper right',
        'fontsize': 10,
        'title': 'Nivel de Cobertura'
    }
)

ax.set_title(
    'Mapa de Equidad en Cobertura de Transporte Público\nCDMX - Clasificación por Área de Influencia',
    fontsize=16,
    fontweight='bold',
    pad=20
)
ax.set_xlabel('Coordenada Este (m)', fontsize=12)
ax.set_ylabel('Coordenada Norte (m)', fontsize=12)

# Estadísticas por nivel
nivel_counts = gdf_voronoi['nivel_cobertura'].value_counts()
stats_text = "Distribución de cobertura:\n"
for nivel in ['Excelente', 'Buena', 'Regular', 'Deficiente', 'Desierto']:
    if nivel in nivel_counts.index:
        count = nivel_counts[nivel]
        pct = count / len(gdf_voronoi) * 100
        stats_text += f"• {nivel}: {count} zonas ({pct:.1f}%)\n"

ax.text(
    0.02, 0.02, stats_text,
    transform=ax.transAxes,
    fontsize=9,
    verticalalignment='bottom',
    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
)

plt.tight_layout()

ruta_equidad_mapa = VORONOI_DIR / 'equidad_cobertura_mapa.png'
plt.savefig(ruta_equidad_mapa, dpi=300, bbox_inches='tight')
plt.close()
print(f"✓ Mapa de equidad creado: {ruta_equidad_mapa.name}")

# ==========================================
# 7. RESUMEN FINAL
# ==========================================
print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)

print("\n📊 Estadísticas generales:")
print(f"  • Total de polígonos analizados: {len(gdf_voronoi)}")
print(f"  • Área total de estudio: {gdf_voronoi['area_km2'].sum():.2f} km²")
print(f"  • Área promedio: {gdf_voronoi['area_km2'].mean():.2f} km²")
print(f"  • Área mediana: {gdf_voronoi['area_km2'].median():.2f} km²")

print("\n🏜️ Desiertos de transporte:")
print(f"  • Zonas identificadas: {len(desiertos)}")
print(f"  • Área total afectada: {desiertos['area_km2'].sum():.2f} km²")
print(f"  • Porcentaje del área total: {(desiertos['area_km2'].sum() / gdf_voronoi['area_km2'].sum() * 100):.1f}%")

print("\n📁 Archivos generados:")
print(f"  • {archivo_desiertos.name}")
print(f"  • {ruta_desiertos_mapa.name}")
print(f"  • {ruta_equidad_mapa.name}")
if paradas_por_alcaldia is not None:
    print(f"  • cobertura_por_alcaldia.csv")

print("\n✓ Script completado exitosamente")
