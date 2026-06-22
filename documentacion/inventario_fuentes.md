# Inventario de Fuentes de Información

## Descripción General

Este documento cataloga todos los conjuntos de datos que serán utilizados en el proyecto de análisis de accesibilidad al Aeropuerto Internacional de la Ciudad de México (AICM) mediante transporte público.

## Tabla Resumen de Datasets

| # | Dataset | Fuente | Formato | Registros | Fecha Actualización | Estado |
|---|---------|--------|---------|-----------|---------------------|--------|
| 1 | GTFS Transporte Público CDMX | Portal Datos Abiertos CDMX | TXT/CSV (ZIP) | 11,362 paradas | Feb 2026 | ✅ Descargado |
| 2 | Estaciones Metro CDMX | Portal Datos Abiertos CDMX | GeoJSON/Shapefile | ~195 estaciones | Pendiente | ⏳ Por descargar |
| 3 | Estaciones Metrobús CDMX | Portal Datos Abiertos CDMX | GeoJSON/Shapefile | ~90 estaciones | Pendiente | ⏳ Por descargar |
| 4 | Líneas Metro CDMX | Portal Datos Abiertos CDMX | Shapefile/GeoJSON | 12 líneas | Pendiente | ⏳ Por descargar |
| 5 | Líneas Metrobús CDMX | Portal Datos Abiertos CDMX | Shapefile/GeoJSON | 7 líneas | Pendiente | ⏳ Por descargar |
| 6 | Infraestructura Vial CDMX | Portal Datos Abiertos CDMX | Shapefile/GeoJSON | Red vial completa | Pendiente | ⏳ Por descargar |
| 7 | Localización AICM | Datos Abiertos CDMX / OSM | GeoJSON/CSV | 1 punto | N/A | ⏳ Por descargar |
| 8 | Límites Alcaldías CDMX | Portal Datos Abiertos CDMX | GeoJSON/Shapefile | 16 alcaldías | Pendiente | ⏳ Por descargar |

---

## Descripción Detallada de Cada Dataset

### 1. GTFS Transporte Público CDMX

**Fuente:** Portal de Datos Abiertos de la Ciudad de México  
**URL:** https://datos.cdmx.mx/dataset/gtfs-transporte-publico  
**Formato:** ZIP conteniendo archivos TXT/CSV  
**Fecha de descarga:** 11 junio 2026  
**Tamaño:** ~50 MB comprimido

**Archivos incluidos:**
- `agency.txt`: Información de agencias de transporte (10 agencias)
- `routes.txt`: Definición de rutas (301 rutas)
- `trips.txt`: Viajes programados
- `stop_times.txt`: Horarios de llegada/salida en paradas
- `stops.txt`: Ubicación de paradas (11,362 paradas con coordenadas)
- `calendar.txt`: Calendario de servicio
- `frequencies.txt`: Frecuencias de servicio
- `shapes.txt`: Geometría de rutas

**Columnas principales (stops.txt):**
- `stop_id`: Identificador único de parada
- `stop_name`: Nombre de la parada
- `stop_lat`: Latitud (WGS84)
- `stop_lon`: Longitud (WGS84)
- `location_type`: Tipo de ubicación (parada, estación, etc.)

**Agencias identificadas:**
1. Metro (Sistema de Transporte Colectivo)
2. Metrobús
3. RTP (Red de Transporte de Pasajeros)
4. Trolebús
5. STE (Servicios de Transporte Expreso)
6. Corredores concesionados
7. Otros operadores

**Utilidad para el proyecto:**
- Identificar todas las paradas de transporte público en CDMX
- Filtrar paradas cercanas al AICM (< 2 km)
- Identificar rutas que llegan al aeropuerto
- Calcular tiempos de viaje y conectividad

**Problemas potenciales:**
- Archivos TXT requieren procesamiento especial
- Coordenadas en WGS84 (necesitan validación de rango)
- Tamaño considerable requiere optimización de memoria

---

### 2. Estaciones Metro CDMX

**Fuente:** Portal de Datos Abiertos de la Ciudad de México  
**URL:** https://datos.cdmx.mx/dataset/estaciones-metro  
**Formato:** GeoJSON / Shapefile  
**Registros esperados:** ~195 estaciones  
**Fecha actualización:** Pendiente verificar

