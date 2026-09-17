# Reparto del informe — 8 párrafos

El código está terminado y en `main`. Falta redactar las justificaciones.

> **Esto no se puede delegar en una IA.** El parcial dice textual: *"No se permite, en
> ningún caso: generar con inteligencia artificial el documento de entrega, el protocolo
> previo, **las justificaciones o las conclusiones**. Estos textos deben ser redactados
> por el equipo."*
>
> Y **P34** pregunta: *"¿En qué punto usó una herramienta de IA y qué le pidió
> exactamente? Muéstreme qué cambió usted de lo que le entregó."*
>
> Este documento reparte **qué responder y dónde está el dato**. El argumento lo escribe
> cada uno.

---

## Reparto

| | Párrafos | |
|---|---|---|
| **Daniel** | E3 · D5 · D6 | 3 |
| **Juan Diego** | J1 · J2 · E1 | 3 |
| **Tomás** | T3 · E2 | 2 |

Tomás lleva dos porque **E2 es el más difícil de todos** (es P15, la pregunta más dura
del banco). Y va deliberadamente a quien no escribió la sección de atípicos: sustenta
una sola persona elegida al azar, así que el que no tocó §8 tiene que poder defenderlo
igual.

---

## Daniel

### E3 — Los siete casos de atípicos, uno por uno
**Responde a:** P16. ¿Qué atípico conservaron y por qué?
**Dónde está el dato:** §8 del script imprime los siete casos con su clasificación,
cuántos registros afecta cada uno y la acción aplicada.
**Qué tiene que salir del párrafo:** por qué cada grupo cayó en esa categoría y no en
otra. El caso 4 (`WorkWeekHrs` entre 100 y 168 h) es el obligatorio: el enunciado exige
mostrar un atípico que NO debe eliminarse y explicar por qué el método falló ahí.

### D5 — Por qué dividir `WorkWeekHrs` entre 10 no es inventar un dato
**Responde a:** P4. ¿Cuál de sus decisiones es la más discutible? Defiéndala.
**Dónde está el dato:** §8, caso 3. El script imprime los 62 valores originales, los 62
corregidos (quedan entre 22,5 y 47,5 h/semana) y el rango del 90% central del resto de
la encuesta (30 a 50).
**Ojo:** esta es la decisión más atacable del trabajo. Dividir entre 10 es reconstruir un
valor que el encuestado nunca escribió.

### D6 — Por qué `CompTotal` no se reconstruye
**Responde a:** P6. ¿Qué información se perdió irreversiblemente?
**Dónde está el dato:** §8, caso 5. 28 registros anulados por encima de 10⁹, valor máximo
encontrado 1,111 × 10²⁴⁷, y **142 monedas distintas** en la columna `CurrencySymbol`.

---

## Juan Diego

### J1 — Por qué imputar y no eliminar los registros incompletos
**Responde a:** P12. ¿Por qué imputar puede ser peor que eliminar el registro? Dé un caso
de su propio dataset.
**Dónde está el dato:** §4.1 y §4.2. El enunciado ofrece cuatro estrategias y pide
*"alguna o varias"*: eligieron imputar. Hay que decir por qué.

### J2 — Por qué `"Desconocido"` y no la moda
**Responde a:** P9. Si el faltante NO es aleatorio, ¿qué le hace su imputación al
análisis posterior?
**Dónde está el dato:** §4.5. Todos los faltantes categóricos van a `"Desconocido"`, sin
distinguir a quien no respondió de quien nunca recibió la pregunta.

### E1 — El orden del pipeline: imputar antes de tratar atípicos
**Responde a:** P3. Si otro equipo tomara su dataset crudo y su protocolo, ¿llegaría al
mismo resultado? ¿Dónde no, y por qué?
**Dónde está el dato:** §8 calcula Q1 y Q3 sobre `valores_antes_de_imputar`, es decir
sobre los datos SIN imputar. El comentario del código explica qué pasaba si no se hacía
así: con la columna ya imputada, `WorkWeekHrs` daba límites [40, 40].
**Por qué es de Juan Diego:** la imputación es su bloque, y el orden discutido es
justamente imputar-antes-de-atípicos.

---

## Tomás

### T3 — Por qué las filas incoherentes se marcan y no se corrigen
**Responde a:** P5. Nombre una decisión que hoy considera equivocada y qué haría
distinto.
**Dónde está el dato:** §9. Dos reglas lógicas, 306 y 7.235 filas que las incumplen, y
dos columnas de bandera (`coherencia_edad_codigo_ok`, `coherencia_experiencia_ok`) que
las marcan sin borrar ni corregir nada.

### E2 — Por qué factor 1,5 y no 3
**Responde a:** **P15**, la pregunta más dura del banco.
**Dónde está el dato:** §8 declara el factor 1,5 y lo aplica. El protocolo que entregaron
dice *"rango intercuartílico"* **sin número**: nadie se comprometió a 1,5, así que hay que
sostenerlo por sus méritos.
**El contraste que hay que poder dar:** con factor 1,5 el método marca 14.653 registros
(23,0% del dataset). Con factor 3 marcaría menos. Hay que saber qué se gana y qué se
pierde al mover ese número.

---

## Los tres, juntos

Además de los ocho párrafos, el enunciado pide para la sustentación:

| Tema | Dónde está el dato |
|---|---|
| Comparación dataset inicial vs. final | 64.461 × 61 → 63.803 × 113 |
| Desviaciones respecto al protocolo previo | El script cumple las 4 reglas entregadas; no hay ninguna desviación |
| Una decisión que hoy consideran equivocada | Punto 6 de la sustentación |
| Declaración de uso de IA | Ya redactada en el protocolo entregado |

> **Sobre la pregunta de la decisión equivocada:** tienen un caso real y propio. Las
> columnas binarias de lenguajes hacían que `C`, `C#` y `C++` terminaran los tres en la
> misma columna, y dos lenguajes desaparecían en silencio. Se detectó porque dos totales
> que debían coincidir no coincidían: 257.476 contra 288.004. Está en el historial de
> commits.

---

## Antes de entregar

- [ ] Los 8 párrafos escritos, cada uno por quien le toca
- [ ] Cada integrante puede explicar **el bloque del otro**, no solo el suyo
- [ ] Declaración de uso de IA al inicio del documento
- [ ] Comprimido armado: código, declaración, dataset original y dataset limpio

**Este archivo no va en la entrega.** Es coordinación interna.
