# Estado del Arte: Accesibilidad al AICM mediante Transporte Público

## 1. Introducción

La accesibilidad urbana se define como la facilidad con la que las personas pueden alcanzar destinos deseables utilizando sistemas de transporte disponibles. En el contexto de infraestructura crítica como aeropuertos, la accesibilidad mediante transporte público es un indicador fundamental de equidad territorial y eficiencia del sistema de movilidad urbana.

Este documento presenta una revisión de la literatura existente sobre:
1. Accesibilidad aeroportuaria en la Ciudad de México
2. Metodologías de análisis de accesibilidad usando datos GTFS
3. Identificación de gaps en la investigación actual

## 2. Accesibilidad Aeroportuaria en la Ciudad de México

### 2.1 Estudios sobre el AIFA (Aeropuerto Internacional Felipe Ángeles)

**Linares Zarco (2024)** - "La Conectividad del Aeropuerto Internacional Felipe Ángeles (AIFA). Problemas y Perspectivas"

Este estudio analiza la conectividad del AIFA mediante sistemas de transporte público, con énfasis en el Metrobús. El autor identifica problemas de accesibilidad y propone mejoras en la infraestructura de transporte para conectar el aeropuerto con diversas localizaciones de la Zona Metropolitana del Valle de México (ZMVM).

**Relevancia:** Aunque se enfoca en un aeropuerto diferente (AIFA), proporciona un marco conceptual sobre los desafíos de conectividad aeroportuaria en la CDMX y la importancia del Metrobús como solución de transporte masivo.

### 2.2 Estudios sobre el NAICM (Nuevo Aeropuerto Internacional de la Ciudad de México - Texcoco)

**Moreno Sánchez & Rivero Hernández** - "Accesibilidad en lo local y regional del Nuevo Aeropuerto Internacional de la Ciudad de México en el municipio de Texcoco, Estado de México"

Este trabajo analiza las propuestas para conectar el aeropuerto planeado en Texcoco (proyecto cancelado en 2018) con la ZMVM. Los autores examinan las obras de transporte público propuestas y evalúan la accesibilidad desde diferentes zonas metropolitanas.

**Relevancia:** Proporciona contexto histórico sobre cómo se planeaba la conectividad aeroportuaria en la CDMX, aunque el proyecto fue cancelado. Las metodologías de análisis de accesibilidad son aplicables al AICM actual.

### 2.3 Movilidad Urbana General en CDMX

**Salgado Camarena & Camarena Luhrs (2021)** - "Infraestructura alternativa de movilidad y accesibilidad en la Ciudad de México"

Este estudio examina las necesidades crecientes de transporte urbano en la Ciudad de México y analiza la infraestructura terrestre, marítima y aérea, incluyendo rutas, caminos y aeropuertos como componentes del sistema de movilidad integral.

**González (2013)** - "Movilidad, accesibilidad y transporte en la Ciudad de México"

Trabajo clásico que establece una tipología de zonas urbanas según su nivel de accesibilidad y movilidad en transporte público. Identifica cuatro categorías:
- Alta accesibilidad + Alta movilidad
- Alta accesibilidad + Baja movilidad
- Baja accesibilidad + Alta movilidad
- Baja accesibilidad + Baja movilidad

**Nieto (2020)** - "La gobernanza del transporte público metropolitano en la Ciudad de México"

Analiza la coordinación e integración de los sistemas de transporte en la ZMVM, identificando problemas de gobernanza que afectan la accesibilidad general del sistema.

## 3. Metodologías de Análisis de Accesibilidad usando GTFS

### 3.1 Algoritmos para Análisis de Accesibilidad Dinámica

**Fayyaz, Liu & Zhang (2017)** - "An efficient General Transit Feed Specification (GTFS) enabled algorithm for dynamic transit accessibility analysis" (PLOS ONE)

Este artículo presenta un algoritmo eficiente para calcular medidas de accesibilidad usando datos GTFS. El componente central es la capacidad de encontrar el camino más corto en redes de transporte público considerando horarios y frecuencias.

**Relevancia metodológica:** Establece el estándar para análisis de accesibilidad basado en GTFS, demostrando que estos datos permiten cálculos precisos de tiempos de viaje y conectividad.

### 3.2 Precisión de GTFS para Medir Accesibilidad

