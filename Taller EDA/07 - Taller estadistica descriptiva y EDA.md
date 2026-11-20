# Taller: Estadística descriptiva y análisis exploratorio de datos (EDA)

**Curso:** Estadística III — Ingeniería de Sistemas
**Docente:** Daniel Betancur Trujillo (dbetancur@uco.edu.co)
**Universidad Católica de Oriente**

**Modalidad:** individual o en parejas
**Valor:** ___ % de la nota del corte
**Fecha de entrega:** ___________

---

## 1. Contexto

La industria musical toma decisiones millonarias apoyada en datos: qué canción promocionar, qué artista firmar, qué características tiende a premiar el público. Detrás de esas decisiones hay descripciones estadísticas de catálogos enormes.

En este taller trabajará con `songs_normalize.csv`, un conjunto de canciones que figuraron entre los éxitos de las listas globales entre 2000 y 2019. Cada canción viene descrita por atributos de audio calculados automáticamente (qué tan bailable es, qué tan enérgica, su tempo en BPM) junto con metadatos como el artista, el año y su nivel de popularidad.

Su tarea no es construir un modelo predictivo, sino algo previo y más importante: **entender los datos antes de modelarlos**. Un EDA bien hecho revela errores de medición, distribuciones asimétricas, categorías mal codificadas y relaciones inesperadas que, si pasan desapercibidas, invalidan cualquier análisis posterior.

## 2. Objetivos de aprendizaje

Al terminar el taller, usted debe ser capaz de:

1. Cargar, inspeccionar y transformar un conjunto de datos real con `pandas`.
2. Calcular e **interpretar** medidas de tendencia central y de dispersión, distinguiendo cuándo la media es representativa y cuándo no.
3. Describir variables categóricas mediante frecuencias y proporciones, incluyendo casos donde una celda contiene múltiples valores.
4. Elegir el gráfico adecuado según el tipo de variable y producir figuras legibles y bien etiquetadas.
5. Cuantificar la relación lineal entre variables numéricas y traducir un coeficiente de correlación a una afirmación en lenguaje natural sobre el fenómeno estudiado.

## 3. Datos

**Archivo:** `songs_normalize.csv` (≈ 2.000 registros)

| Variable | Tipo | Descripción |
|---|---|---|
| `artist`, `song` | Texto | Intérprete y título |
| `year` | Entero | Año de publicación |
| `duration_ms` | Numérica | Duración en milisegundos |
| `explicit` | Booleana | Si la letra contiene lenguaje explícito |
| `popularity` | Numérica (0–100) | Índice de popularidad de la plataforma |
| `danceability` | Numérica (0–1) | Qué tan apta es para bailar |
| `energy` | Numérica (0–1) | Intensidad y actividad percibida |
| `loudness` | Numérica (dB) | Volumen promedio; toma valores negativos |
| `valence` | Numérica (0–1) | Positividad emocional transmitida |
| `tempo` | Numérica (BPM) | Pulsos por minuto |
| `speechiness`, `acousticness`, `instrumentalness`, `liveness` | Numéricas (0–1) | Otros atributos de audio |
| `key`, `mode` | Enteras | Tonalidad y modo, **codificados como números pero de naturaleza categórica** |
| `genre` | Texto | Género(s). **Puede contener varios géneros en una misma celda, separados por comas** |

> Dos advertencias que condicionan varios ejercicios: `key` y `mode` son números que representan categorías, y `genre` es una variable multivaluada. Trátelas en consecuencia.

## 4. Instrucciones generales

- Cargue el archivo en su entorno de trabajo (Spyder, VS Code o Jupyter) y resuelva los ejercicios **en orden**, apoyándose en el código visto en clase.
- Cada ejercicio debe entregarse con **dos componentes**: el código que produce el resultado y un **párrafo de análisis** que responda la pregunta planteada. Un bloque de código sin interpretación no recibe puntaje en el criterio de interpretación, que es el de mayor peso.
- Todo gráfico debe tener título, ejes rotulados con nombre y unidad, y leyenda cuando aplique.
- Redacte sus conclusiones refiriéndose al fenómeno, no al procedimiento. "La correlación es 0.74" describe una salida; "las canciones más enérgicas tienden a sonar considerablemente más fuerte" describe un hallazgo.
- El código debe ejecutarse de principio a fin sin errores desde una sesión limpia.

