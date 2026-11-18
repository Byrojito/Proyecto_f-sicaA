"""
Balance de energía del chip y método de Euler (secciones 2 a 7 del notebook).

Ecuación central (primera ley con conducción de Fourier):

    C_th · dT/dt = P − (T − T_amb) / R_th

Con P constante tiene solución exacta (carga exponencial, como un circuito RC):

    T(t) = T_amb + P · R_th · (1 − e^(−t/τ)),     τ = R_th · C_th
"""

import numpy as np

from .parametros import C_TH, P_MAX, T_AMB


def euler(F, T0, dt, t_final):
    """Integra dT/dt = F(t, T) con el método de Euler explícito.

    T_{k+1} = T_k + Δt · F(t_k, T_k)

    Es de orden 1: el error global es proporcional a Δt. Para la ecuación lineal del
    chip, cada paso multiplica la distancia al equilibrio por (1 − Δt/τ), así que oscila
    si Δt > τ y diverge si Δt > 2τ.

    Devuelve los arreglos t y T, con t_final/Δt + 1 puntos.
    """
    n = int(round(t_final / dt))
    t = np.arange(n + 1) * dt
    T = np.empty(n + 1)
    T[0] = T0
    for k in range(n):
        T[k + 1] = T[k] + dt * F(t[k], T[k])
    return t, T


def F_sin_frenado(R_th, P=P_MAX, C_th=C_TH, T_amb=T_AMB):
    """Lado derecho del balance de energía con potencia constante.

    F(t, T) = [P − (T − T_amb)/R_th] / C_th
    """
    def F(t, T):
        return (P - (T - T_amb) / R_th) / C_th
    return F


def T_analitica(t, R_th, P=P_MAX, C_th=C_TH, T_amb=T_AMB):
    """Solución exacta con P constante y T(0) = T_amb.

    T(t) = T_amb + P·R_th·(1 − e^(−t/τ)),  τ = R_th·C_th
    """
    tau = R_th * C_th
    return T_amb + P * R_th * (1 - np.exp(-t / tau))


def T_equilibrio(P, R_th, T_amb=T_AMB):
    """Temperatura final (dT/dt = 0): T_eq = T_amb + P·R_th. No depende de C_th."""
    return T_amb + P * R_th


def factor_euler(dt, tau):
    """Factor por paso de Euler en la ecuación lineal: u_{k+1} = (1 − Δt/τ)·u_k.

    0 < factor < 1: estable · −1 < factor < 0: oscila · factor < −1: diverge.
    """
    return 1 - dt / tau


def enfriamiento(t, T_inf, A, tau):
    """Ley de enfriamiento de Newton (P = 0): T(t) = T_∞ + A·e^(−t/τ)."""
    return T_inf + A * np.exp(-t / tau)


def calentamiento(t, T_inf, A, tau):
    """Carga exponencial (P constante): T(t) = T_∞ − A·e^(−t/τ)."""
    return T_inf - A * np.exp(-t / tau)


def resistencia_termica(T_carga, P_carga, T_reposo, P_reposo):
    """R_th efectiva a partir de dos estados estables: R_th = ΔT / ΔP (K/W)."""
    return (T_carga - T_reposo) / (P_carga - P_reposo)
