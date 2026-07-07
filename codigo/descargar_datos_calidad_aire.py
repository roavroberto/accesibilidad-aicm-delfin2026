#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descarga y Procesamiento de Datos de Calidad del Aire - SIMAT CDMX
Programa Delfín 2026 - Análisis de Contaminación alrededor del AICM

Fuentes de datos:
- Portal de Datos Abiertos CDMX: https://datos.cdmx.gob.mx/
- SIMAT: Sistema de Monitoreo Atmosférico
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import requests
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
EXTERNOS_DIR = Path("datos/externos")
CALIDAD_AIRE_DIR = EXTERNOS_DIR / "calidad_aire"
VIZ_DIR = Path("visualizaciones")

# Coordenadas del AICM
AICM_LAT = 19.43531
AICM_LON = -99.08367

# Radio de búsqueda de estaciones (km)
RADIO_BUSQUEDA_KM = 10

def haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia en km entre dos puntos"""
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

def descargar_datos_simat():
    """
    Descarga datos de calidad del aire desde el portal de datos abiertos de CDMX.
    
    Nota: Este script intenta múltiples fuentes. Si alguna falla, continúa con la siguiente.
    """
    print("="*80)
    print("DESCARGA DE DATOS DE CALIDAD DEL AIRE - SIMAT CDMX")
    print("="*80)
    
    CALIDAD_AIRE_DIR.mkdir(parents=True, exist_ok=True)
    
    # URLs de fuentes de datos
    fuentes = [
        {
            'nombre': 'Datos Abiertos CDMX - Calidad del Aire',
            'url': 'https://datos.cdmx.gob.mx/dataset/5b750c7f-0d0f-4f5f-8f5f-5f5f5f5f5f5f/resource/5b750c7f-0d0f-4f5f-8f5f-5f5f5f5f5f5f/download/calidad_aire.csv',
            'tipo': 'csv'
        },
        {
            'nombre': 'API Datos Abiertos Aire CDMX',
            'url': 'https://datosabiertos.aire.cdmx.gob.mx/api/1/datastore/contaminantes',
            'tipo': 'json'
        }
    ]
    
    datos_descargados = False
    
    for fuente in fuentes:
        print(f"\nIntentando: {fuente['nombre']}")
        print(f"URL: {fuente['url']}")
        
        try:
            response = requests.get(fuente['url'], timeout=30)
            
            if response.status_code == 200:
                archivo_salida = CALIDAD_AIRE_DIR / f"calidad_aire_raw.{fuente['tipo']}"
                
                with open(archivo_salida, 'wb') as f:
                    f.write(response.content)
                
                print(f"✓ Descargado: {archivo_salida}")
                print(f"  Tamaño: {len(response.content) / 1024:.2f} KB")
                
                datos_descargados = True
                break
            else:
                print(f"✗ Error HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error de conexión: {e}")
            continue
    
    if not datos_descargados:
        print("\n⚠️ No se pudieron descargar datos automáticamente.")
        print("\nInstrucciones manuales:")
        print("1. Visita: https://datos.cdmx.gob.mx/")
        print("2. Busca: 'Calidad del Aire' o 'SIMAT'")
        print("3. Descarga el dataset más reciente en formato CSV")
        print("4. Guarda el archivo en: datos/externos/calidad_aire/calidad_aire_manual.csv")
        
        # Crear archivo de instrucciones
        with open(CALIDAD_AIRE_DIR / "instrucciones_descarga.txt", 'w') as f:
            f.write("""
INSTRUCCIONES PARA DESCARGAR DATOS DE CALIDAD DEL AIRE
======================================================

Fuente: Portal de Datos Abiertos de la CDMX
URL: https://datos.cdmx.gob.mx/

Pasos:
1. Visita el portal de datos abiertos
2. Busca "Calidad del Aire" o "SIMAT"
3. Descarga el dataset más reciente (formato CSV)
4. Guarda el archivo en: datos/externos/calidad_aire/calidad_aire_manual.csv

Alternativa - Datos históricos:
- SIMAT: https://www.aire.cdmx.gob.mx/estadisticas-consultas/descargas/
- Contiene datos desde 1992 en formato Excel

