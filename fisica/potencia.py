"""
Potencia eléctrica del chip (secciones 8.6 y 9.1 del notebook).

Cada ciclo de reloj carga y descarga una capacitancia efectiva C, lo que convierte
C·V² en calor. Con f ciclos por segundo:

    P = C · V² · f

El voltaje baja linealmente con la frecuencia, V/V_máx = a + (1 − a)·φ con φ = f/f_máx,
así que la potencia de la GPU en función de φ queda:

    P(φ) = P_máx · φ · (a + (1 − a)·φ)²
"""

import numpy as np

from .parametros import A_DVFS, P_MAX


def potencia(phi, P_max=P_MAX, a=A_DVFS):
    """Potencia eléctrica (W) con frecuencia relativa φ, incluyendo la bajada de voltaje."""
    return P_max * phi * (a + (1 - a) * phi) ** 2


def energia_por_intento_relativa(phi, a=A_DVFS):
    """Energía por intento relativa al máximo: P/r ∝ V², es decir (a + (1 − a)·φ)²."""
    return (a + (1 - a) * phi) ** 2


def capacitancia_efectiva(P, V, f_MHz):
    """Ajusta P = C·V²·f con una recta por el origen (mínimos cuadrados).

    P en W, V en V, f en MHz (como los da HWiNFO). Devuelve (C en F, R²).
    """
    P = np.asarray(P, dtype=float)
    x = np.asarray(V, dtype=float) ** 2 * np.asarray(f_MHz, dtype=float) * 1e6   # V²·Hz
    C = np.sum(x * P) / np.sum(x ** 2)
    residuo = P - C * x
    R2 = 1 - np.sum(residuo ** 2) / np.sum((P - P.mean()) ** 2)
    return C, R2


def ajuste_dvfs(f_MHz, V):
    """Recta V = V0 + m·f entre los modos medidos y a = V(0)/V(f_máx).

    Devuelve (V0 en V, m en V/MHz, a).
    """
    f_MHz = np.asarray(f_MHz, dtype=float)
    m, V0 = np.polyfit(f_MHz, np.asarray(V, dtype=float), 1)
    a = V0 / (m * f_MHz.max() + V0)
    return V0, m, a
