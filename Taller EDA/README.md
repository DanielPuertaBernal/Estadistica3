# estadisticaTrabajos

Coursework for **Estadística III** — Ingeniería de Sistemas, Universidad Católica de Oriente.

## Current work

**Taller 07 — Estadística descriptiva y análisis exploratorio de datos (EDA)**
See [`07 - Taller estadistica descriptiva y EDA.md`](07%20-%20Taller%20estadistica%20descriptiva%20y%20EDA.md)
for the full brief. Dataset: `data/07 - canciones.csv` (2000 rows x 18 columns,
global hit songs, 1998-2020).

## Environment

Dependencies are managed with [uv](https://docs.astral.sh/uv/); the virtual
environment lives in `.venv` (Python 3.12, not committed).

```bash
uv sync                 # recreate .venv from pyproject.toml + uv.lock
uv run jupyter lab      # notebook workflow (deliverable is .ipynb)
```

If `uv` is not on PATH: `export PATH="$HOME/.local/bin:$PATH"`.

In VS Code, select the interpreter at `.venv/bin/python`.

Stack: pandas, numpy, matplotlib, seaborn, jupyterlab, openpyxl.

## Dataset notes

`Taller_EDA_Puerta_Guzman.py` reads `data/07 - canciones.csv` (2000 rows x 18 columns). The `.xlsx`
in the same folder is an **older 17-column export without the `explicit`
column**; it is kept only for reference.

Findings from the inspection:

- No null values, but **59 fully duplicated rows**.
- `popularity` is 0 for **126 songs** - almost certainly a missing-value
  sentinel rather than a real measurement.
- `genre` is multi-valued (1279 of 2000 cells) and comma-separated; **22 songs**
  carry the literal `set()`, a missing genre that `isna()` does not detect.
- `year` spans **1998-2020**, not 2000-2019 as the brief states (42 songs fall
  outside that range).
- `key` and `mode` are integers encoding categories, not quantities.

## Deliverable

`Taller_EDA_Puerta_Guzman.py` - the code: `#%%` cells with the ten exercises in
order. `figuras/` holds the five generated charts to attach.

The written analyses live in the `analisis-parte-*.md` reports, one per part of
the brief, plus `analisis-punto-opcional.md` for the bonus question; the script only points to them. The brief itself asks for the
analyses as block comments inside the script, but the instructor asked for them
to be kept in the reports instead.
