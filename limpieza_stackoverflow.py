

import random
import warnings
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # para poder generar las imagenes sin pantalla
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 0. REPRODUCIBILIDAD
# ---------------------------------------------------------------------------
# Fijamos la semilla en todo lo que use azar (aqui no hacemos muestreo
# aleatorio de filas, pero dejamos la semilla fijada por si en el futuro se
# agrega alguna operacion que lo necesite: dos ejecuciones deben dar
# exactamente el mismo dataset final).
SEMILLA = 42
random.seed(SEMILLA)
np.random.seed(SEMILLA)

# ---------------------------------------------------------------------------
# Rutas de entrada / salida
# ---------------------------------------------------------------------------
# Todas las rutas se resuelven a partir de la carpeta donde vive este archivo
# (la raiz del repositorio), NO del directorio desde el que se ejecuta el
# script. Asi da igual desde donde se lance: siempre encuentra los mismos
# archivos.
RAIZ = Path(__file__).resolve().parent

# Entrada: el ZIP original, tal como lo fija el protocolo (seccion 1.9). El
# CSV descomprimido pesa ~94 MB, asi que nunca se deja suelto en el
# repositorio: pandas lee el miembro directamente desde el ZIP.
ARCHIVO_ZIP = RAIZ / "data" / "archive.zip"
CSV_DENTRO_DEL_ZIP = "survey_results_public.csv"

# Salidas: TODO lo que produce el script vive en salidas/, fuera de data/.
# DESVIACION del protocolo: la seccion 1.9 fija
# "data/stackoverflow_limpio.csv" como archivo de salida. Se cambio porque el
# profesor pidio que el dataset limpio quede en salidas/ y que data/ guarde
# unicamente el original. Queda reportada en doc/2-plan-de-ejecucion.md.
CARPETA_SALIDAS = RAIZ / "salidas"
ARCHIVO_LIMPIO = CARPETA_SALIDAS / "stackoverflow_limpio.csv"
CARPETA_GRAFICAS = CARPETA_SALIDAS / "graficas"
ARCHIVO_TABLA_SESGO = CARPETA_SALIDAS / "tabla_sesgo_imputacion.csv"

CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)


def linea(titulo):
    """Imprime un separador con titulo, solo para que el log de consola
    quede organizado y facil de leer durante la sustentacion."""
    print("\n" + "=" * 78)
    print(titulo)
    print("=" * 78)


# ---------------------------------------------------------------------------
# 1. CARGA DEL DATASET
# ---------------------------------------------------------------------------
linea("1. CARGA DEL DATASET")

# El archivo original nunca se modifica ni se descomprime en disco: se abre el
# ZIP en modo lectura y se lee el CSV como un flujo.
if not ARCHIVO_ZIP.exists():
    raise FileNotFoundError(
        f"No se encontro {ARCHIVO_ZIP}. El dataset original se versiona "
        f"comprimido en data/archive.zip; ver el README para obtenerlo."
    )

with zipfile.ZipFile(ARCHIVO_ZIP) as zip_original:
    miembros = zip_original.namelist()
    if CSV_DENTRO_DEL_ZIP not in miembros:
        raise FileNotFoundError(
            f"El ZIP {ARCHIVO_ZIP.name} no contiene {CSV_DENTRO_DEL_ZIP}. "
            f"Miembros encontrados: {miembros}"
        )
    with zip_original.open(CSV_DENTRO_DEL_ZIP) as flujo_csv:
        df = pd.read_csv(flujo_csv, low_memory=False)

print(f"Dataset cargado desde: data/{ARCHIVO_ZIP.name} -> {CSV_DENTRO_DEL_ZIP}")
print("El ZIP original se abre en solo lectura: no se modifica ni se "
      "descomprime en disco. La limpieza escribe en salidas/.")
print(df.head())


# ---------------------------------------------------------------------------
# 2. EXPLORACION INICIAL
# ---------------------------------------------------------------------------
linea("2. EXPLORACION INICIAL")

n_filas, n_columnas = df.shape
print(f"Filas: {n_filas}  |  Columnas: {n_columnas}")

