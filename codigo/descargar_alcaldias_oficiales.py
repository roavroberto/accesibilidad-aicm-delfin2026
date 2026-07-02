#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descarga de Alcaldías CDMX desde Múltiples Fuentes Oficiales
Programa Delfín 2026 - Accesibilidad al AICM
"""

import geopandas as gpd
import pandas as pd
import requests
import zipfile
import io
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
DATOS_DIR = Path("datos")
RESULTADOS_DIR = Path("datos/resultados")

# URLs de fuentes oficiales
FUENTES = {
    "Datos Abiertos CDMX": {
        "url": "https://datos.cdmx.cdmx.gob.mx/dataset/8c5618f2-3a1b-4d60-b33a-3a5b5b5b5b5b/resource/26c1c1c1-c1c1-c1c1-c1c1-c1c1c1c1c1c1/download/alcaldias.geojson",
        "tipo": "geojson"
    },
    "GitHub Datos MX": {
        "url": "https://raw.githubusercontent.com/angelnmara/geojson/master/cdmxAlcaldias.json",
        "tipo": "geojson"
    },
    "GitHub Geodata MX": {
        "url": "https://raw.githubusercontent.com/angelnmara/geojson/master/cdmx.json",
        "tipo": "geojson"
    },
    "INEGI Shapefile": {
        "url": "https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/718865/2020/Ageestatal_09_2020_shp.zip",
        "tipo": "shapefile"
    }
}

def descargar_y_procesar_fuente(nombre, config):
    """Intenta descargar y procesar una fuente específica"""
    print(f"\n{'='*60}")
    print(f"Intentando: {nombre}")
    print(f"URL: {config['url']}")
    print(f"{'='*60}")
    
    try:
        # Descargar
        print("  - Descargando...")
        response = requests.get(config['url'], timeout=30)
        response.raise_for_status()
        print(f"  ✓ Descargado ({len(response.content)} bytes)")
        
        # Procesar según tipo
        if config['tipo'] == 'geojson':
            print("  - Procesando GeoJSON...")
            # Guardar temporalmente
            temp_path = DATOS_DIR / f"alcaldias_temp_{nombre.replace(' ', '_')}.geojson"
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Cargar con geopandas
            gdf = gpd.read_file(temp_path)
            print(f"  ✓ GeoJSON cargado: {len(gdf)} registros")
            
        elif config['tipo'] == 'shapefile':
            print("  - Procesando Shapefile ZIP...")
            # Extraer ZIP
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(DATOS_DIR / "shapefile_temp")
            
            # Buscar el shapefile
            shp_files = list((DATOS_DIR / "shapefile_temp").glob("*.shp"))
            if len(shp_files) == 0:
                print("  ✗ No se encontró archivo .shp en el ZIP")
                return None
            
            print(f"  - Shapefile encontrado: {shp_files[0].name}")
            gdf = gpd.read_file(shp_files[0])
            print(f"  ✓ Shapefile cargado: {len(gdf)} registros")
        
        # Verificar que tenga geometría
        if 'geometry' not in gdf.columns:
            print("  ✗ No tiene columna 'geometry'")
            return None
        
        print(f"  - Columnas: {list(gdf.columns)}")
        print(f"  - CRS: {gdf.crs}")
        
        # Guardar como GeoJSON limpio
        output_path = DATOS_DIR / "alcaldias_cdmx.geojson"
        gdf.to_file(output_path, driver='GeoJSON')
        print(f"  ✓ Guardado: {output_path}")
        
        return gdf
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

def descargar_alcaldias():
    """Prueba todas las fuentes hasta encontrar una que funcione"""
    print("="*60)
    print("DESCARGA DE ALCALDÍAS CDMX - MÚLTIPLES FUENTES")
    print("="*60)
    
    # Crear directorios
    DATOS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Probar cada fuente
    for nombre, config in FUENTES.items():
        gdf = descargar_y_procesar_fuente(nombre, config)
        
        if gdf is not None and len(gdf) > 0:
            print(f"\n{'='*60}")
            print(f"✓ ÉXITO con: {nombre}")
            print(f"{'='*60}")
            return gdf
    
    print("\n✗ NINGUNA FUENTE FUNCIONÓ")
    return None

def verificar_alcaldias(gdf):
    """Verifica que el GeoDataFrame tenga las 16 alcaldías"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE ALCALDÍAS")
    print("="*60)
    
    # Lista de alcaldías esperadas
    alcaldias_esperadas = [
        "Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán",
        "Cuajimalpa de Morelos", "Cuauhtémoc", "Gustavo A. Madero",
        "Iztacalco", "Iztapalapa", "Magdalena Contreras", "Miguel Hidalgo",
        "Milpa Alta", "Tláhuac", "Tlalpan", "Venustiano Carranza", "Xochimilco"
    ]
    
    print(f"\nAlcaldías esperadas: {len(alcaldias_esperadas)}")
    print(f"Alcaldías encontradas: {len(gdf)}")
    
    # Intentar encontrar columna de nombre
    columnas_posibles = ['NOM_ALC', 'nombre_alcaldia', 'NOMGEO', 'name', 'NOMBRE']
    nombre_col = None
    
    for col in columnas_posibles:
        if col in gdf.columns:
            nombre_col = col
            break
    
    if nombre_col is None:
        print(f"\nColumnas disponibles: {list(gdf.columns)}")
        print("⚠ No se encontró columna de nombre estándar")
        return
    
    print(f"\nUsando columna: {nombre_col}")
    print("\nAlcaldías encontradas:")
    
    for idx, row in gdf.iterrows():
        nombre = row[nombre_col] if nombre_col else f"Alcaldía {idx+1}"
        print(f"  {idx+1}. {nombre}")
    
    # Verificar las 16
    if len(gdf) == 16:
        print("\n✓ Se encontraron las 16 alcaldías")
    else:
        print(f"\n⚠ Se encontraron {len(gdf)} alcaldías (se esperaban 16)")

def main():
    print("="*60)
    print("DESCARGA DE ALCALDÍAS CDMX")
    print("="*60)
    
    # Descargar
    gdf = descargar_alcaldias()
    
    if gdf is None:
        print("\n✗ ERROR: No se pudieron descargar las alcaldías")
        return
    
    # Verificar
    verificar_alcaldias(gdf)
    
    print("\n" + "="*60)
    print("PROCESO COMPLETADO")
    print("="*60)

if __name__ == "__main__":
    main()
