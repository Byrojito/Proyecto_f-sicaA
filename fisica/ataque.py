"""
Ataque de fuerza bruta acoplado al modelo térmico (secciones 10 y 11 del notebook).

Tres ecuaciones que se integran con Euler en el mismo bucle:

    dT/dt = [P(φ(T)) − (T − T_amb)/R_th] / C_th
    dn/dt = r_máx · φ(T)            (intentos)
    dE/dt = P(φ(T))                 (energía eléctrica)

El ataque termina cuando n = 95^N. Después de n_tau·τ el chip ya está en equilibrio
(queda e^(−20) ≈ 2×10⁻⁹ del transitorio), así que el resto se completa a velocidad
constante.
"""

import numpy as np

from .frenado import regla_frenado
from .parametros import ALFABETO, AÑO, C_TH, COP, P_MAX, T_AMB, TARIFA
from .potencia import potencia


def ataque(N, r_max, R_th, P_tope=P_MAX, control="proporcional", dt=0.1, n_tau=20, alfabeto=ALFABETO):
    """Tiempo (s) y energía eléctrica (J) para probar las alfabeto^N combinaciones.

    Devuelve un dict con t, E y la frecuencia relativa φ al final.
    """
    total = float(alfabeto) ** N
    phi = regla_frenado(P_tope, control)
    t_sim = n_tau * R_th * C_TH
    t = n = E = 0.0
    T = T_AMB
    while t < t_sim:
        ph = phi(T)
        r, P = r_max * ph, potencia(ph)
        if n + dt * r >= total:                 # el ataque termina dentro de este paso
            fraccion = (total - n) / r
            return dict(t=t + fraccion, E=E + P * fraccion, phi=ph)
        T += dt * (P - (T - T_AMB) / R_th) / C_TH
        n += dt * r
        E += dt * P
        t += dt
    ph = phi(T)                                 # equilibrio: el resto a velocidad constante
    r, P = r_max * ph, potencia(ph)
    t_resto = (total - n) / r
    return dict(t=t + t_resto, E=E + P * t_resto, phi=ph)


def energia_con_aire(E, cop=COP):
    """Energía total incluyendo el aire acondicionado: E·(1 + 1/COP)."""
    return E * (1 + 1 / cop)


def cop_carnot(T_frio_C, T_caliente_C):
    """COP máximo de un refrigerador (Carnot): T_c / (T_h − T_c), con T en kelvin."""
    T_c = T_frio_C + 273.15
    return T_c / (T_caliente_C - T_frio_C)


def costo_pesos(E, cop=COP, tarifa=TARIFA):
    """Costo en pesos de la energía E (J), con aire acondicionado incluido."""
    return energia_con_aire(E, cop) / 3.6e6 * tarifa


def tamaño_alfabeto(texto):
    """Tamaño del alfabeto que usa una contraseña (minúsculas, mayúsculas, dígitos, símbolos)."""
    n = 0
    if any(c.islower() for c in texto): n += 26
    if any(c.isupper() for c in texto): n += 26
    if any(c.isdigit() for c in texto): n += 10
    if any(not c.isalnum() for c in texto): n += 33
    return n


def bits(N, alfabeto=ALFABETO):
    """Tamaño del espacio de búsqueda en bits: N·log₂(alfabeto)."""
    return N * np.log2(alfabeto)


def tiempo_legible(s):
    if s < 60: return f"{s:.1f} s"
    if s < 3600: return f"{s / 60:.1f} min"
    if s < 86400: return f"{s / 3600:.1f} h"
    if s < AÑO: return f"{s / 86400:.1f} días"
    if s < 1e4 * AÑO: return f"{s / AÑO:.0f} años"
    return f"{s / AÑO:.1e} años"


def pesos(cop):
    if cop < 1: return "menos de $1"
    if cop < 1e6: return f"${cop:,.0f}".replace(",", ".")
    if cop < 1e12: return f"${cop / 1e6:,.1f} millones".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"${cop:.1e}"