print("\nTipos de dato por columna (resumen):")
print(df.dtypes.value_counts())

print("\nValores nulos por columna (porcentaje, de mayor a menor):")
pct_nulos = (df.isnull().mean() * 100).round(1).sort_values(ascending=False)
print(pct_nulos.head(15))

print("\nFilas duplicadas (comparando TODAS las columnas, incluido Respondent):")
print(df.duplicated().sum())

print("\nResumen descriptivo de columnas numericas originales:")
# CompTotal trae valores absurdos (hasta 10^247) que revisamos a fondo en
# la seccion 8; calcular la desviacion estandar sobre esos numeros produce
# un "overflow" de Python (no es un error nuestro, es evidencia del
# problema). Silenciamos solo esa advertencia para no ensuciar el log.
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    print(df.describe())
print("(CompTotal muestra numeros con notacion cientifica extrema en el "
      "max: es justamente el error de digitacion que tratamos en la "
      "seccion 8, por eso su desviacion estandar ni siquiera se puede "
      "calcular aqui arriba.)")


# ---------------------------------------------------------------------------
# 3. CORRECCION DE TIPOS (ADELANTADA) - prerrequisito tecnico
# ---------------------------------------------------------------------------
# El enunciado ubica "Correccion de tipos de datos" mas adelante en la lista,
# pero tres columnas que deberian ser numericas llegan como texto porque la
# encuesta permitia respuestas como "Less than 1 year" en vez de un numero:
#   - YearsCode       ("Less than 1 year", "More than 50 years")
#   - YearsCodePro    ("Less than 1 year", "More than 50 years")
#   - Age1stCode      ("Younger than 5 years", "Older than 85")
# No podemos calcular media, mediana ni desviacion (paso 4) sobre texto, asi
# que adelantamos SOLO esta conversion. El resto de la correccion de tipos
# (verificaciones generales) se hace en la seccion 7, en el orden original.
linea("3. CORRECCION DE TIPOS (ADELANTADA): texto -> numero en 3 columnas")

MAPA_YEARSCODE = {"Less than 1 year": "0.5", "More than 50 years": "51"}
MAPA_AGE1STCODE = {"Younger than 5 years": "4", "Older than 85": "86"}

print("Valores de texto encontrados en YearsCode / YearsCodePro:",
      sorted(set(MAPA_YEARSCODE.keys())))
print("Valores de texto encontrados en Age1stCode:",
      sorted(set(MAPA_AGE1STCODE.keys())))

df["YearsCode"] = pd.to_numeric(df["YearsCode"].replace(MAPA_YEARSCODE), errors="coerce")
df["YearsCodePro"] = pd.to_numeric(df["YearsCodePro"].replace(MAPA_YEARSCODE), errors="coerce")
df["Age1stCode"] = pd.to_numeric(df["Age1stCode"].replace(MAPA_AGE1STCODE), errors="coerce")

print("\nTipos despues de la conversion:")
print(df[["YearsCode", "YearsCodePro", "Age1stCode"]].dtypes)


# ---------------------------------------------------------------------------
# 4. MANEJO DE VALORES NULOS
# ---------------------------------------------------------------------------
linea("4. MANEJO DE VALORES NULOS")

# --- 4.1 Umbral de eliminacion de columnas (regla del protocolo: >50%) -----
print("Columna con mas nulos:", pct_nulos.index[0], f"({pct_nulos.iloc[0]}%)")
columnas_a_eliminar = pct_nulos[pct_nulos > 50].index.tolist()
print("Columnas que superan el 50% de nulos:", columnas_a_eliminar)

if columnas_a_eliminar:
    df = df.drop(columns=columnas_a_eliminar)
    print("Se eliminaron:", columnas_a_eliminar)
else:
    print("NINGUNA columna supera el 50% de nulos, asi que no se elimina "
          "ninguna. Esto confirma la razon por la que en el protocolo "
          "eligieron un umbral alto: la columna con mas faltantes "
          "(ConvertedComp) llega a 46.1%, muy cerca del limite pero sin "
          "cruzarlo, y es justo la variable de sueldo que querian conservar.")

