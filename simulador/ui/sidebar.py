"""
ui/sidebar.py
-------------
Panel lateral de Streamlit: todos los controles de entrada del simulador.
Retorna un dict con los parámetros seleccionados por el usuario.
"""

import streamlit as st


def renderizar_sidebar() -> dict:
    """
    Renderiza el panel lateral con los controles del simulador.

    Retorna
    -------
    dict con las claves:
        m1, m2, theta_deg, g, mu, friccion_activa
    """
    with st.sidebar:
        st.markdown(
            '<div class="card-title">🧮 Parámetros del Sistema</div>',
            unsafe_allow_html=True,
        )

        # ── Masas ─────────────────────────────────────────────────────────────
        st.markdown("**Masas**")
        m1 = st.slider(
            "Masa m₁ (plano inclinado) [kg]",
            min_value=0.1, max_value=20.0, value=5.0, step=0.1,
            help="Masa del bloque sobre el plano inclinado",
        )
        m2 = st.slider(
            "Masa m₂ (suspendida) [kg]",
            min_value=0.1, max_value=20.0, value=3.0, step=0.1,
            help="Masa del bloque suspendido verticalmente",
        )

        st.markdown("---")

        # ── Geometría ─────────────────────────────────────────────────────────
        st.markdown("**Geometría**")
        theta_deg = st.slider(
            "Ángulo del plano θ [°]",
            min_value=0, max_value=90, value=30,
            help="Ángulo de inclinación del plano respecto a la horizontal",
        )

        st.markdown("---")

        # ── Constantes ────────────────────────────────────────────────────────
        st.markdown("**Constantes**")
        g = st.number_input(
            "Gravedad g [m/s²]",
            min_value=0.1, max_value=30.0, value=9.81, step=0.01,
            format="%.2f",
        )

        st.markdown("---")

        # ── Fricción ──────────────────────────────────────────────────────────
        st.markdown("**Fricción**")
        friccion_activa = st.checkbox("Activar fricción", value=False)

        mu = 0.0
        if friccion_activa:
            mu = st.slider(
                "Coeficiente de fricción μ",
                min_value=0.0, max_value=1.0, value=0.2, step=0.01,
            )
        else:
            st.caption("_(Fricción desactivada — sistema ideal)_")

    return {
        "m1":              m1,
        "m2":              m2,
        "theta_deg":       theta_deg,
        "g":               g,
        "mu":              mu,
        "friccion_activa": friccion_activa,
    }
