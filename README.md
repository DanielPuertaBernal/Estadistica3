# Estadistica3

Repositorio que contiene todo el contenido trabajado para el curso de Estadística III.

## Dataset

**Stack Overflow Developer Survey Dataset** (Palvinder, licencia MIT)

- Procedencia: https://www.kaggle.com/datasets/palvinder2006/stackoverflow
- 64.461 registros × 61 variables (5 numéricas, 56 categóricas)

Cumple los mínimos del parcial (≥1000 registros y ≥20 variables combinadas).

## Estructura

```
limpieza_stackoverflow.py     Código de limpieza — un solo archivo, en la raíz
data/                         SOLO el dataset original
  archive.zip                 Descarga de Kaggle, comprimida — se versiona
salidas/                      Todo lo que produce el script — NO se versiona
  stackoverflow_limpio.csv    Dataset limpio
  graficas/                   Histogramas y gráfica de atípicos
```

**El dataset original ya está en el repositorio**, en `data/archive.zip`. No hay que
descargarlo de Kaggle ni tener credenciales: basta con clonar y correr el script.

`data/` contiene únicamente ese dataset original, comprimido. Nada de lo que produce la
limpieza entra ahí: el script escribe siempre en `salidas/`, y el archivo original no
se modifica nunca.

**No hace falta descomprimir nada.** El script lee el CSV directamente desde el ZIP, así
que los ~94 MB del original nunca necesitan existir sueltos en el disco. Por eso
`data/*.csv` está en `.gitignore`: si alguien descomprime ahí para mirar los datos, ese
archivo no llega a un commit por accidente.

**La entrega es un comprimido aparte**, no este repositorio. El dataset limpio se toma
de `salidas/` al armarlo.

## Preparación del entorno

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Limpieza

```bash
.venv/bin/python limpieza_stackoverflow.py
```

El script lee `data/archive.zip` directamente (no hace falta descomprimirlo) y escribe:

| Salida | Contenido |
|---|---|
| `salidas/stackoverflow_limpio.csv` | Dataset limpio |
| `salidas/graficas/` | Histogramas antes/después y gráfica de atípicos |

Las tablas (sesgo por imputación y frecuencias de respuesta múltiple) se imprimen en
consola, no se exportan: son evidencia del informe, no insumo de otro script.

Las rutas se resuelven desde la raíz del repositorio, así que da igual desde qué
carpeta se ejecute.

## Red neuronal: 5 redes, una por país

`red_neuronal_salarios.ipynb` entrena **una red neuronal por país** para explicar las
diferencias de salario entre programadores del mismo país, y compara los resultados de
los 5 países (ver `PROPUESTA-RED-NEURONAL.md`). Los países se eligen solos: los 5 con
más salarios válidos después de quitar los atípicos (hoy Estados Unidos, India, Reino
Unido, Alemania y Canadá). Necesita el dataset limpio, así que primero hay que correr la
limpieza.

```bash
.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=5400 red_neuronal_salarios.ipynb
```

La corrida completa tarda unos 60 minutos en CPU: la comparación de arquitecturas entrena
150 redes (6 arquitecturas × 5 países × 5 pliegues). Escribe en `salidas/`:

| Salida | Contenido |
|---|---|
| `salidas/modelos/<país>.keras` | Red entrenada de cada país |
| `salidas/modelos/<país>_preprocesador.joblib` | Codificación de las entradas, ajustada con el entrenamiento de ese país |
| `salidas/calculadora_opciones.json` | Variables elegidas, opciones de cada pregunta por país, métricas, σ de los residuos e importancia de cada variable |
| `salidas/salarios_referencia.csv` | Salarios reales de los 5 países, para comparar cada estimación |

La semilla es fija y TensorFlow corre en modo determinista: dos corridas dan las
mismas métricas.

### Calculadora

Con las redes ya entrenadas (el notebook las deja en `salidas/`):

```bash
.venv/bin/streamlit run calculadora_salarios.py
```

Se elige el país y se responde el perfil (lenguajes, experiencia, tipo de desarrollador,
plataformas, tamaño de la empresa, estudios…); la red de ese país devuelve el salario
anual estimado en USD. Tiene tres pestañas:

- **Calculadora:** la estimación, el rango del 68 % y una campana normal del error de
  la red, dibujada sobre los salarios reales de personas con un perfil parecido.
- **El mismo perfil en los 5 países:** las mismas respuestas evaluadas por la red de
  cada país, y qué variable pesa más en cada uno.
- **¿Cómo lo calcula la red?:** las capas de la red (entrada → 5 capas ocultas ReLU →
  salida) con las neuronas que se encienden y el recorrido del dato hasta el salario.