# --- 4.2 Imputacion numerica: media (simetrica) o mediana (asimetrica) -----
# Regla del protocolo: se decide con el sesgo (skewness) de cada variable,
# ANTES de imputar. Usamos el umbral estandar |sesgo| < 0.5 = simetrica.
VARIABLES_NUMERICAS = ["Age", "Age1stCode", "YearsCode", "YearsCodePro",
                        "WorkWeekHrs", "ConvertedComp"]
# Nota: dejamos CompTotal por fuera de la imputacion. Esta en distintas
# monedas (ver columna CurrencySymbol) y mezclar sueldos sin convertir no
# tiene sentido estadistico; para eso el propio dataset ya trae
# ConvertedComp (todo en USD). CompTotal solo se usa mas adelante, en la
# seccion de atipicos, como evidencia de errores de digitacion.

resumen_antes = []
for col in VARIABLES_NUMERICAS:
    resumen_antes.append({
        "variable": col,
        "media": df[col].mean(),
        "mediana": df[col].median(),
        "desviacion_std": df[col].std(),
        "n_observaciones": df[col].notna().sum(),
        "sesgo": df[col].skew(),
    })
resumen_antes = pd.DataFrame(resumen_antes).set_index("variable")
print("\nEstadisticos ANTES de imputar:")
print(resumen_antes.round(2))

# Clasificacion simetrica/asimetrica segun el sesgo calculado arriba
estrategia_por_variable = {}
for col in VARIABLES_NUMERICAS:
    sesgo = resumen_antes.loc[col, "sesgo"]
    estrategia_por_variable[col] = "media" if abs(sesgo) < 0.5 else "mediana"

print("\nEstrategia de imputacion decidida por el sesgo de cada variable:")
for col, estrategia in estrategia_por_variable.items():
    print(f"  {col}: sesgo={resumen_antes.loc[col,'sesgo']:.2f} -> se imputa con {estrategia}")
print("\nEn este dataset TODAS las variables numericas dieron asimetricas "
      "(|sesgo| > 0.5), asi que todas se imputan con la mediana. La regla "
      "de la media (numerica simetrica) queda igual implementada en el "
      "codigo, simplemente ninguna columna la disparo con estos datos.")

# Guardamos una copia de cada variable ANTES de tocarla, para las graficas
valores_antes_de_imputar = {col: df[col].copy() for col in VARIABLES_NUMERICAS}

for col in VARIABLES_NUMERICAS:
    valor_relleno = df[col].mean() if estrategia_por_variable[col] == "media" else df[col].median()
    df[col] = df[col].fillna(valor_relleno)

resumen_despues = []
for col in VARIABLES_NUMERICAS:
    resumen_despues.append({
        "variable": col,
        "media": df[col].mean(),
        "mediana": df[col].median(),
        "desviacion_std": df[col].std(),
        "n_observaciones": df[col].notna().sum(),
    })
resumen_despues = pd.DataFrame(resumen_despues).set_index("variable")
print("\nEstadisticos DESPUES de imputar:")
print(resumen_despues.round(2))

tabla_comparativa = resumen_antes[["media", "mediana", "desviacion_std", "n_observaciones"]].add_suffix("_antes")
tabla_comparativa = tabla_comparativa.join(resumen_despues.add_suffix("_despues"))
tabla_comparativa.to_csv(ARCHIVO_TABLA_SESGO)
print(f"\nTabla completa antes/despues guardada en "
      f"{ARCHIVO_TABLA_SESGO.relative_to(RAIZ)}")

# --- 4.3 Histogramas antes/despues superpuestos ----------------------------
for col in VARIABLES_NUMERICAS:
    fig, ax = plt.subplots(figsize=(7, 4))
    datos_antes = valores_antes_de_imputar[col].dropna()
    datos_despues = df[col]
    ax.hist(datos_antes, bins=40, alpha=0.5, label="Antes de imputar", density=True)
    ax.hist(datos_despues, bins=40, alpha=0.5, label="Despues de imputar", density=True)
    ax.set_title(f"Distribucion de {col}: antes vs. despues de imputar")
    ax.set_xlabel(col)
    ax.set_ylabel("Densidad")
    ax.legend()
    fig.tight_layout()
    ruta = CARPETA_GRAFICAS / f"imputacion_{col}.png"
    fig.savefig(ruta, dpi=110)
    plt.close(fig)