Contaminantes de interés:
- PM2.5: Partículas finas
- PM10: Partículas respirables
- O3: Ozono
- NO2: Dióxido de nitrógeno
- SO2: Dióxido de azufre
- CO: Monóxido de carbono
""")
        
        print(f"✓ Instrucciones guardadas en: {CALIDAD_AIRE_DIR / 'instrucciones_descarga.txt'}")
        
        return False
    
    return True

def procesar_datos_calidad_aire():
    """Procesa los datos de calidad del aire descargados"""
    print("\n" + "="*80)
    print("PROCESAMIENTO DE DATOS DE CALIDAD DEL AIRE")
    print("="*80)
    
    # Buscar archivos CSV en el directorio
    archivos_csv = list(CALIDAD_AIRE_DIR.glob("*.csv"))
    
    if not archivos_csv:
        print("\n⚠️ No se encontraron archivos CSV para procesar.")
        print("Por favor, descarga los datos manualmente siguiendo las instrucciones.")
        return None
    
    print(f"\nArchivos encontrados: {len(archivos_csv)}")
    
    for archivo in archivos_csv:
        print(f"  - {archivo.name} ({archivo.stat().st_size / 1024:.2f} KB)")
    
    # Intentar leer el primer CSV
    archivo_datos = archivos_csv[0]
    print(f"\nProcesando: {archivo_datos.name}")
    
    try:
        df = pd.read_csv(archivo_datos)
        print(f"  ✓ Filas: {len(df):,}")
        print(f"  ✓ Columnas: {len(df.columns)}")
        print(f"  ✓ Columnas: {list(df.columns)[:10]}...")
        
        return df
        
    except Exception as e:
        print(f"  ✗ Error al leer: {e}")
        return None

def identificar_estaciones_cercanas_aicm(df_estaciones):
    """Identifica las estaciones de monitoreo cercanas al AICM"""
    print("\n" + "="*80)
    print("IDENTIFICACIÓN DE ESTACIONES CERCANAS AL AICM")
    print("="*80)
    
    # Coordenadas del AICM
    print(f"\nCoordenadas del AICM: {AICM_LAT}, {AICM_LON}")
    print(f"Radio de búsqueda: {RADIO_BUSQUEDA_KM} km")
    
    # Calcular distancia de cada estación al AICM
    df_estaciones['distancia_aicm_km'] = df_estaciones.apply(
        lambda row: haversine(AICM_LAT, AICM_LON, row['latitud'], row['longitud']),
        axis=1
    )
    
    # Filtrar estaciones dentro del radio
    estaciones_cercanas = df_estaciones[df_estaciones['distancia_aicm_km'] <= RADIO_BUSQUEDA_KM].copy()
    estaciones_cercanas = estaciones_cercanas.sort_values('distancia_aicm_km')
    
    print(f"\n✓ Estaciones encontradas dentro del radio: {len(estaciones_cercanas)}")
    
    if len(estaciones_cercanas) > 0:
        print("\nEstaciones más cercanas:")
        for idx, row in estaciones_cercanas.head(5).iterrows():
            print(f"  - {row.get('nombre', row.get('estacion', 'Desconocida'))}: {row['distancia_aicm_km']:.2f} km")
    
    return estaciones_cercanas

def generar_visualizaciones(df_datos, df_estaciones_cercanas):
    """Genera visualizaciones de la calidad del aire"""
    print("\n" + "="*80)
    print("GENERACIÓN DE VISUALIZACIONES")
    print("="*80)
    
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Mapa de estaciones cercanas al AICM
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot del AICM
    ax.scatter([AICM_LON], [AICM_LAT], c='red', s=200, marker='*', 
               label='AICM', zorder=5, edgecolors='black', linewidth=2)
    
    # Plot de estaciones cercanas
    if len(df_estaciones_cercanas) > 0:
        scatter = ax.scatter(
            df_estaciones_cercanas['longitud'],
            df_estaciones_cercanas['latitud'],
            c=df_estaciones_cercanas['distancia_aicm_km'],
            cmap='YlOrRd',
            s=100,
            alpha=0.7,
            edgecolors='black',
            linewidth=1
        )
        
        # Anotar estaciones
        for idx, row in df_estaciones_cercanas.iterrows():
            ax.annotate(
                f"{row.get('nombre', row.get('estacion', ''))}\n{row['distancia_aicm_km']:.1f}km",
                (row['longitud'], row['latitud']),
                fontsize=8,
                ha='center',
                va='bottom',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
            )
        
        plt.colorbar(scatter, label='Distancia al AICM (km)')
    
    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    ax.set_title('Estaciones de Monitoreo de Calidad del Aire\nCercanas al AICM', 
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "estaciones_calidad_aire_aicm.png", dpi=200, bbox_inches='tight')
    print(f"✓ Mapa de estaciones guardado: {VIZ_DIR / 'estaciones_calidad_aire_aicm.png'}")
    plt.close()
    
    # 2. Serie temporal de contaminantes (si hay datos)
    if df_datos is not None and 'fecha' in df_datos.columns:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        contaminantes = ['PM2.5', 'PM10', 'O3', 'NO2']
        
        for i, contaminante in enumerate(contaminantes):
            ax = axes[i // 2, i % 2]
            
            if contaminante in df_datos.columns:
                df_datos['fecha'] = pd.to_datetime(df_datos['fecha'])
                df_datos_plot = df_datos.set_index('fecha')[contaminante].resample('D').mean()
                
                ax.plot(df_datos_plot.index, df_datos_plot.values, linewidth=0.5, alpha=0.7)
                ax.set_title(f'{contaminante} - Serie Temporal', fontsize=12, fontweight='bold')
                ax.set_ylabel('Concentración (µg/m³)')
                ax.grid(True, alpha=0.3)
            else:
                ax.text(0.5, 0.5, f'Datos de {contaminante}\nno disponibles', 
                       ha='center', va='center', fontsize=12)
                ax.set_title(f'{contaminante} - No disponible', fontsize=12)
        
        plt.tight_layout()
        plt.savefig(VIZ_DIR / "series_temporales_contaminantes.png", dpi=200, bbox_inches='tight')
        print(f"✓ Series temporales guardadas: {VIZ_DIR / 'series_temporales_contaminantes.png'}")
        plt.close()

def main():
    print("\n" + "="*80)
    print("ANÁLISIS DE CALIDAD DEL AIRE ALREDEDOR DEL AICM")
    print("Programa Delfín 2026 - Roberto Rojas & Janine Flores")
    print("="*80)
    
    # 1. Descargar datos
    exito_descarga = descargar_datos_simat()
    
    # 2. Procesar datos
    df_datos = procesar_datos_calidad_aire()
    
    # 3. Identificar estaciones cercanas (usando datos de ejemplo si no hay descarga)
    if df_datos is not None and 'latitud' in df_datos.columns and 'longitud' in df_datos.columns:
        # Si los datos tienen coordenadas de estaciones
        df_estaciones = df_datos[['latitud', 'longitud']].drop_duplicates()
        if 'nombre' in df_datos.columns:
            df_estaciones = df_datos[['nombre', 'latitud', 'longitud']].drop_duplicates()
        
        estaciones_cercanas = identificar_estaciones_cercanas_aicm(df_estaciones)
        
        # 4. Generar visualizaciones
        generar_visualizaciones(df_datos, estaciones_cercanas)
    else:
        print("\n⚠️ No hay datos suficientes para identificar estaciones.")
        print("Por favor, descarga los datos manualmente.")
        
        # Crear visualización de ejemplo con estaciones conocidas del SIMAT
        print("\nCreando mapa con estaciones conocidas del SIMAT...")
        
        # Estaciones del SIMAT cercanas al AICM (coordenadas aproximadas)
        estaciones_simat = pd.DataFrame({
            'nombre': ['Merced', 'Peñones', 'UAM-Iztapalapa', 'Tlalnepantla', 'Xalostoc'],
            'latitud': [19.4241, 19.4097, 19.3573, 19.5287, 19.5244],
            'longitud': [-99.1192, -99.0847, -99.0739, -99.1947, -99.0817]
        })
        
        estaciones_cercanas = identificar_estaciones_cercanas_aicm(estaciones_simat)
        generar_visualizaciones(None, estaciones_cercanas)
    
    print("\n" + "="*80)
    print("PROCESO COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()
