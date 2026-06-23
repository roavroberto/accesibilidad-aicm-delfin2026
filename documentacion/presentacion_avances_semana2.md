# Presentación de Avances - Semana 2
## Programa Delfín 2026 - Accesibilidad al AICM

---

## DIAPOSITIVA 1: PORTADA

**Título principal:**
Accesibilidad al Aeropuerto Internacional de la Ciudad de México mediante Transporte Público

**Subtítulo:**
Análisis geoespacial con datos abiertos GTFS

**Información:**
- Equipo: Roberto Alfonso Rojas Avila + Janine Elizabeth Flores Beltran
- Programa: Programa Delfín 2026
- Eje 3: Movilidad, Aeropuerto y Eventos Urbanos
- Fecha: 22 de junio de 2026

**Notas para el presentador:**
"Buenos días. Soy Roberto Rojas, estudiante del Programa Delfín 2026. Junto con Janine, estamos desarrollando un análisis de accesibilidad al Aeropuerto Internacional de la Ciudad de México utilizando datos abiertos de transporte público."

---

## DIAPOSITIVA 2: PREGUNTA DE INVESTIGACIÓN

**Pregunta central:**
¿Qué tan accesible es el Aeropuerto Internacional de la Ciudad de México (AICM) para los usuarios del transporte público de la Ciudad de México?

**Sub-preguntas:**
- ¿Desde qué zonas de CDMX se puede llegar al AICM en transporte público?
- ¿Cuánto tiempo toma llegar desde diferentes puntos de la ciudad?
- ¿Qué sistemas de transporte ofrecen mejor conectividad?
- ¿Existen zonas con desconexión territorial al aeropuerto?

**Enfoque metodológico:**
Análisis cuantitativo usando datos abiertos GTFS (General Transit Feed Specification)

**Notas para el presentador:**
"Nuestra pregunta central busca entender la accesibilidad real al aeropuerto más importante de México. No solo nos preguntamos si hay rutas, sino desde dónde se puede llegar, cuánto tiempo toma, y qué zonas quedan desconectadas."

---

## DIAPOSITIVA 3: ESTADO DEL ARTE - LO QUE SE SABE

**Estudios previos sobre aeropuertos en CDMX:**

1. **Linares Zarco (2024)** - Conectividad del AIFA
   - Analiza Metrobús y accesibilidad al Aeropuerto Felipe Ángeles
   - Enfoque: planeación de infraestructura

2. **Moreno & Rivero** - Accesibilidad del NAICM (Texcoco)
   - Estudia el proyecto cancelado del nuevo aeropuerto
   - Metodología: análisis de rutas propuestas

3. **Salgado & Camarena (2021)** - Infraestructura de movilidad
   - Marco general sobre movilidad urbana en CDMX

4. **González (2013)** - Tipología de accesibilidad
   - Clasifica zonas según nivel de accesibilidad y movilidad

**Metodologías GTFS internacionales:**
- Fayyaz et al. (2017): Algoritmos de accesibilidad con GTFS
- Wessel & Farber (2019): Validación de precisión de GTFS
- Javanmard et al. (2025): GTFS en tiempo real

**Notas para el presentador:**
"La revisión de literatura muestra que la mayoría de estudios se enfocan en el AIFA o el NAICM cancelado, no en el AICM actual. Las metodologías GTFS están bien establecidas internacionalmente, pero no se han aplicado al aeropuerto más importante de México."

---

## DIAPOSITIVA 4: ESTADO DEL ARTE - EL GAP IDENTIFICADO

**Lo que SÍ se ha investigado:**
✅ Conectividad de otros aeropuertos (AIFA, NAICM)
✅ Metodologías GTFS en otras ciudades del mundo
✅ Estudios generales de movilidad en CDMX

**Lo que NO se ha investigado (GAP):**
❌ Medir accesibilidad al AICM usando datos abiertos GTFS
❌ Calcular métricas de accesibilidad desde todas las zonas de CDMX
❌ Identificar zonas con peor acceso al aeropuerto
❌ Comparar accesibilidad entre diferentes sistemas de transporte
❌ Analizar equidad en el acceso al aeropuerto

