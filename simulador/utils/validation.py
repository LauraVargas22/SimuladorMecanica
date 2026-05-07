"""
Validación de los parámetros de entrada del simulador.
"""


def validar_entradas(m1: float, m2: float, theta: float,
                     g: float, mu: float) -> list[str]:
    """
    Verifica que los parámetros de entrada sean físicamente válidos.

    Parámetros
    ----------
    m1    : masa del bloque en el plano [kg]
    m2    : masa del bloque suspendido [kg]
    theta : ángulo del plano [°]
    g     : gravedad [m/s²]
    mu    : coeficiente de fricción

    Retorna
    -------
    Lista de mensajes de error (vacía si todos los valores son válidos).
    """
    errores: list[str] = []

    if m1 <= 0:
        errores.append("⚠ La masa m₁ debe ser mayor que cero.")
    if m2 <= 0:
        errores.append("⚠ La masa m₂ debe ser mayor que cero.")
    if not (0 <= theta <= 90):
        errores.append("⚠ El ángulo debe estar entre 0° y 90°.")
    if g <= 0:
        errores.append("⚠ La gravedad debe ser mayor que cero.")
    if mu < 0:
        errores.append("⚠ El coeficiente de fricción no puede ser negativo.")

    return errores