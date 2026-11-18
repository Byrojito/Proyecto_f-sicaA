"""
Pruebas de la física: cada una comprueba una propiedad que debe cumplirse por la física
o por el método numérico, independientemente de los datos medidos.
"""

import numpy as np
import pytest

from fisica import (C_TH, P_MAX, R_BUENO, R_MALO, T_AMB, F_sin_frenado, T_analitica, T_equilibrio,
                    T_equilibrio_frenado, ataque, biseccion, capacitancia_efectiva, cop_carnot,
                    energia_bit, euler, factor_euler, potencia, regla_frenado, simular, tamaño_alfabeto,
                    tau_efectivo, VEL_HASH)


# ---------- Balance de energía y Euler ----------

@pytest.mark.parametrize("R", [R_BUENO, R_MALO])
def test_euler_sigue_la_solucion_analitica(R):
    t, T = euler(F_sin_frenado(R), T_AMB, 1.0, 600.0)
    assert np.max(np.abs(T - T_analitica(t, R))) < 0.5      # menos de medio grado


def test_euler_es_de_orden_uno():
    tau = R_MALO * C_TH
    pasos = tau * np.logspace(-3, np.log10(0.5), 12)
    errores = []
    for h in pasos:
        t, T = euler(F_sin_frenado(R_MALO), T_AMB, h, 5 * tau)
        errores.append(np.max(np.abs(T - T_analitica(t, R_MALO))))
    pendiente, _ = np.polyfit(np.log10(pasos), np.log10(errores), 1)
    assert pendiente == pytest.approx(1.0, abs=0.1)


def test_euler_estable_oscila_diverge():
    tau = R_MALO * C_TH
    F = F_sin_frenado(R_MALO)
    T_eq = T_equilibrio(P_MAX, R_MALO)
    _, T_est = euler(F, T_AMB, 0.5 * tau, 30 * tau)
    _, T_osc = euler(F, T_AMB, 1.5 * tau, 30 * tau)
    _, T_div = euler(F, T_AMB, 2.2 * tau, 30 * tau)
    assert np.all(np.diff(T_est) >= 0) and T_est[-1] == pytest.approx(T_eq, abs=1e-3)   # sube sin pasarse
    assert np.any(T_osc > T_eq + 1) and T_osc[-1] == pytest.approx(T_eq, abs=1e-3)      # se pasa y vuelve
    assert abs(T_div[-1] - T_eq) > 1e3                                                   # explota
    assert factor_euler(0.5 * tau, tau) == pytest.approx(0.5)
    assert factor_euler(2.2 * tau, tau) < -1


def test_equilibrio_no_depende_de_la_capacidad():
    for C in [100, 600, 5000]:
        T_final = T_analitica(np.array([1e7]), R_BUENO, C_th=C)[0]
        assert T_final == pytest.approx(T_AMB + P_MAX * R_BUENO)


def test_tau_es_el_63_por_ciento():
    tau = R_BUENO * C_TH
    subida = (T_analitica(np.array([tau]), R_BUENO)[0] - T_AMB) / (P_MAX * R_BUENO)
    assert subida == pytest.approx(1 - np.exp(-1))


# ---------- Potencia: P = C·V²·f ----------

def test_potencia_maxima_y_monotona():
    assert potencia(1.0) == pytest.approx(P_MAX)
    phis = np.linspace(0.1, 1, 50)
    assert np.all(np.diff(potencia(phis)) > 0)
    assert potencia(0.8) / P_MAX < 0.8        # baja más que la velocidad (por el voltaje)


def test_capacitancia_recupera_C_conocida():
    rng = np.random.default_rng(0)
    V = rng.uniform(0.8, 1.1, 200)
    f = rng.uniform(2000, 3600, 200)             # MHz
    C_real = 12e-9
    P = C_real * V**2 * f * 1e6
    C, R2 = capacitancia_efectiva(P, V, f)
    assert C == pytest.approx(C_real) and R2 == pytest.approx(1.0)


# ---------- Frenado ----------

def test_biseccion():
    assert biseccion(lambda x: x**2 - 2, 0, 2) == pytest.approx(np.sqrt(2), abs=1e-8)


@pytest.mark.parametrize("R, P_tope", [(R_BUENO, P_MAX), (R_MALO, P_MAX), (R_BUENO, 300.0)])
def test_simulacion_llega_al_equilibrio_de_biseccion(R, P_tope):
    _, T, _ = simular(R, P_tope=P_tope, dt=0.5, t_final=1500)
    assert T[-1] == pytest.approx(T_equilibrio_frenado(R, P_tope), abs=1e-6)


def test_freno_respeta_sus_limites():
    phi = regla_frenado()
    assert phi(20) == 1.0 and phi(200) == 0.5
    assert regla_frenado(control="ninguno")(200) == 1.0
    assert potencia(regla_frenado(P_tope=300.0)(20)) == pytest.approx(300.0, abs=1e-6)


def test_freno_acelera_la_respuesta():
    assert tau_efectivo(R_MALO) < R_MALO * C_TH / 10


# ---------- Ataque ----------

def test_cada_caracter_multiplica_el_tiempo_por_95():
    t7 = ataque(7, VEL_HASH["NTLM"], R_BUENO)["t"]
    t8 = ataque(8, VEL_HASH["NTLM"], R_BUENO)["t"]
    assert t8 / t7 == pytest.approx(95, rel=0.02)


def test_extrapolar_en_equilibrio_no_cambia_el_resultado():
    rapido = ataque(8, VEL_HASH["NTLM"], R_MALO, dt=0.5)
    completo = ataque(8, VEL_HASH["NTLM"], R_MALO, dt=0.5, n_tau=1e6)
    assert rapido["t"] == pytest.approx(completo["t"], rel=1e-9)


def test_frenar_gasta_menos_energia():
    bueno = ataque(8, VEL_HASH["NTLM"], R_BUENO)
    malo = ataque(8, VEL_HASH["NTLM"], R_MALO)
    assert malo["t"] > bueno["t"] and malo["E"] < bueno["E"]


def test_alfabeto():
    assert tamaño_alfabeto("abc") == 26
    assert tamaño_alfabeto("Uniandes2026") == 62
    assert tamaño_alfabeto("a-B1") == 95


# ---------- Segunda ley ----------

def test_carnot():
    assert cop_carnot(25, 35) == pytest.approx(29.8, abs=0.1)


def test_landauer():
    assert energia_bit(300) == pytest.approx(2.87e-21, rel=0.01)
