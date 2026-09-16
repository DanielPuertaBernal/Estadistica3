# 1. Protocolo previo de limpieza

> Transcripción literal del documento entregado al docente. No se modifica.
> El borrador largo de nueve secciones que vivía antes en este archivo nunca se
> entregó y fue descartado.

---

## 1. Cuando eliminamos una columna

Vamos a descartar cualquier columna a la que le falte más de la mitad de los datos. Es un
umbral alto y lo elegimos a propósito: en una encuesta, una celda vacía rara vez quiere
decir que el dato se perdió, sino que esa pregunta no le tocaba a esa persona. Si fuéramos
más estrictos, las primeras en caer serían las preguntas sobre sueldo, que son opcionales
por diseño y a la vez el centro de lo que queremos estudiar. Preferimos conservarlas y ser
cuidadosos al usarlas.

## 2. Cómo completamos los datos que faltan

| Tipo de variable | Qué hacemos | Por qué |
|---|---|---|
| Numérica simétrica | Rellenar con el promedio | Cuando los datos se reparten de forma pareja, el promedio representa bien al encuestado típico. |
| Numérica asimétrica | Rellenar con la mediana | Si la distribución tiene una cola larga, el promedio se va detrás de los valores extremos y deja de parecerse a nadie. |
| Categórica | Crear una categoría "Desconocido" | Poner la respuesta más frecuente es inventar lo que esa persona contestó, y además infla una categoría que ya era grande. Dejarla marcada conserva el dato de que no sabemos. |

## 3. Cómo detectamos valores atípicos

Usamos el rango intercuartílico y no el criterio de las k desviaciones estándar. El
problema del segundo es que se muerde la cola: en variables como la remuneración, el
promedio y la desviación ya vienen corridos por los mismos valores extremos que queremos
detectar, así que los atípicos terminan definiendo el umbral que debería atraparlos. Si los
montos son lo bastante grandes, la desviación ni siquiera llega a calcularse. El rango
intercuartílico se apoya en la posición de los datos y no en su magnitud, así que un valor
desmedido no lo mueve.

## 4. Qué consideramos un duplicado

Dos filas son la misma respuesta sí coinciden en todas las columnas menos en Respondentm,
ya que este es distinto en cada fila por definición. Si lo incluimos en la comparación nos
aseguramos de no encontrar nunca un duplicado.

## 5. Declaración de uso de la IA

Usamos Claude (Anthropic) como apoyo en la parte de código: para resolver dudas de
sintaxis, depurar errores y revisar que la lógica de las reglas de este protocolo quedara
bien implementada. La definición de las reglas, los umbrales y las justificaciones
metodológicas fueron decisión nuestra, no de la IA.

Para la redacción del informe usamos Gemini (Google) como apoyo de estilo, ortografía y
claridad del texto, sin delegarle la argumentación ni las conclusiones.

---

**Integrantes:**

- Daniel Puerta Bernal
- Tomás Marín Estrada
- Juan Diego Guzman Chalarca