**Nuestro aporte:**
Primer análisis cuantitativo de accesibilidad al AICM utilizando 11,362 paradas de transporte público y metodologías validadas internacionalmente.

**Notas para el presentador:**
"Existe un gap significativo: no hay estudios que apliquen metodologías GTFS al AICM usando datos abiertos. Nuestro proyecto llena ese vacío con un análisis integral y cuantitativo."

---

## DIAPOSITIVA 5: METODOLOGÍA - DATOS UTILIZADOS

**Dataset principal: GTFS Transporte Público CDMX**
- Fuente: Portal de Datos Abiertos de la Ciudad de México
- Fecha: Febrero 2026
- Cobertura: Toda la ZMVM

**Características:**
- **11,362 paradas** de transporte público
- **301 rutas** diferentes
- **10 agencias** operadoras (Metro, Metrobús, RTP, Trolebús, etc.)
- **42,789 registros** de horarios
- Coordenadas geográficas (WGS84)

**Análisis multi-radio:**
Evaluamos accesibilidad en 4 umbrales:
- 0.5 km (accesibilidad peatonal inmediata)
- 1.0 km (accesibilidad peatonal)
- 2.0 km (accesibilidad en transporte local)
- 5.0 km (accesibilidad metropolitana)

**Notas para el presentador:**
"Utilizamos el estándar internacional GTFS, que incluye todas las paradas de transporte público de la CDMX con sus coordenadas geográficas. Esto nos permite hacer un análisis espacial preciso."

---

## DIAPOSITIVA 6: CORRECCIÓN METODOLÓGICA Y HALLAZGO REFINADO

**Error inicial identificado:**
- Medimos desde el centro geométrico del AICM (las pistas)
- Esto creaba una falsa "zona muerta" de 1 km

**Corrección metodológica:**
- Ahora medimos desde las Terminales 1 y 2 (puntos reales de llegada)
- Terminal 1: 19.4353, -99.0725
- Terminal 2: 19.4341, -99.0643

**Resultados corregidos:**

| Radio | Paradas | Interpretación |
|-------|---------|----------------|
| 0.5 km | 3 paradas | Accesibilidad peatonal inmediata |
| 1.0 km | 11 paradas | Accesibilidad peatonal |
| 2.0 km | 155 paradas | Accesibilidad local |
| 5.0 km | 1,141 paradas | Accesibilidad metropolitana |

**Hallazgo importante:**
- Las 11 paradas cercanas están todas en la zona de la Terminal 2 (Peñón de los Baños)
- La Terminal 1 NO tiene paradas cercanas (rodeada de infraestructura aeroportuaria)
- Existe **asimetría en la accesibilidad** entre terminales

**Notas para el presentador:**
"Durante el análisis, identificamos un error metodológico: estábamos midiendo desde el centro del aeropuerto (las pistas) en lugar de las terminales reales. Al corregir esto, descubrimos que sí existen paradas cercanas, pero solo en la Terminal 2. La Terminal 1, que es la más antigua y con mayor tráfico, no tiene paradas de transporte público cercanas, lo que representa un problema de accesibilidad específico."

---

## DIAPOSITIVA 6.5: ANÁLISIS DE PARADAS CERCANAS A TERMINALES

**Las 11 paradas a menos de 1 km:**

| Distancia | Nombre de Parada | Ubicación |
|-----------|------------------|-----------|
| 0.39 km | C. C. Arenal Cuarta Sección | Terminal 2 |
| 0.47 km | Xaltocan - Xocoyote | Terminal 2 |
| 0.49 km | Xocoyote - Xano | Terminal 2 |
| 0.64 km | Xana - Xico | Terminal 2 |
| 0.68 km | Xocoyote - Xochitlan Sur | Terminal 2 |
| 0.79 km | Xaltocan - Xocoyote | Terminal 2 |
| 0.82 km | Xico - Xochistlahuaca | Terminal 2 |
| 0.96 km | Xochitlan Norte - Xaltocan | Terminal 2 |
| 0.99 km | C. C. Alameda Oriente | Terminal 2 |
| 1.00 km | Xochitlan Norte - Xocoyote | Terminal 2 |
| 1.00 km | Nezahualcoyotl - Moctezuma | Terminal 2 |