---

## 5. Ejercicios

### Parte 1 — Ingesta y limpieza inicial

**1.** Cargue el conjunto de datos y muestre sus primeras 5 filas.

**2.** Imprima un resumen del DataFrame que incluya número de filas y columnas, tipos de datos y verificación de valores nulos. Indique si el conjunto requiere alguna limpieza antes de continuar y justifique su respuesta.

### Parte 2 — Estadística descriptiva univariada

**3.** La columna `duration_ms` está en milisegundos. Cree una nueva columna llamada `duration_min` que exprese la duración en minutos.

**4.** Calcule media, mediana, desviación estándar, mínimo y máximo para `duration_min`, `popularity` y `danceability`.
> **Analice:** compare la media y la mediana de `popularity`. ¿Qué le indica esa diferencia sobre la forma de la distribución? ¿Cuál de las dos medidas reportaría usted si tuviera que describir la popularidad "típica" con un solo número, y por qué?

**5.** Determine los 5 géneros más frecuentes y el porcentaje de canciones explícitas.
> **Atención:** una canción puede tener varios géneros en la misma celda. Decida cómo tratar esos casos —contar la combinación completa como una categoría o separarla en géneros individuales—, aplique su decisión y **justifíquela**. Ambas rutas son defendibles; lo que se evalúa es que sea consciente del problema y explique su criterio.

### Parte 3 — Visualización de datos

**6.** Construya un histograma de `tempo` con una línea vertical roja que marque la media.
> **Analice:** ¿en qué rango de BPM se concentra la mayor parte del repertorio? ¿La distribución es unimodal o aparecen varias concentraciones? Si observa más de un pico, proponga una explicación musical.

**7.** Construya un boxplot que compare `popularity` según la canción sea explícita o no.
> **Analice:** ¿hay una diferencia visual apreciable entre ambos grupos? Compare medianas y dispersión, no solo la posición de las cajas. Advierta si los tamaños de los dos grupos son muy desiguales y qué implica eso para la comparación.

### Parte 4 — Análisis bivariado y correlación

**8.** Seleccione `danceability`, `energy`, `valence` y `loudness` y calcule la matriz de correlación de Pearson.

**9.** Visualice esa matriz con un mapa de calor. Use una paleta divergente y muestre los valores anotados sobre las celdas.

**10.** Identifique el par con la correlación más fuerte en valor absoluto (positiva o negativa), construya su diagrama de dispersión y describa la relación.
> **Analice:** caracterice dirección, fuerza y forma. ¿La nube de puntos sugiere una relación lineal o hay curvatura? ¿Observa valores atípicos que puedan estar inflando el coeficiente? Cierre advirtiendo qué **no** permite concluir esta correlación.

### Punto opcional (bonificación hasta 0.5)

Elija una pregunta propia que los datos puedan responder —por ejemplo, cómo ha evolucionado la duración promedio de los éxitos a lo largo de los años, o si algún género se distingue sistemáticamente en sus atributos de audio—, resuélvala con las técnicas del curso y presente el hallazgo en un solo gráfico bien construido.

---

## 6. Entrega

- **Formato:** notebook (`.ipynb`) con las conclusiones en celdas de texto, o script `.py` con separadores `#%%` y los análisis en comentarios de bloque.
- **Nombre del archivo:** `Taller_EDA_Apellido1_Apellido2.ipynb`
- **Adjuntar:** el archivo de código y, si trabaja con script, las figuras generadas.
- **Medio y fecha:** ___________

---

## 7. Rúbrica de evaluación

Escala 0.0 – 5.0. La nota final es el promedio ponderado de los cuatro criterios.

### Criterio 1 — Manejo de datos con pandas · 20 %

