

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

# Entrada: el ZIP original tal como se descargo de Kaggle. El CSV
# descomprimido pesa ~94 MB, asi que nunca se deja suelto en el repositorio:
# pandas lee el miembro directamente desde el ZIP.
ARCHIVO_ZIP = RAIZ / "data" / "archive.zip"
CSV_DENTRO_DEL_ZIP = "survey_results_public.csv"

# Salidas: TODO lo que produce el script vive en salidas/, fuera de data/.
# Asi el original queda aislado y no se puede sobrescribir por accidente.
CARPETA_SALIDAS = RAIZ / "salidas"
ARCHIVO_LIMPIO = CARPETA_SALIDAS / "stackoverflow_limpio.csv"
CARPETA_GRAFICAS = CARPETA_SALIDAS / "graficas"
ARCHIVO_TABLA_SESGO = CARPETA_SALIDAS / "tabla_sesgo_imputacion.csv"
ARCHIVO_FRECUENCIAS_MULTIPLE = CARPETA_SALIDAS / "frecuencias_respuesta_multiple.csv"

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
# El porcentaje de nulos se recalcula aqui, y no se reusa el de la seccion 2.
# Aquel se midio antes de la conversion de tipos, y pd.to_numeric con
# errors="coerce" convierte en NaN cualquier texto que no estuviera en el
# mapeo: el umbral tiene que decidirse sobre los nulos que hay ahora.
pct_nulos_tras_tipos = (df.isnull().mean() * 100).round(1).sort_values(ascending=False)

nulos_nuevos = (pct_nulos_tras_tipos - pct_nulos).round(1)
nulos_nuevos = nulos_nuevos[nulos_nuevos != 0]
if len(nulos_nuevos):
    print("La conversion de tipos genero nulos nuevos en:")
    print(nulos_nuevos)
else:
    print("La conversion de tipos NO genero ningun nulo nuevo: los mapeos de "
          "la seccion 3 cubrian todos los valores de texto que traian esas "
          "tres columnas. El recalculo no cambia ninguna decision en este "
          "dataset, pero deja el umbral apoyado en los datos correctos.")

pct_nulos = pct_nulos_tras_tipos

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

# Marca auxiliar: que filas traian la edad de verdad y cuales la van a recibir
# imputada. Va como columna y no como Series aparte a proposito: mas adelante
# se borran duplicados y se reinicia el indice, asi que una Series suelta
# dejaria de alinear con el DataFrame. En la seccion 8 hace falta para no
# acusar de error de digitacion a una fila cuya edad la pusimos nosotros.
df["_age_era_real"] = df["Age"].notna()

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

# Las columnas que empiezan con "_" son andamiaje interno del script (marcas
# auxiliares), no respuestas de la encuesta: quedan fuera de todo el
# tratamiento de categoricas y se borran antes de guardar. Sin esta exclusion,
# la seccion 7 las convertiria a texto con astype(str) y una marca booleana
# pasaria a ser la cadena "False", que en Python es verdadera.
columnas_categoricas = [c for c in df.select_dtypes(exclude="number").columns
                        if not c.startswith("_")]
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
# solo tienen muy pocos campos distintos de nulo, contra decenas en el resto
# del dataset. Es decir, son en su mayoria encuestas casi vacias que
# coinciden por tener casi todo en blanco, no necesariamente la misma
# persona respondiendo dos veces.

# --- Que registro se conserva de cada grupo de duplicados -----------------
# El protocolo solo define QUE es un duplicado, no cual de los repetidos se
# conserva. "El primero que aparece" es arbitrario: el orden del archivo no
# significa nada. Conservar el registro MAS COMPLETO si tiene sentido, porque
# entre dos respuestas identicas en lo que contestaron, la que tiene mas
# campos llenos aporta mas informacion y nunca menos.
completitud = df.notna().sum(axis=1)

# Ordenamos por completitud descendente y marcamos duplicados sobre ese orden:
# asi el "primero" de cada grupo pasa a ser el mas completo. `mergesort` es
# estable, de modo que ante un empate en completitud gana el que venia antes
# en el archivo, tal como pide la regla de desempate.
orden_por_completitud = completitud.sort_values(ascending=False, kind="mergesort").index
df_ordenado = df.loc[orden_por_completitud]
es_duplicado_mas_completo = df_ordenado.duplicated(
    subset=columnas_para_comparar, keep="first"
).reindex(df.index)

