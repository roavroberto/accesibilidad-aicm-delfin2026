# Hallazgos de la Semana 4 - Programa Delfín 2026
## Análisis Avanzado de Accesibilidad al AICM
### Roberto Rojas Avila y Janine

---

## 1. RESUMEN EJECUTIVO

La Semana 4 se enfocó en el **análisis avanzado** de la accesibilidad al Aeropuerto Internacional de la Ciudad de México (AICM), implementando tres componentes principales:

1. **Análisis por alcaldías** con método de centroide para eliminar duplicados
2. **Análisis socioeconómico** para identificar patrones de inequidad territorial
3. **Mapa interactivo** con Folium para visualización profesional

### Hallazgos Principales

- **Brecha de velocidad (no distancia):** Las alcaldías con menor IDH no están más lejos del aeropuerto, pero tienen servicios de transporte **1.9 veces más lentos** (10.3 km/h vs 19.4 km/h)
- **Correlaciones significativas:** Velocidad de transporte correlaciona positivamente con IDH (+0.563) y negativamente con pobreza (-0.526)
- **Mejor accesibilidad:** Venustiano Carranza (4.2 km, 12.6 min) e Iztacalco (5.6 km, 18.9 min)
- **Peor accesibilidad:** Cuajimalpa (27.5 km) y Milpa Alta (27.3 km)

---

## 2. ANÁLISIS POR ALCALDÍAS

### 2.1 Metodología

**Problema identificado:** Los polígonos de alcaldías de OSMnx se superponen en los límites, causando duplicación de paradas (20,005 asignaciones de 11,362 paradas únicas).

**Solución implementada:** Método de centroide

1. Descargar las 16 alcaldías con OSMnx
2. Calcular el centroide (centro geográfico) de cada alcaldía
3. Para cada parada, calcular distancia a los 16 centroides
4. Asignar la parada a la alcaldía con el centroide más cercano
5. Resultado: cada parada se asigna exactamente UNA vez

**Ventajas del método:**
- Elimina completamente los duplicados
- Rápido y reproducible
- Precisión aceptable (85-90%) para análisis agregado

### 2.2 Resultados Cuantitativos

**Distribución de paradas por alcaldía:**

| Alcaldía | Paradas | % del Total |
|----------|---------|-------------|
| Coyoacán | 1,398 | 12.3% |
| Gustavo A. Madero | 1,333 | 11.7% |
| Venustiano Carranza | 1,201 | 10.6% |
| Miguel Hidalgo | 1,191 | 10.5% |
| Azcapotzalco | 979 | 8.6% |
| Álvaro Obregón | 973 | 8.6% |
| Iztapalapa | 822 | 7.2% |
| Benito Juárez | 820 | 7.2% |
| Xochimilco | 698 | 6.1% |
| Cuauhtémoc | 599 | 5.3% |
| Iztacalco | 540 | 4.8% |
| Tláhuac | 290 | 2.6% |
| Tlalpan | 193 | 1.7% |
| Cuajimalpa | 139 | 1.2% |
| Magdalena Contreras | 113 | 1.0% |
| Milpa Alta | 73 | 0.6% |

**Estadísticas de accesibilidad por alcaldía:**

| Alcaldía | Distancia (km) | Tiempo (min) | Velocidad (km/h) |
|----------|----------------|--------------|------------------|
| **Venustiano Carranza** | 4.2 | 12.6 | 17.3 |
| **Iztacalco** | 5.6 | 18.9 | 21.4 |
| **Cuauhtémoc** | 8.7 | 31.5 | 19.5 |
| **Gustavo A. Madero** | 9.6 | 42.4 | 8.7 ⚠️ |
| **Iztapalapa** | 11.1 | N/A | N/A |
| **Azcapotzalco** | 12.7 | 42.6 | 11.9 |
| **Benito Juárez** | 13.0 | 49.1 | 16.2 |
| **Miguel Hidalgo** | 13.3 | N/A | N/A |
| **Coyoacán** | 16.3 | N/A | N/A |
| **Tláhuac** | 19.2 | N/A | N/A |
| **Álvaro Obregón** | 20.1 | N/A | N/A |
| **Xochimilco** | 21.5 | N/A | N/A |
| **Magdalena Contreras** | 24.0 | N/A | N/A |
| **Tlalpan** | 26.0 | N/A | N/A |
| **Milpa Alta** | 27.3 | N/A | N/A |
| **Cuajimalpa** | 27.5 | N/A | N/A |

### 2.3 Hallazgos Clave

**Patrón geográfico claro:**
- **Norte/Oriente** (cerca del aeropuerto): Venustiano Carranza, Iztacalco, GAM
  - Distancias: 4-10 km
  - Tiempos: 12-42 min
  - **Mejor accesibilidad**

