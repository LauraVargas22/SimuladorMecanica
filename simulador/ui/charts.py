"""
ui/charts.py
------------
Genera las gráficas de análisis de sensibilidad:
aceleración y tensión en función del ángulo del plano inclinado.
"""

import matplotlib.pyplot as plt
import numpy as np

# Paleta coherente con el resto de la UI
_BG_DEEP  = "#0b0f1a"
_BG_CARD  = "#111827"
_GRID     = "#1e3a5f"
_MUTED    = "#64748b"
_TEXT     = "#e2e8f0"
_ACCENT   = "#00e5ff"
_PURPLE   = "#7c3aed"
_YELLOW   = "#ffd166"


def _estilizar_ax(ax) -> None:
    """Aplica el estilo oscuro uniforme a un eje."""
    ax.set_facecolor(_BG_CARD)
    ax.tick_params(colors=_MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(_GRID)
    ax.grid(True, color=_GRID, alpha=0.7, linewidth=0.8)


def construir_graficas_sensibilidad(
    angulos: np.ndarray,
    aceleraciones: np.ndarray,
    tensiones: np.ndarray,
    theta_actual: float,
    acc_actual: float,
    tension_actual: float,
) -> plt.Figure:
    """
    Construye la figura de dos subplots: aceleración y tensión vs. ángulo.

    Parámetros
    ----------
    angulos        : array de ángulos [°]
    aceleraciones  : array de |aceleración| [m/s²]
    tensiones      : array de tensión [N]
    theta_actual   : ángulo actualmente seleccionado [°]
    acc_actual     : aceleración en el ángulo actual [m/s²]
    tension_actual : tensión en el ángulo actual [N]

    Retorna
    -------
    Figura matplotlib con dos subplots.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.5))
    fig.patch.set_facecolor(_BG_DEEP)

    # ── Aceleración vs. ángulo ────────────────────────────────────────────────
    _estilizar_ax(ax1)
    ax1.plot(angulos, aceleraciones, color=_ACCENT, lw=2.5)
    ax1.axvline(theta_actual, color=_YELLOW, lw=1.5, linestyle="--", alpha=0.8)
    ax1.scatter([theta_actual], [acc_actual],
                color=_YELLOW, s=60, zorder=5)
    ax1.set_xlabel("Ángulo θ [°]",   color=_MUTED, fontsize=8, fontfamily="monospace")
    ax1.set_ylabel("Aceleración [m/s²]", color=_MUTED, fontsize=8, fontfamily="monospace")
    ax1.set_title("Aceleración vs. Ángulo", color=_TEXT, fontsize=9,
                  fontfamily="monospace", pad=8)

    # ── Tensión vs. ángulo ────────────────────────────────────────────────────
    _estilizar_ax(ax2)
    ax2.plot(angulos, tensiones, color=_PURPLE, lw=2.5)
    ax2.axvline(theta_actual, color=_YELLOW, lw=1.5, linestyle="--", alpha=0.8)
    ax2.scatter([theta_actual], [tension_actual],
                color=_YELLOW, s=60, zorder=5)
    ax2.set_xlabel("Ángulo θ [°]", color=_MUTED, fontsize=8, fontfamily="monospace")
    ax2.set_ylabel("Tensión [N]",  color=_MUTED, fontsize=8, fontfamily="monospace")
    ax2.set_title("Tensión vs. Ángulo", color=_TEXT, fontsize=9,
                  fontfamily="monospace", pad=8)

    fig.tight_layout()
    return fig