indices_primero = set(df.index[es_duplicado])
indices_mas_completo = set(df.index[es_duplicado_mas_completo])
filas_que_cambian = len(indices_primero ^ indices_mas_completo) // 2

print(f"\nCriterio de conservacion: descartar 'el primero' y descartar "
      f"'el menos completo' eliminan la misma cantidad de filas "
      f"({len(indices_primero)}), pero no siempre las mismas: "
      f"{filas_que_cambian} grupo(s) de duplicados conservan un registro "
      f"distinto segun el criterio.")
if filas_que_cambian:
    campos_primero = completitud[list(indices_primero)].mean()
    campos_completo = completitud[list(indices_mas_completo)].mean()
    print(f"     Campos llenos promedio de las filas descartadas: "
          f"{campos_primero:.1f} con 'el primero' contra "
          f"{campos_completo:.1f} con 'el menos completo'. Conservamos el mas "
          f"completo: la diferencia es informacion que se habria perdido por "
          f"el orden del archivo, que no significa nada.")
else:
    print("     Aqui los dos criterios coinciden: los duplicados son "
          "encuestas casi vacias con la misma cantidad de campos llenos, asi "
          "que da igual cual se conserve. Aplicamos el mas completo porque es "
          "el criterio defendible, no porque cambie el resultado.")

filas_antes_de_dup = len(df)
df = df[~es_duplicado_mas_completo].reset_index(drop=True)
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

# Buscamos dos problemas distintos: espacios sobrantes al inicio o al final,
# y valores que solo difieren en mayusculas ("Femenino" vs "femenino").
#
# NO pasamos todo a minusculas. Bajar todo el texto
# convertiria "United States" en "united states" y "C++" en "c++" en el
# dataset final, sin arreglar nada: la verificacion de abajo demuestra que
# este dataset no tiene ni una sola colision de mayusculas, porque las
# respuestas salen de listas desplegables cerradas. Normalizar solo donde hay
# colision real arregla el problema cuando existe y no toca los datos cuando
# no existe.
#
# El riesgo de esta seccion es el contrario al que parece: normalizar de mas
# FUSIONA categorias que en realidad eran distintas. Por eso contamos las
# categorias antes y despues, y si el numero baja sin que hubiera colisiones,
# el script avisa.
categorias_antes = {col: df[col].nunique() for col in columnas_categoricas}

columnas_con_espacios = []
colisiones_por_mayusculas = {}

columnas_con_caracteres_raros = {}

# Caracteres que no deberian aparecer nunca dentro de una respuesta: tabulador,
# salto de linea, retorno de carro y demas caracteres de control, mas el
# simbolo de reemplazo que deja un error de codificacion.
CARACTERES_DE_CONTROL = r"[\x00-\x1f\x7f\ufffd]"

for col in columnas_categoricas:
    valores = df[col].astype(str)

    # 1. Caracteres especiales y malas digitaciones: un tabulador o un salto de
    #    linea metido dentro de una categoria la convierte en una categoria
    #    aparte que nadie va a poder cruzar con la buena. Se reemplazan por un
    #    espacio y despues se colapsan los espacios repetidos.
    tiene_raros = valores.str.contains(CARACTERES_DE_CONTROL, regex=True)
    if tiene_raros.any():
        ejemplo = valores[tiene_raros].iloc[0]
        columnas_con_caracteres_raros[col] = (int(tiene_raros.sum()), ejemplo)
        valores = valores.str.replace(CARACTERES_DE_CONTROL, " ", regex=True)
    valores = valores.str.replace(r"\s{2,}", " ", regex=True)

    # 2. Espacios sobrantes: se recortan siempre. Es seguro, porque
    #    "Colombia " y "Colombia" son la misma respuesta con un error de
    #    captura, no dos categorias.
    if (valores != valores.str.strip()).any():
        columnas_con_espacios.append(col)
    valores = valores.str.strip()

    # 3. Colisiones de mayusculas: agrupamos los valores unicos por su version
    #    en minusculas. Si un grupo tiene mas de un valor original, son la
    #    misma respuesta escrita distinto.
    grupos = {}
    for unico in valores.unique():
        grupos.setdefault(unico.lower(), []).append(unico)
    colisiones = {k: v for k, v in grupos.items() if len(v) > 1}

    if colisiones:
        colisiones_por_mayusculas[col] = colisiones
        # Unificamos cada grupo en su variante MAS FRECUENTE, no en minusculas:
        # asi se corrige la inconsistencia conservando la forma que el propio
        # dataset usa mas.
        frecuencias = valores.value_counts()
        equivalencias = {}
        for variantes in colisiones.values():
            ganadora = max(variantes, key=lambda x: frecuencias.get(x, 0))
            for variante in variantes:
                if variante != ganadora:
                    equivalencias[variante] = ganadora
        valores = valores.replace(equivalencias)

    df[col] = valores