**Wessel & Farber (2019)** - "On the accuracy of schedule-based GTFS for measuring accessibility" (Journal of Transport and Land Use)

Este estudio evalúa la precisión de los datos GTFS basados en horarios para medir accesibilidad en diversos contextos. Los autores concluyen que GTFS proporciona medidas confiables de accesibilidad, aunque reconocen limitaciones en la representación de tiempos de espera y transferencias.

**Relevancia metodológica:** Valida el uso de GTFS como fuente de datos para análisis de accesibilidad, proporcionando confianza en la metodología propuesta en este proyecto.

### 3.3 GTFS en Tiempo Real y Accesibilidad bajo Incertidumbre

**Javanmard, Liu, Long & Lee (2025)** - "Using Realtime GTFS to generate easy-to-use transit accessibility measures under travel time uncertainty" (Travel Behaviour and Society)

Este trabajo reciente utiliza GTFS en tiempo real para generar medidas de accesibilidad que consideran la incertidumbre en los tiempos de viaje. Los autores identifican diferencias estadísticamente significativas en accesibilidad a servicios de salud entre diferentes grupos socioeconómicos.

**Relevancia metodológica:** Muestra cómo GTFS puede usarse para análisis de equidad en accesibilidad, metodología aplicable al análisis de accesibilidad al AICM desde diferentes zonas de la CDMX.

### 3.4 Análisis de Accesibilidad Orientado a Equidad

**Pourramazani, Gielen & Miralles-Garcia (2026)** - "Equity-Oriented Public Transport Accessibility Analysis Using GTFS, Spatial Proximity, and Demographic Sensitivity" (Sustainability)

Este artículo combina datos GTFS con información demográfica para analizar la equidad en la accesibilidad del transporte público. Los autores desarrollan indicadores que consideran tanto la proximidad espacial como la sensibilidad demográfica.

**Relevancia metodológica:** Proporciona un marco para analizar no solo la accesibilidad técnica al AICM, sino también la equidad en el acceso desde diferentes zonas socioeconómicas de la CDMX.

### 3.5 Generación de Redes de Tránsito Espacio-Temporales

**Liu, Guo, Gu, King, Han & Brakewood (2025)** - "Analyzing Transit Systems Using General Transit Feed Specification (GTFS) by Generating Spatiotemporal Transit Networks" (Information)

**Liu, Guo, Gu, King, Han (2024)** - "GTFS2STN: analyzing GTFS transit data by generating spatiotemporal transit network" (arXiv)

Estos trabajos presentan metodologías para generar redes de tránsito espacio-temporales a partir de datos GTFS, permitiendo analizar cambios en accesibilidad considerando variaciones temporales y espaciales.

**Relevancia metodológica:** Ofrecen herramientas avanzadas para modelar la red de transporte público de la CDMX y analizar cómo varía la accesibilidad al AICM según la hora del día y el día de la semana.

## 4. Identificación del Gap en la Investigación

### 4.1 Lo que SÍ se ha investigado

1. **Conectividad de otros aeropuertos:**
   - AIFA (Felipe Ángeles): estudios de planeación y conectividad
   - NAICM (Texcoco): análisis de accesibilidad del proyecto cancelado

2. **Movilidad general en CDMX:**
   - Tipologías de accesibilidad urbana
   - Gobernanza del transporte público
   - Infraestructura de movilidad

3. **Metodologías GTFS internacionales:**
   - Algoritmos de cálculo de accesibilidad
   - Validación de precisión de datos GTFS
   - Análisis de equidad en accesibilidad
   - Redes espacio-temporales

### 4.2 Lo que NO se ha investigado (GAP)

**No existen estudios recientes que:**

1. **Utilicen datos abiertos GTFS para medir accesibilidad al AICM**
   - El AICM es el aeropuerto más importante de México
   - Recibe millones de usuarios nacionales e internacionales
   - No hay análisis cuantitativo de su accesibilidad mediante transporte público

2. **Calculen métricas de accesibilidad desde todas las zonas de CDMX**
   - No se sabe qué zonas tienen mejor/peor acceso al aeropuerto
   - No hay análisis de tiempos de viaje desde diferentes alcaldías
   - No se han identificado zonas con desconexión territorial