print(f"\nHistogramas antes/despues guardados en: "
      f"{CARPETA_GRAFICAS.relative_to(RAIZ)}/imputacion_<variable>.png")

# --- 4.4 Comparacion de DOS estrategias de imputacion en la misma columna --
# Lo hacemos sobre ConvertedComp (el sueldo), que es la variable donde mas
# importa la decision: es la mas asimetrica del grupo (sesgo alto) porque
# unos pocos sueldos muy altos empujan la media hacia arriba.
linea("4.4 Comparacion de dos estrategias de imputacion (ConvertedComp)")

serie_original = valores_antes_de_imputar["ConvertedComp"]
media_original = serie_original.mean()
mediana_original = serie_original.median()

imputado_con_media = serie_original.fillna(media_original)
imputado_con_mediana = serie_original.fillna(mediana_original)

print(f"Media de ConvertedComp (sin imputar):    {media_original:,.0f} USD")
print(f"Mediana de ConvertedComp (sin imputar):  {mediana_original:,.0f} USD")
print(f"Desviacion estandar SI se imputa con la media:   {imputado_con_media.std():,.0f}")
print(f"Desviacion estandar SI se imputa con la mediana: {imputado_con_mediana.std():,.0f}")
print("\nConclusion: imputar con la media aqui es enganoso, porque la media "
      "misma ya esta corrida hacia arriba por sueldos extremos (algunos por "
      "encima de USD 1,000,000). Imputar con la mediana no arrastra ese "
      "sesgo y reduce menos la variabilidad real de la variable. Por eso "
      "nos quedamos con la mediana, tal como decidimos en el protocolo.")


# ---------------------------------------------------------------------------
# 4.5 IMPUTACION CATEGORICA: crear categoria "Desconocido"
# ---------------------------------------------------------------------------
linea("4.5 Imputacion de variables categoricas")

columnas_categoricas = df.select_dtypes(exclude="number").columns.tolist()
nulos_categoricos_antes = df[columnas_categoricas].isnull().sum().sum()

for col in columnas_categoricas:
    df[col] = df[col].fillna("Desconocido")

nulos_categoricos_despues = df[columnas_categoricas].isnull().sum().sum()
print(f"Nulos en columnas categoricas: {nulos_categoricos_antes} -> {nulos_categoricos_despues}")
print("Justificacion (igual que en el protocolo): poner la respuesta mas "
      "frecuente inventaria lo que la persona contesto e inflaria una "
      "categoria que ya es grande; dejar 'Desconocido' conserva el hecho "
      "de que no sabemos su respuesta.")


# ---------------------------------------------------------------------------
# 5. TRATAMIENTO DE DUPLICADOS
# ---------------------------------------------------------------------------
linea("5. TRATAMIENTO DE DUPLICADOS")

# Regla del protocolo: dos filas son la misma respuesta si coinciden en
# TODAS las columnas salvo Respondent (que es un identificador distinto por
# definicion en cada fila y por eso no debe compararse).
columnas_para_comparar = [c for c in df.columns if c != "Respondent"]
es_duplicado = df.duplicated(subset=columnas_para_comparar, keep="first")
print(f"Filas duplicadas encontradas (segun la regla del protocolo): {es_duplicado.sum()}")

# Nota para la sustentacion: revisamos estas filas duplicadas y en promedio
# solo tienen ~3.5 campos distintos de nulo (de 60), contra ~46 en el resto
# del dataset. Es decir, son en su mayoria encuestas casi vacias que
# coinciden por tener casi todo en blanco, no necesariamente la misma
# persona respondiendo dos veces. Aun asi, aplicamos la regla que ya
# habiamos congelado en el protocolo: no la cambiamos con el resultado ya
# visto, solo dejamos constancia de este matiz.
filas_antes_de_dup = len(df)
df = df[~es_duplicado].reset_index(drop=True)
print(f"Filas antes: {filas_antes_de_dup}  ->  Filas despues: {len(df)}")


