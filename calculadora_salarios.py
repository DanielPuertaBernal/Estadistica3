"""Calculadora de salarios para programadores.

Carga las 5 redes (una por país), sus preprocesadores y los salarios de
referencia que guarda red_neuronal_salarios.ipynb en salidas/, y estima el
salario anual de un perfil dentro del país elegido.

    .venv/bin/streamlit run calculadora_salarios.py
"""

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import tensorflow as tf
from matplotlib.ticker import FuncFormatter
from scipy import stats

SALIDAS = Path(__file__).resolve().parent / "salidas"
COLUMNA_PAIS = "Country"
COLUMNA_EXPERIENCIA = "YearsCodePro"
COLUMNA_OBJETIVO = "ConvertedComp"
GRUPO_LENGUAJES = "Lenguajes"
# Valor que la limpieza usa para las respuestas en blanco: no se ofrece como opción.
SIN_RESPUESTA = "Desconocido"
# "Mismo perfil" en los datos reales: mismo país, usa los lenguajes elegidos y
# tiene una experiencia parecida (± estos años).
TOLERANCIA_EXPERIENCIA = 2

VERDE, ORO, GRIS, ROJO = "#13501B", "#B07A1E", "#8A8984", "#B03A2E"


@st.cache_resource
def cargar_opciones():
    opciones = json.loads((SALIDAS / "calculadora_opciones.json").read_text())
    referencia = pd.read_csv(SALIDAS / "salarios_referencia.csv")
    return opciones, referencia


@st.cache_resource
def cargar_red(archivo):
    modelo = tf.keras.models.load_model(SALIDAS / "modelos" / f"{archivo}.keras")
    preprocesador = joblib.load(SALIDAS / "modelos" / f"{archivo}_preprocesador.joblib")
    return modelo, preprocesador


def pedir_perfil(opciones, pais):
    """Dibuja un control por cada variable de la red y devuelve la fila de entrada."""
    datos_pais = opciones["paises"][pais]
    fila, elegidos = {}, {}
    columnas = st.columns(3)
    for i, (grupo, info) in enumerate(opciones["grupos"].items()):
        col = columnas[i % 3]
        if info["tipo"] == "multiple":
            nombres = [c.removeprefix(info["prefijo"]) for c in info["columnas"]]
            visibles = [n for n in nombres if n != SIN_RESPUESTA]
            por_defecto = ["Python"] if grupo == GRUPO_LENGUAJES and "Python" in visibles else []
            elegidos[grupo] = col.multiselect(grupo, visibles, default=por_defecto)
            fila.update({c: int(n in elegidos[grupo]) for c, n in zip(info["columnas"], nombres)})
        elif info["tipo"] == "numerica":
            columna = info["columnas"][0]
            rango = datos_pais["numericas"][columna]
            inicial = 3.0 if columna == COLUMNA_EXPERIENCIA else rango["mediana"]
            fila[columna] = col.number_input(grupo, min_value=rango["min"], max_value=rango["max"],
                                             value=min(max(inicial, rango["min"]), rango["max"]), step=0.5)
        else:
            columna = info["columnas"][0]
            categorias = [c for c in datos_pais["categorias"][columna] if c != SIN_RESPUESTA]
            # Ordenadas por frecuencia: la primera es la respuesta más común en el país.
            fila[columna] = col.selectbox(grupo, categorias, index=0)
    return fila, elegidos


def transformar(preprocesador, fila):
    return preprocesador.transform(pd.DataFrame([fila])).astype("float32")[0]


def recorrer_red(modelo, x):
    """Hace a mano el mismo cálculo que modelo.predict, capa por capa.

    El dropout solo actúa durante el entrenamiento, así que aquí no aparece.
    """
    densas = [c for c in modelo.layers if isinstance(c, tf.keras.layers.Dense)]
    activacion, ocultas = x, []
    for capa in densas[:-1]:
        pesos, sesgo = capa.get_weights()
        entrada = activacion
        activacion = np.maximum(0, entrada @ pesos + sesgo)
        ocultas.append({"pesos": pesos, "entrada": entrada, "activacion": activacion})
    pesos_salida, sesgo_salida = densas[-1].get_weights()
    estandarizada = float(activacion @ pesos_salida[:, 0] + sesgo_salida[0])
    reescalado = modelo.get_layer("log_salario").get_config()
    log_salario = estandarizada * float(reescalado["scale"]) + float(reescalado["offset"])
    return {"ocultas": ocultas, "pesos_salida": pesos_salida[:, 0], "estandarizada": estandarizada,
            "escala": float(reescalado["scale"]), "desplazamiento": float(reescalado["offset"]),
            "log_salario": log_salario}


