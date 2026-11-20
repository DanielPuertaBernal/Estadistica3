# %% ============================================================================
# TALLER 07 - ESTADISTICA DESCRIPTIVA Y ANALISIS EXPLORATORIO DE DATOS (EDA)
# Curso: Estadistica III - Ingenieria de Sistemas
# Universidad Catolica de Oriente
# Integrantes: Daniel Puerta Bernal - Juan Diego Guzman
# ==============================================================================

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

RUTA_DATOS = Path(__file__).resolve().parent / "data" / "07 - canciones.csv"

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)

sns.set_theme(style="whitegrid")


# %% ============================================================================
# PARTE 1 - INGESTA Y LIMPIEZA INICIAL
# ==============================================================================

print("\n" + "=" * 78)
print("  PARTE 1 - INGESTA Y LIMPIEZA INICIAL")
print("=" * 78)

# %% Ejercicio 1 - Cargue el conjunto de datos y muestre sus primeras 5 filas

print("\n--- Ejercicio 1: primeras 5 filas ---")

df = pd.read_csv(RUTA_DATOS)

print(df.head())

# ANALISIS EJERCICIO 1: ver `analisis.md`

# %% Ejercicio 2 - Resumen del DataFrame: dimensiones, tipos y valores nulos

print("\n--- Ejercicio 2: estructura, tipos y valores nulos ---")

filas, columnas = df.shape
print(f"Filas: {filas}")
print(f"Columnas: {columnas}")

print("\nTipos de datos:")
print(df.dtypes)

nulos = df.isna().sum()
print("\nValores nulos por columna:")
print(nulos)
print(f"Total de valores nulos: {nulos.sum()}")

print(f"\nFilas duplicadas exactas: {df.duplicated().sum()}")
print(f"Canciones con popularity = 0: {(df['popularity'] == 0).sum()}")
print(f"Canciones con genre = 'set()': {(df['genre'] == 'set()').sum()}")

# ANALISIS EJERCICIO 2: ver `analisis.md`


# %% ============================================================================
# PARTE 2 - ESTADISTICA DESCRIPTIVA UNIVARIADA
# ==============================================================================

print("\n" + "=" * 78)
print("  PARTE 2 - ESTADISTICA DESCRIPTIVA UNIVARIADA")
print("=" * 78)

# %% Ejercicio 3 - Cree la columna duration_min a partir de duration_ms

print("\n--- Ejercicio 3: duracion en minutos ---")

df["duration_min"] = df["duration_ms"] / 60000

print(df[["song", "duration_ms", "duration_min"]].head())

# ANALISIS EJERCICIO 3: ver `analisis.md`

# %% Ejercicio 4 - Media, mediana, desviacion estandar, minimo y maximo

print("\n--- Ejercicio 4: medidas de tendencia central y dispersion ---")

variables = ["duration_min", "popularity", "danceability"]

resumen_4 = df[variables].agg(["mean", "median", "std", "min", "max"]).T
resumen_4.columns = ["media", "mediana", "desv_est", "minimo", "maximo"]

print(resumen_4.round(3))

media_pop = resumen_4.loc["popularity", "media"]
mediana_pop = resumen_4.loc["popularity", "mediana"]
print(f"\npopularity -> media {media_pop:.2f} | mediana {mediana_pop:.1f} | "
      f"diferencia {media_pop - mediana_pop:.2f}")
print(f"popularity -> coeficiente de asimetria: {df['popularity'].skew():.3f}")

# ANALISIS EJERCICIO 4: ver `analisis.md`

# %% Ejercicio 5 - Cinco generos mas frecuentes y porcentaje de explicitas

print("\n--- Ejercicio 5: generos frecuentes y canciones explicitas ---")

# Los generos compuestos se separan en generos individuales.
# Criterio justificado en `analisis-parte-2.md`.
generos = df["genre"].str.split(",").explode().str.strip()
generos = generos[generos != "set()"]

frecuencia_generos = generos.value_counts()
canciones_con_genero = (df["genre"] != "set()").sum()

top_5 = frecuencia_generos.head(5).to_frame("canciones")
top_5["% de esas canciones"] = (top_5["canciones"] / canciones_con_genero * 100).round(1)

print(f"Celdas con mas de un genero: {df['genre'].str.contains(',').sum()} de {len(df)}")
print(f"Canciones sin genero identificado: {(df['genre'] == 'set()').sum()}")
print(f"Generos individuales distintos: {frecuencia_generos.size}")

print(f"Base del porcentaje: {canciones_con_genero} canciones con genero\n")
print("Top 5 generos mas frecuentes:")
print(top_5)

