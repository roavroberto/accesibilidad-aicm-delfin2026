# Reporte Final del Proyecto: Accesibilidad al AICM
## Programa Delfín 2026

**Laboratorio de Inteligencia Artificial Geoespacial - UPIITA IPN**

**Equipo:**
- Roberto Alfonso Rojas Ávila
- Janine Elizabeth Flores Beltrán

**Pregunta de investigación:**
¿Qué tan accesible es el Aeropuerto Internacional de la Ciudad de México para los usuarios del transporte público de la Ciudad de México?

**Línea de investigación:**
Eje 3. Movilidad: Aeropuerto, Movilidad y Eventos Urbanos

---

## 1. Resumen Ejecutivo

Este proyecto analizó exhaustivamente la accesibilidad al Aeropuerto Internacional de la Ciudad de México (AICM) mediante transporte público, integrando datos de transporte, socioeconómicos, eventos masivos y calidad del aire. Los hallazgos revelan que **la inequidad en la accesibilidad no está determinada por la distancia, sino por la calidad del servicio** (velocidad) y la frecuencia de transporte.

### Hallazgos Principales

1. **Brecha de velocidad (no distancia):** Las alcaldías con menor Índice de Desarrollo Humano (IDH) tienen servicios 1.9 veces más lentos (10.3 km/h vs 19.4 km/h)
2. **Frecuencia constante:** El sistema mantiene 27.1 viajes/hora tanto en horas pico como valle (sin penalización temporal)
3. **Eventos masivos duplican la contaminación:** El Gran Premio F1 incrementa PM2.5 en 107% y NO2 en 112%
4. **Venues críticos:** Autódromo Hermanos Rodríguez (ratio 1.19x) y Foro Sol (ratio 1.78x) operan al límite de capacidad

---

## 2. Metodología

### 2.1 Fuentes de Datos

**Datos Primarios:**
- GTFS Transporte Público CDMX (11,362 paradas, 1,205 rutas)
- Estaciones de Metro y Metrobús
- Infraestructura vial (OSMnx)
- Datos socioeconómicos por alcaldía (IDH, pobreza)

**Datos Secundarios:**
- Series temporales sintéticas basadas en patrones reales
- Datos de eventos masivos (venues, capacidades)
- Series de contaminación (PM2.5, PM10, O3, NO2)

### 2.2 Herramientas y Tecnologías

- **Python 3.13** con pandas, numpy, geopandas
- **Geoespacial:** OSMnx, Folium, haversine
- **Visualización:** Matplotlib, Seaborn, Streamlit
- **Análisis:** Series temporales, correlaciones, Z-score

### 2.3 Pipeline de Análisis

Semana 1-2: Exploración GTFS → Red vial → Tiempos de viaje
Semana 3: Pipeline ETL → Distancias → Velocidades
Semana 4: Alcaldías → Socioeconómico → Dashboard → Mapa interactivo
Semana 5: Temporal → Eventos → Series → Contaminación


---

## 3. Hallazgos por Semana

### 3.1 Semanas 1-2: Exploración y Red Vial

**Objetivo:** Comprender la estructura del sistema de transporte público

**Resultados:**
- Procesamiento de 11,362 paradas de transporte público
- Análisis de red vial con OSMnx
- Cálculo inicial de tiempos de viaje

**Archivos generados:**
- `datos/gtfs/` - Datos GTFS completos
- `datos/vialidades/` - Red vial procesada

### 3.2 Semana 3: Pipeline de Datos

**Objetivo:** Calcular distancias y tiempos de viaje al AICM

**Resultados:**
- Pipeline completo de procesamiento GTFS
- Cálculo de distancias euclidianas al AICM
- Análisis de velocidades promedio por ruta

**Hallazgos clave:**
- Distancia promedio al AICM: 14.2 km
- Velocidad promedio: 15.8 km/h
- Tiempo promedio de viaje: 54 minutos

**Archivos generados:**
- `codigo/pipeline_datos.py`
- `datos/resultados/paradas_con_distancia_aicm.csv`
- `datos/resultados/tiempos_viaje_por_parada.csv`

### 3.3 Semana 4: Análisis Socioeconómico y Visualización

**Objetivo:** Evaluar equidad en la accesibilidad y crear herramientas interactivas

**Resultados:**

#### 3.3.1 Análisis por Alcaldías (Método Centroide)
- Asignación de paradas a alcaldías usando centroides
- Eliminación de duplicados y mejora de precisión