def perfil_similar(referencia, pais, fila, lenguajes):
    mascara = ((referencia[COLUMNA_PAIS] == pais)
               & ((referencia[COLUMNA_EXPERIENCIA] - fila[COLUMNA_EXPERIENCIA]).abs() <= TOLERANCIA_EXPERIENCIA))
    for lenguaje in lenguajes:
        mascara &= referencia[f"usa_{lenguaje}"] == 1
    return referencia.loc[mascara, COLUMNA_OBJETIVO]


def usd(valor, _=None):
    return f"{valor / 1000:,.0f} k" if valor >= 1000 else f"{valor:,.0f}"


def grafica_campana(salario, sigma, reales):
    log_est = np.log(salario)
    xs = np.linspace(log_est - 4 * sigma, log_est + 4 * sigma, 400)
    fig, eje = plt.subplots(figsize=(8, 3.6))
    if len(reales):
        log_reales = np.log(reales)
        log_reales = log_reales[(log_reales >= xs[0]) & (log_reales <= xs[-1])]
        eje.hist(log_reales, bins=30, range=(xs[0], xs[-1]), density=True, color=GRIS,
                 alpha=0.45, label="salarios reales de personas con un perfil parecido")
    eje.plot(xs, stats.norm.pdf(xs, log_est, sigma), color=VERDE, linewidth=2,
             label="distribución normal del error de la red")
    franja = (xs >= log_est - sigma) & (xs <= log_est + sigma)
    eje.fill_between(xs[franja], stats.norm.pdf(xs[franja], log_est, sigma), color=VERDE,
                     alpha=0.18, label="rango del 68 % (±1σ)")
    eje.axvline(log_est, color=ORO, linewidth=2, label=f"estimación: {salario:,.0f} USD")
    eje.xaxis.set_major_formatter(FuncFormatter(lambda v, p: usd(np.exp(v))))
    eje.set_xlabel("Salario anual (USD, escala logarítmica)")
    eje.set_yticks([])
    for borde in ["top", "right", "left"]:
        eje.spines[borde].set_visible(False)
    eje.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    return fig


def dibujar_conexiones(eje, x0, x1, y_origen, y_destino, aportes, minimo=0.0):
    """Una línea por conexión: verde suma, roja resta; más gruesa = aporta más."""
    escala = np.abs(aportes).max() or 1
    for i, j in zip(*np.nonzero(np.abs(aportes) > minimo * escala)):
        a = aportes[i, j]
        eje.plot([x0, x1], [y_origen[i], y_destino[j]], color=VERDE if a > 0 else ROJO,
                 alpha=0.05 + 0.6 * abs(a) / escala, linewidth=0.3 + 1.7 * abs(a) / escala)