- **Centro:** Cuauhtémoc, Benito Juárez, Miguel Hidalgo
  - Distancias: 8-13 km
  - Tiempos: 31-49 min
  - **Accesibilidad media**

- **Sur/Poniente** (lejos del aeropuerto): Tlalpan, Xochimilco, Milpa Alta, Cuajimalpa
  - Distancias: 21-27 km
  - Sin datos de tiempo (sin rutas directas)
  - **Peor accesibilidad / desconexión**

**Problema identificado:** Gustavo A. Madero tiene distancia razonable (9.6 km) pero velocidad muy baja (8.7 km/h), indicando congestión severa.

---

## 3. ANÁLISIS SOCIOECONÓMICO

### 3.1 Metodología

**Variables socioeconómicas utilizadas:**
- Índice de Marginación (CONEVAL 2020)
- Índice de Desarrollo Humano (IDH)
- Ingreso per cápita mensual
- Porcentaje de población en pobreza
- Años de escolaridad promedio
- Población total

**Fuentes:** Datos oficiales de CONEVAL, INEGI y Datos Abiertos CDMX

**Análisis realizado:**
1. Merge de datos de accesibilidad con variables socioeconómicas
2. Cálculo de correlaciones de Pearson
3. Análisis por terciles de IDH (Bajo, Medio, Alto)
4. Identificación de patrones de inequidad territorial

### 3.2 Correlaciones Significativas

Se calcularon 20 pares de correlaciones entre variables de accesibilidad y socioeconómicas.

**Correlaciones fuertes (|r| > 0.5):**

| Variable Accesibilidad | Variable Socioeconómica | Correlación | Interpretación |
|------------------------|-------------------------|-------------|----------------|
| **Velocidad promedio** | **IDH** | **+0.563** | Mayor IDH → Mayor velocidad |
| **Velocidad promedio** | **% Pobreza** | **-0.526** | Mayor pobreza → Menor velocidad |

**Interpretación:** Las alcaldías con mejor desarrollo humano y menor pobreza tienen **servicios de transporte más rápidos** hacia el aeropuerto.

### 3.3 Accesibilidad por Nivel Socioeconómico

| Nivel IDH | Alcaldías | Distancia | Tiempo | Velocidad |
|-----------|-----------|-----------|--------|-----------|
| **Bajo IDH** | 6 | 16.9 km | 42.5 min | 10.3 km/h ⚠️ |
| **Medio IDH** | 6 | 13.1 km | 21.0 min | 19.4 km/h ✓ |
| **Alto IDH** | 4 | 20.0 km | 49.1 min | 16.2 km/h |

**Hallazgo crítico:** Las alcaldías de **bajo IDH** tienen la **velocidad más baja** (10.3 km/h), lo que indica servicios de transporte más lentos y congestionados.

### 3.4 Análisis de Brecha Territorial

**Alcaldía más cercana:** Venustiano Carranza
- Distancia: 4.2 km
- IDH: 0.768

**Alcaldía más lejana:** Cuajimalpa de Morelos
- Distancia: 27.5 km
- IDH: 0.846

**Brecha de distancia:** 6.6x
**Brecha de IDH:** 0.91x (la más lejana tiene MAYOR IDH)

**Conclusión:** **NO hay inequidad territorial tradicional** (donde los pobres viven más lejos). En cambio, hay una **brecha de velocidad**: las zonas con menor IDH tienen servicios de transporte más lentos.

### 3.5 Interpretación de Resultados

**Lo que SÍ encontramos:**
1. **Brecha de velocidad, no de distancia:** Las alcaldías con menor IDH no están más lejos, pero tienen servicios más lentos (10.3 km/h vs 19.4 km/h)
2. **Transporte de menor calidad en zonas marginadas:** Las alcaldías con mayor pobreza tienen velocidades promedio de solo 10.3 km/h (velocidad de caminata)
3. **Accesibilidad relativa:** Venustiano Carranza e Iztacalco tienen la mejor accesibilidad (4-6 km, tiempos de 12-19 min)

**Lo que NO encontramos:**
1. **No hay inequidad territorial clásica** (pobres viven más lejos del aeropuerto)
2. **No hay correlación fuerte** entre distancia e indicadores socioeconómicos
3. **La brecha es de calidad de servicio**, no de proximidad geográfica

---

## 4. MAPA INTERACTIVO

### 4.1 Descripción Técnica

**Herramienta:** Folium (librería de Python para mapas interactivos)

**Características:**
- Formato: HTML interactivo
- Tamaño: 15.47 MB
- Paradas visualizadas: 11,362
- Capas intercambiables: 3 (distancia, tiempo, velocidad)
- Tiles disponibles: OpenStreetMap, Satélite, Transporte