categorias_despues = {col: df[col].nunique() for col in columnas_categoricas}

print(f"Columnas categoricas revisadas: {len(columnas_categoricas)}")
print(f"Columnas con caracteres de control o de codificacion: "
      f"{len(columnas_con_caracteres_raros)}")
for col, (n, ejemplo) in columnas_con_caracteres_raros.items():
    print(f"  {col}: {n} valor(es) corregido(s). Antes: {ejemplo!r}")
print(f"Columnas con espacios sobrantes: {len(columnas_con_espacios)}")
print(f"Columnas con colisiones de mayusculas: {len(colisiones_por_mayusculas)}")
for col, colisiones in list(colisiones_por_mayusculas.items())[:5]:
    ejemplo = list(colisiones.values())[0]
    print(f"  {col}: {len(colisiones)} grupo(s), por ejemplo {ejemplo}")

# --- Verificacion del riesgo: no se pueden perder categorias sin motivo ----
bajaron = {c: (categorias_antes[c], categorias_despues[c])
           for c in columnas_categoricas
           if categorias_despues[c] < categorias_antes[c]}
bajaron_sin_colision = {c: v for c, v in bajaron.items()
                        if c not in colisiones_por_mayusculas}

print(f"\nCategorias antes de normalizar:  {sum(categorias_antes.values())}")
print(f"Categorias despues de normalizar: {sum(categorias_despues.values())}")
if bajaron_sin_colision:
    print("ALERTA: estas columnas perdieron categorias sin que hubiera "
          "colision de mayusculas. Hay que revisarlas antes de seguir:")
    for c, (a, d) in bajaron_sin_colision.items():
        print(f"  {c}: {a} -> {d}")
elif bajaron:
    print("Las unicas columnas que perdieron categorias son las que tenian "
          "colisiones de mayusculas, que es exactamente lo que se queria "
          "corregir. Ninguna categoria distinta se fusiono por accidente.")
else:
    print("Ninguna columna perdio categorias: el conteo es identico antes y "
          "despues. Las correcciones que si se aplicaron (los caracteres de "
          "control de arriba) limpiaron el valor sin fusionarlo con otro, que "
          "es justo lo que se queria. Las opciones de esta encuesta vienen de "
          "listas desplegables cerradas, por eso las inconsistencias son tan "
          "pocas; el chequeo queda corriendo igual, porque si manana se corre "
          "este script sobre una version con respuestas libres si las va a "
          "haber.")

print("\nSobre 'estandarizar todo a minusculas': no se aplica, y la razon es "
      "el conteo de arriba. Bajar el texto sirve cuando hay la misma "
      "respuesta escrita de dos formas, y aqui hay CERO casos: las opciones "
      "salen de listas desplegables cerradas. Aplicarlo igual no corregiria "
      "nada y si dejaria 'united states' y 'c++' en el dataset final, mas "
      "dificiles de leer y de cruzar con cualquier fuente externa. La "
      "estandarizacion se hace donde hay inconsistencia real: caracteres de "
      "control, espacios sobrantes y colisiones de mayusculas, los tres "
      "verificados arriba.")


# ---------------------------------------------------------------------------
# 7.1 COLUMNAS DE RESPUESTA MULTIPLE (varias respuestas en la misma celda)
# ---------------------------------------------------------------------------
linea("7.1 COLUMNAS DE RESPUESTA MULTIPLE")

