Exploración Inicial de Datos (ETL) - Semana 2

Autor: Roberto Alfonso Rojas Ávila (Responsable Técnico/Datos)Fecha: 15 de junio de 2026Proyecto: Análisis de accesibilidad al AICM mediante transporte público
1. Objetivo de la Exploración

Identificar y filtrar las rutas de transporte público (específicamente Metrobús) que conectan con la zona de influencia del Aeropuerto Internacional de la Ciudad de México (AICM), utilizando el dataset GTFS de la CDMX.
2. Metodología (Pipeline)

    Carga de datos: Se leyeron los archivos routes.txt, stops.txt, trips.txt y stop_times.txt usando la librería pandas en Python.
    Filtro de agencia: Se aislaron las rutas pertenecientes a la agencia 'MB' (Metrobús).
    Filtro geoespacial (Bounding Box): Se definieron coordenadas límite alrededor del AICM (Latitud: 19.38 a 19.49, Longitud: -99.13 a -99.01) para aislar las paradas en un radio aproximado de 5 km.
    Cruce relacional (Join): Se cruzaron las paradas filtradas con los viajes y rutas para identificar qué líneas de Metrobús sirven a esta zona.

3. Resultados Obtenidos

Se identificaron 7 rutas de Metrobús que transitan por la zona de influencia del AICM:
Línea	Nombre de la Ruta
1	Indios Verdes - El Caminero
2	Tepalcates - Tacubaya
3	Tenayuca - Pueblo Sta. Cruz Atoyac
4	Centro Histórico - Buenavista - San Lázaro/AICM T1 y T2/Pantitlán
5	Río de lo Remedios - Preparatoria 1
6	Villa de Aragón - El Rosario
7	Indios Verdes - Campo Marte
Análisis de la Ruta Directa (Línea 4)

La Línea 4 es la única ruta que ingresa directamente a las terminales del aeropuerto. Al filtrar sus paradas, se obtuvieron 26 paradas únicas en la zona, confirmando la conexión directa con:

    Terminal 1 - Aeropuerto (Lat: 19.43531, Lon: -99.08367)
    Terminal 2 - Aeropuerto (Lat: 19.42148, Lon: -99.07725)

El recorrido de la Línea 4 cruza puntos estratégicos como San Lázaro, Morelos, Teatro del Pueblo y termina en Pantitlán y Alameda Oriente.
4. Próximos Pasos

    Visualizar geográficamente las 26 paradas de la Línea 4 en un mapa interactivo (Folium).
    Calcular distancias entre paradas y tiempos de viaje estimados.
    Cruzar esta información con datos del Metro para evaluar la accesibilidad combinada desde otras alcaldías.