# ---------------------------------------------------------------------------
# 6. CORRECCION DE TIPOS DE DATOS (verificacion general)
# ---------------------------------------------------------------------------
linea("6. CORRECCION DE TIPOS DE DATOS (verificacion general)")

# Las 3 columnas numericas-que-llegaban-como-texto ya se corrigieron en la
# seccion 3 (era un prerrequisito para poder imputar). Aqui solo dejamos la
# verificacion formal de que ninguna variable pensada como numerica sigue
# en formato de texto.
for col in VARIABLES_NUMERICAS:
    tipo = df[col].dtype
    print(f"  {col}: {tipo}  {'OK' if pd.api.types.is_numeric_dtype(tipo) else 'REVISAR'}")

# Este dataset no trae columnas de fecha (no hay una pregunta tipo
# "fecha de registro"), asi que no aplica unificar formato de fechas.
print("\nEl dataset no contiene columnas de fecha, asi que no aplica el "
      "punto de formato de fechas (%Y-%m-%d %H:%M:%S).")


# ---------------------------------------------------------------------------
# 7. NORMALIZACION DE VALORES CATEGORICOS
# ---------------------------------------------------------------------------
linea("7. NORMALIZACION DE VALORES CATEGORICOS")

# Revisamos espacios en blanco al inicio/final y valores que solo difieren
# en mayusculas/minusculas (ej. "Femenino" vs "femenino").
columnas_con_problemas = []
for col in columnas_categoricas:
    valores = df[col].astype(str)
    tiene_espacios = (valores != valores.str.strip()).sum()
    valores_unicos = valores.unique()
    minusculas = {}
    for v in valores_unicos:
        minusculas.setdefault(v.lower(), []).append(v)
    duplicados_por_mayus = {k: v for k, v in minusculas.items() if len(v) > 1}
    if tiene_espacios > 0 or duplicados_por_mayus:
        columnas_con_problemas.append(col)
    # Se aplica el trim de todas formas, de manera preventiva
    df[col] = valores.str.strip()

print(f"Columnas categoricas revisadas: {len(columnas_categoricas)}")
print(f"Columnas con inconsistencias de texto encontradas: {len(columnas_con_problemas)}")
print("Las opciones de esta encuesta vienen de listas desplegables "
      "cerradas, por eso no aparecieron inconsistencias de mayusculas ni "
      "textos raros. Igual dejamos el chequeo (y un str.strip() preventivo) "
      "corriendo en todas las columnas de texto, por si algun dia se corre "
      "este script sobre una version de los datos con respuestas libres.")


# ---------------------------------------------------------------------------
# 8. TRATAMIENTO DE VALORES ATIPICOS
# ---------------------------------------------------------------------------
linea("8. TRATAMIENTO DE VALORES ATIPICOS")

# Metodo y parametro fijados en el protocolo: rango intercuartilico (RIC)
# con factor 1.5. Cualquier valor fuera de [Q1 - 1.5*RIC, Q3 + 1.5*RIC]
# queda marcado como CANDIDATO a atipico (la marca todavia no borra nada).

def limites_ric(serie, factor=1.5):
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    ric = q3 - q1
    return q1 - factor * ric, q3 + factor * ric


VARIABLES_PARA_ATIPICOS = ["Age", "WorkWeekHrs", "ConvertedComp",
                            "CompTotal", "YearsCode", "YearsCodePro"]