**Conclusión:**
- Todas las paradas cercanas están en Peñón de los Baños (zona Terminal 2)
- La Terminal 1 requiere transporte motorizado para acceso
- Esto sugiere necesidad de mejorar conectividad en Terminal 1

**Notas para el presentador:**
"Al analizar las paradas más cercanas, todas están en la zona de Peñón de los Baños, cerca de la Terminal 2. Esto es interesante porque la Terminal 1, que maneja el 70% del tráfico del aeropuerto, no tiene acceso peatonal directo a transporte público. Esto podría ser un área de oportunidad para mejorar la accesibilidad."

---

## DIAPOSITIVA 7: ANÁLISIS COMPLETO DE ACCESIBILIDAD

**Análisis de 11,362 paradas con red vial completa:**
- **199,981 nodos** y **488,999 calles** procesadas
- **11,299 paradas** conectadas a la red vial (99.4%)
- **Distancia mínima:** 0.91 km
- **Distancia promedio:** 15.29 km
- **Distancia máxima:** 32.73 km
- **Mediana:** 15.28 km

**Factor de desvío:**
- Distancia euclidiana promedio: 3.50 km
- Distancia real en red vial: 5.00 km
- **Factor de corrección: 1.52x**

**Implicaciones:**
- Las distancias en línea recta subestiman la accesibilidad real
- La mayoría de paradas están a 15+ km del aeropuerto
- Existe una desconexión territorial significativa

**Notas para el presentador:**
"Al calcular las distancias reales por carretera usando la red vial completa de la CDMX, descubrimos que la distancia promedio es 15 km, mucho mayor de lo que se pensaba. Además, la distancia real es 52% mayor que la distancia en línea recta, lo que afecta significativamente los tiempos de viaje."

---

## DIAPOSITIVA 8: VISUALIZACIÓN - MAPA DE CALOR

**[INSERTAR IMAGEN: visualizaciones/mapa_calor_accesibilidad_aicm.png]**

**Descripción del mapa:**
- Mapa de calor de toda la CDMX
- Colores: Verde (cerca) a Rojo (lejos)
- Muestra la accesibilidad real desde cada parada al AICM
- Red vial de fondo en gris tenue

**Mensaje clave:**
La visualización revela patrones espaciales de accesibilidad que no son evidentes con análisis tabulares.

**Notas para el presentador:**
"Este mapa de calor muestra la accesibilidad real al aeropuerto desde cada punto de la ciudad. Pueden observar que las zonas más cercanas (en verde) están concentradas en el oriente, mientras que el poniente y sur tienen menor accesibilidad."

---
---

## DIAPOSITIVA 9: VISUALIZACIÓN - MAPA DE CALOR DE VIALIDADES

**[INSERTAR IMAGEN: visualizaciones/mapa_calor_vialidades_aicm.png]**

**Descripción del mapa:**
- Cada calle de la CDMX coloreada según accesibilidad al AICM
- Verde = calles cercanas al aeropuerto
- Rojo = calles lejanas al aeropuerto
- 488,332 calles analizadas
- Misma escala de colores que el mapa de paradas

**Estadísticas:**
- Distancia mínima: 0.02 km
- Distancia máxima: 38.69 km
- Distancia promedio: 18.43 km
- Mediana: 18.44 km

**Mensaje clave:**
Este mapa muestra la accesibilidad real desde CUALQUIER punto de la red vial, no solo desde paradas de transporte público.

**Notas para el presentador:**
"Este mapa muestra cada calle de la ciudad coloreada según qué tan fácil es llegar al aeropuerto. El verde indica calles cercanas, el rojo indica calles lejanas. Esto nos da una visión completa de la accesibilidad vial."

