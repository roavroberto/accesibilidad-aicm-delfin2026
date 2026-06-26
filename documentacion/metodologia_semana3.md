# Documento Metodológico - Semana 3
## Programa Delfín 2026 - Accesibilidad al AICM
### Roberto Rojas Avila y Janine

---

## 1. INTRODUCCIÓN

### 1.1 Contexto

El Aeropuerto Internacional de la Ciudad de México (AICM) es la principal terminal aérea del país y uno de los más transitados de América Latina. La accesibilidad al aeropuerto mediante transporte público es un tema crítico para la equidad territorial y la eficiencia del sistema de movilidad urbana.

### 1.2 Objetivos de la Semana 3

1. **Diseñar e implementar un pipeline de datos** completo y reproducible
2. **Calcular tiempos de viaje reales** desde las paradas de transporte público hacia las Terminales 1 y 2
3. **Definir métricas de accesibilidad** para comparar zonas de la ciudad
4. **Documentar metodológicamente** todo el proceso de análisis

### 1.3 Preguntas de Investigación

- ¿Cuál es el tiempo promedio de viaje desde diferentes zonas de la CDMX al AICM?
- ¿Qué rutas de transporte público son más eficientes (mayor velocidad)?
- ¿Existen zonas con peor accesibilidad temporal al aeropuerto?
- ¿Cómo varía la accesibilidad según la hora del día?

---

## 2. ARQUITECTURA DEL PIPELINE DE DATOS

### 2.1 Estructura del Pipeline

┌─────────────────┐
│  DATOS GTFS     │
│  (stops.txt,    │
│   stop_times,   │
│   trips.txt,    │
│   routes.txt)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CARGA Y        │
│  PREPROCESAM.   │
│  (Python/       │
│   Pandas)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IDENTIFICACIÓN │
│  DE RUTAS AL    │
│  AEROPUERTO     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CÁLCULO DE     │
│  DISTANCIAS     │
│  (Haversine +   │
│   Red Vial)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CÁLCULO DE     │
│  TIEMPOS DE     │
│  VIAJE          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ANÁLISIS DE    │
│  VELOCIDAD      │
│  PROMEDIO       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  VISUALIZACIÓN  │
│  Y REPORTES     │
└─────────────────┘


### 2.2 Scripts del Pipeline

| Script | Función | Entrada | Salida |
|--------|---------|---------|--------|
| `01_cargar_gtfs.py` | Carga datos GTFS | Archivos GTFS | DataFrames |
| `02_identificar_rutas_aeropuerto.py` | Identifica rutas al AICM | routes.txt | Lista de rutas |
| `03_calcular_distancias.py` | Calcula distancias euclidianas | stops.txt | distancias_euclidianas.csv |
| `04_calcular_distancias_red_vial.py` | Calcula distancias reales | Red vial OSM | distancias_red_vial.csv |
| `05_calcular_tiempos_viaje.py` | Calcula tiempos de viaje | stop_times.txt | tiempos_viaje_por_parada.csv |
| `06_analisis_velocidad_promedio.py` | Analiza velocidad | Tiempos + distancias | velocidad_promedio_filtrado.csv |
| `07_mapa_calor_accesibilidad.py` | Genera mapas de calor | Datos procesados | Visualizaciones PNG |

### 2.3 Dependencias y Entorno

**Lenguaje:** Python 3.13

**Librerías principales:**
- pandas (2.2.0) - Manipulación de datos
- numpy (1.26.0) - Cálculos numéricos
- geopandas (0.14.0) - Datos geoespaciales
- osmnx (1.9.0) - Descarga de red vial
- networkx (3.2.0) - Análisis de grafos
- matplotlib (3.8.0) - Visualizaciones
- scikit-learn (1.4.0) - Cálculos de distancia

**Archivo de entorno:** `environment.yml`

---

## 3. METODOLOGÍA DETALLADA

### 3.1 Cálculo de Distancias

#### 3.1.1 Distancia Euclidiana (Haversine)

**Fórmula:**