3. **Comparen accesibilidad entre diferentes sistemas de transporte**
   - La literatura se enfoca en Metrobús (rutas directas al AICM)
   - No hay análisis comparativo: Metro vs Metrobús vs otras rutas
   - No se sabe si las rutas directas son realmente las mejores opciones

4. **Identifiquen patrones de equidad en el acceso al aeropuerto**
   - No se sabe si zonas marginadas tienen peor acceso
   - No hay análisis de accesibilidad considerando variables socioeconómicas

### 4.3 Oportunidad de Investigación

Este proyecto aborda el gap identificado mediante:

**Datos:**
- GTFS de transporte público CDMX (11,362 paradas, 301 rutas, 10 agencias)
- Estaciones de Metro y Metrobús
- Infraestructura vial
- Localización del AICM

**Metodología:**
- Análisis geoespacial con Python (GeoPandas)
- Cálculo de distancias y tiempos de viaje
- Identificación de rutas que llegan al aeropuerto
- Clasificación de zonas según nivel de accesibilidad

**Aporte:**
- Primer análisis cuantitativo de accesibilidad al AICM usando datos abiertos
- Identificación de zonas con mejor y peor acceso
- Comparación de accesibilidad entre diferentes sistemas de transporte
- Herramienta visual (dashboard) para exploración de resultados

## 5. Conclusión

La revisión de literatura revela que:

1. **Existe abundante investigación sobre aeropuertos en la CDMX**, pero se enfoca en el AIFA (operativo) y el NAICM (cancelado), no en el AICM (el más importante).

2. **Las metodologías GTFS están bien establecidas internacionalmente**, con algoritmos validados para análisis de accesibilidad.

3. **Existe un gap significativo:** no hay estudios que apliquen estas metodologías al AICM usando datos abiertos de la CDMX.

4. **La oportunidad es clara:** utilizar datos GTFS y análisis geoespacial para medir cuantitativamente la accesibilidad al AICM, identificar zonas con mejor/peor acceso, y generar herramientas visuales para la toma de decisiones.

Este proyecto llena ese gap mediante un análisis integral de la accesibilidad al Aeropuerto Internacional de la Ciudad de México utilizando 11,362 paradas de transporte público y metodologías establecidas internacionalmente.

## 6. Referencias

1. Fayyaz, S. K., Liu, X. C., & Zhang, G. (2017). An efficient General Transit Feed Specification (GTFS) enabled algorithm for dynamic transit accessibility analysis. PLOS ONE.

2. González, S. (2013). Movilidad, accesibilidad y transporte en la Ciudad de México. Infraestructura Vial.

3. Javanmard, R., Liu, L., Long, J. A., & Lee, J. (2025). Using Realtime GTFS to generate easy-to-use transit accessibility measures under travel time uncertainty. Travel Behaviour and Society.

4. Linares Zarco, J. (2024). La Conectividad del Aeropuerto Internacional Felipe Ángeles (AIFA). Problemas y Perspectivas.

5. Liu, D., Guo, J., Gu, Y., King, M., Han, L. D., & Brakewood, C. (2025). Analyzing Transit Systems Using General Transit Feed Specification (GTFS) by Generating Spatiotemporal Transit Networks. Information.

6. Liu, D., Guo, J., Gu, Y., King, M., & Han, L. D. (2024). GTFS2STN: analyzing GTFS transit data by generating spatiotemporal transit network. arXiv.

7. Moreno Sánchez, E., & Rivero Hernández, M. Accesibilidad en lo local y regional del Nuevo Aeropuerto Internacional de la Ciudad de México en el municipio de Texcoco, Estado de México.

8. Nieto, A. T. (2020). La gobernanza del transporte público metropolitano en la Ciudad de México. Espacialidades.

9. Pourramazani, H., Gielen, E., & Miralles-Garcia, J. L. (2026). Equity-Oriented Public Transport Accessibility Analysis Using GTFS, Spatial Proximity, and Demographic Sensitivity. Sustainability.

10. Salgado Camarena, S. M., & Camarena Luhrs, M. (2021). Infraestructura alternativa de movilidad y accesibilidad en la Ciudad de México.

11. Wessel, N., & Farber, S. (2019). On the accuracy of schedule-based GTFS for measuring accessibility. Journal of Transport and Land Use.