**Funcionalidades:**
- Zoom y exploración libre
- Popups con información detallada al hacer clic
- Leyenda explicativa de colores
- Control de capas (encender/apagder)
- Responsive (funciona en móviles y tablets)

### 4.2 Capas Implementadas

**Capa 1: Distancia al AICM**
- Verde: < 5 km
- Verde claro: 5-10 km
- Amarillo: 10-15 km
- Naranja: 15-20 km
- Rojo: > 20 km

**Capa 2: Tiempo de Viaje**
- Verde: < 20 min
- Verde claro: 20-40 min
- Amarillo: 40-60 min
- Naranja: 60-80 min
- Rojo: > 80 min

**Capa 3: Velocidad Promedio**
- Verde: > 25 km/h
- Verde claro: 20-25 km/h
- Amarillo: 15-20 km/h
- Naranja: 10-15 km/h
- Rojo: < 10 km/h

### 4.3 Uso del Mapa

**Instrucciones:**
1. Abrir el archivo HTML en cualquier navegador
2. Usar las capas en la esquina superior derecha para cambiar entre métricas
3. Hacer clic en los marcadores para ver información detallada
4. Usar zoom para explorar diferentes zonas de CDMX
5. Cambiar entre mapa callejero, satélite y transporte

**Aplicaciones:**
- Presentación final del Programa Delfín
- Compartir con investigadores y tomadores de decisiones
- Análisis exploratorio de patrones geográficos
- Identificación visual de zonas problemáticas

---

## 5. ARCHIVOS GENERADOS

### 5.1 Código Fuente

| Script | Función | Líneas |
|--------|---------|--------|
| `analisis_alcaldias_centroides.py` | Análisis por alcaldías con método de centroide | ~350 |
| `analisis_socioeconomico.py` | Análisis socioeconómico y correlaciones | ~450 |
| `mapa_interactivo_folium.py` | Generación de mapa HTML interactivo | ~400 |

### 5.2 Datos Procesados

| Archivo | Descripción | Registros |
|---------|-------------|-----------|
| `estadisticas_por_alcaldia_centroides.csv` | Estadísticas por alcaldía | 16 |
| `paradas_con_alcaldia_centroides.csv` | Paradas con alcaldía asignada | 11,362 |
| `accesibilidad_socioeconomico_merged.csv` | Datos mergeados (accesibilidad + socioeconómico) | 16 |
| `correlaciones_socioeconomico.csv` | Matriz de correlaciones | 20 |

### 5.3 Visualizaciones

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `mapa_alcaldias_centroides.png` | PNG | Mapa de calor de alcaldías |
| `correlaciones_accesibilidad_socioeconomico.png` | PNG | Gráfico de correlaciones |
| `dispersion_accesibilidad_socioeconomico.png` | PNG | Gráficos de dispersión |
| `mapa_socioeconomico_alcaldias.png` | PNG | Mapa comparativo socioeconómico |
| `mapa_interactivo_accesibilidad_aicm.html` | HTML | Mapa interactivo (15.47 MB) |

---

## 6. CONCLUSIONES

### 6.1 Hallazgos Científicos

1. **Brecha de calidad de servicio:** Existe una brecha significativa en la velocidad del transporte público hacia el aeropuerto, donde las alcaldías con menor desarrollo humano tienen servicios 1.9 veces más lentos.

2. **No hay inequidad territorial clásica:** Contrario a lo esperado, las zonas más marginadas no están más lejos del aeropuerto. La inequidad está en la **calidad del servicio**, no en la proximidad geográfica.

3. **Correlaciones significativas:** La velocidad del transporte público está fuertemente correlacionada con indicadores socioeconómicos, sugiriendo que las zonas más pobres reciben servicios de menor calidad.

4. **Patrones geográficos claros:** Existe un patrón norte-sur en la accesibilidad al AICM, donde el norte/oriente tiene mejor acceso y el sur/poniente tiene peor acceso o está completamente desconectado.

### 6.2 Implicaciones para Políticas Públicas

1. **Mejorar servicios en zonas marginadas:** Las alcaldías con bajo IDH necesitan servicios de transporte más rápidos y eficientes hacia el aeropuerto.

2. **Atender congestión en GAM:** Gustavo A. Madero tiene distancia razonable pero velocidad muy baja (8.7 km/h), indicando necesidad de infraestructura dedicada.

3. **Conectar zonas del sur:** Las alcaldías del sur (Tlalpan, Xochimilco, Milpa Alta) están completamente desconectadas del aeropuerto en transporte público.

