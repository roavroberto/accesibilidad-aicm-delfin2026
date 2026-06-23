#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación de la "Zona Muerta": Distancias a Terminales vs Centro Geométrico
Programa Delfín 2026 - Accesibilidad al AICM
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuración
RESULTADOS_DIR = Path("datos/resultados")
AICM_T1 = (19.4353, -99.0725)  # Coordenadas aproximadas Terminal 1
AICM_T2 = (19.4341, -99.0643)  # Coordenadas aproximadas Terminal 2
RADIOS_KM = [0.5, 1.0, 2.0, 5.0]

def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia en km entre dos puntos."""
    R = 6371
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    
    a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c

def main():
    print("="*60)
    print("VERIFICACIÓN DE ZONA MUERTA: TERMINALES VS CENTRO")
    print("="*60)
    
    # Cargar paradas
    print("\nCargando datos de paradas...")
    paradas = pd.read_csv(RESULTADOS_DIR / "paradas_con_distancia_aicm.csv")
    print(f"  - Paradas cargadas: {len(paradas):,}")

    # Calcular distancias a T1 y T2
    print("Calculando distancias a Terminales 1 y 2...")
    paradas['dist_a_t1'] = haversine(paradas['stop_lat'], paradas['stop_lon'], AICM_T1[0], AICM_T1[1])
    paradas['dist_a_t2'] = haversine(paradas['stop_lat'], paradas['stop_lon'], AICM_T2[0], AICM_T2[1])
    
    # Distancia mínima a cualquier terminal (lo que realmente le importa al pasajero)
    paradas['dist_min_terminal'] = np.minimum(paradas['dist_a_t1'], paradas['dist_a_t2'])

    # Comparar radios
    print("\nComparación de paradas por radio (km):")
    print(f"{'Radio (km)':<12} | {'Al Centro (Pistas)':<20} | {'A Terminales (T1/T2)':<22}")
    print("-" * 60)
    
    for radio in RADIOS_KM:
        n_centro = len(paradas[paradas['distancia_km'] <= radio])
        n_term = len(paradas[paradas['dist_min_terminal'] <= radio])
        print(f"{radio:<12} | {n_centro:<20} | {n_term:<22}")

    # Guardar
    print("\nGuardando resultados actualizados...")
    paradas.to_csv(RESULTADOS_DIR / "paradas_distancias_terminales.csv", index=False)
    print(f"  - Archivo guardado: {RESULTADOS_DIR / 'paradas_distancias_terminales.csv'}")

    print("\n" + "="*60)
    print("VERIFICACIÓN COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    main()