| Nivel | Descriptor |
|---|---|
| **Excelente (4.5 – 5.0)** | Carga el archivo sin errores, describe correctamente la estructura (filas, columnas, tipos), verifica nulos y crea `duration_min` con la conversión correcta. El código corre completo desde cero y es legible. |
| **Bueno (3.5 – 4.4)** | Alcanza los mismos resultados, pero con pasos redundantes, advertencias de pandas no atendidas o una transformación resuelta de forma innecesariamente enrevesada. |
| **Regular (2.5 – 3.4)** | La nueva variable tiene un error de escala o de nombre, o la descripción de la estructura es incompleta (omite tipos o no revisa nulos). |
| **Insuficiente (< 2.5)** | No logra cargar los datos o no realiza las transformaciones solicitadas. |

### Criterio 2 — Cálculos estadísticos · 25 %

| Nivel | Descriptor |
|---|---|
| **Excelente (4.5 – 5.0)** | Reporta las cinco medidas para las tres variables pedidas con los métodos adecuados. Resuelve correctamente las frecuencias de `genre` explicando el tratamiento de los valores compuestos, y calcula bien el porcentaje de canciones explícitas. La matriz de correlación se construye sobre las variables correctas. |
| **Bueno (3.5 – 4.4)** | Los cálculos son correctos pero omite una medida o una variable, o resuelve `genre` sin explicitar el criterio usado con los valores compuestos. |
| **Regular (2.5 – 3.4)** | Errores en la aplicación de funciones básicas: confunde medidas, calcula porcentajes sobre una base equivocada o ignora por completo el problema de los géneros compuestos. |
| **Insuficiente (< 2.5)** | No presenta los cálculos solicitados o los resultados no corresponden a los datos. |

### Criterio 3 — Visualización · 25 %

| Nivel | Descriptor |
|---|---|
| **Excelente (4.5 – 5.0)** | Los tres gráficos son del tipo correcto para el tipo de variable, llevan título y ejes rotulados con unidades, el histograma incluye la línea de la media, el mapa de calor usa paleta divergente con valores anotados y la dispersión es legible (control de solapamiento si aplica). |
| **Bueno (3.5 – 4.4)** | Produce todos los gráficos solicitados, pero faltan títulos, rótulos de eje, la línea guía de la media o la anotación de valores en el mapa de calor. |
| **Regular (2.5 – 3.4)** | Usa un gráfico inapropiado para el tipo de variable (por ejemplo, dispersión donde se pide comparación entre categorías), o las figuras son difíciles de leer. |
| **Insuficiente (< 2.5)** | No presenta gráficos o son ininteligibles. |

### Criterio 4 — Interpretación analítica · 30 %

| Nivel | Descriptor |
|---|---|
| **Excelente (4.5 – 5.0)** | Contrasta media y mediana concluyendo correctamente sobre la asimetría de `popularity`. Lee el histograma identificando el rango de concentración y comentando la forma. Compara los grupos del boxplot atendiendo a medianas y dispersión. Interpreta la correlación en dirección, fuerza y forma, y advierte que no implica causalidad. Las conclusiones hablan del fenómeno musical, no solo de las salidas del código. |
| **Bueno (3.5 – 4.4)** | Las interpretaciones son correctas pero se quedan en la superficie: describen el resultado sin explicar qué significa, o responden algunas preguntas y dejan otras sin desarrollar. |
| **Regular (2.5 – 3.4)** | Las conclusiones no se derivan de los resultados obtenidos, se contradicen con las cifras o repiten enunciados generales aplicables a cualquier conjunto de datos. |
| **Insuficiente (< 2.5)** | Entrega únicamente código, sin análisis textual. |

### Consideraciones adicionales

- **Código no ejecutable:** si el archivo no corre de principio a fin, se descuentan 0.3 sobre la nota final.
- **Bonificación:** hasta 0.5 por el punto opcional, sin exceder 5.0.
- **Trabajo en parejas:** ambos integrantes deben poder explicar cualquier parte de la entrega.

---

## 8. Lista de chequeo antes de entregar

- [ ] El código corre completo desde una sesión nueva, sin errores.
- [ ] Los 10 ejercicios están resueltos y numerados.
- [ ] Cada ejercicio con pregunta tiene su párrafo de análisis.
- [ ] Todos los gráficos tienen título y ejes rotulados.
- [ ] El histograma incluye la línea roja de la media.
- [ ] Está explicado el criterio usado con los géneros compuestos.
- [ ] La conclusión sobre la correlación aclara que no implica causalidad.
