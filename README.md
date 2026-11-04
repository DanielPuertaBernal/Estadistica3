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

## Red neuronal: calculadora de salarios

`red_neuronal_salarios.ipynb` entrena una red neuronal que predice el salario anual a
partir del lenguaje, los años de experiencia profesional y el país (ver
`PROPUESTA-RED-NEURONAL.md`). Necesita el dataset limpio, así que primero hay que
correr la limpieza.

```bash
.venv/bin/jupyter nbconvert --to notebook --execute --inplace red_neuronal_salarios.ipynb
```

Entrena solo con los salarios que la persona reportó de verdad (columna
`ConvertedComp_reportado` del dataset limpio) y escribe en `salidas/`:

| Salida | Contenido |
|---|---|
| `salidas/modelo_salarios.keras` | Red entrenada |
| `salidas/preprocesador_salarios.joblib` | Codificación de las entradas, ajustada con el entrenamiento |
| `salidas/calculadora_opciones.json` | Lenguajes, países, métricas de prueba y σ de los residuos |
| `salidas/salarios_referencia.csv` | Salarios reales de entrenamiento, para comparar cada estimación |

La semilla es fija y TensorFlow corre en modo determinista: dos corridas dan las
mismas métricas.

### Calculadora

Con el modelo ya entrenado (el notebook lo deja en `salidas/`):

```bash
.venv/bin/streamlit run calculadora_salarios.py
```

Se elige un lenguaje, los años de experiencia profesional y un país, y devuelve el
salario anual estimado en USD. Tiene dos pestañas:

- **Calculadora:** la estimación, el rango del 68 % y una campana normal del error de
  la red, dibujada sobre los salarios reales de personas con ese mismo perfil.
- **¿Cómo lo calcula la red?:** las tres capas (44 entradas → 32 neuronas ReLU → 1
  salida) con las neuronas que se encienden y el recorrido del dato hasta el salario.
