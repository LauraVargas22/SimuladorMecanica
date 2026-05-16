"""
ui/diagram.py
-------------
Genera la figura matplotlib del sistema físico con:
  - Vectores proporcionales a sus magnitudes físicas
  - Etiquetas con valores numéricos en cada vector
  - Indicadores direccionales de desplazamiento sobre cada masa
  - Leyenda completa con todos los vectores
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc, FancyArrowPatch
import matplotlib.patheffects as pe

from physics.forces import SystemResult

# ── Paleta de colores ────────────────────────────────────────────────────────
COLORS = {
    "bg_deep":       "#0b0f1a",
    "bg_card":       "#111827",
    "plano":         "#1e3a5f",
    "plano_e":       "#00e5ff",
    "bloque":        "#1e2a4a",
    "bloque_borde":  "#7c3aed",
    "cuerda":        "#cbd5e1",
    "polea":         "#ffd166",
    "peso":          "#ff6b6b",   # rojo  — fuerzas peso
    "normal":        "#00ff9d",   # verde — fuerza normal
    "tension":       "#00e5ff",   # cyan  — tensión
    "friccion":      "#f59e0b",   # ámbar — fricción
    "desplaz":       "#ffffff",   # blanco — vector desplazamiento
    "texto":         "#e2e8f0",
    "texto_dim":     "#64748b",
}

# ── Escala máxima visual para vectores (unidades de figura) ──────────────────
_VECTOR_MAX_LEN = 1.1   # longitud máxima en unidades de figura
_VECTOR_MIN_LEN = 0.30  # longitud mínima para que sea visible


def _normalizar_longitud(valor: float, referencia: float) -> float:
    """
    Escala el valor a longitud visual proporcional.
    `referencia` es el valor que corresponde a _VECTOR_MAX_LEN.
    """
    if referencia == 0:
        return _VECTOR_MIN_LEN
    raw = (valor / referencia) * _VECTOR_MAX_LEN
    return max(raw, _VECTOR_MIN_LEN if valor > 0 else 0.0)

def _vector(
    ax,
    ox: float,
    oy: float,
    dx: float,
    dy: float,
    color: str,
    label: str = "",
    valor: float | None = None,
    lw: float = 3.0,
    zorder: int = 10,
) -> None:

    # Glow
    ax.annotate(
        "",
        xy=(ox + dx, oy + dy),
        xytext=(ox, oy),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=lw + 5,
            alpha=0.18,
            mutation_scale=28,
        ),
        zorder=zorder - 1,
    )

    # Vector principal
    ax.annotate(
        "",
        xy=(ox + dx, oy + dy),
        xytext=(ox, oy),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=lw,
            mutation_scale=22,
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=zorder,
    )


def _flecha_desplazamiento(ax, ox: float, oy: float,
                            dx: float, dy: float,
                            color: str, label: str,
                            zorder: int = 12) -> None:
    """
    Dibuja una flecha gruesa punteada que indica la dirección
    de desplazamiento de una masa, con etiqueta.
    """
    # Línea discontinua de trayecto
    ax.annotate(
        "",
        xy=(ox + dx, oy + dy),
        xytext=(ox, oy),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=2.8,
            mutation_scale=20,
            linestyle="dashed",
            connectionstyle="arc3,rad=0.0",
        ),
        zorder=zorder,
    )
    # Etiqueta centrada sobre la flecha
    mx = ox + dx / 2
    my = oy + dy / 2
    # Perpendicular para offset de etiqueta
    mag = np.hypot(dx, dy) + 1e-9
    perp_x = -dy / mag * 0.22
    perp_y =  dx / mag * 0.22
    ax.text(
        mx + perp_x, my + perp_y, label,
        color=color, fontsize=8, fontfamily="monospace",
        fontweight="bold", ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.25",
                  facecolor=COLORS["bg_deep"],
                  edgecolor=color, linewidth=1.2, alpha=0.9),
        zorder=zorder + 1,
    )


def _dibujar_plano(ax, theta: float, base_x: float,
                   base_y: float, L: float) -> tuple:
    """Dibuja el plano inclinado. Retorna (top_x, top_y)."""
    top_x = base_x + L * np.cos(theta)
    top_y = base_y + L * np.sin(theta)

    # Sombra / relleno
    ax.fill(
        [base_x, top_x, top_x, base_x],
        [base_y, top_y, base_y, base_y],
        color=COLORS["plano"], zorder=1, alpha=1.0,
    )
    # Superficie del plano
    ax.plot([base_x, top_x], [base_y, top_y],
            color=COLORS["plano_e"], lw=2.5, zorder=2)
    # Base horizontal (referencia)
    ax.plot([base_x, top_x], [base_y, base_y],
            color=COLORS["plano_e"], lw=1.2,
            linestyle="--", alpha=0.4, zorder=2)

    # Arco y etiqueta del ángulo θ
    theta_deg = np.degrees(theta)
    arc = Arc((base_x, base_y), 1.3, 1.3, angle=0,
              theta1=0, theta2=theta_deg,
              color=COLORS["plano_e"], lw=1.5, zorder=3)
    ax.add_patch(arc)
    lx = base_x + 0.82 * np.cos(theta / 2)
    ly = base_y + 0.82 * np.sin(theta / 2)
    ax.text(lx, ly, f"θ={theta_deg:.0f}°",
            color=COLORS["plano_e"], fontsize=9, ha="center", va="center",
            fontfamily="monospace", fontweight="bold", zorder=4,
            path_effects=[pe.withStroke(linewidth=2, foreground=COLORS["bg_deep"])])

    return top_x, top_y


def _dibujar_bloque1(ax, theta: float, base_x: float, base_y: float,
                     L: float, m1: float, bl_size: float) -> tuple:
    """
    Dibuja m1 sobre el plano inclinado.
    Retorna (cx, cy, R) — centro y matriz de rotación.
    """
    cx = base_x + 0.52 * L * np.cos(theta)
    cy = base_y + 0.52 * L * np.sin(theta)

    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta),  np.cos(theta)]])
    corners_local = np.array([
        [-bl_size / 2, 0],
        [ bl_size / 2, 0],
        [ bl_size / 2, bl_size],
        [-bl_size / 2, bl_size],
    ])
    corners_world = (R @ corners_local.T).T + np.array([cx, cy])

    # Sombra interior
    ax.add_patch(plt.Polygon(
        corners_world,
        closed=True,
        facecolor=COLORS["bloque"],
        edgecolor=COLORS["bloque_borde"],
        linewidth=2.8,
        zorder=5,
        path_effects=[
            pe.withStroke(
                linewidth=8,
                foreground="#7c3aed33"
            )
        ]
    ))

    # Bloque
    ax.add_patch(plt.Polygon(
        corners_world, closed=True,
        facecolor=COLORS["bloque"],
        edgecolor=COLORS["bloque_borde"],
        linewidth=2.8, zorder=5,
    ))

    # Etiqueta de masa dentro del bloque
    centro = corners_world.mean(axis=0)
    ax.text(centro[0], centro[1], f"m₁\n{m1} kg",
            color=COLORS["texto"], fontsize=7.5, ha="center", va="center",
            fontfamily="monospace", fontweight="bold", zorder=7)

    return cx, cy, R


def _dibujar_polea(ax, px: float, py: float, r: float) -> None:
    """Dibuja la polea con detalles visuales."""
    # Aro exterior
    ax.add_patch(plt.Circle(
        (px, py), r,
        facecolor="#131c30", edgecolor=COLORS["polea"],
        linewidth=2.8, zorder=6,
    ))
    # Aro interior decorativo
    ax.add_patch(plt.Circle(
        (px, py), r * 0.55,
        facecolor="none", edgecolor=COLORS["polea"],
        linewidth=1.0, alpha=0.5, zorder=6,
    ))
    # Eje central
    ax.add_patch(plt.Circle(
        (px, py), 0.07,
        facecolor=COLORS["polea"], zorder=7,
    ))


def _dibujar_bloque2(ax, px: float, py: float,
                     polea_r: float, m2: float, bl_size: float) -> tuple:
    """
    Dibuja m2 suspendido verticalmente.
    Retorna (b2x, b2y) — esquina inferior izquierda.
    """
    b2x = px + polea_r - bl_size / 2
    b2y = py - 1.9 - bl_size

    # Sombra
    ax.add_patch(mpatches.FancyBboxPatch(
        (b2x + 0.04, b2y - 0.04), bl_size, bl_size,
        boxstyle="round,pad=0.05",
        facecolor="#0d1424", edgecolor="none",
        zorder=4, alpha=0.6,
    ))
    # Bloque
    ax.add_patch(mpatches.FancyBboxPatch(
        (b2x, b2y), bl_size, bl_size,
        boxstyle="round,pad=0.05",
        facecolor=COLORS["bloque"],
        edgecolor=COLORS["bloque_borde"],
        linewidth=2.8, zorder=5,
    ))
    ax.text(b2x + bl_size / 2, b2y + bl_size / 2,
            f"m₂\n{m2} kg",
            color=COLORS["texto"], fontsize=7.5,
            ha="center", va="center",
            fontfamily="monospace", fontweight="bold", zorder=7)

    return b2x, b2y


def _dibujar_cuerda(ax, theta: float, cx1: float, cy1: float, R,
                    bl_size: float, px: float, py: float,
                    polea_r: float) -> None:
    """Dibuja la cuerda inextensible bloque1 → polea → bloque2."""
    top_b1 = (R @ np.array([0, bl_size])) + np.array([cx1, cy1])
    tan1   = np.array([px - polea_r * np.sin(theta),
                       py - polea_r * np.cos(theta)])
    tan2   = np.array([px + polea_r, py])

    kw = dict(color=COLORS["cuerda"], lw=2.0, zorder=4, solid_capstyle="round")
    ax.plot([top_b1[0], tan1[0]], [top_b1[1], tan1[1]], **kw)
    ax.plot([tan2[0], tan2[0]], [tan2[1], tan2[1] - 1.9], **kw)


def _dibujar_vectores_fuerzas(ax, cx1: float, cy1: float, R,
                              bl_size: float, theta: float,
                              b2x: float, b2y: float,
                              res: SystemResult) -> None:
    """
    Dibuja todos los vectores de fuerza con longitud proporcional
    a su magnitud física y etiqueta con el valor en N.
    """

    # Referencia de escala
    fuerzas_ref = max(
        res.F_paralela,
        res.F_normal,
        res.P2,
        res.tension,
        1.0
    )

    def lon(f: float) -> float:
        return _normalizar_longitud(f, fuerzas_ref)

    # Centro geométrico del bloque 1
    centro1_local = np.array([0, bl_size / 2])
    centro1 = (R @ centro1_local) + np.array([cx1, cy1])

    # Vectores unitarios
    dir_paralela = np.array([np.cos(theta), np.sin(theta)])
    dir_normal = np.array([-np.sin(theta), np.cos(theta)])
    dir_vertical = np.array([0, -1])

    # Control de offsets para etiquetas
    origen_counts = {}

    # def _compute_offset_label(ox, oy, dx, dy, base=(0.06, 0.06)):
    #     key = (round(float(ox), 3), round(float(oy), 3))

    #     idx = origen_counts.get(key, 0)
    #     origen_counts[key] = idx + 1

    #     perp = np.array([-dy, dx])
    #     norm = np.hypot(perp[0], perp[1])

    #     if norm < 1e-6:
    #         perp_unit = np.array([0.0, 0.0])
    #     else:
    #         perp_unit = perp / norm

    #     extra = perp_unit * (0.10 * idx)

    #     return (
    #         base[0] + extra[0],
    #         base[1] + extra[1]
    #     )

    # ── PESO de m1 ─────────────────────────────
    L_peso1 = lon(res.F_paralela)

    # off = _compute_offset_label(
    #     centro1[0],
    #     centro1[1],
    #     dir_vertical[0] * L_peso1,
    #     dir_vertical[1] * L_peso1
    # )

    peso_m1 = (
        res.F_paralela / np.sin(theta)
        if np.sin(theta) > 0.01
        else res.P2
    )

    _vector(
        ax,
        centro1[0],
        centro1[1],
        dir_vertical[0] * L_peso1,
        dir_vertical[1] * L_peso1,
        color=COLORS["peso"],
        label="m₁g",
        valor=peso_m1,
        lw=2.0,
        zorder=10
    )

    # ── NORMAL ─────────────────────────────
    L_normal = lon(res.F_normal)

    # off = _compute_offset_label(
    #     centro1[0],
    #     centro1[1],
    #     dir_normal[0] * L_normal,
    #     dir_normal[1] * L_normal
    # )

    _vector(
        ax,
        centro1[0],
        centro1[1],
        dir_normal[0] * L_normal,
        dir_normal[1] * L_normal,
        color=COLORS["normal"],
        label="N",
        valor=res.F_normal,
        lw=2.0,
        zorder=10
    )

    # ── FRICCIÓN ─────────────────────────────
    if res.F_friccion > 0.01:

        if res.estado == "m2_baja":
            dir_fric = -dir_paralela
        else:
            dir_fric = dir_paralela

        L_fric = lon(res.F_friccion)

        origen_fric = (
            (R @ np.array([0, 0]))
            + np.array([cx1, cy1])
        )

        _vector(
            ax,
            origen_fric[0],
            origen_fric[1],
            dir_fric[0] * L_fric,
            dir_fric[1] * L_fric,
            color=COLORS["friccion"],
            label="Ff",
            valor=res.F_friccion,
            lw=2.0,
            zorder=10
        )

    # ── TENSIÓN sobre m1 ─────────────────────────────
    top_b1 = (
        (R @ np.array([0, bl_size]))
        + np.array([cx1, cy1])
    )

    L_t1 = lon(res.tension)

    _vector(
        ax,
        top_b1[0],
        top_b1[1],
        dir_paralela[0] * L_t1,
        dir_paralela[1] * L_t1,
        color=COLORS["tension"],
        label="T",
        valor=res.tension,
        lw=2.0,
        zorder=10
    )

    # ── PESO de m2 ─────────────────────────────
    cx2 = b2x + 0.275

    L_peso2 = lon(res.P2)

    _vector(
        ax,
        cx2,
        b2y,
        0,
        -L_peso2,
        color=COLORS["peso"],
        label="m₂g",
        valor=res.P2,
        lw=2.0,
        zorder=10
    )

    # ── TENSIÓN sobre m2 ─────────────────────────────
    cy2_top = b2y + 0.55

    L_t2 = lon(res.tension)

    _vector(
        ax,
        cx2,
        cy2_top,
        0,
        L_t2,
        color=COLORS["tension"],
        label="T",
        valor=res.tension,
        lw=2.0,
        zorder=10
    )


def _dibujar_desplazamiento(ax, cx1: float, cy1: float, R,
                             bl_size: float, theta: float,
                             b2x: float, b2y: float,
                             estado: str) -> None:
    """
    Dibuja flechas punteadas que indican la dirección de desplazamiento
    de cada masa según el estado dinámico del sistema.
    En equilibrio no dibuja nada.
    """
    if estado == "equilibrio":
        return

    color_mov = COLORS["desplaz"]
    largo = 0.75   # longitud de la flecha de desplazamiento

    # Dirección de movimiento de m1 a lo largo del plano
    dir_sube = np.array([np.cos(theta), np.sin(theta)])

    if estado == "m2_baja":
        # m1 sube por el plano
        dir_m1 =  dir_sube
        # m2 baja
        dir_m2 = np.array([0, -1])
        lbl_m1 = "sube"
        lbl_m2 = "baja"
    else:
        # m1 baja por el plano
        dir_m1 = -dir_sube
        # m2 sube
        dir_m2 = np.array([0, 1])
        lbl_m1 = "baja"
        lbl_m2 = "sube"

    # Punto de salida de la flecha de m1 (lateral del bloque)
    lado_b1 = (R @ np.array([bl_size / 2 + 0.05, bl_size / 2])) + np.array([cx1, cy1])
    _flecha_desplazamiento(
        ax,
        lado_b1[0], lado_b1[1],
        dir_m1[0] * largo, dir_m1[1] * largo,
        color=color_mov, label=f"m₁ {lbl_m1}",
        zorder=13,
    )

    # Punto de salida de m2 (lateral del bloque)
    cx2 = b2x + 0.55 + 0.1   # a la derecha del bloque 2
    cy2 = b2y + 0.275
    _flecha_desplazamiento(
        ax,
        cx2, cy2,
        dir_m2[0] * largo, dir_m2[1] * largo,
        color=color_mov, label=f"m₂ {lbl_m2}",
        zorder=13,
    )

def _dibujar_leyenda(ax, tiene_friccion: bool):

    handles = [
        plt.Line2D([0], [0], color=COLORS["peso"], lw=4, label="Peso"),
        plt.Line2D([0], [0], color=COLORS["normal"], lw=4, label="Normal"),
        plt.Line2D([0], [0], color=COLORS["tension"], lw=4, label="Tensión"),
    ]

    if tiene_friccion:
        handles.append(
            plt.Line2D(
                [0], [0],
                color=COLORS["friccion"],
                lw=4,
                label="Fricción"
            )
        )

    handles.append(
        plt.Line2D(
            [0], [0],
            color="white",
            lw=3,
            linestyle="--",
            label="Movimiento"
        )
    )

    leg = ax.legend(
        handles=handles,
        loc="lower right",
        fontsize=10,
        facecolor="#08111f",
        edgecolor="#334155",
        framealpha=0.95,
        fancybox=True,
        borderpad=1,
        bbox_to_anchor=(0.03, 0.42),
    )

    for txt in leg.get_texts():
        txt.set_color("#e2e8f0")

    leg.set_zorder(100)


def _dibujar_panel_estado(ax, estado: str, res: SystemResult) -> None:
    """
    Panel superior con el estado dinámico del sistema
    y la aceleración resultante.
    """
    cfg = {
        "equilibrio": ("⚖  EQUILIBRIO  —  a = 0 m/s²",          "#00ff9d"),
        "m2_baja":    (f"▼ m₂ desciende · ▲ m₁ asciende   "
                       f"a = {abs(res.aceleracion):.2f} m/s²",   "#00e5ff"),
        "m1_baja":    (f"▲ m₂ asciende · ▼ m₁ desciende   "
                       f"a = {abs(res.aceleracion):.2f} m/s²",   "#ff6b6b"),
    }
    texto, color = cfg[estado]

    ax.text(7.8, 8.45, texto,
            color=color, fontsize=11, ha="center", va="center",
            fontfamily="monospace", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.6",
                      facecolor="#08111f",
                      edgecolor=color,
                      linewidth=2.2,
                      alpha=0.96),
            zorder=15)


# ── Función pública principal ────────────────────────────────────────────────

def construir_diagrama(m1: float, m2: float,
                       theta_deg: float, res: SystemResult) -> plt.Figure:
    """
    Construye y retorna la figura completa del sistema físico.

    Parámetros
    ----------
    m1, m2    : masas del sistema [kg]
    theta_deg : ángulo del plano inclinado [°]
    res       : resultado del cálculo físico (SystemResult)

    Retorna
    -------
    Figura matplotlib lista para renderizar con st.pyplot().
    """
    fig, ax = plt.subplots(
        figsize=(14, 8),
        facecolor=COLORS["bg_deep"]
    )

    ax.grid(
        color="#1e293b",
        linestyle="--",
        linewidth=0.5,
        alpha=0.15
    )
    fig.patch.set_facecolor("#020617")
    ax.set_facecolor("#020617")
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["figure.dpi"] = 150
    fig.patch.set_facecolor(COLORS["bg_deep"])
    ax.set_facecolor(COLORS["bg_deep"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9)
    ax.set_aspect("equal")
    ax.axis("off")

    theta   = np.radians(theta_deg)
    base_x  = 0.6
    base_y  = 0.8
    L       = 5.5
    bl_size = 0.82
    polea_r = 0.33

    # ── Construcción del diagrama (orden de capas) ────────────────────────────
    top_x, top_y = _dibujar_plano(ax, theta, base_x, base_y, L)
    cx1, cy1, R  = _dibujar_bloque1(ax, theta, base_x, base_y, L, m1, bl_size)

    polea_x = top_x + 0.18
    polea_y = top_y + 0.06
    _dibujar_polea(ax, polea_x, polea_y, polea_r)

    b2x, b2y = _dibujar_bloque2(ax, polea_x, polea_y, polea_r, m2, bl_size)
    _dibujar_cuerda(ax, theta, cx1, cy1, R, bl_size, polea_x, polea_y, polea_r)

    # Vectores de fuerza (proporcionales a magnitud)
    _dibujar_vectores_fuerzas(ax, cx1, cy1, R, bl_size, theta, b2x, b2y, res)

    _dibujar_panel_fuerzas(ax, res)

    # Indicadores de dirección de desplazamiento
    #_dibujar_desplazamiento(ax, cx1, cy1, R, bl_size, theta, b2x, b2y, res.estado)

    # Panel de estado y aceleración
    _dibujar_panel_estado(ax, res.estado, res)

    # Leyenda
    _dibujar_leyenda(ax, tiene_friccion=res.F_friccion > 0.01)

    fig.tight_layout(pad=0.3)
    return fig

def _dibujar_panel_fuerzas(ax, res: SystemResult) -> None:

    panel = mpatches.FancyBboxPatch(
        (0.25, 6.95),
        9.4,
        1.0,
        boxstyle="round,pad=0.18",
        facecolor="#08111f",
        edgecolor="#334155",
        linewidth=1.8,
        alpha=0.96,
        zorder=30,
    )

    ax.add_patch(panel)

    items = [
        ("m₁g", res.F_paralela, COLORS["peso"]),
        ("N", res.F_normal, COLORS["normal"]),
        ("T", res.tension, COLORS["tension"]),
    ]

    if res.F_friccion > 0.01:
        items.append(
            ("Ff", res.F_friccion, COLORS["friccion"])
        )

    items.extend([
        ("m₂g", res.P2, COLORS["peso"])
    ])

    x = 0.8

    for nombre, valor, color in items:

        # Línea de color
        ax.plot(
            [x - 0.08, x + 0.08],
            [7.55, 7.55],
            color=color,
            lw=6,
            solid_capstyle="round",
            zorder=35,
        )

        # Nombre
        ax.text(
            x,
            7.30,
            nombre,
            color=color,
            fontsize=13,
            fontweight="bold",
            ha="center",
            zorder=40,
        )

        # Valor
        ax.text(
            x,
            7.02,
            f"{valor:.1f} N",
            color="#f8fafc",
            fontsize=11,
            fontweight="bold",
            ha="center",
            zorder=40,
        )

        x += 1.6