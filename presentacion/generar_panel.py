"""
Construye presentacion/panel.html: toma panel_plantilla.html y le incrusta las
mediciones reales (para que la página funcione sola, sin servidor y sin internet).

    python presentacion/generar_panel.py
"""
import csv
import json
import os
from datetime import datetime

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, "..", "medicion", "datos")

# Mediciones que se muestran en "Lo que medimos": (persona, modo, etiqueta)
GPU = [
    ("felipe", "gpu_turbo", "GPU GTX 1650 de Felipe atacando con hashcat"),
]
MEDICIONES = [
    ("alejandra", "silencio", "CPU del portátil de Alejandra, modo Silencio"),
    ("felipe", "turbo", "CPU del portátil de Felipe, modo Turbo"),
]

COLUMNAS = {
    "T": ["CPU Entera [°C]", "CPU Package [°C]", "CPU (Tctl/Tdie) [°C]"],
    "P": ["Potencia total de CPU [W]", "CPU Package Power [W]"],
    "f": ["Relojes efectivos núcleo (avg) [MHz]", "Core Effective Clocks (avg) [MHz]"],
    "ft": ["Desaceleración térmica del núcleo (avg) [Yes/No]", "Core Thermal Throttling (avg) [Yes/No]"],
    "fan": ["CPU [RPM]"],
    "fp": ["Límite de potencia del paquete / anillo excedido [Yes/No]", "Package/Ring Power Limit Exceeded [Yes/No]"],
}


def hora_hwinfo(fecha, hora):
    d, m, a = fecha.split(".")
    h, mi, s = hora.split(":")
    seg, _, ms = s.partition(".")
    return datetime(int(a), int(m), int(d), int(h), int(mi), int(seg), int(ms.ljust(6, "0")[:6]))


def numero(x):
    if x in ("Sí", "Si", "Yes"):
        return 1.0
    if x == "No":
        return 0.0
    try:
        return float(x)
    except ValueError:
        return None


def leer(quien, modo, etiqueta):
    bm = list(csv.DictReader(open(os.path.join(DATOS, f"{quien}_{modo}_benchmark.csv"), encoding="utf-8")))
    inicio = datetime.fromisoformat(bm[0]["hora"])
    bt = np.array([float(r["t_s"]) for r in bm])
    br = np.array([float(r["hashes_por_s"]) for r in bm])
    fin = max(float(r["t_s"]) for r in bm if r["fase"] == "carga")
    filas = list(csv.reader(open(os.path.join(DATOS, f"{quien}_{modo}_hwinfo.csv"),
                                 encoding="utf-8-sig", errors="replace")))
    enc = filas[0]
    idx = {k: next((enc.index(n) for n in v if n in enc), None) for k, v in COLUMNAS.items()}
    serie = []
    for r in filas[1:]:
        if not r or not r[0][:1].isdigit():
            continue
        t = (hora_hwinfo(r[0], r[1]) - inicio).total_seconds()
        if t < -20 or t > bt.max():
            continue
        g = lambda k: numero(r[idx[k]]) if idx[k] is not None else None
        tasa = float(np.interp(t, bt[1:], br[1:])) if 0 < t <= fin else 0.0
        serie.append([round(t, 1), g("T"), g("P"), round(g("f") or 0), int(g("ft") or 0), round(tasa), g("fan"), int(g("fp") or 0)])
    return {"etiqueta": etiqueta, "fin_carga": fin, "serie": serie}


def leer_gpu(quien, modo, etiqueta):
    """El CSV de gpu_benchmark.py ya trae temperatura, potencia, velocidad y frenos."""
    filas = list(csv.DictReader(open(os.path.join(DATOS, f"{quien}_{modo}_benchmark.csv"), encoding="utf-8")))
    fin = max(float(r["t_s"]) for r in filas if r["fase"] == "carga")
    serie = []
    for r in filas:
        g = lambda k: numero(r[k]) if r.get(k, "") != "" else None
        serie.append([round(float(r["t_s"]), 1), g("temp_C"), g("potencia_W"), round(g("freq_MHz") or 0),
                      int(g("freno_termico") or 0), round(g("hashes_por_s") or 0), None, int(g("freno_potencia") or 0)])
    return {"etiqueta": etiqueta, "fin_carga": fin, "serie": serie}


def main():
    medidas = {f"{q}_{m}": leer_gpu(q, m, e) for q, m, e in GPU}
    medidas.update({f"{q}_{m}": leer(q, m, e) for q, m, e in MEDICIONES})
    plantilla = open(os.path.join(AQUI, "panel_plantilla.html"), encoding="utf-8").read()
    html = plantilla.replace("__MEDIDAS__", json.dumps(medidas, separators=(",", ":")))
    salida = os.path.join(AQUI, "panel.html")
    open(salida, "w", encoding="utf-8").write(html)
    print(f"Listo: {salida} ({len(html) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