# IMPORTANTE: los limites (Q1 y Q3) los calculamos sobre los datos
# ORIGINALES, antes de imputar (guardados en "valores_antes_de_imputar" en
# la seccion 4). Si los calculamos sobre la columna ya imputada, el relleno
# masivo con la mediana amontona miles de valores exactamente en el centro
# y "aprieta" a Q1 y Q3 hacia ese mismo numero, lo que dispara falsos
# atipicos por todos lados (nos paso: con la columna imputada, WorkWeekHrs
# daba limites [40, 40], marcando como atipico casi cualquier valor
# distinto de 40). Los valores imputados son, por construccion, la mediana:
# nunca van a ser atipicos, y no deben usarse para calcular el propio
# limite. CompTotal no se imputo, asi que para esa columna no hay
# diferencia.
series_para_calcular_limites = {}
for col in VARIABLES_PARA_ATIPICOS:
    if col in valores_antes_de_imputar:
        series_para_calcular_limites[col] = valores_antes_de_imputar[col].dropna()
    else:
        series_para_calcular_limites[col] = df[col].dropna()

print("Candidatos a atipico por variable (metodo RIC, factor 1.5, "
      "limites calculados sobre los datos originales sin imputar):")
registros_totales = len(df)
for col in VARIABLES_PARA_ATIPICOS:
    limite_inf, limite_sup = limites_ric(series_para_calcular_limites[col])
    candidatos = (df[col] < limite_inf) | (df[col] > limite_sup)
    n_candidatos = candidatos.sum()
    print(f"  {col}: limites=[{limite_inf:,.1f} , {limite_sup:,.1f}]  "
          f"-> {n_candidatos} candidatos "
          f"({100*n_candidatos/registros_totales:.2f}% del total)")

# --- Caso 1: Age = 279 -> error de digitacion --------------------------
# Un ser humano no tiene 279 anios. Es un error de digitacion (un digito de
# mas). No podemos adivinar con certeza el valor real (?27? ?29? ?79?), asi
# que en vez de inventarlo lo tratamos como dato faltante y lo rellenamos
# con la mediana YA calculada en la seccion 4 (no reabrimos todo el proceso
# de imputacion por un solo valor puntual).
mediana_age = resumen_antes.loc["Age", "mediana"]
mascara_edad_imposible = df["Age"] > 100
print(f"\nCaso 1 - Age: {mascara_edad_imposible.sum()} registro(s) con edad "
      f"> 100 anios (ej. 279). Clasificacion: ERROR DE DIGITACION. "
      f"Accion: se reemplazan por la mediana ({mediana_age:.0f} anios), "
      f"la misma que se uso para imputar nulos.")
df.loc[mascara_edad_imposible, "Age"] = mediana_age

# --- Caso 2: Age < 10 -> observacion contaminante -----------------------
# Esta encuesta es para desarrolladores de software. Una persona de 1, 3, 5
# o 7 anios no puede ser una respuesta real de la poblacion que se estudia.
# Clasificacion: OBSERVACION CONTAMINANTE (no viene de la poblacion de
# interes). Accion: igual que el caso anterior, se reemplaza por la mediana.
mascara_edad_contaminante = df["Age"] < 10
print(f"\nCaso 2 - Age: {mascara_edad_contaminante.sum()} registro(s) con "
      f"edad menor a 10 anios. Clasificacion: OBSERVACION CONTAMINANTE. "
      f"Accion: se reemplazan por la mediana ({mediana_age:.0f} anios).")
df.loc[mascara_edad_contaminante, "Age"] = mediana_age

# --- Caso 3: WorkWeekHrs > 168 -> error de escala (sobra un digito) -----
# Una semana solo tiene 168 horas (24 x 7), asi que CUALQUIER valor por
# encima de eso es fisicamente imposible. Al dividir estos valores entre 10
# todos caen en un rango de horas de trabajo perfectamente creible
# (22.5 a 47.5 horas/semana), lo que sugiere que a la persona se le fue un
# digito de mas (o le sobra un cero). Clasificacion: ERROR DE ESCALA.
# Accion: CORREGIR dividiendo entre 10 (no eliminar).
mascara_horas_imposibles = df["WorkWeekHrs"] > 168
valores_antes_correccion = df.loc[mascara_horas_imposibles, "WorkWeekHrs"].tolist()
print(f"\nCaso 3 - WorkWeekHrs: {mascara_horas_imposibles.sum()} registro(s) "
      f"por encima de 168 horas/semana (fisicamente imposible). "
      f"Valores originales: {sorted(valores_antes_correccion)}")