**Columnas esperadas:**
- `id`: Identificador único
- `nombre`: Nombre de la estación
- `linea`: Número de línea (1-12)
- `latitud`: Coordenada Y (WGS84)
- `longitud`: Coordenada X (WGS84)
- `alcaldia`: Alcaldía donde se ubica

**Utilidad para el proyecto:**
- Identificar estaciones de Metro con conexión al AICM
- Calcular distancias desde cada estación al aeropuerto
- Analizar cobertura espacial del Metro

**Notas:**
- El Metro tiene conexión directa al AICM (Línea 5, estación Terminal Aérea)
- Necesita validación de coordenadas
- Puede requerir conversión de formato

---

### 3. Estaciones Metrobús CDMX

**Fuente:** Portal de Datos Abiertos de la Ciudad de México  
**URL:** https://datos.cdmx.mx/dataset/estaciones-metrobus  
**Formato:** GeoJSON / Shapefile  
**Registros esperados:** ~90 estaciones  
**Fecha actualización:** Pendiente verificar

**Columnas esperadas:**
- `id`: Identificador único
- `nombre`: Nombre de la estación
- `linea`: Número de línea (1-7)
- `latitud`: Coordenada Y (WGS84)
- `longitud`: Coordenada X (WGS84)
- `alcaldia`: Alcaldía donde se ubica

**Utilidad para el proyecto:**
- Identificar estaciones de Metrobús con conexión al AICM
- Línea 4 tiene ruta directa al aeropuerto
- Línea 5 pasa cerca del AICM
- Calcular distancias y accesibilidad

**Notas:**
- Metrobús es mencionado frecuentemente en literatura como solución de conectividad aeroportuaria
- Necesita validación de coordenadas

---

### 4. Líneas Metro CDMX

**Fuente:** Portal de Datos Abiertos de la Ciudad de México  
**URL:** https://datos.cdmx.mx/dataset/lineas-metro  
**Formato:** Shapefile / GeoJSON  
**Registros esperados:** 12 líneas  
**Fecha actualización:** Pendiente verificar

**Columnas esperadas:**
- `id`: Identificador de línea
- `nombre`: Nombre/número de línea
- `color`: Color identificator
- `geometry`: Geometría de la línea (polilínea)

**Utilidad para el proyecto:**
- Visualizar red completa de Metro
- Identificar conexiones entre líneas
- Analizar cobertura espacial

---

### 5. Líneas Metrobús CDMX

**Fuente:** Portal de Datos Abiertos de la Ciudad de México  
**URL:** https://datos.cdmx.mx/dataset/lineas-metrobus  
**Formato:** Shapefile / GeoJSON  
**Registros esperados:** 7 líneas  
**Fecha actualización:** Pendiente verificar

**Columnas esperadas:**
- `id`: Identificador de línea
- `nombre`: Nombre/número de línea
- `geometry`: Geometría de la línea (polilínea)

**Utilidad para el proyecto:**
- Visualizar red completa de Metrobús
- Identificar rutas que llegan al aeropuerto
- Analizar conectividad con otras líneas

---

### 6. Infraestructura Vial CDMX

**Fuente:** Portal de Datos Abiertos de la Ciudad de México  
**URL:** https://datos.cdmx.mx/dataset/infraestructura-vial  
**Formato:** Shapefile / GeoJSON  
**Registros esperados:** Red vial completa  
**Fecha actualización:** Pendiente verificar

**Columnas esperadas:**
- `id`: Identificador de vía
- `nombre`: Nombre de la vía
- `tipo`: Tipo de vía (primaria, secundaria, etc.)
- `geometry`: Geometría de la vía (polilínea)

**Utilidad para el proyecto:**
- Análisis de conectividad vial al aeropuerto
- Cálculo de distancias en red (no solo euclidianas)
- Identificar principales vías de acceso al AICM

**Notas:**
- Dataset puede ser muy grande
- Requiere procesamiento eficiente

---

### 7. Localización AICM

**Fuente:** Portal de Datos Abiertos CDMX / OpenStreetMap  
**URL:** Múltiples fuentes posibles  
**Formato:** GeoJSON / CSV  
**Registros:** 1 punto (o varios si se consideran terminales)  
**Coordenadas esperadas:** 19.4361, -99.0719 (aproximado)

