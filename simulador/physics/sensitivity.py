"""
Análisis de sensibilidad: barrido del ángulo para observar
cómo varían la aceleración y la tensión en todo el rango [0°, 90°].
"""

import numpy as np
from .forces import calcular_fuerzas, SystemResult


def barrer_angulos(
    m1: float,
    m2: float,
    g: float,
    mu: float,
    friccion_activa: bool,
    paso: int = 5,
) -> dict:
    """
    Calcula aceleración y tensión para cada ángulo en [0°, 90°].

    Parámetros
    ----------
    m1, m2          : masas del sistema [kg]
    g               : gravedad [m/s²]
    mu              : coeficiente de fricción
    friccion_activa : activar fricción
    paso            : resolución del barrido en grados

    Retorna
    -------
    dict con claves:
        "angulos"       : ndarray de ángulos
        "aceleraciones" : ndarray de |aceleración| en cada ángulo
        "tensiones"     : ndarray de tensión en cada ángulo
    """
    angulos       = np.arange(0, 91, paso)
    aceleraciones = []
    tensiones     = []

    for ang in angulos:
        r = calcular_fuerzas(m1, m2, float(ang), g, mu, friccion_activa)
        aceleraciones.append(abs(r.aceleracion))
        tensiones.append(r.tension)

    return {
        "angulos":       angulos,
        "aceleraciones": np.array(aceleraciones),
        "tensiones":     np.array(tensiones),
    }