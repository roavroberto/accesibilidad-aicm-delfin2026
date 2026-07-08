#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapas de Contaminación: Antes, Durante y Después de Eventos Masivos
Programa Delfín 2026 - Accesibilidad al AICM

Genera mapas de calor mostrando la evolución de la contaminación
en ventanas temporales alrededor de eventos masivos.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime, timedelta
import folium
from folium import plugins
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
SERIES_DIR = RESULTADOS_DIR / "series_temporales"
VIZ_DIR = Path("visualizaciones")
MAPAS_DIR = VIZ_DIR / "mapas_contaminacion"

# Coordenadas del AICM
AICM_LAT = 19.43531
AICM_LON = -99.08367

# Estaciones del SIMAT cercanas al AICM
ESTACIONES_SIMAT = {
    'Peñones': {'lat': 19.4097, 'lon': -99.0847, 'distancia_km': 2.85},
    'Merced': {'lat': 19.4241, 'lon': -99.1192, 'distancia_km': 3.93},
    'UAM-Iztapalapa': {'lat': 19.3573, 'lon': -99.0739, 'distancia_km': 8.73},
    'Xalostoc': {'lat': 19.5244, 'lon': -99.0817, 'distancia_km': 9.91}
}

# Eventos masivos
EVENTOS = [
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
        'duracion_horas': 72,
        'asistentes': 80000,
        'tipo': 'deportivo'
    },
    {
        'nombre': 'Temporada Decembrina',
        'fecha_inicio': '2025-12-20 00:00:00',
        'duracion_horas': 288,
        'asistentes': 30000,
        'tipo': 'temporada'
    }
]

def cargar_datos():
    """Carga las series de contaminación"""
    print("="*80)
    print("CARGA DE DATOS")
    print("="*80)
    
    df_contaminacion = pd.read_csv(SERIES_DIR / "series_contaminacion_aicm.csv")
    df_contaminacion['fecha'] = pd.to_datetime(df_contaminacion['fecha'])
    
    print(f"✓ Series de contaminación cargadas: {len(df_contaminacion):,} registros")
    print(f"  Rango: {df_contaminacion['fecha'].min()} a {df_contaminacion['fecha'].max()}")
    
    return df_contaminacion

def extraer_ventanas_temporales(df_contaminacion, evento):
    """Extrae datos en ventanas antes, durante y después del evento"""
    fecha_inicio = pd.Timestamp(evento['fecha_inicio'])
    duracion = timedelta(hours=evento['duracion_horas'])
    fecha_fin = fecha_inicio + duracion
    
    # Ventanas temporales
    ventana_antes_inicio = fecha_inicio - timedelta(days=7)
    ventana_despues_fin = fecha_fin + timedelta(days=7)
    
    # Extraer datos
    datos_antes = df_contaminacion[
        (df_contaminacion['fecha'] >= ventana_antes_inicio) & 
        (df_contaminacion['fecha'] < fecha_inicio)
    ].copy()
    
    datos_durante = df_contaminacion[
        (df_contaminacion['fecha'] >= fecha_inicio) & 
        (df_contaminacion['fecha'] <= fecha_fin)
    ].copy()
    
    datos_despues = df_contaminacion[
        (df_contaminacion['fecha'] > fecha_fin) & 
        (df_contaminacion['fecha'] <= ventana_despues_fin)
    ].copy()
    
    return {
        'antes': datos_antes,
        'durante': datos_durante,
        'despues': datos_despues
    }

def calcular_estadisticas_ventanas(ventanas):
    """Calcula estadísticas por ventana temporal"""
    stats = {}
    
    for periodo, datos in ventanas.items():
        if len(datos) > 0:
            stats[periodo] = {
                'PM25_mean': datos['PM25'].mean(),
                'PM10_mean': datos['PM10'].mean(),
                'O3_mean': datos['O3'].mean(),
                'NO2_mean': datos['NO2'].mean(),
                'n_registros': len(datos)
            }
        else:
            stats[periodo] = {
                'PM25_mean': 0,
                'PM10_mean': 0,
                'O3_mean': 0,
                'NO2_mean': 0,
                'n_registros': 0
            }
    
    return stats

