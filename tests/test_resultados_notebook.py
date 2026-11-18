"""
Pruebas de reproducción: el paquete `fisica` debe dar los mismos números que imprime
proyecto.ipynb. Si alguien cambia el notebook o el paquete y dejan de coincidir, falla.
"""

import numpy as np
import pytest

from fisica import (A_DVFS, COP, P_MAX, R_BUENO, R_MALO, TARIFA, VEL_HASH, ataque, capacitancia_efectiva,
                    costo_pesos, energia_con_aire, simular, tau_efectivo)
from fisica.mediciones import resumen
from fisica.potencia import ajuste_dvfs

ESCENARIOS = {
    "A": dict(R_th=R_BUENO, P_tope=P_MAX),
    "B": dict(R_th=R_MALO, P_tope=P_MAX),
    "C": dict(R_th=R_BUENO, P_tope=300.0),
}


@pytest.fixture(scope="module")
def felipe():
    return {m: resumen("felipe", m) for m in ["silencio", "rendimiento", "turbo"]}


@pytest.fixture(scope="module")
def alejandra():
    return {m: resumen("alejandra", m) for m in ["silencio", "rendimiento"]}


# ---------- Sección 8: mediciones ----------

def test_medicion_felipe_silencio(felipe):
    x = felipe["silencio"]
    assert x["T"] == pytest.approx(76.9, abs=0.05)
    assert x["P"] == pytest.approx(28.9, abs=0.05)
    assert x["R_th"] == pytest.approx(1.22, abs=0.005)
    assert x["tau"] == pytest.approx(44, abs=0.5)
    assert x["E_hash"] * 1e6 == pytest.approx(9.08, abs=0.005)


def test_turbo_mas_rapido_pero_mas_caro(felipe):
    s, t = felipe["silencio"], felipe["turbo"]
    assert 100 * (t["r"] / s["r"] - 1) == pytest.approx(22, abs=0.5)
    assert 100 * (t["E_hash"] / s["E_hash"] - 1) == pytest.approx(30, abs=0.5)


def test_capacitancia_efectiva_felipe(felipe):
    P = np.concatenate([x["muestras"][0] for x in felipe.values()])
    V = np.concatenate([x["muestras"][1] for x in felipe.values()])
    f = np.concatenate([x["muestras"][2] for x in felipe.values()])
    C, R2 = capacitancia_efectiva(P, V, f)
    assert C * 1e9 == pytest.approx(12.0, abs=0.05)
    assert R2 == pytest.approx(0.986, abs=0.0005)


def test_capacitancia_efectiva_alejandra(alejandra):
    P = np.concatenate([x["muestras"][0] for x in alejandra.values()])
    V = np.concatenate([x["muestras"][1] for x in alejandra.values()])
    f = np.concatenate([x["muestras"][2] for x in alejandra.values()])
    C, _ = capacitancia_efectiva(P, V, f)
    assert C * 1e9 == pytest.approx(9.5, abs=0.15)


def test_alejandra_mismo_P_mas_ventilador_menos_T(alejandra):
    s, r = alejandra["silencio"], alejandra["rendimiento"]
    assert s["P"] == pytest.approx(r["P"], abs=0.2)
    assert r["ventilador"] > s["ventilador"] and r["T"] < s["T"]


def test_a_dvfs_sale_de_los_datos(felipe):
    _, _, a = ajuste_dvfs([x["f"] for x in felipe.values()], [x["V"] for x in felipe.values()])
    assert a == pytest.approx(A_DVFS, abs=0.0005)


# ---------- Sección 9: frenado ----------

def test_escenarios_de_frenado():
    esperado = {"A": (70.0, 1.000), "B": (84.2, 0.875), "C": (55.0, 0.841)}
    for nombre, esc in ESCENARIOS.items():
        _, T, phi = simular(**esc, dt=0.5, t_final=600)
        assert T[-1] == pytest.approx(esperado[nombre][0], abs=0.05)
        assert phi[-1] == pytest.approx(esperado[nombre][1], abs=0.0005)


def test_tau_efectivo():
    assert tau_efectivo(R_MALO) == pytest.approx(6.5, abs=0.05)


# ---------- Secciones 10 y 11: ataque y costo (tabla 10.3) ----------

@pytest.mark.parametrize("esc, horas, kwh", [("A", 6.1, 3.69), ("B", 7.0, 3.08), ("C", 7.3, 2.92)])
def test_tabla_8_caracteres_ntlm(esc, horas, kwh):
    res = ataque(8, VEL_HASH["NTLM"], **ESCENARIOS[esc])
    assert res["t"] / 3600 == pytest.approx(horas, abs=0.05)
    assert energia_con_aire(res["E"], COP) / 3.6e6 == pytest.approx(kwh, abs=0.005)


def test_costo_8_caracteres():
    res = ataque(8, VEL_HASH["NTLM"], **ESCENARIOS["A"])
    assert costo_pesos(res["E"], COP, TARIFA) == pytest.approx(3183, abs=1)
