# Estadistica3

Repositorio que contiene todo el contenido trabajado para el curso de Estadística III.

## Dataset

**Stack Overflow Developer Survey Dataset** (Palvinder, licencia MIT)

- Enlace: https://www.kaggle.com/datasets/palvinder2006/stackoverflow
- Referencia Kaggle: `palvinder2006/stackoverflow`
- 64.461 registros × 61 variables (5 numéricas, 56 categóricas)

Cumple los mínimos del parcial (≥1000 registros y ≥20 variables combinadas).

## Estructura

```
limpieza_stackoverflow.py     Código de limpieza
data/                         Datasets — la única carpeta de datos
  archive.zip                 Original de Kaggle, comprimido — se versiona
  stackoverflow_limpio.zip    Resultado de la limpieza, comprimido — se versiona
salidas/                      Tablas y gráficas del script — NO se versiona
doc/                          Enunciado del parcial y entregables
```

**No hace falta descomprimir nada.** El script lee el CSV directamente desde
`data/archive.zip`, así que el dataset original nunca necesita existir suelto en el
disco.

Ningún CSV grande se versiona sin comprimir. El original pesa ~94 MB y el limpio
103 MB: ambos por encima del umbral recomendado de 50 MB de GitHub, y el limpio a
1,6 MB del límite duro de 100 MB. Por eso los dos viven comprimidos en `data/` y sus
versiones sueltas están en `.gitignore`.

El nombre `archive.zip` viene de la descarga de Kaggle y lo congela la sección 1.9 del
protocolo (`doc/1-protocolo-previo-de-limpieza.md`) como archivo de entrada. Por eso no
se renombra: cambiarlo sería una desviación del protocolo que habría que reportar.

## Preparación del entorno

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Descarga desde Kaggle

Kaggle no permite la descarga anónima: la API responde 404 sin credenciales.

**Opción A — API de Kaggle**

1. Generar el token en https://www.kaggle.com/settings → *Create New API Token*.
2. Ubicarlo en `~/.kaggle/kaggle.json` con permisos `600`.
3. Ejecutar:

```bash
.venv/bin/kaggle datasets download -d palvinder2006/stackoverflow -p data/
```

**Opción B — Descarga manual**

Descargar el ZIP desde la página del dataset y guardarlo como `data/archive.zip`.

El archivo original no se modifica: la limpieza produce un archivo nuevo.

## Limpieza

```bash
.venv/bin/python limpieza_stackoverflow.py
```

El script lee `data/archive.zip` directamente (no hace falta descomprimirlo) y escribe:

| Salida | Contenido |
|---|---|
| `data/stackoverflow_limpio.csv` | Dataset limpio |
| `salidas/tabla_sesgo_imputacion.csv` | Estadísticos antes/después de imputar |
| `salidas/graficas/` | Histogramas antes/después por variable |

Las rutas se resuelven desde la raíz del repositorio, así que da igual desde qué
carpeta se ejecute.

Después de regenerar el dataset limpio hay que volver a comprimirlo para versionarlo:

```bash
zip -j -9 data/stackoverflow_limpio.zip data/stackoverflow_limpio.csv
```

El plan de revisión y los pendientes están en `doc/2-plan-de-ejecucion.md`.