def grafica_red(x, recorrido, nombres_entrada):
    # Solo se dibujan las entradas distintas de 0: las demás no aportan nada.
    activos = np.flatnonzero(x)
    ocultas = recorrido["ocultas"]
    x_capas = np.arange(len(ocultas) + 2, dtype=float)
    y_entrada = np.linspace(0.95, 0.05, len(activos))
    y_ocultas = [np.linspace(0.97, 0.03, len(c["activacion"])) for c in ocultas]

    fig, eje = plt.subplots(figsize=(11, 7.5))
    aportes = x[activos, None] * ocultas[0]["pesos"][activos]
    dibujar_conexiones(eje, x_capas[0], x_capas[1], y_entrada, y_ocultas[0], aportes)
    for k in range(1, len(ocultas)):
        aportes = ocultas[k - 1]["activacion"][:, None] * ocultas[k]["pesos"]
        dibujar_conexiones(eje, x_capas[k], x_capas[k + 1], y_ocultas[k - 1], y_ocultas[k], aportes, minimo=0.05)
    aportes_salida = (ocultas[-1]["activacion"] * recorrido["pesos_salida"])[:, None]
    dibujar_conexiones(eje, x_capas[-2], x_capas[-1], y_ocultas[-1], [0.5], aportes_salida)

    eje.scatter([x_capas[0]] * len(activos), y_entrada, s=45, color=ORO, zorder=3)
    for i, y in zip(activos, y_entrada):
        nombre = nombres_entrada[i] if len(nombres_entrada[i]) <= 45 else nombres_entrada[i][:42] + "…"
        eje.annotate(f"{nombre} = {x[i]:.2f}", (x_capas[0], y), xytext=(-8, 0), textcoords="offset points",
                     ha="right", va="center", fontsize=8)
    for k, capa in enumerate(ocultas):
        activacion = capa["activacion"]
        eje.scatter([x_capas[k + 1]] * len(activacion), y_ocultas[k], s=40, zorder=3, edgecolors=VERDE,
                    linewidths=0.6, c=activacion, cmap="Greens", vmin=0, vmax=activacion.max() or 1)
    eje.scatter([x_capas[-1]], [0.5], s=400, color=ORO, zorder=3)
    eje.annotate(f"log(salario) = {recorrido['log_salario']:.2f}\n→ {np.exp(recorrido['log_salario']):,.0f} USD",
                 (x_capas[-1], 0.5), xytext=(14, 0), textcoords="offset points", va="center", fontsize=10)

    titulos = ([f"Entrada\n{len(activos)} de {len(x)} ≠ 0"]
               + [f"Oculta {k + 1} (ReLU)\n{len(c['activacion'])} neuronas" for k, c in enumerate(ocultas)]
               + ["Salida\n1 neurona"])
    for xc, titulo in zip(x_capas, titulos):
        eje.text(xc, 1.03, titulo, ha="center", va="bottom", fontsize=10, fontweight="bold")
    eje.set_xlim(-2.6, x_capas[-1] + 1.4)
    eje.set_ylim(-0.03, 1.13)
    eje.axis("off")
    fig.tight_layout()
    return fig


def grafica_paises(estimaciones):
    fig, eje = plt.subplots(figsize=(8, 3.2))
    nombres = list(estimaciones)
    eje.barh(nombres, [estimaciones[n] for n in nombres], color=VERDE)
    for i, n in enumerate(nombres):
        eje.text(estimaciones[n], i, f"  {estimaciones[n]:,.0f} USD", va="center", fontsize=9)
    eje.xaxis.set_major_formatter(FuncFormatter(usd))
    eje.set_xlim(0, max(estimaciones.values()) * 1.3)
    eje.invert_yaxis()
    for borde in ["top", "right"]:
        eje.spines[borde].set_visible(False)
    fig.tight_layout()
    return fig


st.set_page_config(page_title="Calculadora de salarios", page_icon="💻", layout="wide")
st.title("Calculadora de salarios para programadores")
st.caption("Una red neuronal por país, entrenada con la encuesta Stack Overflow 2020")

if not (SALIDAS / "calculadora_opciones.json").exists() or not (SALIDAS / "modelos").exists():
    st.error("No hay modelos entrenados. Corre primero `red_neuronal_salarios.ipynb`.")
    st.stop()

opciones, referencia = cargar_opciones()
paises = opciones["paises"]
pais = st.selectbox("País", list(paises), format_func=lambda p: paises[p]["nombre"])
datos_pais = paises[pais]
modelo, preprocesador = cargar_red(datos_pais["archivo"])
sigma = datos_pais["sigma_residuos_log"]

fila, elegidos = pedir_perfil(opciones, pais)
x = transformar(preprocesador, fila)
recorrido = recorrer_red(modelo, x)
salario = float(np.exp(recorrido["log_salario"]))

pestana_calculadora, pestana_paises, pestana_red = st.tabs(
    ["Calculadora", "El mismo perfil en los 5 países", "¿Cómo lo calcula la red?"])