df.loc[mascara_horas_imposibles, "WorkWeekHrs"] = df.loc[mascara_horas_imposibles, "WorkWeekHrs"] / 10
print("Clasificacion: ERROR DE ESCALA (sobra un digito). "
      "Accion: se corrige dividiendo entre 10. Valores corregidos:",
      sorted(df.loc[mascara_horas_imposibles, "WorkWeekHrs"].tolist()))

# --- Caso 4 (OBLIGATORIO): un atipico que NO se debe eliminar -----------
# WorkWeekHrs entre 100 y 168 horas/semana: el metodo RIC los marca como
# candidatos (estan muy por encima del limite superior calculado arriba),
# pero SI son fisicamente posibles. Representan devs en jornadas extremas
# (crunch, freelancers con varios contratos, etc.), es decir, observaciones
# reales y validas de la poblacion, no errores.
mascara_horas_extremas_reales = (df["WorkWeekHrs"] >= 100) & (df["WorkWeekHrs"] <= 168)
n_extremas_reales = mascara_horas_extremas_reales.sum()
print(f"\nCaso 4 (obligatorio) - WorkWeekHrs entre 100 y 168 horas/semana: "
      f"{n_extremas_reales} registro(s). El metodo RIC los marca como "
      f"atipicos porque estan lejos del resto de los datos, PERO no se "
      f"eliminan: 168 horas es el maximo fisico de una semana, asi que son "
      f"valores posibles (jornadas extremas reales), no errores. "
      f"Clasificacion: OBSERVACION VALIDA EXTREMA. Accion: CONSERVAR tal "
      f"cual.")

# --- Caso 5: CompTotal con valores absurdos -> error de digitacion/escala
# CompTotal llega en la moneda local de cada persona (columna
# CurrencySymbol), asi que no lo usamos para el analisis de sueldos (para
# eso esta ConvertedComp, ya en USD). Aun asi lo revisamos porque aqui
# aparece el caso mas extremo de todo el dataset: valores como
# 1.11 x 10^247, fisicamente imposibles en cualquier moneda del mundo.
# Clasificacion: ERROR DE DIGITACION / ENTRADA INVALIDA. No hay forma de
# adivinar el valor real, asi que la accion es anular ese valor puntual
# (queda como dato faltante, sin inventar un numero). Es la unica columna
# donde "eliminar" el valor es la mejor opcion, y aqui la justificamos.
UMBRAL_COMPTOTAL_ABSURDO = 1e9  # nadie gana mil millones en compensacion individual
mascara_comptotal_absurdo = df["CompTotal"] > UMBRAL_COMPTOTAL_ABSURDO
print(f"\nCaso 5 - CompTotal: {mascara_comptotal_absurdo.sum()} registro(s) "
      f"por encima de {UMBRAL_COMPTOTAL_ABSURDO:,.0f} (valor maximo real "
      f"encontrado: {df['CompTotal'].max():.3e}). "
      f"Clasificacion: ERROR DE DIGITACION. Accion: se anula el valor "
      f"(queda como dato faltante); no se imputa porque esta columna no "
      f"forma parte del analisis de sueldos (se usa ConvertedComp).")
df.loc[mascara_comptotal_absurdo, "CompTotal"] = np.nan

# --- Registro de cuantos datos se habrian perdido si se eliminaran TODOS los
#     atipicos detectados (en vez de clasificarlos como hicimos arriba) ----
linea("Cuantos registros se habrian perdido eliminando TODOS los atipicos")
total_afectado_si_se_eliminara_todo = set()
for col in VARIABLES_PARA_ATIPICOS:
    # Mismos limites "honestos" calculados arriba sobre los datos sin
    # imputar, pero contados sobre el dataset ya corregido (casos 1 a 5).
    limite_inf, limite_sup = limites_ric(series_para_calcular_limites[col])
    candidatos = df.index[(df[col] < limite_inf) | (df[col] > limite_sup)]
    total_afectado_si_se_eliminara_todo.update(candidatos)

