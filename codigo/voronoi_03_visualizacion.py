"""
voronoi_03_visualizacion.py
Proyecto Verano Delfín 2026 - Accesibilidad al AICM
Autor: Roberto Rojas Avila | Co-investigadora: Janine Flores

Descripción: 
Genera visualizaciones de los diagramas de Voronoi para cada modo de transporte.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.style.use('seaborn-v0_8-darkgrid')

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTADOS_DIR = BASE_DIR / "datos" / "resultados"
VISUALIZACIONES_DIR = BASE_DIR / "visualizaciones"
VORONOI_DIR = VISUALIZACIONES_DIR / "voronoi"

# Crear carpeta voronoi si no existe
VORONOI_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("VORONOI - SCRIPT 3: VISUALIZACIÓN")
print("=" * 60)

# ==========================================
# 2. CARGAR TODOS LOS ARCHIVOS VORONOI
# ==========================================
print("\n[1/4] Cargando polígonos de Voronoi...")

archivos_voronoi = {
    'Metro': RESULTADOS_DIR / 'voronoi_Metro.geojson',
    'Autobús/CC': RESULTADOS_DIR / 'voronoi_Autobús_CC.geojson',
    'Góndola/Cablebús': RESULTADOS_DIR / 'voronoi_Góndola_Cablebús.geojson',
    'Tranvía/Ligero': RESULTADOS_DIR / 'voronoi_Tranvía_Ligero.geojson',
    'Tren': RESULTADOS_DIR / 'voronoi_Tren.geojson',
    'Multimodal': RESULTADOS_DIR / 'voronoi_Multimodal.geojson'
}

datos_voronoi = {}
for modo, archivo in archivos_voronoi.items():
    if archivo.exists():
        gdf = gpd.read_file(archivo)
        datos_voronoi[modo] = gdf
        print(f"✓ {modo}: {len(gdf)} regiones cargadas")
    else:
        print(f"✗ {modo}: archivo no encontrado")

# ==========================================
# 3. FUNCIÓN PARA CREAR MAPA INDIVIDUAL
# ==========================================
def crear_mapa_individual(modo, gdf, carpeta_salida):
    """
    Crea un mapa individual de Voronoi coloreado por área
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Crear colormap personalizado (de áreas pequeñas a grandes)
    norm = mcolors.LogNorm(vmin=gdf['area_km2'].min(), vmax=gdf['area_km2'].max())
    
    # Graficar polígonos
    gdf.plot(
        column='area_km2',
        ax=ax,
        legend=True,
        cmap='RdYlGn_r',  # Rojo=áreas grandes (desiertos), Verde=áreas pequeñas (buena cobertura)
        norm=norm,
        edgecolor='black',
        linewidth=0.5,
        alpha=0.7,
        legend_kwds={
            'label': 'Área de influencia (km²)',
            'orientation': 'vertical',
            'shrink': 0.8
        }
    )
    
    # Configurar título y etiquetas
    ax.set_title(
        f'Diagrama de Voronoi - {modo}\nÁreas de Influencia por Estación',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    ax.set_xlabel('Coordenada Este (m)', fontsize=12)
    ax.set_ylabel('Coordenada Norte (m)', fontsize=12)
    
    # Estadísticas en el mapa
    stats_text = f"Regiones: {len(gdf)}\n"
    stats_text += f"Área promedio: {gdf['area_km2'].mean():.2f} km²\n"
    stats_text += f"Área total: {gdf['area_km2'].sum():.2f} km²"
    
    ax.text(
        0.02, 0.02, stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='bottom',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )
    
    plt.tight_layout()
    
    # Guardar
    nombre_seguro = modo.replace('/', '_').replace(' ', '_')
    ruta_salida = carpeta_salida / f'voronoi_{nombre_seguro}_areas.png'
    plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
    plt.close()
    
    return ruta_salida

# ==========================================
# 4. GENERAR MAPAS INDIVIDUALES
# ==========================================
print("\n[2/4] Generando mapas individuales...")

mapas_generados = []
for modo, gdf in datos_voronoi.items():
    if modo != 'Multimodal':  # Saltar multimodal para mapa individual
        ruta = crear_mapa_individual(modo, gdf, VORONOI_DIR)
        mapas_generados.append(ruta)
        print(f"✓ Mapa creado: {ruta.name}")

# ==========================================
# 5. CREAR MAPA COMPARATIVO (SUBPLOTS)
# ==========================================
print("\n[3/4] Creando mapa comparativo...")

modos_comparar = ['Metro', 'Autobús/CC', 'Góndola/Cablebús', 'Tranvía/Ligero']
n_modos = len(modos_comparar)

fig, axes = plt.subplots(2, 2, figsize=(16, 14))
axes = axes.flatten()

for idx, modo in enumerate(modos_comparar):
    if modo in datos_voronoi:
        gdf = datos_voronoi[modo]
        ax = axes[idx]
        
        # Normalización logarítmica para mejor visualización
        norm = mcolors.LogNorm(vmin=0.1, vmax=100)
        
        gdf.plot(
            column='area_km2',
            ax=ax,
            cmap='RdYlGn_r',
            norm=norm,
            edgecolor='black',
            linewidth=0.3,
            alpha=0.7
        )
        
        ax.set_title(
            f'{modo}\n({len(gdf)} regiones)',
            fontsize=12,
            fontweight='bold'
        )
        ax.set_xlabel('Este (m)', fontsize=9)
        ax.set_ylabel('Norte (m)', fontsize=9)

# Eliminar subplots vacíos
for idx in range(len(modos_comparar), len(axes)):
    fig.delaxes(axes[idx])

# Agregar colorbar común
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
sm = plt.cm.ScalarMappable(cmap='RdYlGn_r', norm=mcolors.LogNorm(vmin=0.1, vmax=100))
sm._A = []
cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.set_label('Área (km²)', fontsize=11)

plt.suptitle(
    'Comparación de Diagramas de Voronoi por Modo de Transporte\nCDMX - Accesibilidad al AICM',
    fontsize=16,
    fontweight='bold',
    y=0.95
)

plt.tight_layout(rect=[0, 0, 0.9, 0.93])

ruta_comparativo = VORONOI_DIR / 'voronoi_comparativo_todos.png'
plt.savefig(ruta_comparativo, dpi=300, bbox_inches='tight')
plt.close()
print(f"✓ Mapa comparativo creado: {ruta_comparativo.name}")

# ==========================================
# 6. CREAR MAPA MULTIMODAL DESTACADO
# ==========================================
print("\n[4/4] Creando mapa multimodal...")

if 'Multimodal' in datos_voronoi:
    gdf_multi = datos_voronoi['Multimodal']
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Normalización para multimodal (áreas más pequeñas)
    norm = mcolors.LogNorm(vmin=0.01, vmax=10)
    
    gdf_multi.plot(
        column='area_km2',
        ax=ax,
        legend=True,
        cmap='viridis',
        norm=norm,
        edgecolor='black',
        linewidth=0.2,
        alpha=0.6,
        legend_kwds={
            'label': 'Área de influencia (km²)',
            'orientation': 'vertical'
        }
    )
    
    ax.set_title(
        'Diagrama de Voronoi Multimodal\nTodas las Paradas de Transporte Público',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    ax.set_xlabel('Coordenada Este (m)', fontsize=12)
    ax.set_ylabel('Coordenada Norte (m)', fontsize=12)
    
    # Estadísticas
    stats_text = f"Total de regiones: {len(gdf_multi)}\n"
    stats_text += f"Área promedio: {gdf_multi['area_km2'].mean():.2f} km²\n"
    stats_text += f"Área mediana: {gdf_multi['area_km2'].median():.2f} km²"
    
    ax.text(
        0.02, 0.02, stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='bottom',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5)
    )
    
    plt.tight_layout()
    
    ruta_multi = VORONOI_DIR / 'voronoi_multimodal_completo.png'
    plt.savefig(ruta_multi, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Mapa multimodal creado: {ruta_multi.name}")

# ==========================================
# 7. RESUMEN FINAL
# ==========================================
print("\n" + "=" * 60)
print("RESUMEN DE VISUALIZACIONES")
print("=" * 60)

print(f"\nArchivos generados en: {VORONOI_DIR}")
print("\nMapas individuales:")
for ruta in mapas_generados:
    print(f"  • {ruta.name}")

print(f"\nMapa comparativo:")
print(f"  • voronoi_comparativo_todos.png")

print(f"\nMapa multimodal:")
print(f"  • voronoi_multimodal_completo.png")

print("\n✓ Script completado exitosamente")