def generar_mapa_calor_estatico(evento, ventanas, contaminante='PM25'):
    """Genera mapa de calor estático para un evento y contaminante"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    periodos = ['antes', 'durante', 'despues']
    titulos = ['Antes del Evento\n(7 días previos)', 
               'Durante el Evento', 
               'Después del Evento\n(7 días posteriores)']
    
    for idx, (periodo, titulo) in enumerate(zip(periodos, titulos)):
        ax = axes[idx]
        datos = ventanas[periodo]
        
        if len(datos) > 0:
            # Calcular promedio por hora del día para suavizar
            datos_agg = datos.set_index('fecha').resample('h').mean()
            
            # Crear heatmap de tiempo vs contaminante
            horas = datos_agg.index.hour
            dias = (datos_agg.index - datos_agg.index[0]).days
            
            # Scatter plot con intensidad de color
            scatter = ax.scatter(
                horas, 
                dias,
                c=datos_agg[contaminante],
                cmap='YlOrRd',
                s=50,
                alpha=0.7,
                edgecolors='black',
                linewidth=0.5
            )
            
            plt.colorbar(scatter, ax=ax, label=f'{contaminante} (µg/m³)')
        
        ax.set_xlabel('Hora del día')
        ax.set_ylabel('Día')
        ax.set_title(titulo, fontsize=12, fontweight='bold')
        ax.set_xticks(range(0, 24, 3))
        ax.grid(True, alpha=0.3)
        
        # Marcar evento en el centro
        if periodo == 'durante':
            ax.axhline(y=0, color='red', linestyle='--', linewidth=2, alpha=0.5)
    
    plt.suptitle(f'{evento["nombre"]} - Evolución de {contaminante}\n' +
                 f'({evento["asistentes"]:,} asistentes)', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    # Guardar
    nombre_archivo = f"mapa_calor_{evento['nombre'].replace(' ', '_')}_{contaminante}.png"
    MAPAS_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(MAPAS_DIR / nombre_archivo, dpi=200, bbox_inches='tight')
    print(f"✓ Mapa de calor guardado: {MAPAS_DIR / nombre_archivo}")
    plt.close()

def generar_mapa_geografico_interactivo(evento, ventanas):
    """Genera mapa geográfico interactivo con Folium"""
    print(f"\nGenerando mapa interactivo para: {evento['nombre']}")
    
    # Crear mapa base centrado en el AICM
    mapa = folium.Map(
        location=[AICM_LAT, AICM_LON],
        zoom_start=11,
        tiles='CartoDB positron'
    )
    
    # Agregar marcador del AICM
    folium.Marker(
        location=[AICM_LAT, AICM_LON],
        popup='AICM',
        icon=folium.Icon(color='red', icon='plane', prefix='fa')
    ).add_to(mapa)
    
    # Agregar marcadores de estaciones SIMAT
    for nombre, coords in ESTACIONES_SIMAT.items():
        folium.Marker(
            location=[coords['lat'], coords['lon']],
            popup=f'{nombre}<br>Distancia: {coords["distancia_km"]:.2f} km',
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mapa)
    
    # Agregar marcador del venue del evento
    # Coordenadas aproximadas de venues
    venues_coords = {
        'Concierto Foro Sol': [19.39472, -99.09333],
        'Gran Premio F1': [19.39167, -99.09833],
        'Temporada Decembrina': [19.43531, -99.08367]  # Centro
    }
    
    venue_coords = venues_coords.get(evento['nombre'], [AICM_LAT, AICM_LON])
    
    folium.Marker(
        location=venue_coords,
        popup=f'{evento["nombre"]}<br>{evento["asistentes"]:,} asistentes',
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(mapa)
    
    # Crear capas para cada período temporal
    periodos_nombres = {
        'antes': 'Antes del Evento',
        'durante': 'Durante el Evento',
        'despues': 'Después del Evento'
    }
    
    for periodo, datos in ventanas.items():
        if len(datos) > 0:
            # Calcular promedio de contaminantes
            pm25_prom = datos['PM25'].mean()
            pm10_prom = datos['PM10'].mean()
            no2_prom = datos['NO2'].mean()
            
            # Crear popup con información
            popup_text = f"""
            <b>{periodos_nombres[periodo]}</b><br>
            PM2.5: {pm25_prom:.1f} µg/m³<br>
            PM10: {pm10_prom:.1f} µg/m³<br>
            NO2: {no2_prom:.1f} µg/m³<br>
            Registros: {len(datos)}
            """
            
            # Agregar círculo con color según nivel de contaminación
            # Verde: <50, Amarillo: 50-100, Rojo: >100
            if pm25_prom < 50:
                color = 'green'
            elif pm25_prom < 100:
                color = 'orange'
            else:
                color = 'red'
            
            folium.Circle(
                location=[AICM_LAT, AICM_LON],
                radius=5000,  # 5 km de radio
                popup=popup_text,
                color=color,
                fill=True,
                fill_opacity=0.3,
                weight=2
            ).add_to(mapa)
    
    # Agregar leyenda
    leyenda_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
        <b>Niveles de PM2.5</b><br>
        <i class="fa fa-circle fa-1x" style="color:green"></i> Bueno (<50 µg/m³)<br>
        <i class="fa fa-circle fa-1x" style="color:orange"></i> Moderado (50-100 µg/m³)<br>
        <i class="fa fa-circle fa-1x" style="color:red"></i> Dañino (>100 µg/m³)
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(leyenda_html))
    
    # Guardar mapa
    nombre_archivo = f"mapa_interactivo_{evento['nombre'].replace(' ', '_')}.html"
    mapa.save(MAPAS_DIR / nombre_archivo)
    print(f"✓ Mapa interactivo guardado: {MAPAS_DIR / nombre_archivo}")

def generar_comparativa_eventos(df_contaminacion):
    """Genera comparativa de todos los eventos"""
    print("\n" + "="*80)
    print("COMPARATIVA DE EVENTOS")
    print("="*80)
    
    fig, axes = plt.subplots(len(EVENTOS), 3, figsize=(18, 4 * len(EVENTOS)))
    
    contaminantes = ['PM25', 'PM10', 'NO2']
    titulos_contam = ['PM2.5', 'PM10', 'NO2']
    
    for idx_evento, evento in enumerate(EVENTOS):
        ventanas = extraer_ventanas_temporales(df_contaminacion, evento)
        
        for idx_contam, (contam, titulo) in enumerate(zip(contaminantes, titulos_contam)):
            ax = axes[idx_evento, idx_contam]
            
            # Plot evolución temporal
            for periodo, color, label in [
                ('antes', '#3498db', 'Antes'),
                ('durante', '#e74c3c', 'Durante'),
                ('despues', '#2ecc71', 'Después')
            ]:
                datos = ventanas[periodo]
                if len(datos) > 0:
                    ax.plot(
                        range(len(datos)),
                        datos[contam].values,
                        color=color,
                        alpha=0.7,
                        linewidth=1,
                        label=label
                    )
            
            ax.set_ylabel(f'{titulo} (µg/m³)')
            ax.set_title(f'{evento["nombre"]} - {titulo}', fontsize=10, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            if idx_evento == 0 and idx_contam == 2:
                ax.legend(fontsize=8)
    
    plt.suptitle('Evolución de Contaminantes en Eventos Masivos\n' +
                 'Comparación Antes, Durante y Después', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    # Guardar
    MAPAS_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(MAPAS_DIR / "comparativa_todos_eventos.png", dpi=200, bbox_inches='tight')
    print(f"✓ Comparativa guardada: {MAPAS_DIR / 'comparativa_todos_eventos.png'}")
    plt.close()

def generar_tabla_resumen(df_contaminacion):
    """Genera tabla resumen de todos los eventos"""
    print("\n" + "="*80)
    print("TABLA RESUMEN: IMPACTO DE EVENTOS EN CONTAMINACIÓN")
    print("="*80)
    
    resultados = []
    
    for evento in EVENTOS:
        ventanas = extraer_ventanas_temporales(df_contaminacion, evento)
        stats = calcular_estadisticas_ventanas(ventanas)
        
        # Calcular incrementos
        incremento_pm25 = ((stats['durante']['PM25_mean'] - stats['antes']['PM25_mean']) / 
                          stats['antes']['PM25_mean'] * 100) if stats['antes']['PM25_mean'] > 0 else 0
        
        incremento_pm10 = ((stats['durante']['PM10_mean'] - stats['antes']['PM10_mean']) / 
                          stats['antes']['PM10_mean'] * 100) if stats['antes']['PM10_mean'] > 0 else 0
        
        incremento_no2 = ((stats['durante']['NO2_mean'] - stats['antes']['NO2_mean']) / 
                         stats['antes']['NO2_mean'] * 100) if stats['antes']['NO2_mean'] > 0 else 0
        
        resultados.append({
            'evento': evento['nombre'],
            'asistentes': evento['asistentes'],
            'pm25_antes': stats['antes']['PM25_mean'],
            'pm25_durante': stats['durante']['PM25_mean'],
            'incremento_pm25': incremento_pm25,
            'pm10_antes': stats['antes']['PM10_mean'],
            'pm10_durante': stats['durante']['PM10_mean'],
            'incremento_pm10': incremento_pm10,
            'no2_antes': stats['antes']['NO2_mean'],
            'no2_durante': stats['durante']['NO2_mean'],
            'incremento_no2': incremento_no2
        })
    
    df_resultados = pd.DataFrame(resultados)
    
    # Imprimir tabla
    print(f"\n{'Evento':<25} | {'Asistentes':<12} | {'PM2.5 Antes':<12} | {'PM2.5 Durante':<14} | {'Incremento':<10}")
    print("-"*80)
    
    for idx, row in df_resultados.iterrows():
        print(f"{row['evento']:<25} | {row['asistentes']:<12,} | " +
              f"{row['pm25_antes']:<12.1f} | {row['pm25_durante']:<14.1f} | " +
              f"+{row['incremento_pm25']:<9.1f}%")
    
    # Guardar
    df_resultados.to_csv(RESULTADOS_DIR / "resumen_mapas_contaminacion.csv", index=False)
    print(f"\n✓ Tabla guardada: {RESULTADOS_DIR / 'resumen_mapas_contaminacion.csv'}")
    
    return df_resultados

def main():
    print("\n" + "="*80)
    print("MAPAS DE CONTAMINACIÓN: ANTES, DURANTE Y DESPUÉS DE EVENTOS")
    print("Programa Delfín 2026 - Roberto Rojas & Janine Flores")
    print("="*80)
    
    # 1. Cargar datos
    df_contaminacion = cargar_datos()
    
    # 2. Generar mapas para cada evento
    print("\n" + "="*80)
    print("GENERACIÓN DE MAPAS POR EVENTO")
    print("="*80)
    
    for evento in EVENTOS:
        print(f"\n{'='*80}")
        print(f"Procesando: {evento['nombre']}")
        print(f"{'='*80}")
        
        # Extraer ventanas temporales
        ventanas = extraer_ventanas_temporales(df_contaminacion, evento)
        
        print(f"✓ Ventanas extraídas:")
        print(f"  - Antes: {len(ventanas['antes']):,} registros")
        print(f"  - Durante: {len(ventanas['durante']):,} registros")
        print(f"  - Después: {len(ventanas['despues']):,} registros")
        
        # Generar mapas de calor estáticos para cada contaminante
        for contaminante in ['PM25', 'PM10', 'NO2']:
            generar_mapa_calor_estatico(evento, ventanas, contaminante)
        
        # Generar mapa geográfico interactivo
        generar_mapa_geografico_interactivo(evento, ventanas)
    
    # 3. Generar comparativa de todos los eventos
    generar_comparativa_eventos(df_contaminacion)
    
    # 4. Generar tabla resumen
    df_resumen = generar_tabla_resumen(df_contaminacion)
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)
    print(f"\n📁 Archivos generados en: {MAPAS_DIR}")
    print(f"  - Mapas de calor estáticos (PNG)")
    print(f"  - Mapas interactivos (HTML)")
    print(f"  - Comparativa de eventos (PNG)")
    print(f"  - Tabla resumen (CSV)")

if __name__ == "__main__":
    main()
