# Análisis de Accesibilidad al AICM

## Programa Delfín 2026
Laboratorio de Inteligencia Artificial Geoespacial - UPIITA IPN

**Equipo:**
- Roberto Alfonso Rojas Ávila
- Janine Elizabeth Flores Beltrán

**Pregunta de investigación:**
¿Qué tan accesible es el Aeropuerto Internacional de la Ciudad de México para los usuarios del transporte público de la Ciudad de México?

**Línea de investigación:**
Eje 3. Movilidad: Aeropuerto, Movilidad y Eventos Urbanos

## Estructura del repositorio

/datos          - Datasets crudos y procesados
/codigo         - Scripts de Python (ETL, análisis, visualización)
/documentacion  - Estado del arte, metodología, bitácoras
/visualizaciones - Mapas, gráficos, dashboards


## Datasets

1. GTFS Transporte Público CDMX
2. Estaciones Metro CDMX
3. Estaciones Metrobús CDMX
4. Infraestructura vial
5. Localización AICM

## Estado actual

- Semana 1: Exploración inicial GTFS completada
- Semana 2: En progreso

## Estado actual (actualizado)

- Semana 1: Exploración inicial GTFS completada
- Semana 2: Análisis de red vial y tiempos de viaje completada
- Semana 3: Pipeline de datos y cálculo de distancias/tiempos completado
- Semana 4: Análisis por alcaldías (método centroide), análisis socioeconómico, mapa interactivo (Folium) y Dashboard (Streamlit) completados

## Hallazgos Principales (Semana 4)

1. **Brecha de Velocidad (No de Distancia):** Las alcaldías con menor Índice de Desarrollo Humano (IDH) no están más lejos del aeropuerto, pero cuentan con servicios de transporte **1.9 veces más lentos** (10.3 km/h vs 19.4 km/h).
2. **Correlaciones Socioeconómicas:** La velocidad del transporte público está fuertemente correlacionada con el IDH (+0.563) y negativamente con el porcentaje de pobreza (-0.526).
3. **Mejor Accesibilidad:** Venustiano Carranza (4.2 km, 12.6 min) e Iztacalco (5.6 km, 18.9 min).
4. **Peor Accesibilidad / Desconexión:** Cuajimalpa (27.5 km) y Milpa Alta (27.3 km), las cuales carecen de rutas directas eficientes.

## Dashboard Interactivo y Visualizaciones

El proyecto cuenta con herramientas interactivas para la exploración de los datos:

### 1. Dashboard de Streamlit
Un panel de control interactivo que permite filtrar paradas por alcaldía, radio de búsqueda y distancia al AICM. Incluye una pestaña dedicada a la "Accesibilidad por Alcaldía".

**Para ejecutar el dashboard:**
```bash
streamlit run codigo/dashboard_streamlit.py
2. Mapa HTML Interactivo (Folium)
Un mapa web independiente con más de 11,000 paradas georreferenciadas, capas intercambiables (distancia, tiempo, velocidad) y marcadores de las terminales T1 y T2.
Para abrir el mapa:
Abre el archivo visualizaciones/mapa_interactivo_accesibilidad_aicm.html en cualquier navegador web.

## Análisis Temporal: Horas Pico vs Horas Valle (Semana 4)

Utilizando el archivo `frequencies.txt` del GTFS, analizamos si la frecuencia del servicio varía entre horas pico (7-9 AM, 6-8 PM) y horas valle (10 AM - 4 PM).

### Hallazgo Principal: Frecuencia Constante

El sistema de transporte público de la CDMX mantiene una **frecuencia prácticamente idéntica** entre ambos períodos:

| Métrica | Hora Pico | Hora Valle | Diferencia |
|---------|-----------|------------|------------|
| Frecuencia promedio | 27.1 viajes/hora | 27.1 viajes/hora | 0.0% |
| Zonas cercanas (<10 km) | 36.7 viajes/hora | 36.5 viajes/hora | 0.4% |
| Zonas lejanas (≥20 km) | 13.1 viajes/hora | 13.3 viajes/hora | -1.2% |

### Interpretación

- **No hay penalización temporal:** La accesibilidad al AICM no empeora en horas valle
- **Diseño orientado a cobertura constante:** El sistema prioriza mantener servicio uniforme durante todo el día
- **La brecha es geográfica, no temporal:** Las zonas lejanas tienen 2.8 veces menos frecuencia que las cercanas, pero esta brecha se mantiene constante en ambos períodos

### Archivos del análisis temporal

- `codigo/analisis_horas_pico_valle_v2.py` - Script de análisis
- `datos/resultados/frecuencia_pico_valle.csv` - Datos procesados
- `visualizaciones/analisis_pico_vs_valle_v2.png` - Gráfico comparativo
- `visualizaciones/alcaldias_pico_vs_valle_v2.png` - Análisis por alcaldía

## Análisis de Eventos y Movilidad (Semana 5)

Analizamos la capacidad del transporte público para atender la demanda de los principales venues de eventos alrededor del AICM.

### Venues Analizados
1. **Palacio de los Deportes** (20,000 cap.) - Ratio: 6.02x ✅
2. **Arena CDMX** (22,500 cap.) - Ratio: 5.94x ✅
3. **Centro de Exposiciones Banamex** (10,000 cap.) - Ratio: 6.57x ✅
4. **Estadio GNP Seguros / Foro Sol** (65,000 cap.) - Ratio: 1.78x ⚠️
5. **Autódromo Hermanos Rodríguez** (80,000 cap.) - Ratio: 1.19x 🔴

### Hallazgo Principal
El **Autódromo Hermanos Rodríguez** y el **Foro Sol** operan en zona crítica durante eventos masivos. La capacidad del transporte público apenas cubre la demanda (ratio < 2x), lo que requiere rutas especiales y buses lanzadera obligatorios para evitar el colapso de la movilidad.