with pestana_calculadora:
    bajo, alto = salario * np.exp(-sigma), salario * np.exp(sigma)
    c1, c2 = st.columns(2)
    c1.metric(f"Salario anual estimado en {datos_pais['nombre']}", f"{salario:,.0f} USD")
    c2.metric("Rango del 68 %", f"{bajo:,.0f} – {alto:,.0f} USD")

    lenguajes = elegidos.get(GRUPO_LENGUAJES, [])
    reales = perfil_similar(referencia, pais, fila, lenguajes)
    st.pyplot(grafica_campana(salario, sigma, reales))
    if len(reales):
        dentro = ((reales >= bajo) & (reales <= alto)).mean()
        usa = f"usan {', '.join(lenguajes)} y " if lenguajes else ""
        st.write(
            f"En la encuesta hay **{len(reales)} personas** en {datos_pais['nombre']} que {usa}"
            f"tienen entre {max(fila[COLUMNA_EXPERIENCIA] - TOLERANCIA_EXPERIENCIA, 0):g} y "
            f"{fila[COLUMNA_EXPERIENCIA] + TOLERANCIA_EXPERIENCIA:g} años de experiencia. Su salario mediano es "
            f"**{reales.median():,.0f} USD** y el **{dentro:.0%}** cae dentro del rango del 68 %."
        )
    else:
        st.info("No hay personas en la encuesta con ese país, esos lenguajes y esa experiencia para comparar.")
    st.caption(
        "La campana es la distribución del error de la red: el logaritmo del salario real "
        f"se reparte alrededor de la estimación como una normal con σ = {sigma:.2f}. Fuera del "
        "rango del 68 % hay más casos extremos de los que una normal predice, por eso no se "
        "muestra el rango del 95 %."
    )

    metricas = datos_pais["metricas"]
    with st.expander("¿Qué tan confiable es?"):
        st.write(
            f"La red de {datos_pais['nombre']} explica el **{metricas['R² validación cruzada · red']:.0%}** "
            f"de la diferencia de salario entre programadores del país (validación cruzada, escala "
            f"logarítmica) y se equivoca en promedio por **{metricas['MAE red (USD)']:,.0f} USD** con "
            f"personas que nunca vio. Se entrenó con {metricas['personas (entren.)']:,.0f} personas."
        )
        if metricas["personas (entren.)"] < 500:
            st.warning("Este país tiene pocas respuestas en la encuesta: la estimación es menos precisa.")

with pestana_paises:
    st.write("Las mismas respuestas, evaluadas por la red de cada país. Las opciones que no "
             "existen en otro país (por ejemplo, una categoría muy rara) simplemente no se encienden.")
    estimaciones = {}
    for otro, info in paises.items():
        modelo_otro, pre_otro = cargar_red(info["archivo"])
        estimaciones[info["nombre"]] = float(np.exp(modelo_otro.predict(
            transformar(pre_otro, fila)[None, :], verbose=0)[0, 0]))
    st.pyplot(grafica_paises(estimaciones))
    st.write("**¿Qué pesa más en cada país?** Caída del R² al desordenar cada variable "
             "(importancia por permutación, del notebook):")
    importancia = pd.DataFrame(opciones["importancia"])
    st.dataframe(importancia.style.format("{:.3f}").background_gradient(cmap="Greens", axis=None))

with pestana_red:
    nombres_entrada = [n.split("__", 1)[1] for n in preprocesador.get_feature_names_out()]
    ocultas = recorrido["ocultas"]
    st.pyplot(grafica_red(x, recorrido, nombres_entrada))
    encendidas = " · ".join(f"capa {k + 1}: **{int((c['activacion'] > 0).sum())} de {len(c['activacion'])}**"
                            for k, c in enumerate(ocultas))
    st.markdown(
        f"""
**1 · Entrada.** Las respuestas se convierten en {len(x)} números: un 1 por cada opción
elegida (lenguajes, plataformas, tamaño de empresa…), un 0 para las demás, y la experiencia,
la edad y las horas estandarizadas (`(valor − media) / desviación`). Solo se dibujan las
{int(np.count_nonzero(x))} entradas distintas de 0: un 0 multiplicado por cualquier peso no aporta nada.

**2 · Capas ocultas.** Cada neurona calcula una suma ponderada `z = w·x + b` de la capa
anterior y aplica `ReLU(z) = max(0, z)`. Neuronas encendidas: {encendidas}. Verde más
intenso = más activación; las líneas verdes suman y las rojas restan. Cada capa combina
los patrones que encontró la anterior.

**3 · Salida.** Una neurona lineal da el salario estandarizado, {recorrido['estandarizada']:.3f}, y
se deshace la estandarización: `{recorrido['estandarizada']:.3f} × {recorrido['escala']:.3f} +
{recorrido['desplazamiento']:.3f} = {recorrido['log_salario']:.3f}` = log(salario), y
`e^{recorrido['log_salario']:.3f} = {salario:,.0f} USD`.
"""
    )