---

## DIAPOSITIVA 10: COMPARACIÓN - TRANSPORTE PÚBLICO VS VIALIDADES

**Dos vistas de la accesibilidad al AICM:**

| Métrica | Transporte Público | Vialidades | Diferencia |
|---------|-------------------|------------|-----------|
| Distancia mínima | 0.91 km | 0.02 km | Paradas más lejos |
| Distancia máxima | 32.73 km | 38.69 km | Vialidades más lejos |
| **Distancia promedio** | **15.29 km** | **18.43 km** | **+3.14 km** |
| **Mediana** | **15.28 km** | **18.44 km** | **+3.16 km** |
| Elementos analizados | 11,362 paradas | 488,332 calles | - |

**Interpretación:**
- Las paradas de transporte público están en promedio 3 km más cerca del aeropuerto
- El transporte público está estratégicamente ubicado para optimizar acceso
- Las vialidades incluyen todas las calles, incluso las más alejadas
- Existe una brecha de accesibilidad entre infraestructura vial y transporte público

**Visualizaciones comparables:**
[INSERTAR: Ambos mapas lado a lado con la misma escala de colores]

**Notas para el presentador:**
"Al comparar ambos mapas con la misma escala de colores, podemos ver que el transporte público tiende a concentrarse en zonas con mejor acceso al aeropuerto, mientras que muchas calles residenciales están más alejadas. Esto sugiere que el transporte público está optimizando rutas, pero dejando zonas con menor cobertura."
---

## DIAPOSITIVA 11: PRÓXIMOS PASOS - SEMANA 3

**Objetivos de la Semana 3 (22-26 junio):**

1. **Cálculo de tiempos de viaje:**
   - Ir más allá de distancias
   - Considerar frecuencias y horarios
   - Analizar transbordos necesarios

2. **Análisis por alcaldías:**
   - Cruzar datos con límites administrativos
   - Identificar zonas con peor acceso
   - Análisis socioeconómico

3. **Integración de datos de vialidades:**
   - Análisis de infraestructura vial
   - Identificación de cuellos de botella
   - Comparación transporte público vs auto

4. **Documento metodológico:**
   - Protocolo completo de análisis
   - Justificación de decisiones metodológicas
   - Replicabilidad del análisis

**Notas para el presentador:**
"En la Semana 3 refinaremos nuestra metodología. Pasaremos de distancias a tiempos de viaje reales, integraremos análisis por alcaldías, y crearemos un documento metodológico completo."

---

## DIAPOSITIVA 12: REPOSITORIO GITHUB

**[INSERTAR CAPTURA DE PANTALLA del repositorio]**

**URL:** https://github.com/roavroberto/accesibilidad-aicm-delfin2026

**Contenido del repositorio:**

/
├── codigo/ (7 scripts Python)
├── datos/
│   ├── gtfs/ (datos originales)
│   ├── vialidades/ (red vial)
│   └── resultados/ (datos procesados)
├── documentacion/
│   ├── estado_del_arte.md
│   ├── inventario_fuentes.md
│   └── presentacion_avances_semana2.md
├── visualizaciones/ (5 mapas/gráficos)
└── README.md


**Características:**
- Código abierto y reproducible
- Documentación completa
- Datos procesados disponibles
- Visualizaciones de alta calidad

**Notas para el presentador:**
"Todo nuestro trabajo está documentado en un repositorio público de GitHub. Esto garantiza transparencia, reproducibilidad y permite que otros investigadores construyan sobre nuestro trabajo."

---

## DIAPOSITIVA 13: CONCLUSIONES PRELIMINARES

**Hallazgos principales:**
✅ 27 rutas llegan al AICM (9% del total de rutas)
✅ Asimetría entre terminales: T2 tiene mejor accesibilidad que T1
✅ Distancia promedio real: 15.29 km (no 3.5 km euclidiana)
✅ Factor de desvío: 1.52x (distancia real vs línea recta)
✅ 11,299 de 11,362 paradas conectadas a red vial (99.4%)