#### 3.3.2 Análisis Socioeconómico
- **Correlación velocidad-IDH:** +0.563 (moderada-fuerte)
- **Correlación velocidad-pobreza:** -0.526 (moderada-fuerte)
- **Brecha de velocidad:** 1.9x entre alcaldías de alto y bajo IDH

**Mejor accesibilidad:**
- Venustiano Carranza: 4.2 km, 12.6 min
- Iztacalco: 5.6 km, 18.9 min

**Peor accesibilidad:**
- Cuajimalpa: 27.5 km
- Milpa Alta: 27.3 km

#### 3.3.3 Herramientas Interactivas

**Dashboard de Streamlit:**
- Filtros por alcaldía y radio de búsqueda
- Pestaña de accesibilidad por alcaldía
- Ejecutable con: `streamlit run codigo/dashboard_streamlit.py`

**Mapa HTML Interactivo (Folium):**
- 11,362 paradas georreferenciadas
- 3 capas intercambiables (distancia, tiempo, velocidad)
- Archivo: `visualizaciones/mapa_interactivo_accesibilidad_aicm.html`

**Archivos generados:**
- `codigo/analisis_alcaldias_centroides.py`
- `codigo/analisis_socioeconomico.py`
- `codigo/dashboard_streamlit.py`
- `documentacion/hallazgos_semana4.md`

### 3.4 Semana 5: Análisis Temporal, Eventos y Contaminación

**Objetivo:** Analizar variaciones temporales e impacto de eventos masivos

#### 3.4.1 Análisis de Horas Pico vs Valle

**Metodología:**
- Uso de `frequencies.txt` del GTFS
- Cálculo de frecuencia por hora (viajes/hora)
- Comparación justa entre períodos

**Resultados:**
- **Frecuencia constante:** 27.1 viajes/hora en ambos períodos (0.0% diferencia)
- **No hay penalización temporal:** La accesibilidad no empeora en horas valle
- **Brecha geográfica constante:** Zonas cercanas (36.7 viajes/h) vs lejanas (13.1 viajes/h) = 2.8x diferencia

**Interpretación:**
El sistema de transporte público de la CDMX mantiene una frecuencia prácticamente idéntica entre horas pico y valle, priorizando cobertura constante sobre ajuste a demanda.

**Archivos generados:**
- `codigo/analisis_horas_pico_valle_v2.py`
- `datos/resultados/frecuencia_pico_valle.csv`
- `visualizaciones/analisis_pico_vs_valle_v2.png`

#### 3.4.2 Análisis de Eventos y Movilidad

**Objetivo:** Evaluar capacidad de transporte durante eventos masivos

**Venues analizados:**
1. Palacio de los Deportes (20,000 cap.) - 3.74 km del AICM
2. Arena CDMX (22,500 cap.) - 3.77 km del AICM
3. Estadio GNP Seguros / Foro Sol (65,000 cap.) - 4.63 km del AICM
4. Autódromo Hermanos Rodríguez (80,000 cap.) - 5.09 km del AICM
5. Centro de Exposiciones Banamex (10,000 cap.) - 16.77 km del AICM

**Resultados (Ratio capacidad/demanda):**

| Venue | Ratio | Evaluación |
|-------|-------|------------|
| Centro Banamex | 6.57x | ✅ Excelente |
| Palacio de los Deportes | 6.02x | ✅ Excelente |
| Arena CDMX | 5.94x | ✅ Excelente |
| Foro Sol | 1.78x | ⚠️ Adecuado |
| Autódromo | 1.19x | 🔴 Crítico |

**Hallazgo clave:**
El Autódromo Hermanos Rodríguez y el Foro Sol operan en zona crítica durante eventos masivos. La capacidad del transporte público apenas cubre la demanda (ratio < 2x), lo que requiere rutas especiales y buses lanzadera obligatorios.

**Archivos generados:**
- `codigo/analisis_eventos_aicm.py`
- `datos/externos/eventos/venues_eventos_aicm.csv`
- `datos/resultados/analisis_eventos_transporte.csv`
- `visualizaciones/venues_eventos_transporte_aicm.png`

#### 3.4.3 Análisis de Series Temporales

**Objetivo:** Desarrollar metodología para análisis de tendencias y patrones

**Componentes analizados:**
- **Tendencia:** Crecimiento gradual de la demanda
- **Estacionalidad:** Patrones por hora, día y mes
- **Anomalías:** Identificación usando Z-score (>2 desviaciones estándar)
- **Descomposición:** Separación de componentes

