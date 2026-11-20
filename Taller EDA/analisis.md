# Taller 07 — Estadística descriptiva y análisis exploratorio de datos

**Curso:** Estadística III — Ingeniería de Sistemas
**Universidad Católica de Oriente**
**Integrantes:** Daniel Puerta Bernal · Juan Diego Guzmán

Análisis de los diez ejercicios y del punto opcional. El código que produce cada
resultado está en `Taller_EDA_Puerta_Guzman.py`, y las figuras en `figuras/`.
Los datos son `data/07 - canciones.csv` (2000 canciones, 18 columnas).

---

# Parte 1 — Ingesta y limpieza inicial

## Ejercicio 1 — Análisis

**Resultados:** el archivo se carga correctamente y `df.head()` muestra las
primeras 5 filas con las 18 columnas del conjunto.

Se carga con `pandas.read_csv()` y no con `read_excel()` porque solo el `.csv`
incluye la columna `explicit`. El `.xlsx` de la misma carpeta es una versión
anterior de 17 columnas y sin esa variable no se podrían resolver los ejercicios
5 y 7.

## Ejercicio 2 — Análisis

**Resultados:** 2000 filas, 18 columnas, 0 valores nulos en todas las columnas.

**Pregunta:** ¿el conjunto requiere limpieza antes de continuar?**

Sí, aunque `isna()` no marque nulos. Hay problemas de calidad que no se detectan como "faltantes" pero sí condicionan el análisis:

- 59 filas duplicadas exactas tienen el mismo artista, canción y todos sus atributos.
-126 canciones con `popularity = 0`, un 0 en un éxito global que no es tan creíble. Hay canciones que aparecen dos veces, una con 0 y otra con una popularidad real por ejemplo *Hotline Bling* con 0 y con 77. El 0 es un dato faltante que no es tan claro, no una medición.
- 22 filas con `genre = "set()"`, texto residual de Python que no es un género real.
- `key` y `mode` son categorías codificadas como números que son tonalidad y modo musical y no cantidades que no tiene sentido calcular su media.
La decisión fue  no eliminar filas ya que su efecto sobre las medidas es mínimo este es menos del 3% del conjunto de los datos y no cambia ninguna conclusión del taller.

---

# Parte 2 — Estadística descriptiva univariada

## Ejercicio 3 — Análisis

**Resultados:** se crea la columna `duration_min` dividiendo `duration_ms` entre
60 000.

El divisor sale de multiplicar los 1000 milisegundos de un segundo por los 60
segundos de un minuto. La conversión se verifica con la primera fila: *Oops!...I
Did It Again* registra 211 160 ms y queda en 3.52 minutos, una duración
plausible para una canción pop. Si el resultado hubiera dado 211 o 0.06, el
factor estaría equivocado.

## Ejercicio 4 — Análisis

**Resultados:**

| | duration_min | popularity | danceability |
|---|---|---|---|
| media | 3.81 | 59.87 | 0.667 |
| mediana | 3.72 | 65.50 | 0.676 |
| desv. estándar | 0.65 | 21.34 | 0.140 |
| mínimo | 1.88 | 0.00 | 0.129 |
| máximo | 8.07 | 89.00 | 0.975 |

**Pregunta: compare media y mediana de `popularity`. ¿Qué indica esa diferencia? ¿Cuál reportaría usted como valor "típico" y por qué?

La media (59.87) es menor que la mediana (65.5). Esa diferencia indica una distribución con asimetría negativa  hay un grupo de canciones con popularidad muy baja incluyendo 126 casos en exactamente 0, que en realidad son datos faltantes que se aparecen como 0, no canciones genuinamente que no tengan popularidad que arrastra la media hacia abajo, mientras la mayoría del catálogo se concentra en valores más altos.

Reportaría la **mediana** como valor típico, porque no se ve afectada por esos valores extremos bajos y refleja mejor dónde se agrupa realmente la mayor parte de las canciones.

## Ejercicio 5 — Análisis

**Resultados:** los cinco géneros más frecuentes son pop (1633 canciones,
82.6 %), hip hop (778, 39.3 %), R&B (452, 22.9 %), Dance/Electronic (390,
19.7 %) y rock (234, 11.8 %). Las canciones explícitas son 551 de 2000, es decir
el 27.6 %.

**Pregunta:** una canción puede tener varios géneros en la misma celda. Decida
cómo tratar esos casos —contar la combinación completa como una categoría o
separarla en géneros individuales—, aplique su decisión y justifíquela.

