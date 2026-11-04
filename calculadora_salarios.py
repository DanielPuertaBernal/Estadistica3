"""Calculadora de salarios para programadores (fase 7).

Carga la red, el preprocesador y los salarios de referencia que guarda
red_neuronal_salarios.ipynb en salidas/ y estima el salario anual a partir del
lenguaje, los años de experiencia profesional y el país.

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
COLUMNA_EXPERIENCIA = "YearsCodePro"
COLUMNA_PAIS = "Country_agrupado"
COLUMNA_OBJETIVO = "ConvertedComp"
# Categoria que agrupa los paises con menos del 1 % de las respuestas: mezcla
# realidades salariales muy distintas, asi que su estimacion es poco precisa.
PAIS_AGRUPADO = "Otros"
# "Mismo perfil" en los datos reales: mismo pais, usa el lenguaje y tiene una
# experiencia parecida (± estos años).
TOLERANCIA_EXPERIENCIA = 2

VERDE, ORO, GRIS, ROJO = "#13501B", "#B07A1E", "#8A8984", "#B03A2E"


@st.cache_resource
def cargar_artefactos():
    modelo = tf.keras.models.load_model(SALIDAS / "modelo_salarios.keras")
    preprocesador = joblib.load(SALIDAS / "preprocesador_salarios.joblib")
    opciones = json.loads((SALIDAS / "calculadora_opciones.json").read_text())
    referencia = pd.read_csv(SALIDAS / "salarios_referencia.csv")
    return modelo, preprocesador, opciones, referencia


def preparar_entrada(preprocesador, opciones, lenguaje, anios_experiencia, pais):
    # Un solo lenguaje encendido y los demas en 0: la simplificacion que
    # decidio la propuesta para la calculadora.
    fila = {f"usa_{l}": 0 for l in opciones["lenguajes"]}
    fila[f"usa_{lenguaje}"] = 1
    fila[COLUMNA_EXPERIENCIA] = anios_experiencia
    fila[COLUMNA_PAIS] = pais
    return preprocesador.transform(pd.DataFrame([fila])).astype("float32")[0]


def recorrer_red(modelo, x):
    """Hace a mano el mismo calculo que modelo.predict, capa por capa."""
    pesos_oculta, sesgo_oculta = modelo.get_layer("oculta_1").get_weights()
    pesos_salida, sesgo_salida = modelo.get_layer("salida_log_salario").get_weights()
    z = x @ pesos_oculta + sesgo_oculta
    activacion = np.maximum(0, z)
    log_salario = float(activacion @ pesos_salida[:, 0] + sesgo_salida[0])
    return {"z": z, "activacion": activacion, "pesos_oculta": pesos_oculta,
            "pesos_salida": pesos_salida[:, 0], "log_salario": log_salario}


def perfil_similar(referencia, lenguaje, anios_experiencia, pais):
    mascara = ((referencia[COLUMNA_PAIS] == pais)
               & (referencia[f"usa_{lenguaje}"] == 1)
               & ((referencia[COLUMNA_EXPERIENCIA] - anios_experiencia).abs() <= TOLERANCIA_EXPERIENCIA))
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
                 alpha=0.45, label="salarios reales de personas con ese perfil")
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


def grafica_red(x, recorrido, nombres_entrada):
    activos = np.flatnonzero(x)
    n_entrada, n_oculta = len(x), len(recorrido["activacion"])
    y_entrada = np.linspace(1, 0, n_entrada)
    y_oculta = np.linspace(0.95, 0.05, n_oculta)
    x_capas = [0.0, 1.0, 2.0]

    fig, eje = plt.subplots(figsize=(9, 7))
    # Entrada -> oculta: solo las entradas encendidas aportan (x = 0 anula el peso)
    aportes = x[activos, None] * recorrido["pesos_oculta"][activos]
    escala = np.abs(aportes).max() or 1
    for k, i in enumerate(activos):
        for j in range(n_oculta):
            a = aportes[k, j]
            eje.plot(x_capas[:2], [y_entrada[i], y_oculta[j]], color=VERDE if a > 0 else ROJO,
                     alpha=0.08 + 0.6 * abs(a) / escala, linewidth=0.4 + 1.6 * abs(a) / escala)
    # Oculta -> salida: el aporte de cada neurona es su activacion por su peso
    aportes_salida = recorrido["activacion"] * recorrido["pesos_salida"]
    escala_salida = np.abs(aportes_salida).max() or 1
    for j in range(n_oculta):
        a = aportes_salida[j]
        if a == 0:
            continue
        eje.plot(x_capas[1:], [y_oculta[j], 0.5], color=VERDE if a > 0 else ROJO,
                 alpha=0.15 + 0.7 * abs(a) / escala_salida, linewidth=0.5 + 2.5 * abs(a) / escala_salida)

    colores_entrada = [ORO if i in activos else "#DDDDDA" for i in range(n_entrada)]
    eje.scatter([x_capas[0]] * n_entrada, y_entrada, s=40, c=colores_entrada, zorder=3, edgecolors="none")
    for i in activos:
        eje.annotate(f"{nombres_entrada[i]} = {x[i]:.2f}", (x_capas[0], y_entrada[i]),
                     xytext=(-8, 0), textcoords="offset points", ha="right", va="center", fontsize=9)
    activacion = recorrido["activacion"]
    eje.scatter([x_capas[1]] * n_oculta, y_oculta, s=90, zorder=3, edgecolors=VERDE, linewidths=0.8,
                c=activacion, cmap="Greens", vmin=0, vmax=activacion.max() or 1)
    eje.scatter([x_capas[2]], [0.5], s=400, color=ORO, zorder=3)
    eje.annotate(f"log(salario) = {recorrido['log_salario']:.2f}\n→ {np.exp(recorrido['log_salario']):,.0f} USD",
                 (x_capas[2], 0.5), xytext=(14, 0), textcoords="offset points", va="center", fontsize=10)

    for xc, titulo in zip(x_capas, [f"Entrada\n{n_entrada} valores", f"Capa oculta (ReLU)\n{n_oculta} neuronas",
                                    "Salida\n1 neurona"]):
        eje.text(xc, 1.07, titulo, ha="center", va="bottom", fontsize=10, fontweight="bold")
    eje.set_xlim(-1.3, 3.0)
    eje.set_ylim(-0.03, 1.17)
    eje.axis("off")
    fig.tight_layout()
    return fig


st.set_page_config(page_title="Calculadora de salarios", page_icon="💻", layout="wide")
st.title("Calculadora de salarios para programadores")
st.caption("Red neuronal entrenada con la encuesta Stack Overflow 2020")

if not (SALIDAS / "salarios_referencia.csv").exists():
    st.error("No hay modelo entrenado. Corre primero `red_neuronal_salarios.ipynb`.")
    st.stop()

modelo, preprocesador, opciones, referencia = cargar_artefactos()
sigma = opciones["sigma_residuos_log"]

col_lenguaje, col_anios, col_pais = st.columns(3)
lenguaje = col_lenguaje.selectbox("Lenguaje principal", opciones["lenguajes"],
                                  index=opciones["lenguajes"].index("Python"))
anios = col_anios.number_input("Años de experiencia profesional", min_value=0.5,
                               max_value=opciones["experiencia_max"], value=3.0, step=0.5)
pais = col_pais.selectbox("País", opciones["paises"], index=opciones["paises"].index("United States"))

x = preparar_entrada(preprocesador, opciones, lenguaje, anios, pais)
recorrido = recorrer_red(modelo, x)
salario = float(np.exp(recorrido["log_salario"]))

pestana_calculadora, pestana_red = st.tabs(["Calculadora", "¿Cómo lo calcula la red?"])

with pestana_calculadora:
    bajo, alto = salario * np.exp(-sigma), salario * np.exp(sigma)
    c1, c2 = st.columns(2)
    c1.metric("Salario anual estimado", f"{salario:,.0f} USD")
    c2.metric("Rango del 68 %", f"{bajo:,.0f} – {alto:,.0f} USD")
    if pais == PAIS_AGRUPADO:
        st.warning("'Otros' agrupa muchos países con salarios muy distintos: "
                   "esta estimación es poco precisa.")

    reales = perfil_similar(referencia, lenguaje, anios, pais)
    st.pyplot(grafica_campana(salario, sigma, reales))
    if len(reales):
        dentro = ((reales >= bajo) & (reales <= alto)).mean()
        st.write(
            f"En la encuesta hay **{len(reales)} personas** en {pais} que usan {lenguaje} y "
            f"tienen entre {max(anios - TOLERANCIA_EXPERIENCIA, 0):g} y {anios + TOLERANCIA_EXPERIENCIA:g} años "
            f"de experiencia. Su salario mediano es **{reales.median():,.0f} USD** y el "
            f"**{dentro:.0%}** cae dentro del rango del 68 %."
        )
    else:
        st.info("No hay personas en la encuesta con exactamente ese perfil para comparar.")
    st.caption(
        "La campana es la distribución del error de la red: el logaritmo del salario real "
        "se reparte alrededor de la estimación como una normal con σ = "
        f"{sigma:.2f}. Fuera del rango del 68 % hay más casos extremos de los que una "
        "normal predice, por eso no se muestra el rango del 95 %."
    )

    metricas = opciones["metricas_prueba"]
    with st.expander("¿Qué tan confiable es?"):
        st.write(
            f"Sobre personas que la red nunca vio, explica el "
            f"**{metricas['R² log(salario)']:.0%}** de la variación del salario "
            f"(en escala logarítmica) y se equivoca en promedio por "
            f"**{metricas['MAE (USD)']:,.0f} USD**. Solo usa tres datos: el salario "
            f"también depende del cargo, la empresa y la formación, así que el "
            f"resultado es una referencia, no una oferta."
        )

with pestana_red:
    nombres_entrada = ([f"usa_{l}" for l in opciones["lenguajes"]] + ["experiencia (estandarizada)"]
                       + [f"país: {p}" for p in opciones["paises"]])
    encendidas = int((recorrido["activacion"] > 0).sum())
    st.pyplot(grafica_red(x, recorrido, nombres_entrada))
    st.markdown(
        f"""
**1 · Entrada.** Los datos se convierten en {len(x)} números: un 1 para el lenguaje
elegido, un 1 para el país y la experiencia estandarizada
(`({anios:g} − media) / desviación` = {x[len(opciones['lenguajes'])]:.2f}). El resto
son ceros y no aportan nada (puntos grises).

**2 · Capa oculta.** Cada una de las {len(recorrido['z'])} neuronas calcula una suma
ponderada `z = w·x + b` y aplica `ReLU(z) = max(0, z)`. Con estos datos
**{encendidas} de {len(recorrido['z'])}** quedan encendidas (verde más intenso = más
activación); las demás dan 0 y se apagan. Las líneas verdes suman y las rojas restan.

**3 · Salida.** Una sola neurona lineal combina las activaciones:
`log(salario) = {recorrido['log_salario']:.3f}`, y
`e^{recorrido['log_salario']:.3f} = {salario:,.0f} USD`.
"""
    )