print(f"\nCanciones explicitas: {df['explicit'].sum()} de {len(df)} "
      f"({df['explicit'].mean() * 100:.1f} %)")

# ANALISIS EJERCICIO 5: ver `analisis.md`


# %% ============================================================================
# PARTE 3 - VISUALIZACION DE DATOS
# ==============================================================================

print("\n" + "=" * 78)
print("  PARTE 3 - VISUALIZACION DE DATOS")
print("=" * 78)

# %% Ejercicio 6 - Histograma de tempo con linea vertical roja en la media

print("\n--- Ejercicio 6: histograma de tempo ---")

tempo_medio = df["tempo"].mean()

fig, ax = plt.subplots(figsize=(10, 6))

sns.histplot(data=df, x="tempo", bins=40, color="#4C72B0", edgecolor="white", ax=ax)

ax.axvline(tempo_medio, color="red", linestyle="--", linewidth=2,
           label=f"Media = {tempo_medio:.1f} BPM")

ax.set_title("Distribución del tempo en los éxitos globales (1998-2020)", fontsize=13)
ax.set_xlabel("Tempo (pulsos por minuto, BPM)")
ax.set_ylabel("Frecuencia (número de canciones)")
ax.legend()

fig.tight_layout()
plt.show()

print(f"Media del tempo: {tempo_medio:.2f} BPM")
print(f"Mediana del tempo: {df['tempo'].median():.2f} BPM")

# ANALISIS EJERCICIO 6: ver `analisis.md`

# %% Ejercicio 7 - Boxplot de popularity segun explicit

print("\n--- Ejercicio 7: boxplot de popularidad segun contenido explicito ---")

n_grupo = df["explicit"].value_counts()

fig, ax = plt.subplots(figsize=(8, 6))

sns.boxplot(data=df, x="explicit", y="popularity", hue="explicit",
            palette="Set2", legend=False, ax=ax)

ax.set_title("Popularidad según contenido explícito", fontsize=13)
ax.set_xlabel("Contenido explícito")
ax.set_ylabel("Popularidad (índice 0-100)")
ax.set_xticks([0, 1])
ax.set_xticklabels([f"No explícita\n(n = {n_grupo[False]})",
                    f"Explícita\n(n = {n_grupo[True]})"])

fig.tight_layout()
plt.show()

resumen_7 = df.groupby("explicit")["popularity"].agg(
    n="count", mediana="median", media="mean", desv="std",
    Q1=lambda s: s.quantile(0.25), Q3=lambda s: s.quantile(0.75),
)
resumen_7["RIC"] = resumen_7["Q3"] - resumen_7["Q1"]

print(resumen_7.round(2))

# ANALISIS EJERCICIO 7: ver `analisis.md`


# %% ============================================================================
# PARTE 4 - ANALISIS BIVARIADO Y CORRELACION
# ==============================================================================

print("\n" + "=" * 78)
print("  PARTE 4 - ANALISIS BIVARIADO Y CORRELACION")
print("=" * 78)

# %% Ejercicio 8 - Matriz de correlacion de Pearson

print("\n--- Ejercicio 8: matriz de correlacion de Pearson ---")

atributos = ["danceability", "energy", "valence", "loudness"]

matriz_correlacion = df[atributos].corr(method="pearson")

print(matriz_correlacion.round(4))

# ANALISIS EJERCICIO 8: ver `analisis.md`

# %% Ejercicio 9 - Mapa de calor con paleta divergente y valores anotados

print("\n--- Ejercicio 9: mapa de calor ---")

ETIQUETAS = {
    "danceability": "Bailabilidad\n(0-1)",
    "energy": "Energía\n(0-1)",
    "valence": "Positividad\n(0-1)",
    "loudness": "Volumen\n(dB)",
}

fig, ax = plt.subplots(figsize=(8, 6.5))

sns.heatmap(
    matriz_correlacion.rename(index=ETIQUETAS, columns=ETIQUETAS),
    annot=True,              # muestra los valores sobre las celdas
    fmt=".3f",
    cmap="coolwarm",         # paleta divergente
    vmin=-1,
    vmax=1,
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"label": "Coeficiente de correlación de Pearson"},
    ax=ax,
)

ax.set_title("Correlación entre atributos de audio", fontsize=13, pad=14)
ax.set_xlabel("Atributo de audio")
ax.set_ylabel("Atributo de audio")

fig.tight_layout()
plt.show()

# ANALISIS EJERCICIO 9: ver `analisis.md`

# %% Ejercicio 10 - Par mas correlacionado y diagrama de dispersion