Se separó cada celda en géneros individuales y se contó cada aparición. El
problema afecta a la mayoría del conjunto: 1279 de las 2000 celdas contienen más
de un género separado por comas. La razón de separar es que el enunciado pide
los géneros más frecuentes, no las combinaciones más frecuentes. Contar la
combinación completa como categoría habría tratado `hip hop, pop` y
`hip hop, pop, R&B` como categorías ajenas al pop, ocultando que el pop aparece
en 1633 canciones, más de ocho de cada diez.

El costo de esta decisión, que conviene declarar, es que los porcentajes ya no
suman 100 % y deben leerse por separado. Aparte, las 22 canciones cuyo género es
`set()` se excluyeron por tratarse de un dato faltante y no de un género, por lo
que los porcentajes se calculan sobre las 1978 canciones con género
identificado.

---

# Parte 3 — Visualización de datos

## Ejercicio 6 — Análisis

**Resultado:** media de `tempo` ≈ 120.1 BPM (línea roja del histograma).

**Pregunta:** ¿en qué rango se concentra el repertorio? ¿Es unimodal o hay varios picos? Si hay más de uno, proponga una explicación musical.

La mayor parte de las canciones se concentra entre 90 y 140 BPM, con el pico más alto entre 125 y 130 BPM, tempo característico de la música de baile de raíz house y del EDM que dominó las listas en la segunda mitad del periodo.

La distribución no es estrictamente unimodal aparece una segunda concentración más baja, alrededor de 95-105 BPM. Una explicación musical razonable es la presencia de baladas, hip hop y canciones de R&B, géneros con tempos naturalmente más lentos que conviven en las listas de éxitos junto con el material más bailable.

Vale la pena notar que la media de 120.1 BPM no coincide con ninguno de los dos picos: queda entre ambos, más cerca del segundo. Decir que "las canciones rondan los 120 BPM" es cierto en promedio pero incompleto, porque un solo número no resume bien una distribución con dos concentraciones separadas.

## Ejercicio 7 — Análisis

**Resultados:**

| | No explícitas | Explícitas |
|---|---|---|
| n | 1449 | 551 |
| mediana | 65.0 | 67.0 |
| media | 59.26 | 61.48 |
| desv. estándar | 21.57 | 20.64 |
| rango intercuartílico | 17.0 | 17.0 |

**Pregunta:** ¿hay una diferencia visual apreciable entre ambos grupos? Compare
medianas y dispersión, no solo la posición de las cajas. Advierta si los tamaños
de los dos grupos son muy desiguales y qué implica eso para la comparación.

No hay diferencia apreciable: las cajas se superponen casi por completo. Las
medianas difieren en apenas dos puntos sobre una escala de 0 a 100 —65 en las no
explícitas frente a 67 en las explícitas— y la dispersión es prácticamente
idéntica, con un rango intercuartílico de exactamente 17 en los dos grupos y
desviaciones estándar de 21.57 y 20.64. Los dos grupos no solo se centran en el
mismo lugar, sino que varían igual. La lectura es negativa y no por ello pobre:
el contenido explícito no separa a las canciones exitosas por su nivel de
popularidad.

Los grupos sí son de tamaños desiguales, 1449 canciones no explícitas frente a
551 explícitas. Con 551 observaciones la mediana del grupo menor sigue siendo
estable, así que la comparación de medianas es válida; el riesgo está en la
lectura visual. El grupo no explícito aparenta mayor dispersión porque muestra
más puntos atípicos por debajo, pero eso ocurre simplemente porque tiene 2.6
veces más canciones y, por tanto, más oportunidades de contener valores
extremos. Como el rango intercuartílico es idéntico, concluir que las canciones
no explícitas son más heterogéneas sería un error inducido por el tamaño de la
muestra. Por eso la comparación debe apoyarse en los estadísticos de dispersión
y no en la extensión aparente de bigotes y atípicos.

---

# Parte 4 — Análisis bivariado y correlación

## Ejercicio 8 — Análisis

**Resultado — matriz de correlación de Pearson:**

| | danceability | energy | valence | loudness |
|---|---|---|---|---|
| danceability | 1.00 | -0.10 | 0.40 | -0.03 |
| energy | -0.10 | 1.00 | 0.33 | 0.65 |
| valence | 0.40 | 0.33 | 1.00 | 0.23 |
| loudness | -0.03 | 0.65 | 0.23 | 1.00 |