n_perdidos = len(total_afectado_si_se_eliminara_todo)
print(f"Si hubieramos eliminado toda fila marcada como atipica en CUALQUIERA "
      f"de las {len(VARIABLES_PARA_ATIPICOS)} variables revisadas, se "
      f"habrian perdido {n_perdidos} filas de {len(df)} "
      f"({100*n_perdidos/len(df):.1f}% del total). Es una fraccion enorme "
      f"del dataset, y es justamente la razon por la que el protocolo pide "
      f"clasificar antes de actuar, en vez de borrar directamente todo lo "
      f"que el metodo estadistico marca.")


# ---------------------------------------------------------------------------
# 9. VALIDACION DE COHERENCIA
# ---------------------------------------------------------------------------
linea("9. VALIDACION DE COHERENCIA")

# Regla logica 1: la edad a la que alguien escribio su primera linea de
# codigo (Age1stCode) no puede ser mayor que su edad actual (Age).
incoherente_edad = df["Age1stCode"] > df["Age"]
print(f"Regla 1 (Age1stCode <= Age): {incoherente_edad.sum()} filas la "
      f"incumplen, de {len(df)}.")

# Regla logica 2: los anios de experiencia PROFESIONAL (YearsCodePro) no
# pueden ser mas que los anios TOTALES programando (YearsCode), porque el
# total incluye la experiencia profesional.
incoherente_experiencia = df["YearsCodePro"] > df["YearsCode"]
print(f"Regla 2 (YearsCodePro <= YearsCode): {incoherente_experiencia.sum()} "
      f"filas la incumplen, de {len(df)}.")

# No sabemos, para cada fila incoherente, cual de las dos columnas esta mal
# (pudo fallar cualquiera de las dos), asi que en vez de adivinar y corregir
# una de las dos al azar, dejamos dos columnas de bandera para que quede
# documentado y cualquiera que use el dataset limpio pueda filtrarlas.
df["coherencia_edad_codigo_ok"] = ~incoherente_edad
df["coherencia_experiencia_ok"] = ~incoherente_experiencia
print("Se agregaron las columnas 'coherencia_edad_codigo_ok' y "
      "'coherencia_experiencia_ok' (True/False) para dejar marcadas estas "
      "filas sin borrar informacion ni inventar una correccion.")


# ---------------------------------------------------------------------------
# 10. VARIABLES DERIVADAS (opcional)
# ---------------------------------------------------------------------------
linea("10. VARIABLES DERIVADAS (opcional)")

# 10.1 Anios de codigo ANTES de volverse profesional
df["anios_codigo_previo_profesional"] = df["YearsCode"] - df["YearsCodePro"]
# Si la fila es incoherente (regla 2 de arriba), este calculo da negativo;
# lo dejamos en nulo en vez de mostrar un numero que no tiene sentido.
df.loc[df["anios_codigo_previo_profesional"] < 0, "anios_codigo_previo_profesional"] = np.nan
print("Se creo 'anios_codigo_previo_profesional' = YearsCode - YearsCodePro.")

# 10.2 Grupo de edad, para poder agrupar analisis mas adelante sin repetir
# rangos numericos cada vez
df["grupo_edad"] = pd.cut(
    df["Age"],
    bins=[0, 20, 30, 40, 50, 200],
    labels=["<=20", "21-30", "31-40", "41-50", "50+"],
)
print("Se creo 'grupo_edad' agrupando Age en rangos (<=20, 21-30, 31-40, 41-50, 50+).")


# ---------------------------------------------------------------------------
# 11. GUARDAR DATASET LIMPIO (nunca se sobrescribe el original)
# ---------------------------------------------------------------------------
linea("11. GUARDAR DATASET LIMPIO")

df.to_csv(ARCHIVO_LIMPIO, index=False)
print(f"Dataset original:  data/{ARCHIVO_ZIP.name} -> {CSV_DENTRO_DEL_ZIP}  "
      f"({n_filas} filas, {n_columnas} columnas) - sin modificar")
print(f"Dataset limpio:    {ARCHIVO_LIMPIO.relative_to(RAIZ)}  "
      f"({len(df)} filas, {df.shape[1]} columnas)")

linea("FIN DEL SCRIPT")