**Contribuciones del proyecto:**
1. **Metodológica:** Corrección de punto de medición (terminales vs centro)
2. **Empírica:** Primera cuantificación completa de accesibilidad al AICM
3. **Técnica:** Análisis de red vial con factor de desvío
4. **Social:** Identificación de asimetría entre terminales

**Impacto potencial:**
- Información para mejorar conectividad del AICM (especialmente Terminal 1)
- Base para políticas de transporte más equitativas
- Herramienta para planificación urbana

**Notas para el presentador:**
"Nuestro análisis revela problemas de accesibilidad que no habían sido documentados cuantitativamente. La asimetría entre terminales y el factor de desvío son hallazgos que pueden informar políticas públicas."

---

## DIAPOSITIVA 14: PREGUNTAS

**Espacio para:**
- Dudas
- Comentarios
- Sugerencias
- Colaboraciones

**Contacto:**
- Roberto Rojas: roavroberto@gmail.com
- Repositorio: github.com/roavroberto/accesibilidad-aicm-delfin2026

**Mensaje final:**
"Gracias por su atención. Estamos abiertos a preguntas y comentarios."

---

## NOTAS GENERALES PARA EL PRESENTADOR

**Duración estimada:** 10-12 minutos

**Puntos clave a enfatizar:**
1. La corrección metodológica demuestra rigor científico
2. La asimetría entre terminales es un hallazgo importante
3. El factor de desvío (1.52x) es crucial para entender accesibilidad real
4. El análisis completo de 11,362 paradas es exhaustivo
5. **NUEVO: La comparación entre paradas y vialidades revela brechas de accesibilidad**
6. **NUEVO: El transporte público está optimizado pero deja zonas desatendidas**
7. Hay un plan claro para las próximas semanas

**Posibles preguntas y respuestas:**

**P: ¿Por qué cambiaron el punto de medición?**
R: "Identificamos que medir desde el centro del aeropuerto (las pistas) no era metodológicamente correcto. Los pasajeros llegan a las terminales, no a las pistas. Al corregir esto, obtuvimos resultados más precisos."

**P: ¿Por qué la Terminal 1 no tiene paradas cercanas?**
R: "La Terminal 1 está rodeada de infraestructura aeroportuaria (pistas, zonas de servicio). La Terminal 2 está en el borde del aeropuerto, cerca de zonas residenciales como Peñón de los Baños."

**P: ¿Qué significa el factor de desvío de 1.52x?**
R: "Significa que la distancia real por carretera es 52% mayor que la distancia en línea recta. Esto es crucial porque afecta directamente los tiempos de viaje y la percepción de accesibilidad."

**P: ¿Cómo validan que los datos GTFS son correctos?**
R: "En la Semana 3 implementaremos validaciones de calidad: verificar que las coordenadas estén en el rango de CDMX, que no haya valores nulos, y que los datos reflejen la realidad actual."

**P: ¿Qué harían con los resultados?**
R: "El objetivo es generar un dashboard interactivo que permita visualizar la accesibilidad desde cualquier punto de la ciudad. Esto puede usarse para identificar zonas prioritarias de mejora, especialmente en la Terminal 1."

**P: ¿Por qué es relevante este análisis?**
R: "El AICM es el aeropuerto más importante de México. Entender su accesibilidad es crucial para la equidad territorial y la eficiencia del sistema de transporte."

**P: ¿Por qué las paradas de transporte están más cerca que las vialidades en promedio?**
R: "Porque el transporte público está diseñado para dar servicio. Las rutas se planifican estratégicamente para conectar zonas pobladas con destinos importantes como el aeropuerto. Las vialidades, en cambio, incluyen todas las calles de la ciudad, incluso las más alejadas y residenciales. Esta diferencia de 3 km en promedio muestra que el transporte público está optimizando el acceso, pero también revela que hay zonas con menor cobertura."