print("\n--- Ejercicio 10: par con la correlacion mas fuerte ---")

# Se pasa la matriz a formato largo y se conserva un solo sentido de cada par
# (variable_1 < variable_2), lo que elimina la diagonal y las repeticiones.
pares = matriz_correlacion.stack().reset_index()
pares.columns = ["variable_1", "variable_2", "r"]
pares = pares[pares["variable_1"] < pares["variable_2"]].copy()
pares["r_absoluto"] = pares["r"].abs()
pares = pares.sort_values("r_absoluto", ascending=False).reset_index(drop=True)

print(pares.round(4))

var_x = pares.loc[0, "variable_1"]
var_y = pares.loc[0, "variable_2"]
r_max = pares.loc[0, "r"]

print(f"\nPar mas fuerte: {var_x} - {var_y}  (r = {r_max:.4f})")
print(f"Coeficiente de determinacion r^2 = {r_max ** 2:.4f} "
      f"({r_max ** 2 * 100:.1f} % de varianza compartida)")

fig, ax = plt.subplots(figsize=(9, 6.5))

# alpha bajo y puntos pequenos para controlar el solapamiento de 2000 registros
sns.regplot(
    data=df,
    x=var_x,
    y=var_y,
    scatter_kws={"alpha": 0.25, "s": 14, "color": "#4C72B0"},
    line_kws={"color": "red", "linewidth": 2,
              "label": f"Recta de ajuste (r = {r_max:.3f})"},
    ax=ax,
)

ax.set_title("Relación entre energía y volumen promedio", fontsize=13)
ax.set_xlabel("Energía (índice 0-1)")
ax.set_ylabel("Volumen promedio (decibelios, dB)")
ax.legend()

fig.tight_layout()
plt.show()

# ANALISIS EJERCICIO 10: ver `analisis.md`


# %% ============================================================================
# PUNTO OPCIONAL - PREGUNTA PROPIA
# ==============================================================================

print("\n" + "=" * 78)
print("  PUNTO OPCIONAL")
print("=" * 78)

# %% Punto opcional - ¿Deja la ola del EDM una huella medible en el tempo?

print("\n--- Punto opcional: la huella del EDM en el tempo de los exitos ---")

# PREGUNTA: ¿el auge del EDM dejo una huella medible en el tempo de los exitos
# globales? Si la moda de 125-130 BPM del ejercicio 6 se debe al EDM, su peso
# debe subir durante los anos de auge y bajar despues. Se contrasta con la
# etiqueta Dance/Electronic para separar el sonido de la etiqueta, y se acota a
# 2000-2019 porque 1998, 1999 y 2020 tienen muy pocos registros.

periodo = df[(df["year"] >= 2000) & (df["year"] <= 2019)].copy()
periodo["tempo_baile"] = periodo["tempo"].between(120, 135)
periodo["genero_dance"] = periodo["genre"].str.contains("Dance/Electronic")

evolucion = periodo.groupby("year")[["tempo_baile", "genero_dance"]].mean() * 100

print(evolucion.round(1))

fig, ax = plt.subplots(figsize=(11, 6.5))

ax.axvspan(2010, 2014, color="#FFD9B3", alpha=0.45, zorder=0,
           label="Auge del EDM (2010-2014)")
ax.plot(evolucion.index, evolucion["tempo_baile"], marker="o", linewidth=2.5,
        color="#C44E52", label="Canciones con tempo de 120-135 BPM")
ax.plot(evolucion.index, evolucion["genero_dance"], marker="s", linewidth=2.5,
        color="#4C72B0", linestyle="--",
        label="Canciones etiquetadas Dance/Electronic")

anio_maximo = evolucion["tempo_baile"].idxmax()
pico = evolucion.loc[anio_maximo, "tempo_baile"]
ax.annotate(f"Máximo: {pico:.1f} % en {anio_maximo}",
            xy=(anio_maximo, pico), xytext=(anio_maximo + 1.4, 54),
            fontsize=9, arrowprops=dict(arrowstyle="->", color="#C44E52"))

ax.set_title("La huella del EDM en los éxitos globales: "
             "el género se queda, el tempo se va", fontsize=13, pad=12)
ax.set_xlabel("Año de publicación")
ax.set_ylabel("Porcentaje de los éxitos del año (%)")
ax.set_xticks(range(2000, 2020, 2))
ax.set_ylim(0, 60)
ax.legend(loc="upper left", fontsize=9)

fig.tight_layout()
plt.show()

# ANALISIS PUNTO OPCIONAL: ver `analisis.md`