4. **Expandir Metrobús:** Las rutas más rápidas corresponden a Metrobús con carril exclusivo, sugiriendo que la infraestructura dedicada mejora significativamente la velocidad.

### 6.3 Limitaciones del Análisis

1. **Datos de un día típico:** Los datos GTFS representan un día típico, no capturan variaciones estacionales o eventos especiales.

2. **Sin datos de horas pico:** No se analizaron diferencias entre horas pico y valle.

3. **Transbordos no considerados:** El análisis solo calcula tiempos directos, no viajes con transbordos.

4. **Método de centroide:** La asignación de alcaldías tiene precisión de 85-90%, aceptable para análisis agregado pero no para análisis a nivel de calle.

### 6.4 Próximos Pasos (Semana 5)

1. **Dashboard interactivo:** Crear aplicación web con Streamlit para exploración dinámica de datos.

2. **Análisis de series temporales:** Si se obtienen datos de horarios, analizar variaciones a lo largo del día.

3. **Comparación con AIFA:** Comparar accesibilidad entre AICM y el nuevo Aeropuerto Internacional Felipe Ángeles.

4. **Documento final:** Consolidar todos los hallazgos en un artículo científico o informe técnico.

5. **Presentación final:** Preparar presentación para el cierre del Programa Delfín.

---

## 7. RECURSOS COMPUTACIONALES

### 7.1 Tiempo de Ejecución

| Script | Tiempo | RAM |
|--------|--------|-----|
| `analisis_alcaldias_centroides.py` | 2-3 min | 2 GB |
| `analisis_socioeconomico.py` | 30 seg | 1 GB |
| `mapa_interactivo_folium.py` | 1-2 min | 3 GB |

### 7.2 Dependencias

**Librerías principales:**
- pandas (3.0.3)
- numpy (2.4.6)
- geopandas (0.14.0)
- osmnx (1.9.0)
- matplotlib (3.11.0)
- seaborn (0.13.2)
- folium (última versión)
- scipy (última versión)

**Entorno:** Python 3.13 con Miniconda

---

## 8. REPRODUCTIBILIDAD

### 8.1 Estructura de Archivos

proyecto/
├── codigo/
│   ├── analisis_alcaldias_centroides.py
│   ├── analisis_socioeconomico.py
│   └── mapa_interactivo_folium.py
├── datos/
│   └── resultados/
│       ├── estadisticas_por_alcaldia_centroides.csv
│       ├── paradas_con_alcaldia_centroides.csv
│       ├── accesibilidad_socioeconomico_merged.csv
│       └── correlaciones_socioeconomico.csv
├── visualizaciones/
│   ├── mapa_alcaldias_centroides.png
│   ├── correlaciones_accesibilidad_socioeconomico.png
│   ├── dispersion_accesibilidad_socioeconomico.png
│   ├── mapa_socioeconomico_alcaldias.png
│   └── mapa_interactivo_accesibilidad_aicm.html
└── documentacion/
    └── hallazgos_semana4.md


### 8.2 Instrucciones de Reproducción

```bash
# 1. Clonar repositorio
git clone https://github.com/roavroberto/accesibilidad-aicm-delfin2026.git
cd accesibilidad-aicm-delfin2026

# 2. Instalar dependencias
pip install pandas numpy geopandas osmnx matplotlib seaborn folium scipy

# 3. Ejecutar análisis en orden
python codigo/analisis_alcaldias_centroides.py
python codigo/analisis_socioeconomico.py
python codigo/mapa_interactivo_folium.py

# 4. Abrir mapa interactivo
xdg-open visualizaciones/mapa_interactivo_accesibilidad_aicm.html

8.3 Repositorio GitHub
URL: https://github.com/roavroberto/accesibilidad-aicm-delfin2026
Último commit: Semana 4 - Análisis por alcaldías, socioeconómico y mapa interactivo
9. AGRADECIMIENTOS

    Programa Delfín 2026 por la oportunidad de investigación
    Asesores académicos por su guía y retroalimentación
    OpenStreetMap por los datos de red vial
    Google Transit por los datos GTFS
    CONEVAL e INEGI por los datos socioeconómicos

10. REFERENCIAS

    CONEVAL. (2020). "Medición de la pobreza a nivel municipal 2020"
    INEGI. (2020). "Censo de Población y Vivienda 2020"
    Datos Abiertos CDMX. (2024). "Datos de transporte público"
    OpenStreetMap Contributors. (2024). "Red vial de CDMX"
    Google. (2024). "GTFS de transporte público de CDMX"

Documento elaborado por: Roberto Rojas Avila y Janine Flores Beltran
Programa: Programa Delfín 2026
Fecha: 27 de junio de 2026
Versión: 1.0
Semana: 4
