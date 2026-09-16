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
data/                         SOLO el dataset original, sin comprimir
  survey_results_public.csv   Respuestas de la encuesta — se versiona
  survey_results_schema.csv   Diccionario de variables — se versiona
salidas/                      Todo lo que produce el script — NO se versiona
  stackoverflow_limpio.csv    Dataset limpio
  tabla_sesgo_imputacion.csv  Estadísticos antes/después de imputar
  graficas/                   Histogramas antes/después por variable
doc/                          Enunciado, entregables y plan de revisión
```

`data/` contiene únicamente el dataset original, sin comprimir. Nada de lo que produce
la limpieza entra ahí: el script escribe siempre en `salidas/`, y el archivo original
no se modifica nunca.

`survey_results_public.csv` pesa 94.603.888 bytes (90 MiB). Está por debajo del límite
duro de GitHub (100 MiB) pero muy por encima del umbral recomendado de 50 MB, así que
GitHub avisa al subirlo. Como el original nunca cambia, git guarda una sola copia.

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

Descargar el ZIP desde la página del dataset y descomprimirlo dentro de `data/`.

El archivo original no se modifica: la limpieza produce un archivo nuevo.

## Limpieza

```bash
.venv/bin/python limpieza_stackoverflow.py
```

El script lee `data/archive.zip` directamente (no hace falta descomprimirlo) y escribe:

| Salida | Contenido |
|---|---|
| `salidas/stackoverflow_limpio.csv` | Dataset limpio |
| `salidas/tabla_sesgo_imputacion.csv` | Estadísticos antes/después de imputar |
| `salidas/graficas/` | Histogramas antes/después por variable |

Las rutas se resuelven desde la raíz del repositorio, así que da igual desde qué
carpeta se ejecute.

El plan de revisión y los pendientes están en `doc/2-plan-de-ejecucion.md`.