La relación más fuerte es entre `energy` y `loudness` que es de r = 0.65, las canciones más enérgicas tienden a sonar  más fuerte. Le sigue `danceability` y `valence` con r = 0.40, esta es  moderada las canciones más bailables tienden a ser también más alegres. En contraste, `danceability` y `loudness` casi no se relacionan con r = -0.03.

## Ejercicio 9 — Análisis

**Resultados:** mapa de calor de la matriz anterior, con paleta divergente
`coolwarm`, escala fijada entre −1 y 1 centrada en 0, y los coeficientes
anotados sobre cada celda.

Fijar la escala no es un detalle estético: garantiza que el blanco corresponda
siempre a correlación nula y que la intensidad del color sea comparable entre
celdas. Si la escala se ajustara automáticamente al rango de los datos, una
correlación débil podría aparecer con el mismo color intenso que una fuerte y la
lectura visual resultaría engañosa.

## Ejercicio 10 — Análisis

**Resultado:** el par con correlación más fuerte en valor absoluto es `energy` – `loudness` con r = 0.65.

**Pregunta:** caracterice dirección, fuerza y forma. ¿Sugiere relación lineal o hay curvatura? ¿Hay atípicos que inflen el coeficiente? ¿Qué no permite concluir esta correlación?

La relación es positiva y tiene una fuerza moderada-alta,  a mayor energía, mayor volumen promedio de la canción. La nube de puntos sigue una tendencia lineal razonablemente clara, sin una curvatura marcada. Sí se ven algunos atípicos abajo a la izquierda, canciones acústicas muy suaves como *I See Fire* de Ed Sheeran (-20.5 dB) o *Mad World* de Gary Jules (-17.2 dB), pero no están inflando el coeficiente: si se sacan, r apenas baja de 0.65 a 0.64.

Lo que no permite concluir esta correlación es que  no se puede afirmar que una canción suene más fuerte porque es enérgica y tampoco lo contrario Solo indica que ambas variables tienden a moverse juntas en el catálogo; la explicación real puede deberse a decisiones conjuntas de producción y mezcla que afectan ambos atributos a la vez.

---

# Punto opcional

**Pregunta:** ¿el auge del EDM dejó una huella medible en el tempo de los
éxitos globales?

**Hipótesis:** en el ejercicio 6 se atribuyó a la corriente EDM la moda de
125-130 BPM del histograma, pero esa explicación quedó sin comprobar. Si es
correcta, la proporción de éxitos en esa banda de tempo no debería ser constante
a lo largo de los años: tendría que subir durante los años de auge del EDM y
bajar después. Para distinguir el sonido de la etiqueta comercial, la serie se
contrasta con el porcentaje de canciones marcadas como Dance/Electronic. El
análisis se acota a 2000-2019 porque 1998, 1999 y 2020 tienen muy pocos
registros.

**Resultados:**

| Periodo | Éxitos con tempo de 120-135 BPM | Éxitos etiquetados Dance/Electronic |
|---|---|---|
| 2000 – 2009 | 21 % en promedio | 3.3 – 14.3 % |
| 2010 – 2014 | 34.6 – 48.7 % (máximo en 2012) | 26.2 – 39.4 % |
| 2015 – 2019 | 18.7 – 24.2 % | 23.6 – 42.4 % |

Correlación entre ambas series: 0.504. Cada año aporta entre 74 y 115 canciones.

---

La hipótesis se confirma. El tempo de baile solo manda en las listas entre 2010
y 2014, y después vuelve al mismo nivel que tenía antes. En 2012 casi la mitad
de los éxitos del año estaban en esa banda. O sea que el segundo pico del
histograma del ejercicio 6 no es algo permanente del pop: es la huella que
dejaron esos cinco años.

Lo que no esperábamos es que la etiqueta no cayera junto con el tempo. Las
canciones marcadas como Dance/Electronic se triplican hacia 2010 y
siguen altas hasta 2019, cuando el tempo característico ya había desaparecido.
Desde 2014 las dos líneas se separan: el pop siguió llamándose música de baile,
pero dejó de sonar a 128 BPM. Se quedó el nombre y se fue el sonido.

Hay que aclarar hasta dónde llega esto. La correlación entre las dos series es
moderada, y el conjunto solo trae canciones que ya fueron éxitos, así que no
podemos decir nada sobre la música que no llegó a las listas. Tampoco podemos
hablar de causa: que las fechas coincidan con el auge del EDM encaja con lo que
dijimos en el ejercicio 6, pero no lo demuestra.