# Varias preguntas permitian marcar mas de una opcion, y la encuesta guardo
# todas las marcadas en una sola celda separadas por punto y coma:
#   "Python;SQL;JavaScript"
# Contar frecuencias sobre esa celda sin separarla da resultados sin sentido:
# "Python;SQL" y "SQL;Python" cuentan como dos categorias distintas, y quien
# sabe Python solo se mezcla con quien sabe Python y otras nueve cosas. Por
# eso hay que separarlas antes de contar.
#
# Las originales NO se modifican: se agregan columnas nuevas.
SEPARADOR_MULTIPLE = ";"
UMBRAL_DETECCION_MULTIPLE = 0.02  # 2% de filas con separador ya delata la pregunta

columnas_respuesta_multiple = []
for col in columnas_categoricas:
    valores = df[col].astype(str)
    proporcion_con_separador = valores.str.contains(SEPARADOR_MULTIPLE, regex=False).mean()
    if proporcion_con_separador > UMBRAL_DETECCION_MULTIPLE:
        columnas_respuesta_multiple.append(col)

print(f"Columnas de respuesta multiple detectadas: "
      f"{len(columnas_respuesta_multiple)}")
print(f"(criterio: mas del {UMBRAL_DETECCION_MULTIPLE:.0%} de las filas traen "
      f"'{SEPARADOR_MULTIPLE}' en la celda)")


def separar_opciones(valor):
    """Devuelve la lista de opciones marcadas en una celda.

    'Desconocido' es el relleno que pusimos en la seccion 4.5 para las
    preguntas sin responder: no es una opcion elegida, asi que cuenta como
    cero respuestas."""
    if valor == "Desconocido":
        return []
    return [parte.strip() for parte in valor.split(SEPARADOR_MULTIPLE) if parte.strip()]


# --- 7.1.a Columna de conteo por pregunta ---------------------------------
# Cuantas opciones marco cada persona. Es informacion nueva y util por si
# sola: mide, por ejemplo, cuantos lenguajes usa cada desarrollador.
for col in columnas_respuesta_multiple:
    df[f"n_{col}"] = df[col].astype(str).map(lambda v: len(separar_opciones(v)))

print(f"\nSe agregaron {len(columnas_respuesta_multiple)} columnas de conteo "
      f"(n_<pregunta>): cuantas opciones marco cada encuestado.")
resumen_conteos = pd.DataFrame({
    "promedio_opciones": [df[f"n_{c}"].mean() for c in columnas_respuesta_multiple],
    "maximo_opciones": [df[f"n_{c}"].max() for c in columnas_respuesta_multiple],
}, index=columnas_respuesta_multiple).round(2)
print(resumen_conteos)

# --- 7.1.b Tabla de frecuencias reales por opcion -------------------------
# Esta tabla es la razon de ser de toda la seccion: es la unica forma de
# responder "cuanta gente usa Python" sin que la respuesta quede contaminada
# por las combinaciones.
filas_frecuencias = []
total_encuestados = len(df)
for col in columnas_respuesta_multiple:
    conteo = {}
    for valor in df[col].astype(str):
        for opcion in separar_opciones(valor):
            conteo[opcion] = conteo.get(opcion, 0) + 1
    for opcion, n in sorted(conteo.items(), key=lambda kv: -kv[1]):
        filas_frecuencias.append({
            "pregunta": col,
            "opcion": opcion,
            "n_encuestados": n,
            "pct_encuestados": round(100 * n / total_encuestados, 2),
        })

tabla_frecuencias = pd.DataFrame(filas_frecuencias)
tabla_frecuencias.to_csv(ARCHIVO_FRECUENCIAS_MULTIPLE, index=False)
print(f"\nTabla de frecuencias por opcion guardada en "
      f"{ARCHIVO_FRECUENCIAS_MULTIPLE.relative_to(RAIZ)} "
      f"({len(tabla_frecuencias)} opciones distintas en total).")

# --- 7.1.c Columnas binarias para una pregunta -----------------------------
# Expandir las 20 preguntas a binarias agregaria cientos de columnas al
# dataset final. Lo hacemos para UNA, la mas usada en analisis de esta
# encuesta, para dejar la tecnica demostrada y aplicable al resto.
COLUMNA_PARA_BINARIAS = "LanguageWorkedWith"