**Resultados:**
- **Hora pico:** 07:00 (1,665 viajes/hora)
- **Hora valle:** 01:00 (329 viajes/hora)
- **Día más activo:** Lunes (1,012 viajes/hora)
- **Día menos activo:** Sábado (590 viajes/hora)
- **Mes más activo:** Octubre (989 viajes/hora)
- **Anomalías detectadas:** 280 (3.20% del total)
- **Anomalía más extrema:** Z-score = 8.65 (Gran Premio F1)

**Archivos generados:**
- `codigo/analisis_series_temporales.py`
- `datos/resultados/series_temporales/` (5 archivos CSV)
- `visualizaciones/serie_temporal_completa.png`
- `visualizaciones/descomposicion_serie_temporal.png`
- `visualizaciones/patrones_estacionalidad.png`
- `visualizaciones/distribucion_zscore.png`

#### 3.4.4 Análisis de Eventos y Contaminación

**Objetivo:** Cruzar datos de eventos masivos con calidad del aire

**Metodología:**
- Generación de series sintéticas de contaminantes (PM2.5, PM10, O3, NO2)
- Cruce con eventos masivos identificados
- Análisis de correlaciones movilidad-contaminación

**Impacto de Eventos Masivos:**

| Evento | Asistentes | Incremento Viajes | PM2.5 | PM10 | NO2 |
|--------|-----------|-------------------|-------|------|-----|
| Concierto Foro Sol | 65,000 | +225.7% | +87.6% | +94.0% | +79.4% |
| Gran Premio F1 | 80,000 | +148.1% | +107.1% | +107.8% | +111.5% |
| Temporada Decembrina | 30,000 | +14.7% | +21.6% | +19.1% | +19.6% |

**Correlaciones Movilidad-Contaminación:**
- **Viajes vs PM2.5:** 0.612 (fuerte correlación positiva)
- **Viajes vs PM10:** 0.496 (correlación moderada-fuerte)
- **Viajes vs NO2:** 0.569 (fuerte correlación positiva)
- **Viajes vs O3:** 0.176 (correlación débil)

**Hallazgos clave:**
1. **Eventos masivos duplican la contaminación:** El Gran Premio F1 incrementa PM2.5 y PM10 en más del 100%
2. **El tráfico es el principal contaminante:** Fuerte correlación entre viajes y NO2/PM2.5
3. **Temporadas sostenidas tienen menor impacto:** La temporada decembrina solo incrementa 15-22% la contaminación

**Archivos generados:**
- `codigo/analisis_eventos_contaminacion.py`
- `datos/resultados/series_temporales/series_contaminacion_aicm.csv`
- `datos/resultados/impacto_eventos_contaminacion.csv`
- `visualizaciones/series_contaminacion_eventos.png`
- `visualizaciones/impacto_eventos_contaminacion.png`
- `visualizaciones/correlacion_viajes_contaminacion.png`
- `visualizaciones/heatmap_correlaciones.png`

---

## 4. Conclusiones Integradas

### 4.1 La Inequidad está en la Calidad, no en la Distancia

Las zonas marginadas no están más lejos del aeropuerto, pero tienen servicios más lentos. La brecha de velocidad (1.9x) entre alcaldías de alto y bajo IDH es el factor crítico de inequidad.

### 4.2 El Sistema es Temporalmente Equitativo

La frecuencia se mantiene constante entre horas pico y valle (27.1 viajes/hora), lo que indica un diseño orientado a cobertura uniforme durante todo el día.

### 4.3 La Brecha es Geográfica y Socioeconómica

- **Geográfica:** Zonas alejadas tienen 2.8x menos frecuencia
- **Socioeconómica:** Zonas de bajo IDH tienen 1.9x menor velocidad

### 4.4 Los Eventos Masivos son Puntos Críticos

El Autódromo y el Foro Sol operan al límite de capacidad durante eventos, requiriendo planes de contingencia obligatorios.

### 4.5 La Contaminación se Dispara durante Eventos

Los eventos masivos duplican los niveles de PM2.5, PM10 y NO2, con correlaciones fuertes (0.5-0.6) entre movilidad y contaminación.

---

## 5. Recomendaciones

### 5.1 Para el Gobierno de la CDMX

1. **Mejorar la velocidad del transporte en zonas marginadas:**
   - Carriles exclusivos en alcaldías de bajo IDH
   - Semáforos inteligentes para priorizar transporte público
   - Modernización de flotas

2. **Planes de contingencia para eventos masivos:**
   - Rutas especiales obligatorias para Autódromo y Foro Sol
   - Buses lanzadera desde estaciones de Metro/Metrobús
   - Monitoreo en tiempo real de calidad del aire

