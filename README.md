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
doc/                          Enunciado, protocolo y plan de revisión
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

## Documentos

| Archivo | Contenido |
|---|---|
| `doc/1-protocolo-previo-de-limpieza.md` | Protocolo entregado al docente — transcripción literal |
| `doc/2-plan-de-ejecucion.md` | Reparto de revisión y pendientes — uso interno, no va en la entrega |
| `doc/Parcial - Estadística III.pdf` | Enunciado |
| `REPARTO-DEL-INFORME.md` | Quién escribe cada párrafo del informe — uso interno |
| `EVIDENCIA-DANIEL.md` | Datos y figuras para los párrafos de Daniel — uso interno |
