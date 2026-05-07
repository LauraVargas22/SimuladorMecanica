"""
Cálculo de todas las fuerzas y magnitudes físicas del sistema
de dos cuerpos conectados mediante polea ideal y plano inclinado.
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class SystemResult:
    """Contenedor de resultados del cálculo físico."""
    F_paralela:  float   # Componente del peso de m1 paralela al plano [N]
    F_normal:    float   # Fuerza normal sobre m1 [N]
    F_friccion:  float   # Fuerza de fricción (magnitud) [N]
    P2:          float   # Peso de m2 [N]
    F_neta:      float   # Fuerza neta del sistema [N]
    aceleracion: float   # Aceleración del sistema [m/s²]
    tension:     float   # Tensión en la cuerda [N]
    estado:      str     # "equilibrio" | "m2_baja" | "m1_baja"
    theta_rad:   float   # Ángulo en radianes (uso interno)


def calcular_fuerzas(
    m1: float,
    m2: float,
    theta_deg: float,
    g: float,
    mu: float,
    friccion_activa: bool,
) -> SystemResult:
    """
    Aplica las leyes de Newton al sistema de dos cuerpos.

    Parámetros
    ----------
    m1              : masa del bloque en el plano inclinado [kg]
    m2              : masa del bloque suspendido [kg]
    theta_deg       : ángulo del plano inclinado [°]
    g               : aceleración gravitacional [m/s²]
    mu              : coeficiente de fricción cinética
    friccion_activa : activar o desactivar la fricción

    Retorna
    -------
    SystemResult con todas las magnitudes calculadas.
    """
    theta = np.radians(theta_deg)

    # ── Fuerzas sobre m1 ──────────────────────────────────────────────────────
    F_paralela       = m1 * g * np.sin(theta)   # componente paralela al plano
    F_normal         = m1 * g * np.cos(theta)   # fuerza normal
    F_friccion_max   = mu * F_normal if friccion_activa else 0.0

    # ── Fuerza motriz de m2 ───────────────────────────────────────────────────
    P2 = m2 * g

    # ── Fuerza neta sin considerar fricción (signo: + → m2 baja) ─────────────
    F_sin_friccion = P2 - F_paralela

    # ── Determinación de estado y fuerza neta real ────────────────────────────
    if abs(F_sin_friccion) <= F_friccion_max:
        # Fricción estática suficiente → equilibrio
        estado      = "equilibrio"
        F_friccion  = F_sin_friccion   # fricción estática iguala el desequilibrio
        F_neta      = 0.0
        aceleracion = 0.0

    elif F_sin_friccion > 0:
        # m2 desciende, m1 asciende → fricción actúa cuesta abajo sobre m1
        estado      = "m2_baja"
        F_friccion  = F_friccion_max
        F_neta      = P2 - F_paralela - F_friccion
        aceleracion = F_neta / (m1 + m2)

    else:
        # m1 desciende, m2 asciende → fricción actúa cuesta arriba sobre m1
        estado      = "m1_baja"
        F_friccion  = F_friccion_max
        F_neta      = P2 - F_paralela + F_friccion   # (P2 - F_par < 0, +Ff acerca a 0)
        aceleracion = F_neta / (m1 + m2)

    # ── Tensión en la cuerda ──────────────────────────────────────────────────
    if estado == "equilibrio":
        tension = P2
    else:
        tension = m2 * (g - aceleracion)

    return SystemResult(
        F_paralela  = F_paralela,
        F_normal    = F_normal,
        F_friccion  = abs(F_friccion),
        P2          = P2,
        F_neta      = F_neta,
        aceleracion = aceleracion,
        tension     = tension,
        estado      = estado,
        theta_rad   = theta,
    )