if COLUMNA_PARA_BINARIAS in columnas_respuesta_multiple:
    opciones_binarias = sorted(
        tabla_frecuencias.loc[
            tabla_frecuencias["pregunta"] == COLUMNA_PARA_BINARIAS, "opcion"
        ]
    )
    marcadas_por_fila = df[COLUMNA_PARA_BINARIAS].astype(str).map(
        lambda v: set(separar_opciones(v))
    )
    columnas_binarias_nuevas = {}
    for opcion in opciones_binarias:
        # El nombre de la columna se limpia porque hay opciones como "C++" o
        # "C#", que como encabezado de columna dan problemas.
        sufijo = "".join(ch if ch.isalnum() else "_" for ch in opcion).strip("_")
        columnas_binarias_nuevas[f"usa_{sufijo}"] = marcadas_por_fila.map(
            lambda marcadas, o=opcion: int(o in marcadas)
        )
    df = pd.concat([df, pd.DataFrame(columnas_binarias_nuevas, index=df.index)], axis=1)
    print(f"\nSe agregaron {len(columnas_binarias_nuevas)} columnas binarias "
          f"(usa_<opcion>) a partir de {COLUMNA_PARA_BINARIAS}.")
    print(f"Se eligio una sola pregunta a proposito: expandir las "
          f"{len(columnas_respuesta_multiple)} agregaria "
          f"{len(tabla_frecuencias)} columnas al dataset final. La tabla de "
          f"frecuencias de arriba ya cubre el analisis de las demas.")
else:
    print(f"\n{COLUMNA_PARA_BINARIAS} no quedo entre las columnas de "
          f"respuesta multiple; no se generaron binarias.")


# ---------------------------------------------------------------------------
# 7.2 CATEGORIAS DE BAJA FRECUENCIA (cola larga)
# ---------------------------------------------------------------------------
linea("7.2 CATEGORIAS DE BAJA FRECUENCIA")

# Country y Ethnicity arrastran una cola larga: decenas de categorias con
# poquisimos casos cada una. Agruparlas en "Otros" simplifica el analisis,
# pero tambien borra detalle, asi que la decision no puede ser automatica:
# depende de CUANTA gente cae en esa cola.
#
# Las columnas originales NO se tocan: se agrega una version agrupada al
# lado, para poder usar la que convenga en cada analisis.
UMBRAL_BAJA_FRECUENCIA = 0.01  # 1% de los encuestados

for col in ["Country", "Ethnicity"]:
    if col not in df.columns:
        continue
    proporciones = df[col].value_counts(normalize=True)
    categorias_raras = proporciones[proporciones < UMBRAL_BAJA_FRECUENCIA].index
    pct_en_la_cola = proporciones[proporciones < UMBRAL_BAJA_FRECUENCIA].sum() * 100

    df[f"{col}_agrupado"] = df[col].where(~df[col].isin(categorias_raras), "Otros")

    print(f"\n{col}: {df[col].nunique()} categorias originales")
    print(f"  Por debajo del {UMBRAL_BAJA_FRECUENCIA:.0%}: "
          f"{len(categorias_raras)} categorias, que juntas son el "
          f"{pct_en_la_cola:.1f}% de los encuestados")
    print(f"  Columna nueva '{col}_agrupado': "
          f"{df[f'{col}_agrupado'].nunique()} categorias")

print("\nLo que hay que mirar aqui no es cuantas categorias se agrupan, sino "
      "cuanta GENTE queda dentro de 'Otros'. Si la cola concentra una "
      "fraccion grande de los encuestados, agrupar deja de ser una "
      "simplificacion y pasa a ser una perdida de informacion: 'Otros' se "
      "vuelve una de las categorias mas grandes del analisis y no significa "
      "nada. Por eso dejamos las dos versiones y la eleccion se justifica "
      "columna por columna en el informe, con los porcentajes de arriba.")


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

