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
data/archive.zip   Dataset original comprimido — se versiona (histórico)
archive/           Dataset descomprimido para consultas — NO se versiona
doc/               Enunciado del parcial y entregables
```

El CSV descomprimido pesa ~94 MB, por encima del límite de 100 MB de GitHub y muy por
encima del umbral recomendado de 50 MB. Por eso el original se conserva comprimido en
`data/archive.zip` (9.4 MB) y `archive/` está en `.gitignore`.

## Preparación del entorno

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
unzip data/archive.zip -d archive/
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
