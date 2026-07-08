#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapas de Accesibilidad al AICM: Antes, Durante y Después de Eventos Masivos
Programa Delfín 2026 - Accesibilidad al AICM

Genera mapas mostrando cómo la accesibilidad al AICM (tiempos de viaje)
cambia antes, durante y después de eventos masivos debido a la congestión.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import folium
from folium.plugins import HeatMap
import warnings
warnings.filterwarnings('ignore')

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
VIZ_DIR = Path("visualizaciones")
MAPAS_ACC_DIR = VIZ_DIR / "mapas_accesibilidad_eventos"

# Coordenadas del AICM
AICM_LAT = 19.43531
AICM_LON = -99.08367

# Eventos masivos con coordenadas de venues
EVENTOS = [
    {
        'nombre': 'Concierto Foro Sol',
        'fecha_inicio': '2025-03-15 18:00:00',
        'duracion_horas': 6,
        'asistentes': 65000,
        'venue_lat': 19.39472,
        'venue_lon': -99.09333,
        'factor_congestion': 0.6  # 40% reducción de velocidad
    },
    {
        'nombre': 'Gran Premio F1',
        'fecha_inicio': '2025-10-25 10:00:00',
        'duracion_horas': 72,
        'asistentes': 80000,
        'venue_lat': 19.39167,
        'venue_lon': -99.09833,
        'factor_congestion': 0.5  # 50% reducción de velocidad
    },
    {
        'nombre': 'Temporada Decembrina',
        'fecha_inicio': '2025-12-20 00:00:00',
        'duracion_horas': 288,
        'asistentes': 30000,
        'venue_lat': 19.43531,
        'venue_lon': -99.08367,
        'factor_congestion': 0.75  # 25% reducción de velocidad
    }
]

def haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia en km entre dos puntos"""
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

def cargar_datos_paradas():
    """Carga datos de paradas de transporte público"""
    print("="*80)
    print("CARGA DE DATOS DE PARADAS")
    print("="*80)
    
    # Cargar paradas con distancia al AICM
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    print(f"✓ Paradas cargadas: {len(paradas):,}")
    
    # Intentar cargar datos de velocidad
    try:
        velocidades = pd.read_csv(RESULTADOS_DIR / "tiempos_viaje_por_parada.csv")
        paradas = paradas.merge(velocidades[['stop_id', 'velocidad_kmh']], on='stop_id', how='left')
        print(f"✓ Datos de velocidad cargados")
    except:
        # Si no hay datos de velocidad, usar valores por defecto
        paradas['velocidad_kmh'] = 15.0  # Velocidad promedio
        print(f"⚠️ Usando velocidad promedio de 15 km/h")
    
    # Calcular tiempo base al AICM (en minutos)
    paradas['tiempo_base_min'] = (paradas['distancia_km'] / paradas['velocidad_kmh']) * 60
    
    print(f"✓ Tiempo base promedio al AICM: {paradas['tiempo_base_min'].mean():.1f} minutos")
    
    return paradas

def calcular_congestion_punto(lat, lon, evento, periodo):
    """
    Calcula el factor de congestión en un punto específico.
    Modelo mejorado con incrementos más dramáticos durante eventos.
    Retorna un factor multiplicador (1.0 = sin congestión, 3.5 = triple tiempo)
    """
    # Distancia al venue
    dist_venue = haversine(lat, lon, evento['venue_lat'], evento['venue_lon'])
    
    # Distancia al AICM
    dist_aicm = haversine(lat, lon, AICM_LAT, AICM_LON)
    
    if periodo == 'antes':
        # Sin congestión adicional
        return 1.0
    
    elif periodo == 'durante':
        # Congestión MASIVA durante el evento
        # Impacto del venue (gaussiana muy pronunciada)
        impacto_venue = np.exp(-(dist_venue ** 2) / (2 * 2 ** 2))
        
        # Impacto del AICM (congestión general amplia)
        impacto_aicm = np.exp(-(dist_aicm ** 2) / (2 * 4 ** 2))
        
        # Factor de congestión total (MUCHO MÁS DRAMÁTICO)
        factor = 1.0 + 2.0 * impacto_venue + 1.5 * impacto_aicm
        
        return min(factor, 3.5)  # Máximo 3.5x el tiempo
    
    else:  # después
        # Congestión residual significativa
        impacto_venue = np.exp(-(dist_venue ** 2) / (2 * 3 ** 2)) * 0.6
        impacto_aicm = np.exp(-(dist_aicm ** 2) / (2 * 5 ** 2)) * 0.4
        
        factor = 1.0 + 1.5 * impacto_venue + 1.0 * impacto_aicm
        
        return min(factor, 2.5)  # Máximo 2.5x el tiempo

def generar_mapa_accesibilidad(evento, paradas, periodo='durante'):
    """Genera un mapa de accesibilidad al AICM"""
    print(f"\nGenerando mapa {periodo} para: {evento['nombre']}")
    
    # Crear mapa base
    mapa = folium.Map(
        location=[AICM_LAT, AICM_LON],
        zoom_start=11,
        tiles='CartoDB positron'
    )
    
    # Calcular tiempos de viaje para cada parada
    tiempos = []
    for idx, row in paradas.iterrows():
        # Factor de congestión en esta parada
        factor_congestion = calcular_congestion_punto(
            row['stop_lat'], row['stop_lon'], evento, periodo
        )
        
        # Tiempo de viaje con congestión
        tiempo_con_congestion = row['tiempo_base_min'] * factor_congestion
        
        tiempos.append(tiempo_con_congestion)
    
    paradas['tiempo_viaje_min'] = tiempos
    
    # Preparar datos para HeatMap (tiempo de viaje como intensidad)
    heat_data = []
    for idx, row in paradas.iterrows():
        # Invertir el tiempo para que tiempos más bajos sean más "calientes" (mejor accesibilidad)
        # Normalizar a 0-1 donde 1 = mejor accesibilidad (menor tiempo)
        tiempo_max = 120  # 2 horas máximo
        accesibilidad = max(0, 1 - (row['tiempo_viaje_min'] / tiempo_max))
        
        heat_data.append([row['stop_lat'], row['stop_lon'], accesibilidad])
    
    # Agregar capa de calor (colores invertidos: rojo = buena accesibilidad, azul = mala)
    HeatMap(
        heat_data,
        radius=10,
        blur=15,
        max_zoom=13,
        gradient={
            0.0: 'red',       # Mala accesibilidad (>120 min)
            0.25: 'orange',   # Accesibilidad regular
            0.5: 'yellow',    # Accesibilidad moderada
            0.75: 'lightgreen',  # Buena accesibilidad
            1.0: 'green'      # Excelente accesibilidad (<30 min)
        }
    ).add_to(mapa)
    
    # Agregar marcador del AICM
    folium.Marker(
        location=[AICM_LAT, AICM_LON],
        popup='<b>AICM</b><br>Aeropuerto Internacional',
        icon=folium.Icon(color='red', icon='plane', prefix='fa')
    ).add_to(mapa)
    
    # Agregar marcador del venue
    folium.Marker(
        location=[evento['venue_lat'], evento['venue_lon']],
        popup=f'<b>{evento["nombre"]}</b><br>{evento["asistentes"]:,} asistentes',
        icon=folium.Icon(color='orange', icon='star', prefix='fa')
    ).add_to(mapa)
    
    # Estadísticas del período
    tiempo_prom = paradas['tiempo_viaje_min'].mean()
    tiempo_max = paradas['tiempo_viaje_min'].max()
    tiempo_min = paradas['tiempo_viaje_min'].min()
    
    # Agregar leyenda
    periodo_nombres = {
        'antes': 'Antes del Evento',
        'durante': 'Durante el Evento',
        'despues': 'Después del Evento'
    }
    
    leyenda_html = f"""
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 280px; height: 220px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; padding: 10px">
        <b>{periodo_nombres[periodo]}</b><br>
        <b>{evento['nombre']}</b><br>
        {evento['asistentes']:,} asistentes<br><br>
        <b>Estadísticas de Accesibilidad:</b><br>
        • Tiempo promedio: {tiempo_prom:.1f} min<br>
        • Tiempo mínimo: {tiempo_min:.1f} min<br>
        • Tiempo máximo: {tiempo_max:.1f} min<br><br>
        <b>Escala de Accesibilidad:</b><br>
        <i class="fa fa-circle fa-1x" style="color:green"></i> Excelente (<30 min)<br>
        <i class="fa fa-circle fa-1x" style="color:lightgreen"></i> Buena (30-60 min)<br>
        <i class="fa fa-circle fa-1x" style="color:yellow"></i> Moderada (60-90 min)<br>
        <i class="fa fa-circle fa-1x" style="color:orange"></i> Regular (90-120 min)<br>
        <i class="fa fa-circle fa-1x" style="color:red"></i> Mala (>120 min)
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(leyenda_html))
    
    return mapa, paradas

