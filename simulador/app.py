"""
Punto de entrada de la aplicación.
Orquesta los módulos de física, UI y validación.

Ejecutar con:
    streamlit run app.py
"""

import streamlit as st
import matplotlib.pyplot as plt

from physics import calcular_fuerzas, barrer_angulos
from ui      import (
    inyectar_estilos,
    renderizar_sidebar,
    renderizar_resultados,
    construir_diagrama,
    construir_graficas_sensibilidad,
)
from utils import validar_entradas


# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador Mecánico | Polea & Plano Inclinado",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos globales ─────────────────────────────────────────────────────────
inyectar_estilos()

# ── Hero header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>⚙️ Simulador Mecánico</h1>
    <p>Sistema de dos cuerpos · Polea ideal · Plano inclinado · Leyes de Newton</p>
</div>
""", unsafe_allow_html=True)

# ── Parámetros desde el sidebar ──────────────────────────────────────────────
params = renderizar_sidebar()
m1              = params["m1"]
m2              = params["m2"]
theta_deg       = params["theta_deg"]
g               = params["g"]
mu              = params["mu"]
friccion_activa = params["friccion_activa"]

# ── Validación de entradas ───────────────────────────────────────────────────
errores = validar_entradas(m1, m2, theta_deg, g, mu)
if errores:
    for err in errores:
        st.markdown(f'<div class="err-banner">{err}</div>',
                    unsafe_allow_html=True)
    st.stop()

# ── Cálculos físicos ─────────────────────────────────────────────────────────
resultado = calcular_fuerzas(m1, m2, theta_deg, g, mu, friccion_activa)

# ── Layout principal: diagrama + resultados ───────────────────────────────────
col_viz, col_res = st.columns([1.35, 1], gap="large")

with col_viz:
    st.markdown('<div class="card-title">📐 Diagrama del Sistema</div>',
                unsafe_allow_html=True)
    fig_diag = construir_diagrama(m1, m2, theta_deg, resultado)
    st.pyplot(fig_diag, use_container_width=True)
    plt.close(fig_diag)

with col_res:
    renderizar_resultados(resultado, m1, m2, mu)

# ── Análisis de sensibilidad ─────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<div class="card-title">🔬 Análisis de Sensibilidad — Variación de Ángulo</div>',
    unsafe_allow_html=True,
)

datos_sens = barrer_angulos(m1, m2, g, mu, friccion_activa)

fig_charts = construir_graficas_sensibilidad(
    angulos        = datos_sens["angulos"],
    aceleraciones  = datos_sens["aceleraciones"],
    tensiones      = datos_sens["tensiones"],
    theta_actual   = theta_deg,
    acc_actual     = abs(resultado.aceleracion),
    tension_actual = resultado.tension,
)
st.pyplot(fig_charts, use_container_width=True)
plt.close(fig_charts)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#1e3a5f; margin-top:2rem;">
<p style="text-align:center; font-family:'Space Mono',monospace; font-size:0.7rem;
   color:#334155; letter-spacing:1px;">
   ⚙️ SIMULADOR MECÁNICO · PLANO INCLINADO + POLEA IDEAL · FÍSICA CLÁSICA
</p>
""", unsafe_allow_html=True)