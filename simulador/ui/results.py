"""
ui/results.py
-------------
Panel de resultados de Streamlit: estado del sistema, métricas
y ecuaciones aplicadas.
"""

import streamlit as st
from physics.forces import SystemResult


# Configuración de estados: (clase CSS badge, texto badge, tipo alerta streamlit)
_ESTADO_CFG = {
    "equilibrio": ("state-equilibrio", "⚖️ EQUILIBRIO",        "success"),
    "m2_baja":    ("state-sube",       "▼ m₂ DESCIENDE",       "info"),
    "m1_baja":    ("state-baja",       "▼ m₁ DESCIENDE",       "warning"),
}

_ESTADO_MSG = {
    "equilibrio": "Las fuerzas se compensan. El sistema permanece en reposo o velocidad constante.",
    "m2_baja":    lambda a: f"m₂ desciende y m₁ asciende con a = {a:.3f} m/s²",
    "m1_baja":    lambda a: f"m₁ desciende por el plano y m₂ asciende con a = {abs(a):.3f} m/s²",
}


def _alerta_estado(estado: str, aceleracion: float) -> None:
    """Muestra el mensaje de estado correcto usando el componente apropiado."""
    badge_class, badge_text, alert_type = _ESTADO_CFG[estado]

    msg_raw = _ESTADO_MSG[estado]
    msg = msg_raw if isinstance(msg_raw, str) else msg_raw(aceleracion)

    getattr(st, alert_type)(msg)
    st.markdown(
        f'<span class="state-badge {badge_class}">{badge_text}</span>',
        unsafe_allow_html=True,
    )


def _grid_metricas(res: SystemResult, m1: float, m2: float) -> None:
    """Renderiza las 8 métricas en un grid HTML personalizado."""
    def fmt(v): return f"{v:.3f}"

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-box">
            <div class="label">Fuerza paralela</div>
            <div class="value">{fmt(res.F_paralela)}<span class="unit">N</span></div>
        </div>
        <div class="metric-box">
            <div class="label">Fuerza normal</div>
            <div class="value">{fmt(res.F_normal)}<span class="unit">N</span></div>
        </div>
        <div class="metric-box">
            <div class="label">Fricción</div>
            <div class="value">{fmt(res.F_friccion)}<span class="unit">N</span></div>
        </div>
        <div class="metric-box">
            <div class="label">Peso m₂</div>
            <div class="value">{fmt(res.P2)}<span class="unit">N</span></div>
        </div>
        <div class="metric-box">
            <div class="label">Fuerza neta</div>
            <div class="value">{fmt(abs(res.F_neta))}<span class="unit">N</span></div>
        </div>
        <div class="metric-box">
            <div class="label">Aceleración</div>
            <div class="value">{fmt(abs(res.aceleracion))}<span class="unit">m/s²</span></div>
        </div>
        <div class="metric-box">
            <div class="label">Tensión (T)</div>
            <div class="value">{fmt(res.tension)}<span class="unit">N</span></div>
        </div>
        <div class="metric-box">
            <div class="label">Masa total</div>
            <div class="value">{fmt(m1 + m2)}<span class="unit">kg</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _ecuaciones(res: SystemResult, mu: float) -> None:
    """Muestra un expander con las ecuaciones aplicadas y sus valores."""
    with st.expander("📖 Ecuaciones aplicadas"):
        st.markdown(f"""
**Fuerzas sobre m₁ (plano inclinado)**
- Componente paralela: `F∥ = m₁·g·sin(θ) = {res.F_paralela:.3f} N`
- Fuerza normal: `N = m₁·g·cos(θ) = {res.F_normal:.3f} N`
- Fricción: `Ff = μ·N = {res.F_friccion:.3f} N`  _(μ = {mu})_

**Fuerza sobre m₂ (suspendido)**
- Peso: `P₂ = m₂·g = {res.P2:.3f} N`

**Fuerza neta del sistema**
- `Fnet = P₂ − F∥ ± Ff = {res.F_neta:.3f} N`

**Aceleración**
- `a = Fnet / (m₁ + m₂) = {res.aceleracion:.4f} m/s²`

**Tensión en la cuerda**
- `T = {res.tension:.3f} N`
        """)


def renderizar_resultados(res: SystemResult, m1: float,
                           m2: float, mu: float) -> None:
    """
    Renderiza la sección completa de resultados.

    Parámetros
    ----------
    res  : resultado del cálculo físico
    m1   : masa del bloque en el plano [kg]
    m2   : masa del bloque suspendido [kg]
    mu   : coeficiente de fricción activo
    """
    st.markdown(
        '<div class="card-title">📊 Resultados del Sistema</div>',
        unsafe_allow_html=True,
    )

    _alerta_estado(res.estado, res.aceleracion)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    _grid_metricas(res, m1, m2)
    st.markdown("<br>", unsafe_allow_html=True)
    _ecuaciones(res, mu)