**Columnas esperadas:**
- `nombre`: "Aeropuerto Internacional de la Ciudad de México"
- `tipo`: "Aeropuerto"
- `latitud`: 19.4361
- `longitud`: -99.0719

**Utilidad para el proyecto:**
- Punto de referencia para cálculos de distancia
- Centro del análisis de accesibilidad
- Base para buffer de 2 km

**Notas:**
- Puede incluir terminales T1 y T2 como puntos separados
- Coordenadas deben ser validadas

---

### 8. Límites Alcaldías CDMX

**Fuente:** Portal de Datos Abiertos de la Ciudad de México  
**URL:** https://datos.cdmx.mx/dataset/limites-alcaldias  
**Formato:** GeoJSON / Shapefile  
**Registros:** 16 alcaldías  
**Fecha actualización:** Pendiente verificar

**Columnas esperadas:**
- `id`: Identificador de alcaldía
- `nombre`: Nombre de la alcaldía
- `geometry`: Polígono de límites

**Utilidad para el proyecto:**
- Análisis de accesibilidad por alcaldía
- Clasificación de zonas según nivel de conectividad
- Visualización de resultados por zona administrativa

**Alcaldías de la CDMX:**
1. Álvaro Obregón
2. Azcapotzalco
3. Benito Juárez
4. Coyoacán
5. Cuajimalpa
6. Cuauhtémoc
7. Gustavo A. Madero
8. Iztacalco
9. Iztapalapa
10. Magdalena Contreras
11. Miguel Hidalgo
12. Milpa Alta
13. Tláhuac
14. Tlalpan
15. Venustiano Carranza
16. Xochimilco

**Notas:**
- El AICM se ubica en la alcaldía Venustiano Carranza
- Necesario para análisis espacial por zona

---

## Plan de Descarga de Datos

### Prioridad 1 (Semana 2 - Hoy/Mañana)
- ✅ GTFS (ya descargado)
- ⏳ Estaciones Metro
- ⏳ Estaciones Metrobús
- ⏳ Localización AICM

### Prioridad 2 (Semana 3)
- ⏳ Límites Alcaldías
- ⏳ Líneas Metro
- ⏳ Líneas Metrobús

### Prioridad 3 (Semana 4)
- ⏳ Infraestructura Vial (si es necesario)

---

## Validación de Calidad de Datos

Para cada dataset se verificará:

1. **Integridad:**
   - ¿Todos los registros tienen coordenadas?
   - ¿Hay valores nulos en campos críticos?

2. **Consistencia:**
   - ¿Las coordenadas están en el rango de CDMX?
     - Latitud: 19.2 a 19.6
     - Longitud: -99.4 a -98.9
   - ¿Los sistemas de coordenadas son consistentes (WGS84)?

3. **Actualización:**
   - ¿Cuándo fue la última actualización?
   - ¿Los datos reflejan la realidad actual?

4. **Completitud:**
   - ¿Faltan rutas o estaciones?
   - ¿Hay cobertura completa de la ZMVM?

---

## Notas sobre Acceso a Datos

**Portal de Datos Abiertos CDMX:**
- URL principal: https://datos.cdmx.mx/
- No requiere autenticación para descarga
- Formatos disponibles: CSV, GeoJSON, Shapefile, Excel
- Documentación variable (algunos datasets tienen metadatos completos)

**OpenStreetMap (OSM):**
- URL: https://www.openstreetmap.org/
- Alternativa si datos oficiales no están disponibles
- Requiere herramientas de extracción (Overpass API, QGIS)

**Consideraciones legales:**
- Todos los datos son de acceso público
- Se debe dar crédito a las fuentes
- Uso académico/investigación está permitido
- No hay restricciones de redistribución para fines académicos

---

## Próximos Pasos

1. **Hoy (21 junio):**
   - Descargar Estaciones Metro
   - Descargar Estaciones Metrobús
   - Crear/localizar dataset de AICM
   - Validar coordenadas de todos los datasets

2. **Mañana (22 junio):**
   - Descargar Límites Alcaldías
   - Explorar estructura de cada dataset
   - Documentar problemas encontrados
   - Actualizar este inventario con resultados

3. **Semana 3:**
   - Descargar datasets restantes
   - Iniciar ETL (limpieza y transformación)
   - Integrar datasets en formato común