def guardar_mapa(mapa, evento, periodo):
    """Guarda el mapa en formato HTML"""
    nombre_archivo = f"accesibilidad_{evento['nombre'].replace(' ', '_')}_{periodo}.html"
    MAPAS_ACC_DIR.mkdir(parents=True, exist_ok=True)
    mapa.save(MAPAS_ACC_DIR / nombre_archivo)
    print(f"✓ Mapa guardado: {MAPAS_ACC_DIR / nombre_archivo}")

def generar_comparativa_visual(evento, paradas_base):
    """Genera una visualización comparativa de los 3 períodos"""
    print(f"\nGenerando comparativa visual para: {evento['nombre']}")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    periodos = ['antes', 'durante', 'despues']
    titulos = ['Antes del Evento', 'Durante el Evento', 'Después del Evento']
    
    for idx, (periodo, titulo) in enumerate(zip(periodos, titulos)):
        ax = axes[idx]
        
        # Calcular tiempos para este período
        tiempos = []
        for _, row in paradas_base.iterrows():
            factor = calcular_congestion_punto(
                row['stop_lat'], row['stop_lon'], evento, periodo
            )
            tiempos.append(row['tiempo_base_min'] * factor)
        
        paradas_temp = paradas_base.copy()
        paradas_temp['tiempo_viaje_min'] = tiempos
        
        # Scatter plot con colores según tiempo
        scatter = ax.scatter(
            paradas_temp['stop_lon'],
            paradas_temp['stop_lat'],
            c=paradas_temp['tiempo_viaje_min'],
            cmap='RdYlGn_r',  # Rojo=malo, Verde=bueno (invertido)
            s=15,
            alpha=0.6,
            edgecolors='none'
        )
        
        # Marcar AICM
        ax.scatter([AICM_LON], [AICM_LAT], c='red', s=200, marker='*', 
                  edgecolors='black', linewidth=2, zorder=5, label='AICM')
        
        # Marcar venue
        ax.scatter([evento['venue_lon']], [evento['venue_lat']], c='orange', 
                  s=150, marker='s', edgecolors='black', linewidth=2, 
                  zorder=5, label='Venue')
        
        ax.set_xlabel('Longitud')
        ax.set_ylabel('Latitud')
        ax.set_title(f'{titulo}\nPromedio: {paradas_temp["tiempo_viaje_min"].mean():.1f} min', 
                     fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        if idx == 0:
            ax.legend(loc='upper right')
        
        plt.colorbar(scatter, ax=ax, label='Tiempo al AICM (min)')
    
    plt.suptitle(f'{evento["nombre"]} ({evento["asistentes"]:,} asistentes)\n' +
                 'Evolución de Accesibilidad al AICM', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    # Guardar
    nombre_archivo = f"comparativa_accesibilidad_{evento['nombre'].replace(' ', '_')}.png"
    plt.savefig(MAPAS_ACC_DIR / nombre_archivo, dpi=200, bbox_inches='tight')
    print(f"✓ Comparativa guardada: {MAPAS_ACC_DIR / nombre_archivo}")
    plt.close()

def generar_tabla_resumen(paradas_base):
    """Genera tabla resumen del impacto de eventos en accesibilidad"""
    print("\n" + "="*80)
    print("TABLA RESUMEN: IMPACTO DE EVENTOS EN ACCESIBILIDAD")
    print("="*80)
    
    resultados = []
    
    for evento in EVENTOS:
        # Calcular tiempos para cada período
        tiempos_antes = []
        tiempos_durante = []
        tiempos_despues = []
        
        for _, row in paradas_base.iterrows():
            factor_antes = calcular_congestion_punto(row['stop_lat'], row['stop_lon'], evento, 'antes')
            factor_durante = calcular_congestion_punto(row['stop_lat'], row['stop_lon'], evento, 'durante')
            factor_despues = calcular_congestion_punto(row['stop_lat'], row['stop_lon'], evento, 'despues')
            
            tiempos_antes.append(row['tiempo_base_min'] * factor_antes)
            tiempos_durante.append(row['tiempo_base_min'] * factor_durante)
            tiempos_despues.append(row['tiempo_base_min'] * factor_despues)
        
        # Estadísticas
        prom_antes = np.mean(tiempos_antes)
        prom_durante = np.mean(tiempos_durante)
        prom_despues = np.mean(tiempos_despues)
        
        incremento = ((prom_durante - prom_antes) / prom_antes) * 100
        
        resultados.append({
            'evento': evento['nombre'],
            'asistentes': evento['asistentes'],
            'tiempo_antes_min': prom_antes,
            'tiempo_durante_min': prom_durante,
            'tiempo_despues_min': prom_despues,
            'incremento_pct': incremento
        })
    
    df_resultados = pd.DataFrame(resultados)
    
    # Imprimir tabla
    print(f"\n{'Evento':<25} | {'Asistentes':<12} | {'Antes (min)':<12} | {'Durante (min)':<14} | {'Incremento':<10}")
    print("-"*80)
    
    for idx, row in df_resultados.iterrows():
        print(f"{row['evento']:<25} | {row['asistentes']:<12,} | " +
              f"{row['tiempo_antes_min']:<12.1f} | {row['tiempo_durante_min']:<14.1f} | " +
              f"+{row['incremento_pct']:<9.1f}%")
    
    # Guardar
    df_resultados.to_csv(RESULTADOS_DIR / "resumen_accesibilidad_eventos.csv", index=False)
    print(f"\n✓ Tabla guardada: {RESULTADOS_DIR / 'resumen_accesibilidad_eventos.csv'}")
    
    return df_resultados

def main():
    print("\n" + "="*80)
    print("MAPAS DE ACCESIBILIDAD AL AICM: ANTES, DURANTE Y DESPUÉS DE EVENTOS")
    print("Programa Delfín 2026 - Roberto Rojas & Janine Flores")
    print("="*80)
    
    # 1. Cargar datos
    paradas = cargar_datos_paradas()
    
    # 2. Generar mapas para cada evento
    print("\n" + "="*80)
    print("GENERACIÓN DE MAPAS DE ACCESIBILIDAD")
    print("="*80)
    
    for evento in EVENTOS:
        print(f"\n{'='*80}")
        print(f"Procesando: {evento['nombre']}")
        print(f"{'='*80}")
        
        # Generar mapas para los 3 períodos
        for periodo in ['antes', 'durante', 'despues']:
            mapa, _ = generar_mapa_accesibilidad(evento, paradas, periodo)
            guardar_mapa(mapa, evento, periodo)
        
        # Generar comparativa visual
        generar_comparativa_visual(evento, paradas)
    
    # 3. Generar tabla resumen
    df_resumen = generar_tabla_resumen(paradas)
    
    print("\n" + "="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)
    print(f"\n📁 Archivos generados en: {MAPAS_ACC_DIR}")
    print(f"  - 9 mapas de accesibilidad (HTML)")
    print(f"  - 3 comparativas visuales (PNG)")
    print(f"  - 1 tabla resumen (CSV)")

if __name__ == "__main__":
    main()
