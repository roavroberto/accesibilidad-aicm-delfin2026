"""
voronoi_05_analisis_integrado.py
Proyecto Verano Delfín 2026 - Accesibilidad al AICM
Autor: Roberto Rojas Avila | Co-investigadora: Janine Flores

Descripción: 
Análisis integrado de desiertos de transporte por alcaldía con métricas de equidad.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
DATOS_EXTERNOS = BASE_DIR / "datos" / "externos"
VISUALIZACIONES_DIR = BASE_DIR / "visualizaciones"
VORONOI_DIR = VISUALIZACIONES_DIR / "voronoi"

VORONOI_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("VORONOI - SCRIPT 5: ANÁLISIS INTEGRADO")
print("=" * 60)

# ==========================================
# 2. CARGAR DATOS
# ==========================================
print("\n[1/6] Cargando desiertos de transporte...")

archivo_desiertos = RESULTADOS_DIR / 'desiertos_transporte.geojson'
gdf_desiertos = gpd.read_file(archivo_desiertos)
print(f"✓ {len(gdf_desiertos)} desiertos cargados")

print("\n[2/6] Cargando datos de alcaldías...")

# Intentar cargar shapefiles de alcaldías
archivos_alcaldias = [
    DATOS_EXTERNOS / "alcaldias_cdmx.geojson",
    DATOS_EXTERNOS / "alcaldias_cdmx.shp",
    RESULTADOS_DIR / "alcaldias_cdmx.geojson",
    RESULTADOS_DIR / "alcaldias_cdmx.shp"
]

gdf_alcaldias = None
for archivo in archivos_alcaldias:
    if archivo.exists():
        try:
            gdf_alcaldias = gpd.read_file(archivo)
            print(f"✓ Alcaldías cargadas desde: {archivo.name}")
            break
        except Exception as e:
            print(f"  ⚠ Error cargando {archivo.name}: {e}")

if gdf_alcaldias is None:
    print("  ⚠ No se encontraron shapefiles de alcaldías")
    print("  → Se usará análisis basado en paradas")
    
    # Cargar datos de paradas con alcaldía como alternativa
    archivo_paradas_alc = RESULTADOS_DIR / 'paradas_con_alcaldia.csv'
    if archivo_paradas_alc.exists():
        df_paradas_alc = pd.read_csv(archivo_paradas_alc)
        print(f"✓ Datos de paradas con alcaldía cargados: {len(df_paradas_alc)} registros")
    else:
        df_paradas_alc = None

# ==========================================
# 3. FUNCIÓN PARA CALCULAR ÍNDICE DE GINI
# ==========================================
def calcular_gini(valores):
    """
    Calcula el coeficiente de Gini para medir desigualdad
    0 = perfecta igualdad, 1 = perfecta desigualdad
    """
    valores = np.array(valores)
    valores = valores[valores > 0]  # Eliminar ceros
    
    if len(valores) == 0:
        return 0
    
    valores_ordenados = np.sort(valores)
    n = len(valores_ordenados)
    
    # Fórmula del coeficiente de Gini
    indices = np.arange(1, n + 1)
    gini = (np.sum((2 * indices - n - 1) * valores_ordenados)) / (n * np.sum(valores_ordenados))
    
    return gini

# ==========================================
# 4. ANÁLISIS ESPACIAL DE DESIERTOS POR ALCALDÍA
# ==========================================
print("\n[3/6] Analizando desiertos por alcaldía...")

if gdf_alcaldias is not None:
    # Asegurar que ambos GeoDataFrames tengan el mismo CRS
    gdf_desiertos = gdf_desiertos.to_crs(gdf_alcaldias.crs)
    
    # Spatial join: intersectar desiertos con alcaldías
    print("  → Realizando intersección espacial...")
    desiertos_con_alcaldia = gpd.sjoin(
        gdf_desiertos, 
        gdf_alcaldias, 
        how='left', 
        predicate='intersects'
    )
    
    # Identificar columna de nombre de alcaldía
    col_alcaldia = None
    for col in desiertos_con_alcaldia.columns:
        if 'nom' in col.lower() and 'geo' in col.lower():
            col_alcaldia = col
            break
        elif 'alcaldia' in col.lower():
            col_alcaldia = col
            break
        elif 'municipio' in col.lower():
            col_alcaldia = col
            break
    
    if col_alcaldia is None:
        # Intentar con columnas comunes
        posibles = ['NOMGEO', 'CVE_ENT', 'NOM_ENT', 'alcaldia', 'municipio']
        for col in posibles:
            if col in desiertos_con_alcaldia.columns:
                col_alcaldia = col
                break
    
    if col_alcaldia:
        print(f"  • Columna de alcaldía: {col_alcaldia}")
        
        # Agregar por alcaldía
        resumen_alcaldias = desiertos_con_alcaldia.groupby(col_alcaldia).agg({
            'area_km2': ['count', 'sum', 'mean'],
            'geometry': 'first'
        }).round(2)
        
        resumen_alcaldias.columns = ['num_desiertos', 'area_total_km2', 'area_promedio_km2', 'geometry']
        resumen_alcaldias = gpd.GeoDataFrame(resumen_alcaldias, crs=gdf_alcaldias.crs)
        
        # Ordenar por área total de desiertos
        resumen_alcaldias = resumen_alcaldias.sort_values('area_total_km2', ascending=False)
        
        print("\n  Top 5 alcaldías con más área de desiertos:")
        for idx, row in resumen_alcaldias.head(5).iterrows():
            print(f"    • {idx}: {row['num_desiertos']} desiertos, {row['area_total_km2']:.2f} km²")
        
        # Calcular índice de Gini
        gini_area = calcular_gini(resumen_alcaldias['area_total_km2'])
        gini_num = calcular_gini(resumen_alcaldias['num_desiertos'])
        
        print(f"\n  📊 ÍNDICES DE EQUIDAD:")
        print(f"    • Gini (área de desiertos): {gini_area:.3f}")
        print(f"    • Gini (número de desiertos): {gini_num:.3f}")
        print(f"    → Interpretación: 0=igualdad perfecta, 1=desigualdad máxima")
        
        if gini_area > 0.4:
            print(f"    ⚠ ALTA DESIGUALDAD en distribución de desiertos")
        elif gini_area > 0.25:
            print(f"    ⚠ DESIGUALDAD MODERADA en distribución de desiertos")
        else:
            print(f"    ✓ Distribución relativamente equitativa")
        
        # Guardar resumen
        archivo_resumen = RESULTADOS_DIR / 'desiertos_por_alcaldia.csv'
        resumen_alcaldias[['num_desiertos', 'area_total_km2', 'area_promedio_km2']].to_csv(archivo_resumen)
        print(f"\n✓ Resumen guardado: {archivo_resumen.name}")
        
        # ==========================================
        # 5. MAPA DE DESIERTOS POR ALCALDÍA
        # ==========================================
        print("\n[4/6] Generando mapa de desiertos por alcaldía...")
        
        fig, ax = plt.subplots(figsize=(14, 12))
        
        # Dibujar alcaldías como fondo
        gdf_alcaldias.plot(
            ax=ax,
            color='lightgray',
            edgecolor='gray',
            linewidth=0.5,
            alpha=0.5
        )
        
        # Dibujar desiertos coloreados por alcaldía
        if 'area_total_km2' in resumen_alcaldias.columns:
            resumen_alcaldias.plot(
                ax=ax,
                column='area_total_km2',
                cmap='Reds',
                edgecolor='black',
                linewidth=0.5,
                alpha=0.7,
                legend=True,
                legend_kwds={'label': 'Área de desiertos (km²)', 'orientation': 'vertical'}
            )
        
        # Agregar etiquetas de alcaldías
        for idx, row in resumen_alcaldias.iterrows():
            if row['area_total_km2'] > 100:  # Solo etiquetar alcaldías con muchos desiertos
                centroide = row.geometry.centroid
                ax.text(
                    centroide.x, 
                    centroide.y, 
                    f"{idx}\n{row['area_total_km2']:.0f} km²",
                    ha='center',
                    va='center',
                    fontsize=8,
                    fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
                )
        
        ax.set_title(
            'Desiertos de Transporte Público por Alcaldía\nCDMX - Áreas con Cobertura Deficiente',
            fontsize=16,
            fontweight='bold',
            pad=20
        )
        ax.set_xlabel('Coordenada Este (m)', fontsize=12)
        ax.set_ylabel('Coordenada Norte (m)', fontsize=12)
        
        # Estadísticas en el mapa
        stats_text = f"Total desiertos: {len(gdf_desiertos)}\n"
        stats_text += f"Área total: {gdf_desiertos['area_km2'].sum():.1f} km²\n"
        stats_text += f"Índice Gini: {gini_area:.3f}"
        
        ax.text(
            0.02, 0.02, stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8)
        )
        
        plt.tight_layout()
        
        ruta_mapa = VORONOI_DIR / 'desiertos_por_alcaldia.png'
        plt.savefig(ruta_mapa, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Mapa creado: {ruta_mapa.name}")
        
        # ==========================================
        # 6. GRÁFICO DE BARRAS: TOP ALCALDÍAS
        # ==========================================
        print("\n[5/6] Generando gráfico de barras...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Gráfico 1: Número de desiertos por alcaldía
        top_10 = resumen_alcaldias.head(10)
        ax1.barh(range(len(top_10)), top_10['num_desiertos'], color='coral', edgecolor='black')
        ax1.set_yticks(range(len(top_10)))
        ax1.set_yticklabels(top_10.index)
        ax1.set_xlabel('Número de Desiertos', fontsize=11)
        ax1.set_title('Top 10 Alcaldías con Más Desiertos\n(por cantidad)', fontsize=12, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Agregar valores en las barras
        for i, (idx, row) in enumerate(top_10.iterrows()):
            ax1.text(row['num_desiertos'] + 0.5, i, str(int(row['num_desiertos'])),
                    va='center', fontsize=9)
        
        # Gráfico 2: Área total de desiertos por alcaldía
        ax2.barh(range(len(top_10)), top_10['area_total_km2'], color='salmon', edgecolor='black')
        ax2.set_yticks(range(len(top_10)))
        ax2.set_yticklabels(top_10.index)
        ax2.set_xlabel('Área Total de Desiertos (km²)', fontsize=11)
        ax2.set_title('Top 10 Alcaldías con Más Desiertos\n(por área total)', fontsize=12, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # Agregar valores en las barras
        for i, (idx, row) in enumerate(top_10.iterrows()):
            ax2.text(row['area_total_km2'] + 10, i, f"{row['area_total_km2']:.0f} km²",
                    va='center', fontsize=9)
        
        plt.tight_layout()
        
        ruta_barras = VORONOI_DIR / 'desiertos_alcaldias_barras.png'
        plt.savefig(ruta_barras, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Gráfico de barras creado: {ruta_barras.name}")
        
    else:
        print("  ⚠ No se pudo identificar columna de alcaldía")
        resumen_alcaldias = None

else:
    print("\n[4/6] Saltando análisis espacial (sin shapefiles de alcaldías)")
    print("  → Generando análisis alternativo basado en paradas...")
    
    if df_paradas_alc is not None:
        # Análisis simple basado en conteo de paradas
        col_alcaldia = None
        for col in df_paradas_alc.columns:
            if 'alcaldia' in col.lower() or 'municipio' in col.lower():
                col_alcaldia = col
                break
        
        if col_alcaldia:
            resumen_paradas = df_paradas_alc.groupby(col_alcaldia).size().reset_index(name='num_paradas')
            resumen_paradas = resumen_paradas.sort_values('num_paradas', ascending=False)
            
            print("\n  Top 10 alcaldías por número de paradas:")
            for _, row in resumen_paradas.head(10).iterrows():
                print(f"    • {row[col_alcaldia]}: {row['num_paradas']} paradas")
            
            # Gráfico de barras
            fig, ax = plt.subplots(figsize=(10, 6))
            top_10_paradas = resumen_paradas.head(10)
            ax.barh(range(len(top_10_paradas)), top_10_paradas['num_paradas'], color='skyblue', edgecolor='black')
            ax.set_yticks(range(len(top_10_paradas)))
            ax.set_yticklabels(top_10_paradas[col_alcaldia])
            ax.set_xlabel('Número de Paradas', fontsize=11)
            ax.set_title('Top 10 Alcaldías por Número de Paradas', fontsize=12, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            
            ruta_barras = VORONOI_DIR / 'paradas_por_alcaldia.png'
            plt.savefig(ruta_barras, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"\n✓ Gráfico creado: {ruta_barras.name}")
    
    resumen_alcaldias = None

# ==========================================
# 7. MAPA FINAL INTEGRADO
# ==========================================
print("\n[6/6] Generando mapa final integrado...")

fig, axes = plt.subplots(2, 2, figsize=(18, 16))

# Panel 1: Mapa de cobertura general
ax1 = axes[0, 0]
archivo_voronoi = RESULTADOS_DIR / 'voronoi_Multimodal.geojson'
gdf_voronoi = gpd.read_file(archivo_voronoi)

gdf_voronoi.plot(
    ax=ax1,
    column='area_km2',
    cmap='RdYlGn_r',
    edgecolor='black',
    linewidth=0.2,
    alpha=0.6,
    legend=True,
    legend_kwds={'label': 'Área (km²)', 'shrink': 0.8}
)
ax1.set_title('Cobertura General de Transporte', fontsize=12, fontweight='bold')
ax1.set_xlabel('Este (m)')
ax1.set_ylabel('Norte (m)')

# Panel 2: Desiertos resaltados
ax2 = axes[0, 1]
gdf_voronoi.plot(ax=ax2, color='lightgray', edgecolor='gray', linewidth=0.2, alpha=0.3)
gdf_desiertos.plot(ax=ax2, color='red', edgecolor='darkred', linewidth=0.5, alpha=0.7)
ax2.set_title(f'Desiertos de Transporte ({len(gdf_desiertos)} zonas)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Este (m)')
ax2.set_ylabel('Norte (m)')

# Panel 3: Gráfico de distribución de áreas
ax3 = axes[1, 0]
ax3.hist(gdf_voronoi['area_km2'], bins=100, color='steelblue', edgecolor='black', alpha=0.7)
ax3.axvline(gdf_voronoi['area_km2'].median(), color='green', linestyle='--', label=f'Mediana: {gdf_voronoi["area_km2"].median():.2f} km²')
ax3.axvline(gdf_voronoi['area_km2'].mean(), color='red', linestyle='--', label=f'Media: {gdf_voronoi["area_km2"].mean():.2f} km²')
ax3.set_xlabel('Área de Influencia (km²)', fontsize=11)
ax3.set_ylabel('Frecuencia', fontsize=11)
ax3.set_title('Distribución de Áreas de Influencia', fontsize=12, fontweight='bold')
ax3.legend()
ax3.grid(alpha=0.3)

# Panel 4: Resumen estadístico
ax4 = axes[1, 1]
ax4.axis('off')

resumen_text = "RESUMEN EJECUTIVO\n"
resumen_text += "=" * 50 + "\n\n"
resumen_text += f"📍 Área total de estudio: {gdf_voronoi['area_km2'].sum():.0f} km²\n"
resumen_text += f"🚌 Total de paradas analizadas: {len(gdf_voronoi)}\n"
resumen_text += f"📊 Área promedio por parada: {gdf_voronoi['area_km2'].mean():.2f} km²\n"
resumen_text += f"📊 Área mediana: {gdf_voronoi['area_km2'].median():.2f} km²\n\n"
resumen_text += f"🏜️ DESIERTOS DE TRANSPORTE:\n"
resumen_text += f"  • Zonas identificadas: {len(gdf_desiertos)}\n"
resumen_text += f"  • Área total afectada: {gdf_desiertos['area_km2'].sum():.0f} km²\n"
resumen_text += f"  • % del área total: {(gdf_desiertos['area_km2'].sum() / gdf_voronoi['area_km2'].sum() * 100):.1f}%\n"

if resumen_alcaldias is not None and 'gini_area' in locals():
    resumen_text += f"\n📈 ÍNDICE DE EQUIDAD:\n"
    resumen_text += f"  • Gini (área): {gini_area:.3f}\n"
    resumen_text += f"  • Interpretación: "
    if gini_area > 0.4:
        resumen_text += "ALTA DESIGUALDAD"
    elif gini_area > 0.25:
        resumen_text += "Desigualdad moderada"
    else:
        resumen_text += "Distribución equitativa"

ax4.text(0.1, 0.9, resumen_text, transform=ax4.transAxes,
        fontsize=11, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

plt.suptitle(
    'Análisis Integrado de Accesibilidad al Transporte Público - CDMX\nPrograma Verano Delfín 2026',
    fontsize=16,
    fontweight='bold',
    y=0.98
)

plt.tight_layout(rect=[0, 0, 1, 0.97])

ruta_final = VORONOI_DIR / 'analisis_integrado_final.png'
plt.savefig(ruta_final, dpi=300, bbox_inches='tight')
plt.close()
print(f"✓ Mapa final integrado creado: {ruta_final.name}")

# ==========================================
# 8. RESUMEN FINAL
# ==========================================
print("\n" + "=" * 60)
print("RESUMEN FINAL DEL ANÁLISIS")
print("=" * 60)

print("\n📊 RESULTADOS PRINCIPALES:")
print(f"  • Total de polígonos analizados: {len(gdf_voronoi)}")
print(f"  • Área de estudio: {gdf_voronoi['area_km2'].sum():.2f} km²")
print(f"  • Desiertos identificados: {len(gdf_desiertos)}")
print(f"  • Área de desiertos: {gdf_desiertos['area_km2'].sum():.2f} km² ({(gdf_desiertos['area_km2'].sum() / gdf_voronoi['area_km2'].sum() * 100):.1f}%)")

if resumen_alcaldias is not None and 'gini_area' in locals():
    print(f"\n📈 MÉTRICAS DE EQUIDAD:")
    print(f"  • Índice de Gini (área): {gini_area:.3f}")
    print(f"  • Índice de Gini (cantidad): {gini_num:.3f}")

print("\n📁 ARCHIVOS GENERADOS:")
print(f"  • {archivo_resumen.name if 'archivo_resumen' in locals() else 'desiertos_por_alcaldia.csv'}")
print(f"  • desiertos_por_alcaldia.png")
print(f"  • desiertos_alcaldias_barras.png")
print(f"  • analisis_integrado_final.png")

print("\n" + "=" * 60)
print("✓ ANÁLISIS DE VORONOI COMPLETADO EXITOSAMENTE")
print("=" * 60)
print("\n📍 Todos los resultados están disponibles en:")
print(f"   Datos: {RESULTADOS_DIR}")
print(f"   Mapas: {VORONOI_DIR}")
print("\n🎯 Próximos pasos sugeridos:")
print("   1. Integrar estos mapas en tu reporte final")
print("   2. Cruzar con datos socioeconómicos para análisis de equidad")
print("   3. Proponer ubicaciones para nuevas paradas en zonas desérticas")
