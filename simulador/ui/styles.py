"""
ui/styles.py
------------
Inyecta los estilos CSS personalizados en la aplicación Streamlit.
Centraliza toda la definición visual de la interfaz.
"""

import streamlit as st

_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

    :root {
        --bg-deep:    #0b0f1a;
        --bg-card:    #111827;
        --bg-input:   #1a2234;
        --accent:     #00e5ff;
        --accent2:    #7c3aed;
        --green:      #00ff9d;
        --yellow:     #ffd166;
        --red:        #ff6b6b;
        --text-main:  #e2e8f0;
        --text-muted: #64748b;
        --border:     rgba(0,229,255,0.15);
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-deep) !important;
        color: var(--text-main) !important;
        font-family: 'Syne', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border);
    }

    /* ── Hero header ───────────────────────────────── */
    .hero-header {
        text-align: center;
        padding: 2rem 1rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    .hero-header h1 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 2.6rem;
        letter-spacing: -1px;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.4rem;
    }
    .hero-header p {
        font-family: 'Space Mono', monospace;
        font-size: 0.82rem;
        color: var(--text-muted);
        margin: 0;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* ── Cards ─────────────────────────────────────── */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
    }
    .card-title {
        font-family: 'Space Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.6rem;
    }

    /* ── Metric grid ───────────────────────────────── */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 0.8rem;
        margin-top: 0.5rem;
    }
    .metric-box {
        background: var(--bg-input);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .metric-box .label {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.35rem;
    }
    .metric-box .value {
        font-family: 'Space Mono', monospace;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--accent);
    }
    .metric-box .unit {
        font-size: 0.65rem;
        color: var(--text-muted);
        margin-left: 2px;
    }

    /* ── Estado badges ─────────────────────────────── */
    .state-badge {
        display: inline-block;
        padding: 0.45rem 1.1rem;
        border-radius: 999px;
        font-family: 'Space Mono', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 0.6rem;
    }
    .state-equilibrio {
        background: rgba(0,255,157,0.12);
        border: 1px solid var(--green);
        color: var(--green);
    }
    .state-sube {
        background: rgba(0,229,255,0.12);
        border: 1px solid var(--accent);
        color: var(--accent);
    }
    .state-baja {
        background: rgba(255,107,107,0.12);
        border: 1px solid var(--red);
        color: var(--red);
    }

    /* ── Divider ───────────────────────────────────── */
    .divider {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1.2rem 0;
    }

    /* ── Error banner ──────────────────────────────── */
    .err-banner {
        background: rgba(255,107,107,0.12);
        border: 1px solid var(--red);
        border-radius: 10px;
        padding: 0.8rem 1.1rem;
        font-family: 'Space Mono', monospace;
        font-size: 0.78rem;
        color: var(--red);
        margin: 0.5rem 0;
    }

    footer    { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
"""


def inyectar_estilos() -> None:
    """Inyecta el bloque CSS global en la página Streamlit."""
    st.markdown(_CSS, unsafe_allow_html=True)
