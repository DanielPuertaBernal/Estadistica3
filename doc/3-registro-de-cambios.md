# 3. Registro de cambios

Qué se tocó del código que llegó del compañero, y por qué. Uso interno: **no va en la
entrega**.

## Script de limpieza

| Sección | Cambio | Motivo |
|---|---|---|
| §1 | Lee `data/archive.zip` con `zipfile`, sin descomprimir en disco. Rutas resueltas desde la raíz del repositorio | Leía un CSV suelto del directorio actual; solo corría desde una carpeta |
| §4.1 | El % de nulos se recalcula después de convertir tipos | Se medía en §2, antes de la conversión. `to_numeric(errors="coerce")` puede crear nulos nuevos y el umbral del 50% decidía con datos viejos. **En este dataset no cambia ninguna decisión**, pero el umbral queda apoyado en los números correctos |
| §5 | De cada grupo de duplicados se conserva el registro **más completo**, no el primero del archivo. Empate: el primero | El orden del archivo no significa nada. Se imprime cuántos grupos cambian de ganador: **0** — los duplicados son encuestas casi vacías con la misma cantidad de campos llenos |
| §7 | Normalización: se recortan espacios siempre; las mayúsculas se unifican **solo donde hay colisión real**, hacia la variante más frecuente. Se cuentan categorías antes y después | Pasar todo a minúsculas convertiría `United States` en `united states` sin arreglar nada: **0 columnas** tienen colisiones. El conteo antes/después prueba que no se fusionó ninguna categoría distinta |
| §7.1 | **Nuevo.** Detecta las 20 columnas de respuesta múltiple (`;`), agrega `n_<pregunta>` con cuántas opciones marcó cada persona, exporta `salidas/frecuencias_respuesta_multiple.csv` con las 286 opciones reales, y genera binarias `usa_<opción>` para `LanguageWorkedWith` | Contar frecuencias sin separar da resultados sin sentido: `Python;SQL` y `SQL;Python` cuentan como categorías distintas. Binarias para una sola pregunta porque expandir las 20 agregaría 286 columnas |
| §7.2 | **Nuevo.** Columnas `Country_agrupado` y `Ethnicity_agrupado`: categorías bajo el 1% pasan a `"Otros"`. Las originales no se tocan | Las dos tienen cola larga, pero muy distinta: en `Ethnicity` la cola es el **3,9%** de la gente (agrupar es barato); en `Country` es el **30,1%** (agrupar metería casi un tercio de los encuestados en una categoría que no significa nada) |
| §8 | Evidencia impresa para dos decisiones que antes iban sin respaldo | `WorkWeekHrs ÷ 10`: los 62 valores corregidos quedan entre 22,5 y 47,5 h/semana, todos dentro de jornadas posibles. `CompTotal`: hay **142 monedas** distintas en el dataset, por eso no se reconstruye y el análisis usa `ConvertedComp` (ya en USD) |

**Resultado:** 64.461 × 61 → **63.803 × 110**. Sin errores, de punta a punta.

## Dependencias

`requirements.txt` pasó de **111 paquetes a 3**. El script solo importa `pandas`, `numpy` y
`matplotlib`; el resto era el stack de Jupyter, `kaggle`, `seaborn`, `requests` y su cola de
transitivas, sin ningún consumidor en el código. Las transitivas reales (`pillow`,
`python-dateutil`, `fonttools`, etc.) las resuelve pip sola.

## Repositorio

| Cambio | Motivo |
|---|---|
| Script a la raíz, archivo único | Indicación del profesor |
| Borrada la carpeta `archive/` | Era el original descomprimido; quedó de sobra al leer el ZIP directo |
| `data/` solo con `archive.zip` | Indicación del profesor. El limpio y todo lo derivado van a `salidas/`, ignorado por git |
| Borrado el Excel de entrega | Indicación del profesor |
| `doc/1-protocolo-previo-de-limpieza.md` reemplazado por la transcripción literal de lo entregado | El repo guardaba un borrador de 9 secciones que nunca se firmó ni se entregó, con nombre de protocolo |
| `README` sin instrucciones de descarga de Kaggle | El dataset viaja en el repo: clonar y correr alcanza |

## Lo que NO se tocó

Las cuatro reglas del protocolo entregado: umbral del 50% para columnas, imputación por
sesgo, rango intercuartílico para atípicos, y duplicado = todas las columnas menos
`Respondent`. **El script las cumplía y las sigue cumpliendo.**

Pendientes abiertos y su reparto: `doc/2-plan-de-ejecucion.md`.
