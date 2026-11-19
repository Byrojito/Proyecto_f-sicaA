"""
Lectura de las mediciones (sección 8 del notebook): benchmark.py y HWiNFO64.

`resumen` reúne en un solo dict lo que el notebook calcula para cada medición:
promedios de la carga estable, R_th efectiva y τ de la curva de enfriamiento.
"""

import csv
import os
from datetime import datetime

import numpy as np
from scipy.optimize import curve_fit

from .termico import enfriamiento, resistencia_termica

DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "medicion", "datos")

# Nombres de columna posibles (HWiNFO en español o inglés, Intel o AMD)
COLUMNAS_HWINFO = {
    "T": ["CPU Entera [°C]", "CPU Package [°C]", "CPU (Tctl/Tdie) [°C]"],
    "P": ["Potencia total de CPU [W]", "CPU Package Power [W]"],
    "f": ["Relojes efectivos núcleo (avg) [MHz]", "Core Effective Clocks (avg) [MHz]"],
    "V": ["Core VIDs (avg) [V]", "VID núcleo (avg) [V]", "CPU Core Voltage (SVI2 TFN) [V]"],
    "ventilador": ["CPU [RPM]"],
    "freno_termico": ["Desaceleración térmica del núcleo (avg) [Yes/No]", "Core Thermal Throttling (avg) [Yes/No]"],
}


def leer_benchmark(ruta):
    """CSV de benchmark.py: hora, t_s, fase, hashes_total, hashes_por_s, ..."""
    with open(ruta, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    return {
        "inicio": datetime.fromisoformat(filas[0]["hora"]),
        "t": np.array([float(r["t_s"]) for r in filas]),
        "tasa": np.array([float(r["hashes_por_s"]) for r in filas]),
        "carga": np.array([r["fase"] == "carga" for r in filas]),
    }


def _hora_hwinfo(fecha, hora):
    # HWiNFO escribe la fecha como 15.11.2026 y la hora como 18:2:44.196
    d, m, a = fecha.split(".")
    h, mi, s = hora.split(":")
    seg, _, ms = s.partition(".")
    return datetime(int(a), int(m), int(d), int(h), int(mi), int(seg), int(ms.ljust(6, "0")[:6]))


def _numero(texto):
    if texto in ("Sí", "Si", "Yes"): return 1.0
    if texto == "No": return 0.0
    return float(texto)


def leer_hwinfo(ruta, inicio):
    """CSV de HWiNFO con el tiempo en segundos medido desde el inicio del benchmark."""
    with open(ruta, encoding="utf-8-sig", errors="replace") as f:
        filas = list(csv.reader(f))
    encabezado = filas[0]
    datos = [r for r in filas[1:] if r and r[0][:1].isdigit()]   # descarta filas de resumen
    salida = {"t": np.array([(_hora_hwinfo(r[0], r[1]) - inicio).total_seconds() for r in datos])}
    for clave, nombres in COLUMNAS_HWINFO.items():
        i = next((encabezado.index(n) for n in nombres if n in encabezado), None)
        salida[clave] = np.array([_numero(r[i]) for r in datos]) if i is not None else None
    return salida


def ajustar_tau(t, T):
    """Ajusta la ley de enfriamiento de Newton a una curva. Devuelve (T_∞, A, τ, error de τ)."""
    T_suave = np.array([T[max(0, i - 1):i + 2].min() for i in range(len(T))])   # quita picos de un registro
    (T_inf, A, tau), cov = curve_fit(enfriamiento, t, T_suave, p0=[50, 10, 30])
    return T_inf, A, tau, np.sqrt(cov[2, 2])


def resumen(quien, modo, datos=DATOS):
    """Promedios de la carga estable, R_th efectiva y τ del enfriamiento para una medición."""
    b = leer_benchmark(os.path.join(datos, f"{quien}_{modo}_benchmark.csv"))
    h = leer_hwinfo(os.path.join(datos, f"{quien}_{modo}_hwinfo.csv"), b["inicio"])
    fin = b["t"][b["carga"]].max()
    c = (h["t"] > 60) & (h["t"] < fin)
    rep = h["t"] > b["t"].max() - 100
    r = b["tasa"][b["carga"] & (b["t"] > 60)].mean()
    P, T = h["P"][c].mean(), h["T"][c].mean()
    i0 = np.argmax((h["t"] > fin) & (h["P"] < 15))       # primera muestra ya sin carga
    _, _, tau, err_tau = ajustar_tau(h["t"][i0:] - h["t"][i0], h["T"][i0:])
    return {
        "r": r, "P": P, "T": T, "f": h["f"][c].mean(), "V": h["V"][c].mean(),
        "ventilador": h["ventilador"][c].mean(), "E_hash": P / r,
        "R_th": resistencia_termica(T, P, np.median(h["T"][rep]), np.median(h["P"][rep])),
        "tau": tau, "err_tau": err_tau,
        "muestras": (h["P"][c], h["V"][c], h["f"][c]),
        "hw": h,
    }