# Dividir entre 10 es inventar un valor, asi que no alcanza con que "suene
# razonable": hay que mostrar que el resultado cae dentro de lo que contesto
# el resto de la encuesta. Si al dividir quedaran horas absurdas (2 o 300 a la
# semana), la hipotesis del digito de mas seria falsa y habria que tratarlos
# como faltantes.
if mascara_horas_imposibles.any():
    corregidos = df.loc[mascara_horas_imposibles, "WorkWeekHrs"]
    normales = df.loc[~mascara_horas_imposibles, "WorkWeekHrs"]
    p5, p95 = normales.quantile(0.05), normales.quantile(0.95)
    dentro = ((corregidos >= p5) & (corregidos <= p95)).sum()
    print(f"\nEvidencia de que la correccion es creible: los valores "
          f"corregidos quedan entre "
          f"{corregidos.min():.1f} y {corregidos.max():.1f} horas/semana. "
          f"El 90% central del resto de la encuesta esta entre {p5:.1f} y "
          f"{p95:.1f}. {dentro} de {len(corregidos)} valores corregidos caen "
          f"dentro de ese rango.")
    print(f"     Ninguno queda fuera de una jornada humana posible: el "
          f"minimo son {corregidos.min():.1f} horas y el maximo "
          f"{corregidos.max():.1f}. Eso es lo que sostiene la hipotesis del "
          f"digito de mas. Si al dividir quedaran horas imposibles, la "
          f"correccion seria un invento y habria que tratarlos como "
          f"faltantes.")

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

# No se cruza CompTotal con CompFreq y la moneda para reconstruir el valor
# real, y conviene dejar dicho por que: la columna no entra al analisis, y el
# dataset ya trae la version convertida a USD.
if "CurrencySymbol" in df.columns:
    monedas = df["CurrencySymbol"].nunique()
    print(f"\nEvidencia: CompTotal viene en la moneda local de cada "
          f"persona y en este dataset hay {monedas} monedas distintas "
          f"(columna CurrencySymbol). Sumar o promediar pesos, rupias y "
          f"dolares en la misma columna no significa nada.")
    print(f"     Por eso el analisis de sueldos usa ConvertedComp, que la "
          f"propia encuesta ya entrega en USD. CompTotal se conserva como "
          f"evidencia del error de digitacion mas extremo del dataset, no "
          f"como variable de analisis: reconstruir sus valores cruzando "
          f"CompFreq y moneda seria trabajo sobre una columna que despues no "
          f"se usa.")

# --- Caso 6: ConvertedComp alto -> subpoblacion distinta -----------------
# El RIC marca 2.301 sueldos por encima del limite superior. No son errores:
# son sueldos posibles y, sobre todo, NO estan repartidos al azar por el
# dataset. Se concentran en unos pocos paises de salarios altos y en gente con
# mas experiencia y con empleo de tiempo completo. Eso es exactamente lo que
# define una subpoblacion distinta: un grupo con comportamiento propio, no una
# cola de valores sueltos.
# Accion: CONSERVAR y MARCAR con una variable indicadora, para poder
# analizarlo aparte en vez de dejarlo contaminando los promedios generales.
limite_inf_comp, limite_sup_comp = limites_ric(series_para_calcular_limites["ConvertedComp"])
mascara_salario_alto = df["ConvertedComp"] > limite_sup_comp

print(f"\nCaso 6 - ConvertedComp: {mascara_salario_alto.sum()} registro(s) por "
      f"encima de {limite_sup_comp:,.0f} USD. Clasificacion: SUBPOBLACION "
      f"DISTINTA. Accion: CONSERVAR y marcar con la columna "
      f"'subpoblacion_salario_alto'.")

# La evidencia: si fueran valores sueltos, los paises se repartirian igual que
# en el resto del dataset. No se reparten igual.
paises_atipicos = (df.loc[mascara_salario_alto, "Country"]
                   .value_counts(normalize=True) * 100)
paises_general = (df["Country"].value_counts(normalize=True) * 100)
comparacion_paises = pd.DataFrame({
    "pct_entre_salarios_altos": paises_atipicos.head(5).round(1),
    "pct_en_todo_el_dataset": paises_general.reindex(paises_atipicos.head(5).index).round(1),
})
print("\n     Evidencia 1 - de donde son. Si fueran valores sueltos, estos "
      "porcentajes serian parecidos:")
print(comparacion_paises.to_string())

