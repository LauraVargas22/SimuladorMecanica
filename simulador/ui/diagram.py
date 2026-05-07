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


def _vector(ax, ox: float, oy: float, dx: float, dy: float,
            color: str, label: str = "", valor: float | None = None,
            lw: float = 2.0, offset_label: tuple = (0.08, 0.08),
            zorder: int = 10) -> None:
    """
    Dibuja un vector (flecha) con etiqueta de nombre y valor numérico.

    Parámetros
    ----------
    ox, oy       : origen del vector
    dx, dy       : desplazamiento (ya escalado)
    color        : color de la flecha y etiqueta
    label        : nombre del vector (p.ej. "N")
    valor        : magnitud física en N para mostrar entre paréntesis
    lw           : ancho de línea
    offset_label : desplazamiento (x, y) de la etiqueta respecto al extremo
    zorder       : orden de dibujado
    """
    # Dibuja la flecha principal
    ax.annotate(
        "",
        xy=(ox + dx, oy + dy),
        xytext=(ox, oy),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=lw,
            mutation_scale=16,
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=zorder,
    )

    # Etiqueta con nombre y valor numérico
    if label:
        lx = ox + dx + offset_label[0]
        ly = oy + dy + offset_label[1]
        texto = f"{label}" if valor is None else f"{label}\n{valor:.1f} N"
        ax.text(
            lx, ly, texto,
            color=color, fontsize=7.2, fontfamily="monospace",
            fontweight="bold", ha="left", va="center",
            zorder=zorder + 1,
            path_effects=[
                pe.withStroke(linewidth=2.5, foreground=COLORS["bg_deep"])
            ],
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
        color=COLORS["plano"], zorder=1, alpha=0.9,
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
        corners_world + 0.04, closed=True,
        facecolor="#0d1424", edgecolor="none",
        zorder=4, alpha=0.6,
    ))
    # Bloque
    ax.add_patch(plt.Polygon(
        corners_world, closed=True,
        facecolor=COLORS["bloque"],
        edgecolor=COLORS["bloque_borde"],
        linewidth=2.0, zorder=5,
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
        linewidth=2.0, zorder=5,
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

    Vectores sobre m1: peso (vertical), normal (⊥ al plano),
                       fricción (paralela al plano), tensión (↑ cuerda).
    Vectores sobre m2: peso (↓), tensión (↑).
    """
    # ── Referencia de escala: el mayor valor de fuerza del sistema ────────────
    fuerzas_ref = max(res.F_paralela, res.F_normal, res.P2,
                      res.tension, 1.0)

    def lon(f: float) -> float:
        return _normalizar_longitud(f, fuerzas_ref)

    # ── Centro geométrico del bloque 1 ────────────────────────────────────────
    centro1_local = np.array([0, bl_size / 2])
    centro1 = (R @ centro1_local) + np.array([cx1, cy1])

    # Vectores unitarios
    dir_paralela  = np.array([ np.cos(theta),  np.sin(theta)])   # cuesta arriba
    dir_normal    = np.array([-np.sin(theta),  np.cos(theta)])   # ⊥ al plano
    dir_vertical  = np.array([0, -1])                            # hacia abajo

    # ── PESO de m1 (vertical ↓) ───────────────────────────────────────────────
    L_peso1 = lon(res.F_paralela)   # usamos F_paralela como proxy visual del peso m1g
    _vector(ax,
            centro1[0], centro1[1],
            dir_vertical[0] * L_peso1, dir_vertical[1] * L_peso1,
            color=COLORS["peso"],
            label="m₁g", valor=res.F_paralela / np.sin(theta) if np.sin(theta) > 0.01 else res.P2,
            lw=2.0, offset_label=(-0.55, -0.1), zorder=10)

    # ── NORMAL a m1 (⊥ al plano ↑) ───────────────────────────────────────────
    L_normal = lon(res.F_normal)
    _vector(ax,
            centro1[0], centro1[1],
            dir_normal[0] * L_normal, dir_normal[1] * L_normal,
            color=COLORS["normal"],
            label="N", valor=res.F_normal,
            lw=2.0, offset_label=(0.06, 0.06), zorder=10)

    # ── FRICCIÓN sobre m1 (paralela al plano, opuesta al movimiento) ──────────
    if res.F_friccion > 0.01:
        # Dirección según el estado del sistema
        if res.estado == "m2_baja":
            dir_fric = -dir_paralela   # m1 sube → fricción apunta cuesta abajo
        else:
            dir_fric =  dir_paralela   # m1 baja → fricción apunta cuesta arriba

        L_fric = lon(res.F_friccion)
        origen_fric = (R @ np.array([0, 0])) + np.array([cx1, cy1])
        _vector(ax,
                origen_fric[0], origen_fric[1],
                dir_fric[0] * L_fric, dir_fric[1] * L_fric,
                color=COLORS["friccion"],
                label="Ff", valor=res.F_friccion,
                lw=2.0, offset_label=(0.06, -0.18), zorder=10)

    # ── TENSIÓN sobre m1 (hacia la polea, cuesta arriba) ─────────────────────
    top_b1 = (R @ np.array([0, bl_size])) + np.array([cx1, cy1])
    L_t1 = lon(res.tension)
    _vector(ax,
            top_b1[0], top_b1[1],
            dir_paralela[0] * L_t1, dir_paralela[1] * L_t1,
            color=COLORS["tension"],
            label="T", valor=res.tension,
            lw=2.0, offset_label=(0.06, 0.06), zorder=10)

    # ── PESO de m2 (↓) ────────────────────────────────────────────────────────
    cx2 = b2x + 0.275
    cy2_top = b2y + 0.55
    L_peso2 = lon(res.P2)
    _vector(ax,
            cx2, b2y,
            0, -L_peso2,
            color=COLORS["peso"],
            label="m₂g", valor=res.P2,
            lw=2.0, offset_label=(0.06, -0.10), zorder=10)

    # ── TENSIÓN sobre m2 (↑) ─────────────────────────────────────────────────
    L_t2 = lon(res.tension)
    _vector(ax,
            cx2, cy2_top,
            0, L_t2,
            color=COLORS["tension"],
            label="T", valor=res.tension,
            lw=2.0, offset_label=(0.06, 0.06), zorder=10)


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


def _dibujar_leyenda(ax, tiene_friccion: bool) -> None:
    """Dibuja la leyenda completa de vectores en la esquina inferior derecha."""
    entradas = [
        mpatches.Patch(color=COLORS["peso"],    label="Peso  (m·g)"),
        mpatches.Patch(color=COLORS["normal"],  label="Normal  (N)"),
        mpatches.Patch(color=COLORS["tension"], label="Tensión  (T)"),
    ]
    if tiene_friccion:
        entradas.append(
            mpatches.Patch(color=COLORS["friccion"], label="Fricción  (Ff)")
        )
    entradas.append(
        mpatches.Patch(color=COLORS["desplaz"],
                       label="Desplazamiento",
                       linestyle="--")
    )

    leg = ax.legend(
        handles=entradas,
        loc="lower left",
        facecolor="#111827",
        edgecolor="#334155",
        labelcolor=COLORS["texto"],
        fontsize=7.8,
        prop={"family": "monospace"},
        framealpha=0.92,
        borderpad=0.7,
    )
    leg.set_zorder(20)


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

    ax.text(5, 7.55, texto,
            color=color, fontsize=9.5, ha="center", va="center",
            fontfamily="monospace", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.45",
                      facecolor="#0d1424",
                      edgecolor=color,
                      linewidth=1.8,
                      alpha=0.95),
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
    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor(COLORS["bg_deep"])
    ax.set_facecolor(COLORS["bg_deep"])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.2)
    ax.set_aspect("equal")
    ax.axis("off")

    theta   = np.radians(theta_deg)
    base_x  = 0.6
    base_y  = 0.8
    L       = 5.5
    bl_size = 0.58
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

    # Indicadores de dirección de desplazamiento
    _dibujar_desplazamiento(ax, cx1, cy1, R, bl_size, theta, b2x, b2y, res.estado)

    # Panel de estado y aceleración
    _dibujar_panel_estado(ax, res.estado, res)

    # Leyenda
    _dibujar_leyenda(ax, tiene_friccion=res.F_friccion > 0.01)

    fig.tight_layout(pad=0.3)
    return fig