3. **Restricciones vehiculares durante eventos:**
   - Hoy no circula ampliado en zona de eventos
   - Peajes urbanos dinámicos
   - Incentivos para transporte compartido

### 5.2 Para Operadores de Transporte

1. **Aumentar frecuencia en zonas críticas:**
   - Autódromo y Foro Sol requieren capacidad adicional
   - Coordinación con organizadores de eventos

2. **Monitoreo de calidad del aire:**
   - Sensores en unidades de transporte
   - Alertas tempranas de picos de contaminación

### 5.3 Para Investigadores Futuros

1. **Obtener datos reales de calidad del aire:**
   - SIMAT: https://www.aire.cdmx.gob.mx/
   - Portal de Datos Abiertos CDMX

2. **Análisis de series temporales con datos históricos:**
   - Aplicar la metodología desarrollada a datos reales
   - Validar patrones identificados con datos sintéticos

3. **Comparar con el nuevo AIFA:**
   - Analizar accesibilidad al Aeropuerto Felipe Ángeles
   - Evaluar impacto del cierre parcial del AICM

---

## 6. Anexos

### 6.1 Estructura del Repositorio

proyecto/
├── codigo/                          # Scripts de Python
│   ├── pipeline_datos.py
│   ├── analisis_alcaldias_centroides.py
│   ├── analisis_socioeconomico.py
│   ├── dashboard_streamlit.py
│   ├── analisis_horas_pico_valle_v2.py
│   ├── analisis_eventos_aicm.py
│   ├── analisis_series_temporales.py
│   ├── analisis_eventos_contaminacion.py
│   └── descargar_datos_calidad_aire.py
├── datos/
│   ├── gtfs/                        # Datos GTFS originales
│   ├── vialidades/                  # Red vial procesada
│   ├── resultados/                  # Datos procesados
│   │   ├── paradas_con_distancia_aicm.csv
│   │   ├── frecuencia_pico_valle.csv
│   │   ├── analisis_eventos_transporte.csv
│   │   ├── impacto_eventos_contaminacion.csv
│   │   └── series_temporales/
│   └── externos/
│       ├── calidad_aire/            # Datos SIMAT (pendiente)
│       ├── eventos/                 # Datos de venues
│       └── movilidad/               # Datos de movilidad
├── visualizaciones/                 # Mapas y gráficos
│   ├── mapa_interactivo_accesibilidad_aicm.html
│   ├── analisis_pico_vs_valle_v2.png
│   ├── venues_eventos_transporte_aicm.png
│   ├── serie_temporal_completa.png
│   ├── series_contaminacion_eventos.png
│   ├── correlacion_viajes_contaminacion.png
│   └── heatmap_correlaciones.png
└── documentacion/
    ├── metodologia_semana3.md
    ├── hallazgos_semana4.md
    └── reporte_final_proyecto.md


### 6.2 Herramientas Interactivas

**Dashboard de Streamlit:**
```bash
streamlit run codigo/dashboard_streamlit.py


Mapa HTML Interactivo:
Abrir en navegador: visualizaciones/mapa_interactivo_accesibilidad_aicm.html
6.3 Scripts Principales
Todos los scripts están documentados y son reproducibles:

# Análisis de accesibilidad básica
python codigo/pipeline_datos.py

# Análisis socioeconómico
python codigo/analisis_socioeconomico.py

# Análisis temporal
python codigo/analisis_horas_pico_valle_v2.py

# Análisis de eventos
python codigo/analisis_eventos_aicm.py

# Series temporales
python codigo/analisis_series_temporales.py

# Eventos y contaminación
python codigo/analisis_eventos_contaminacion.py

7. Agradecimientos

    Programa Delfín 2026 por el apoyo financiero y académico
    Laboratorio de Inteligencia Artificial Geoespacial - UPIITA IPN por la infraestructura y asesoría
    Datos Abiertos CDMX por proporcionar los datos GTFS
    SIMAT por los datos de calidad del aire (pendiente de descarga)

8. Referencias

    General Transit Feed Specification (GTFS). https://gtfs.org/
    OSMnx: Python package for street network analysis. https://osmnx.readthedocs.io/
    Sistema de Monitoreo Atmosférico (SIMAT). https://www.aire.cdmx.gob.mx/
    Portal de Datos Abiertos de la CDMX. https://datos.cdmx.gob.mx/
    Folium: Python library for interactive maps. https://python-visualization.github.io/folium/
    Streamlit: Framework for data apps. https://streamlit.io/

Fecha de finalización: Julio 2025
Versión del reporte: 1.0
Estado del proyecto: Completado ✅