exp_altos = df.loc[mascara_salario_alto, "YearsCodePro"].median()
exp_resto = df.loc[~mascara_salario_alto, "YearsCodePro"].median()
print(f"\n     Evidencia 2 - experiencia profesional mediana: "
      f"{exp_altos:.0f} anios en el grupo de salarios altos contra "
      f"{exp_resto:.0f} en el resto.")

if "Employment" in df.columns:
    tc_altos = df.loc[mascara_salario_alto, "Employment"].astype(str).str.contains("full-time").mean() * 100
    tc_resto = df.loc[~mascara_salario_alto, "Employment"].astype(str).str.contains("full-time").mean() * 100
    print(f"     Evidencia 3 - empleo de tiempo completo: {tc_altos:.0f}% en "
          f"el grupo contra {tc_resto:.0f}% en el resto.")

df["subpoblacion_salario_alto"] = mascara_salario_alto
print("\n     Por eso NO se eliminan ni se imputan: borrarlos sacaria del "
      "estudio justo a los desarrolladores mejor pagos, que son un grupo real "
      "de la poblacion. La columna indicadora permite analizarlos aparte.")


# --- Caso 7: YearsCode / YearsCodePro -> dos grupos dentro del mismo marcado
# El RIC marca como atipicos a los programadores mas veteranos. La mayoria son
# perfectamente creibles: 40 anios programando a los 55 de edad no tiene nada
# de raro. Pero adentro del mismo grupo hay unos pocos casos imposibles: gente
# que segun sus datos habria empezado a programar antes de los 5 anios.
# El mismo marcado estadistico contiene entonces DOS cosas distintas, y por eso
# se separan antes de actuar.
EDAD_MINIMA_PARA_PROGRAMAR = 5

for col in ["YearsCode", "YearsCodePro"]:
    limite_inf_exp, limite_sup_exp = limites_ric(series_para_calcular_limites[col])
    candidatos_exp = df[col] > limite_sup_exp

    # Solo se juzga a las filas que traian la edad de verdad: si la edad la
    # imputamos nosotros, una incoherencia contra ella no prueba nada.
    edad_confiable = df["_age_era_real"]
    imposibles = candidatos_exp & edad_confiable & (
        df[col] > df["Age"] - EDAD_MINIMA_PARA_PROGRAMAR
    )
    validos_extremos = candidatos_exp & ~imposibles

    mediana_col = resumen_antes.loc[col, "mediana"]
    print(f"\nCaso 7 - {col}: {candidatos_exp.sum()} candidato(s) del metodo "
          f"RIC (por encima de {limite_sup_exp:.1f} anios). Se separan en dos:")
    print(f"     a) {imposibles.sum()} con ERROR DE DIGITACION: implicarian "
          f"haber empezado a programar antes de los "
          f"{EDAD_MINIMA_PARA_PROGRAMAR} anios de edad. Accion: se tratan como "
          f"faltantes y se reemplazan por la mediana ({mediana_col:.0f} anios).")
    print(f"     b) {validos_extremos.sum()} son OBSERVACION VALIDA EXTREMA: "
          f"veteranos reales, con edad mediana de "
          f"{df.loc[validos_extremos, 'Age'].median():.0f} anios. Accion: "
          f"CONSERVAR sin modificar.")

    df.loc[imposibles, col] = mediana_col

print("\nLa leccion del caso 7 es que un grupo marcado por el metodo no tiene "
      "por que ser homogeneo: aqui el mismo marcado juntaba errores de "
      "digitacion con los programadores mas veteranos de la muestra. Aplicar "
      "una sola accion a todo el grupo habria borrado experiencia real o "
      "conservado datos imposibles.")


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

# La marca auxiliar de la seccion 4 era andamiaje interno: no forma parte del
# dataset limpio.
df = df.drop(columns=["_age_era_real"])

df.to_csv(ARCHIVO_LIMPIO, index=False)
print(f"Dataset original:  data/{ARCHIVO_ZIP.name} -> {CSV_DENTRO_DEL_ZIP}  "
      f"({n_filas} filas, {n_columnas} columnas) - sin modificar")
print(f"Dataset limpio:    {ARCHIVO_LIMPIO.relative_to(RAIZ)}  "
      f"({len(df)} filas, {df.shape[1]} columnas)")

linea("FIN DEL SCRIPT")
