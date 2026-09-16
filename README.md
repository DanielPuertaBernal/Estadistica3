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
limpieza_stackoverflow.py     Código de limpieza — un solo archivo, en la raíz
data/                         SOLO el dataset original
  archive.zip                 Descarga de Kaggle, comprimida — se versiona
salidas/                      Todo lo que produce el script — NO se versiona
  stackoverflow_limpio.csv    Dataset limpio
  tabla_sesgo_imputacion.csv  Estadísticos antes/después de imputar
  graficas/                   Histogramas antes/después por variable
doc/                          Enunciado, protocolo y plan de revisión
```

`data/` contiene únicamente el dataset original, comprimido. Nada de lo que produce la
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
| `salidas/stackoverflow_limpio.csv` | Dataset limpio |
| `salidas/tabla_sesgo_imputacion.csv` | Estadísticos antes/después de imputar |
| `salidas/graficas/` | Histogramas antes/después por variable |

Las rutas se resuelven desde la raíz del repositorio, así que da igual desde qué
carpeta se ejecute.

El plan de revisión y los pendientes están en `doc/2-plan-de-ejecucion.md`.
