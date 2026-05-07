"""
ui/diagram.py
-------------
Genera la figura matplotlib del sistema físico:
plano inclinado, bloques, polea, cuerda y flechas de fuerzas.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc

from physics.forces import SystemResult

# ── Paleta de colores ────────────────────────────────────────────────────────
COLORS = {
    "bg_deep":   "#0b0f1a",
    "bg_card":   "#111827",
    "plano":     "#1e3a5f",
    "plano_e":   "#00e5ff",
    "bloque":    "#7c3aed",
    "cuerda":    "#e2e8f0",
    "polea":     "#ffd166",
    "flecha":    "#ff6b6b",
    "normal":    "#00ff9d",
    "tension":   "#00e5ff",
    "texto":     "#e2e8f0",
    "mov_baja":  "#00e5ff",
    "mov_sube":  "#ff6b6b",
}


def _arrow(ax, x: float, y: float, dx: float, dy: float,
           color: str, label: str = "", lw: float = 2.0) -> None:
    """Dibuja una flecha anotada en los ejes dados."""
    ax.annotate(
        "", xy=(x + dx, y + dy), xytext=(x, y),
        arrowprops=dict(arrowstyle="-|>", color=color,
                        lw=lw, mutation_scale=14),
        zorder=8,
    )
    if label:
        ax.text(x + dx + 0.06, y + dy + 0.06, label,
                color=color, fontsize=7.5, fontfamily="monospace",
                fontweight="bold", zorder=9)


def _dibujar_plano(ax, theta: float, base_x: float, base_y: float, L: float) -> tuple:
    """Dibuja el plano inclinado y devuelve las coordenadas del extremo superior."""
    top_x = base_x + L * np.cos(theta)
    top_y = base_y + L * np.sin(theta)

    # Relleno del plano
    ax.fill(
        [base_x, top_x, top_x, base_x],
        [base_y, top_y, base_y, base_y],
        color=COLORS["plano"], zorder=1,
    )
    ax.plot([base_x, top_x], [base_y, top_y],
            color=COLORS["plano_e"], lw=2.5, zorder=2)
    ax.plot([base_x, top_x], [base_y, base_y],
            color=COLORS["plano_e"], lw=1.5, linestyle="--", alpha=0.5, zorder=2)

    # Arco y etiqueta del ángulo
    theta_deg = np.degrees(theta)
    arc = Arc((base_x, base_y), 1.2, 1.2, angle=0,
              theta1=0, theta2=theta_deg,
              color=COLORS["plano_e"], lw=1.5, zorder=3)
    ax.add_patch(arc)
    lx = base_x + 0.75 * np.cos(theta / 2)
    ly = base_y + 0.75 * np.sin(theta / 2)
    ax.text(lx, ly, f"{theta_deg:.0f}°",
            color=COLORS["plano_e"], fontsize=9, ha="center", va="center",
            fontfamily="monospace", fontweight="bold", zorder=4)

    return top_x, top_y


def _dibujar_bloque1(ax, theta: float, base_x: float, base_y: float,
                     L: float, m1: float, bl_size: float) -> tuple:
    """Dibuja el bloque m1 sobre el plano y devuelve su posición central."""
    cx = base_x + 0.55 * L * np.cos(theta)
    cy = base_y + 0.55 * L * np.sin(theta)

    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta),  np.cos(theta)]])
    corners_local = np.array([
        [-bl_size / 2, 0],
        [ bl_size / 2, 0],
        [ bl_size / 2, bl_size],
        [-bl_size / 2, bl_size],
    ])
    corners_world = (R @ corners_local.T).T + np.array([cx, cy])

    ax.add_patch(plt.Polygon(
        corners_world, closed=True,
        facecolor=COLORS["bloque"], edgecolor=COLORS["plano_e"],
        linewidth=1.5, zorder=5,
    ))

    label_off = R @ np.array([0, bl_size / 2 + 0.28])
    ax.text(cx + label_off[0], cy + label_off[1],
            f"m₁={m1}kg", color=COLORS["texto"], fontsize=8.5,
            ha="center", va="center", fontfamily="monospace",
            fontweight="bold", zorder=6)

    return cx, cy, R


def _dibujar_polea(ax, px: float, py: float, r: float) -> None:
    """Dibuja la polea en la posición indicada."""
    ax.add_patch(plt.Circle(
        (px, py), r,
        facecolor="#1a1a2e", edgecolor=COLORS["polea"],
        linewidth=2.5, zorder=6,
    ))
    ax.add_patch(plt.Circle((px, py), 0.06,
                             facecolor=COLORS["polea"], zorder=7))


def _dibujar_bloque2(ax, px: float, py: float,
                     polea_r: float, m2: float, bl_size: float) -> tuple:
    """Dibuja el bloque m2 suspendido y devuelve su posición."""
    b2x = px + polea_r - bl_size / 2
    b2y = py - 1.85 - bl_size

    ax.add_patch(mpatches.FancyBboxPatch(
        (b2x, b2y), bl_size, bl_size,
        boxstyle="round,pad=0.05",
        facecolor=COLORS["bloque"], edgecolor=COLORS["plano_e"],
        linewidth=1.5, zorder=5,
    ))
    ax.text(b2x + bl_size / 2, b2y + bl_size / 2,
            f"m₂\n{m2}kg", color=COLORS["texto"], fontsize=8,
            ha="center", va="center", fontfamily="monospace",
            fontweight="bold", zorder=6)

    return b2x, b2y


def _dibujar_cuerda(ax, theta: float, cx1: float, cy1: float, R,
                    bl_size: float, px: float, py: float,
                    polea_r: float) -> None:
    """Dibuja la cuerda que conecta bloque1 → polea → bloque2."""
    top_b1    = (R @ np.array([0, bl_size])) + np.array([cx1, cy1])
    tan1 = np.array([px - polea_r * np.sin(theta),
                     py - polea_r * np.cos(theta)])
    tan2 = np.array([px + polea_r, py])

    ax.plot([top_b1[0], tan1[0]], [top_b1[1], tan1[1]],
            color=COLORS["cuerda"], lw=1.8, zorder=4)
    ax.plot([tan2[0], tan2[0]], [tan2[1], tan2[1] - 1.85],
            color=COLORS["cuerda"], lw=1.8, zorder=4)


def _dibujar_fuerzas(ax, cx1: float, cy1: float, R,
                     bl_size: float, theta: float,
                     b2x: float, b2y: float) -> None:
    """Dibuja las flechas de fuerzas sobre ambos bloques."""
    scale = 0.6
    # Peso de m1
    _arrow(ax, cx1, cy1 + bl_size / 2, 0, -0.7 * scale,
           COLORS["flecha"], "m₁g")
    # Normal a m1
    nx, ny = -np.sin(theta), np.cos(theta)
    _arrow(ax, cx1, cy1 + bl_size,
           nx * 0.65 * scale, ny * 0.65 * scale,
           COLORS["normal"], "N")
    # Peso de m2
    _arrow(ax, b2x + 0.275, b2y, 0, -0.7 * scale,
           COLORS["flecha"], "m₂g")
    # Tensión en m2
    _arrow(ax, b2x + 0.275, b2y + 0.55, 0, 0.7 * scale,
           COLORS["tension"], "T")


def _dibujar_banner_estado(ax, estado: str) -> None:
    """Muestra un banner de estado de movimiento en la parte superior."""
    if estado == "equilibrio":
        text, color = "⚖ SISTEMA EN EQUILIBRIO", "#00ff9d"
    elif estado == "m2_baja":
        text, color = "▼ m₂ baja  ▲ m₁ sube", COLORS["mov_baja"]
    else:
        text, color = "▲ m₂ sube  ▼ m₁ baja", COLORS["mov_sube"]

    ax.text(5, 7.4, text, color=color, fontsize=9,
            ha="center", fontfamily="monospace", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4",
                      facecolor="#1a2234", edgecolor=color, alpha=0.9),
            zorder=10)


def construir_diagrama(m1: float, m2: float,
                       theta_deg: float, res: SystemResult) -> plt.Figure:
    """
    Construye y retorna la figura completa del sistema físico.

    Parámetros
    ----------
    m1, m2    : masas del sistema [kg]
    theta_deg : ángulo del plano [°]
    res       : resultado del cálculo físico

    Retorna
    -------
    Figura matplotlib lista para renderizar.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(COLORS["bg_deep"])
    ax.set_facecolor(COLORS["bg_deep"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")

    theta    = np.radians(theta_deg)
    base_x   = 0.8
    base_y   = 0.8
    L        = 5.5
    bl_size  = 0.55
    polea_r  = 0.32

    top_x, top_y = _dibujar_plano(ax, theta, base_x, base_y, L)
    cx1, cy1, R  = _dibujar_bloque1(ax, theta, base_x, base_y, L, m1, bl_size)

    polea_x = top_x + 0.15
    polea_y = top_y + 0.05
    _dibujar_polea(ax, polea_x, polea_y, polea_r)

    b2x, b2y = _dibujar_bloque2(ax, polea_x, polea_y, polea_r, m2, bl_size)
    _dibujar_cuerda(ax, theta, cx1, cy1, R, bl_size, polea_x, polea_y, polea_r)
    _dibujar_fuerzas(ax, cx1, cy1, R, bl_size, theta, b2x, b2y)
    _dibujar_banner_estado(ax, res.estado)

    # Leyenda
    leyenda = [
        mpatches.Patch(color=COLORS["flecha"],  label="Peso (m·g)"),
        mpatches.Patch(color=COLORS["normal"],  label="Normal (N)"),
        mpatches.Patch(color=COLORS["tension"], label="Tensión (T)"),
    ]
    ax.legend(handles=leyenda, loc="lower right",
              facecolor="#111827", edgecolor="#334155",
              labelcolor=COLORS["texto"], fontsize=8,
              prop={"family": "monospace"})

    fig.tight_layout()
    return fig
