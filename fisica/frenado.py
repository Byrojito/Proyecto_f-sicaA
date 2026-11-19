"""
Frenado del chip y sistema no lineal (sección 9 del notebook).

El chip obedece al freno más estricto:

    φ = mín(φ_tope, φ_térmico(T)),    φ_térmico = 1 − K·(T − T_lím)  (entre φ_mín y 1)

Con eso P depende de T y el balance de energía deja de ser lineal:

    C_th · dT/dt = P(φ(T)) − (T − T_amb)/R_th

No tiene solución exacta sencilla, así que se integra con Euler. El equilibrio se
verifica aparte resolviendo P(φ(T)) = (T − T_amb)/R_th por bisección.
"""

import numpy as np

from .parametros import C_TH, K_FRENO, P_MAX, PHI_MIN, T_AMB, T_LIM
from .potencia import potencia
from .termico import euler


def biseccion(g, izq, der, tol=1e-9):
    """Raíz de g en [izq, der] por bisección. g(izq) y g(der) deben tener signos opuestos."""
    g_izq = g(izq)
    while der - izq > tol:
        medio = (izq + der) / 2
        g_medio = g(medio)
        if (g_medio > 0) == (g_izq > 0):
            izq, g_izq = medio, g_medio
        else:
            der = medio
    return (izq + der) / 2


def phi_por_tope(P_tope, P_max=P_MAX):
    """Frecuencia relativa máxima que permite el tope de potencia: resuelve P(φ) = P_tope."""
    if P_tope >= P_max:
        return 1.0
    return biseccion(lambda p: potencia(p, P_max) - P_tope, 0.0, 1.0)


def regla_frenado(P_tope=P_MAX, control="proporcional", T_lim=T_LIM, k=K_FRENO, phi_min=PHI_MIN):
    """Devuelve la función φ(T) con los dos frenos.

    control: "proporcional" (φ = 1 − k·(T − T_lím)), "on/off" (φ_mín si T > T_lím)
    o cualquier otro valor para no usar freno térmico.
    """
    phi_P = phi_por_tope(P_tope)

    def phi(T):
        if control == "proporcional":
            phi_T = min(1.0, max(phi_min, 1 - k * (T - T_lim)))
        elif control == "on/off":
            phi_T = phi_min if T > T_lim else 1.0
        else:
            phi_T = 1.0
        return min(phi_P, phi_T)

    return phi


def simular(R_th, P_tope=P_MAX, control="proporcional", dt=0.5, t_final=600, C_th=C_TH, T_amb=T_AMB):
    """Integra el sistema no lineal con Euler. Devuelve t, T y φ."""
    phi = regla_frenado(P_tope, control)
    F = lambda t, T: (potencia(phi(T)) - (T - T_amb) / R_th) / C_th
    t, T = euler(F, T_amb, dt, t_final)
    return t, T, np.array([phi(x) for x in T])


def T_equilibrio_frenado(R_th, P_tope=P_MAX, T_amb=T_AMB, T_max=250.0):
    """Temperatura de equilibrio con freno: resuelve P(φ(T)) = (T − T_amb)/R_th por bisección."""
    phi = regla_frenado(P_tope)
    return biseccion(lambda T: potencia(phi(T)) - (T - T_amb) / R_th, T_amb, T_max)


def equilibrio(R_th, T_amb=T_AMB, P_tope=P_MAX):
    """Frecuencia relativa de equilibrio con el freno proporcional."""
    T_eq = T_equilibrio_frenado(R_th, P_tope, T_amb)
    return regla_frenado(P_tope)(T_eq)


def tau_efectivo(R_th, C_th=C_TH, k=K_FRENO, P_tope=P_MAX):
    """Constante de tiempo cerca del equilibrio con freno proporcional (linealización).

    1/τ_ef = (1/R_th + |dP/dT|) / C_th,  con |dP/dT| = k · dP/dφ.
    """
    phi_eq = regla_frenado(P_tope)(T_equilibrio_frenado(R_th, P_tope))
    dP = (potencia(phi_eq + 1e-6) - potencia(phi_eq - 1e-6)) / 2e-6
    return C_th / (1 / R_th + k * dP)