a = sin²(Δφ/2) + cos(φ1) · cos(φ2) · sin²(Δλ/2)
c = 2 · atan2(√a, √(1-a))
d = R · c


Donde:
- φ1, φ2 = latitudes en radianes
- Δφ = diferencia de latitudes
- Δλ = diferencia de longitudes
- R = radio terrestre (6,371 km)

**Implementación:**
```python
from sklearn.metrics.pairwise import haversine_distances

# Convertir coordenadas a radianes
coords_rad = np.radians(coords)

# Calcular matriz de distancias
dist_matrix = haversine_distances(coords_rad) * 6371

3.1.2 Distancia en Red Vial
Algoritmo: Dijkstra de fuente única
Proceso:

    Descargar red vial de OpenStreetMap usando OSMnx
    Identificar nodo más cercano al AICM
    Calcular distancias desde ese nodo a todos los demás
    Asignar distancia a cada parada según su nodo más cercano

Implementación:

python

import osmnx as ox
import networkx as nx

# Descargar red vial
G = ox.graph_from_point((lat, lon), dist=20000, network_type='drive')

# Encontrar nodo más cercano al AICM
aicm_node = ox.distance.nearest_nodes(G, aicm_lon, aicm_lat)

# Calcular distancias desde el AICM
distances = nx.single_source_dijkstra_path_length(G, aicm_node, weight='length')

3.1.3 Factor de Desvío
Definición:

 Factor de Desvío = Distancia Real / Distancia Euclidiana

Resultado: 1.52x (las distancias reales son 52% mayores que las euclidianas)
3.2 Cálculo de Tiempos de Viaje
3.2.1 Identificación de Rutas al Aeropuerto
Criterios:

    Rutas que mencionan "aeropuerto", "aero", "terminal" en route_long_name
    Rutas que pasan por paradas identificadas como del aeropuerto

Paradas del Aeropuerto:

    Terminal 1: B_0300L4-AEROT1 (19.43531, -99.08367)
    Terminal 2: B_0300L4-AEROT2 (19.42148, -99.07725)
    Metro Aeropuerto: B_010Z4J01-METRAERO (19.419165, -99.096465)

Resultado: 10 rutas identificadas, 30 viajes que pasan por el aeropuerto
3.2.2 Cálculo de Tiempos desde Cada Parada
Algoritmo:

    Para cada viaje que pasa por el aeropuerto:
        Ordenar paradas por stop_sequence
        Identificar primera parada del aeropuerto
        Para cada parada anterior, calcular: tiempo_viaje = tiempo_aeropuerto - tiempo_parada

Conversión de tiempos:

python

def convertir_tiempo_a_minutos(time_str):
    """Convierte HH:MM:SS a minutos desde medianoche"""
    hours, minutes, seconds = map(int, time_str.split(':'))
    return hours * 60 + minutes + seconds / 60

Filtros de calidad:

    Tiempo de viaje > 0 minutos
    Tiempo de viaje < 300 minutos (5 horas)

Resultado: 317 tiempos de viaje calculados desde 172 paradas únicas
3.2.3 Estadísticas por Parada
Métricas calculadas:

    Tiempo promedio (min)
    Desviación estándar (min)
    Tiempo mínimo (min)
    Tiempo máximo (min)
    Número de viajes observados

3.3 Análisis de Velocidad Promedio
3.3.1 Fórmula de Velocidad

Velocidad (km/h) = Distancia (km) / Tiempo (horas)
                 = Distancia (km) / (Tiempo (min) / 60)

3.3.2 Filtros de Calidad
Para garantizar resultados realistas, se aplicaron tres filtros:

    Distancia mínima ≥ 2 km:
        Paradas muy cercanas tienen tiempos no confiables
        Descartadas: 4 paradas
    Velocidad máxima ≤ 60 km/h:
        Transporte público urbano no puede exceder 60 km/h
        Descartadas: 6 paradas
    Velocidad mínima ≥ 5 km/h:
        Menos que eso es velocidad de caminata
        Descartadas: 0 paradas

Resultado final: 162 paradas con velocidades válidas
3.3.3 Validación de Resultados
Velocidades esperadas según modo de transporte:

    Autobús urbano: 15-25 km/h
    Metrobús (carril exclusivo): 20-30 km/h
    Metro (incluyendo paradas): 25-35 km/h

Resultados obtenidos:

    Promedio: 16.7 km/h ✓ (consistente con autobús urbano)
    Mediana: 16.6 km/h ✓
    Máximo: 55.6 km/h ✓ (razonable para carril exclusivo)
    Mínimo: 5.5 km/h ✓ (congestión extrema)

4. MÉTRICAS DE ACCESIBILIDAD
4.1 Definición de Accesibilidad
Accesibilidad al AICM se define como la facilidad con la que un usuario puede llegar al aeropuerto desde una zona determinada, considerando:

    Distancia real (km) por la red vial
    Tiempo de viaje (min) en transporte público
    Velocidad promedio (km/h) del servicio
    Frecuencia de servicio (viajes/hora)

4.2 Métricas Implementadas
4.2.1 Distancia de Accesibilidad

python

distancia_accesibilidad = distancia_red_vial_km

Interpretación:

    < 5 km: Alta accesibilidad
    5-10 km: Accesibilidad media
    10-20 km: Accesibilidad baja

        20 km: Muy baja accesibilidad

4.2.2 Tiempo de Accesibilidad

python

tiempo_accesibilidad = tiempo_promedio_min

Interpretación:

    < 20 min: Alta accesibilidad
    20-40 min: Accesibilidad media
    40-60 min: Accesibilidad baja

        60 min: Muy baja accesibilidad

4.2.3 Índice de Velocidad

python

indice_velocidad = velocidad_promedio_kmh

Interpretación:

        25 km/h: Servicio eficiente

    15-25 km/h: Servicio aceptable
    10-15 km/h: Servicio lento
    < 10 km/h: Servicio muy lento

4.2.4 Frecuencia de Servicio

python

frecuencia_servicio = num_viajes_por_hora

Interpretación:

        6 viajes/hora: Alta frecuencia (cada 10 min)

    3-6 viajes/hora: Frecuencia media (cada 10-20 min)
    1-3 viajes/hora: Baja frecuencia (cada 20-60 min)
    < 1 viaje/hora: Servicio muy limitado

4.3 Análisis Multi-Radio
Se evaluó la accesibilidad en 4 umbrales de distancia:
Radio
	
Paradas
	
Interpretación
0.5 km
	
3 paradas
	
Accesibilidad peatonal inmediata
1.0 km
	
11 paradas
	
Accesibilidad peatonal
2.0 km
	
155 paradas
	
Accesibilidad en transporte local
5.0 km
	
1,141 paradas
	
Accesibilidad metropolitana
5. LIMITACIONES Y SUPUESTOS
5.1 Limitaciones de los Datos

    Cobertura temporal limitada:
        Los datos GTFS representan un día típico
        No capturan variaciones estacionales o eventos especiales
        Frecuencias observadas: 316 viajes a las 00:00, 1 viaje a la 01:00
        Esto sugiere datos incompletos o servicio nocturno predominante
    Cobertura geográfica:
        Solo se analizó CDMX, no el Estado de México
        Muchos pasajeros provienen de municipios conurbados no incluidos
    Ausencia de datos de congestión:
        Los tiempos de viaje no consideran tráfico en horas pico
        Se asume velocidad constante independientemente de la hora
    Transbordos no considerados:
        El análisis solo calcula tiempos directos
        No se consideran viajes con transbordos (más comunes)

5.2 Supuestos Metodológicos

    Velocidad constante:
        Se asume que el autobús viaja a velocidad constante entre paradas
        En realidad, la velocidad varía según congestión, semáforos, etc.
    Tiempos de espera no incluidos:
        El cálculo solo considera tiempo en vehículo
        No incluye tiempo de espera en la parada
    Accesibilidad peatonal no considerada:
        Se asume que el usuario ya está en la parada
        No se calcula tiempo desde el origen real del usuario hasta la parada
    Capacidad no considerada:
        No se analiza si las rutas tienen capacidad suficiente
        En horas pico, algunas rutas pueden estar saturadas

5.3 Validación de Resultados
Comparación con velocidades esperadas:

    ✓ Promedio de 16.7 km/h es consistente con autobús urbano
    ✓ Rutas más rápidas (Rio Churubusco) coinciden con Metrobús
    ✓ Rutas más lentas (Oceanía, Loreto Fabela) coinciden con zonas congestionadas

Comparación con distancias esperadas:

    ✓ Factor de desvío de 1.52x es consistente con literatura
    ✓ Distancia promedio de 15.29 km es razonable para CDMX

6. PROTOCOLO DE REPLICABILIDAD
6.1 Requisitos de Hardware

    RAM mínima: 8 GB (16 GB recomendado)
    Almacenamiento: 500 MB para datos procesados
    Procesador: Multi-core recomendado para cálculos de red vial

6.2 Instalación del Entorno

# Crear entorno conda
conda env create -f environment.yml

# Activar entorno
conda activate accesibilidad-aicm

# Verificar instalación
python -c "import pandas, geopandas, osmnx; print('OK')"

6.3 Ejecución del Pipeline

# Ejecutar todos los scripts en orden
for script in codigo/*.py; do
    echo "Ejecutando $script..."
    python "$script"
done

6.4 Estructura de Archivos Esperada

proyecto/
├── codigo/
│   ├── 01_cargar_gtfs.py
│   ├── 02_identificar_rutas_aeropuerto.py
│   ├── 03_calcular_distancias.py
│   ├── 04_calcular_distancias_red_vial.py
│   ├── 05_calcular_tiempos_viaje.py
│   ├── 06_analisis_velocidad_promedio.py
│   └── 07_mapa_calor_accesibilidad.py
├── datos/
│   ├── gtfs/ (archivos originales)
│   ├── vialidades/ (red vial OSM)
│   └── resultados/ (datos procesados)
├── visualizaciones/ (mapas y gráficos)
├── documentacion/ (documentos metodológicos)
└── README.md

6.5 Tiempos de Ejecución Estimados
Script
	
Tiempo estimado
Carga de datos GTFS
	
10 segundos
Identificación de rutas
	
5 segundos
Cálculo de distancias euclidianas
	
30 segundos
Cálculo de distancias en red vial
	
5-10 minutos
Cálculo de tiempos de viaje
	
1 minuto
Análisis de velocidad
	
30 segundos
Generación de mapas
	
2-5 minutos
Total estimado: 10-20 minutos
7. RESULTADOS Y HALLAZGOS
7.1 Hallazgos Principales
7.1.1 Asimetría entre Terminales

    Terminal 2: 11 paradas a menos de 1 km
    Terminal 1: 0 paradas a menos de 1 km
    Conclusión: Existe desigualdad territorial en el acceso

7.1.2 Factor de Desvío

    Distancia euclidiana promedio: 3.50 km
    Distancia real promedio: 5.00 km
    Factor de desvío: 1.52x
    Implicación: Las distancias en línea recta subestiman la accesibilidad real en 52%

7.1.3 Velocidad Promedio Baja

    Velocidad promedio: 16.7 km/h
    67.5% de las paradas tienen velocidad < 20 km/h
    Conclusión: El transporte público al aeropuerto es lento y congestionado

7.1.4 Patrones Geográficos
Rutas más rápidas (Rio Churubusco):

    Velocidades de 30-55 km/h
    Corresponde a Metrobús Línea 2 con carril exclusivo
    Demuestra que infraestructura dedicada mejora velocidad

Rutas más lentas (Oceanía, Loreto Fabela):

    Velocidades de 5-7 km/h
    Zonas sin infraestructura dedicada
    Congestión extrema similar a velocidad de caminata

7.2 Contribuciones del Proyecto

    Metodológica:
        Pipeline completo y reproducible
        Corrección del punto de medición (terminales vs centro)
        Cálculo de factor de desvío
    Empírica:
        Primera cuantificación completa de accesibilidad al AICM
        Identificación de asimetría entre terminales
        Análisis de velocidad por ruta
    Técnica:
        Integración de datos GTFS con red vial OSM
        Filtros de calidad para velocidades realistas
        Visualizaciones comparables

7.3 Implicaciones para Políticas Públicas

    Mejorar accesibilidad en Terminal 1:
        Implementar rutas directas desde zonas residenciales
        Considerar servicio tipo Airport Express
    Expandir infraestructura dedicada:
        Metrobús ha demostrado ser eficiente (30-55 km/h)
        Evaluar expansión de carriles exclusivos
    Atender zonas congestionadas:
        Oceanía y Loreto Fabela tienen velocidades de caminata
        Considerar soluciones de movilidad alternativas

8. PRÓXIMOS PASOS (SEMANA 4)
8.1 Análisis por Alcaldías

    Cruzar datos de accesibilidad con límites administrativos
    Identificar alcaldías con peor acceso al aeropuerto
    Analizar correlación con indicadores socioeconómicos

8.2 Integración de Datos Socioeconómicos

    Obtener datos de CONEVAL/INEGI por alcaldía
    Analizar si zonas marginadas tienen peor accesibilidad
    Evaluar equidad territorial

8.3 Dashboard Interactivo

    Crear aplicación web con visualizaciones interactivas
    Permitir consulta de accesibilidad desde cualquier punto
    Incluir filtros por hora, modo de transporte, etc.

8.4 Documento Final

    Consolidar todos los hallazgos
    Redactar artículo científico
    Preparar presentación final

9. REFERENCIAS

    Fayyaz, S., et al. (2017). "GTFS-based accessibility analysis"
    Wessel, N., & Farber, S. (2019). "Validation of GTFS data accuracy"
    Javanmard, M., et al. (2025). "Real-time GTFS applications"
    Linares Zarco, J. (2024). "Conectividad del AIFA"
    Moreno & Rivero. "Accesibilidad del NAICM"
    Salgado & Camarena (2021). "Infraestructura de movilidad en CDMX"
    González, R. (2013). "Tipología de accesibilidad"

10. ANEXOS
10.1 Glosario de Términos

    GTFS: General Transit Feed Specification - estándar para datos de transporte público
    Haversine: fórmula para calcular distancia entre dos puntos en una esfera
    Dijkstra: algoritmo para encontrar el camino más corto en un grafo
    OSMnx: librería de Python para descargar y analizar datos de OpenStreetMap

10.2 Diccionario de Datos
Archivo: tiempos_viaje_por_parada.csv
Columna
	
Tipo
	
Descripción
stop_id
	
string
	
Identificador único de la parada
stop_name
	
string
	
Nombre de la parada
stop_lat
	
float
	
Latitud de la parada
stop_lon
	
float
	
Longitud de la parada
tiempo_promedio_min
	
float
	
Tiempo promedio de viaje al AICM (min)
tiempo_std_min
	
float
	
Desviación estándar del tiempo (min)
tiempo_min_min
	
float
	
Tiempo mínimo observado (min)
tiempo_max_min
	
float
	
Tiempo máximo observado (min)
num_viajes
	
int
	
Número de viajes observados
Archivo: velocidad_promedio_filtrado.csv
Columna
	
Tipo
	
Descripción
stop_id
	
string
	
Identificador único de la parada
stop_name
	
string
	
Nombre de la parada
distancia_km
	
float
	
Distancia al AICM por red vial (km)
tiempo_promedio_min
	
float
	
Tiempo promedio de viaje (min)
velocidad_kmh
	
float
	
Velocidad promedio calculada (km/h)
10.3 Código Fuente
Todo el código está disponible en:
GitHub: https://github.com/roavroberto/accesibilidad-aicm-delfin2026
Documento elaborado por: Roberto Rojas Avila y Janine Flores Beltran
Programa: Programa Delfín 2026
Fecha: 27 de junio de 2026
Versión: 1.0
