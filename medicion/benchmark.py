"""
Medición propia: velocidad de hashes (y temperatura, si se puede) contra el tiempo.

Pone a todos los núcleos del portátil a calcular hashes SHA-256 durante un tiempo
fijo y guarda cada segundo un registro en CSV:

    hora, t_s, fase, hashes_total, hashes_por_s, temp_C, freq_MHz

La columna "hora" (reloj del computador) sirve para unir este CSV con el de un
programa externo de temperatura (HWiNFO en Windows) que registra al mismo tiempo.
Al final, el script deja la CPU en reposo unos minutos (fase "enfriamiento") y
sigue registrando: esa curva de enfriamiento es la forma más limpia de medir tau.

Si el chip se calienta y se frena (throttling), se verá como una caída de
hashes_por_s y de freq_MHz mientras temp_C sube. Con esos datos ajustamos la
constante de tiempo tau = R_th * C_th del modelo del notebook.

Uso (portátil ENCHUFADO, sin otros programas pesados abiertos):

    python medicion/benchmark.py --duracion 900
    python medicion/benchmark.py --duracion 900 --nombre felipe
    python medicion/benchmark.py --duracion 900 --enfriamiento 300 --nombre felipe

Temperatura:
- Linux: se lee automáticamente con psutil (pip install psutil).
- Windows: psutil no da temperatura. Abrir HWiNFO64 (modo "Sensors-only"),
  iniciar el registro a CSV ("Logging start") ANTES de correr este script y
  detenerlo cuando termine. Los dos CSV se unen por la columna "hora".
- macOS: psutil no da temperatura. Se puede usar `sudo powermetrics` en otra
  terminal, o quedarse solo con hashes/s y frecuencia.
"""

import argparse
import csv
import hashlib
import multiprocessing as mp
import os
import platform
import time
from datetime import datetime

try:
    import psutil
except ImportError:  # psutil es opcional
    psutil = None


def trabajador(indice, contadores, parar, lote):
    """Calcula hashes sin parar y suma cada lote a su propio contador."""
    i = indice << 40  # cada proceso recorre un rango distinto de "contraseñas"
    while not parar.is_set():
        for _ in range(lote):
            hashlib.sha256(i.to_bytes(8, "little")).digest()
            i += 1
        contadores[indice] += lote  # solo este proceso escribe en su posición


def leer_temperatura():
    """Temperatura más alta reportada por los sensores de CPU, en °C (o None)."""
    if psutil is None or not hasattr(psutil, "sensors_temperatures"):
        return None
    try:
        sensores = psutil.sensors_temperatures()
    except Exception:
        return None
    lecturas = [s.current for grupo in sensores.values() for s in grupo if s.current]
    return max(lecturas) if lecturas else None


def leer_frecuencia():
    """Frecuencia actual de la CPU en MHz (o None)."""
    if psutil is None:
        return None
    try:
        f = psutil.cpu_freq()
        return f.current if f else None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--duracion", type=float, default=900, help="segundos (por defecto 900 = 15 min)")
    parser.add_argument("--enfriamiento", type=float, default=300,
                        help="segundos registrando en reposo al final (por defecto 300)")
    parser.add_argument("--intervalo", type=float, default=1.0, help="segundos entre registros")
    parser.add_argument("--procesos", type=int, default=os.cpu_count(), help="procesos en paralelo")
    parser.add_argument("--lote", type=int, default=20_000, help="hashes por lote de cada proceso")
    parser.add_argument("--nombre", default=platform.node() or "equipo", help="etiqueta para el archivo")
    args = parser.parse_args()

    carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
    os.makedirs(carpeta, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    salida = os.path.join(carpeta, f"{args.nombre}_{marca}.csv")

    contadores = mp.Array("Q", args.procesos, lock=False)
    parar = mp.Event()
    procesos = [mp.Process(target=trabajador, args=(k, contadores, parar, args.lote))
                for k in range(args.procesos)]

    print(f"Equipo: {platform.platform()} | {args.procesos} procesos | {args.duracion:.0f} s")
    print(f"psutil: {'sí' if psutil else 'no'} | temperatura: "
          f"{'sí' if leer_temperatura() is not None else 'no disponible'}")
    print(f"Guardando en {salida}\n")

    def fila(escritor, t, fase, total, tasa):
        temp, freq = leer_temperatura(), leer_frecuencia()
        hora = datetime.now().isoformat(sep=" ", timespec="milliseconds")
        escritor.writerow([hora, round(t, 3), fase, total, round(tasa, 1), temp, freq])
        return temp, freq

    with open(salida, "w", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["hora", "t_s", "fase", "hashes_total", "hashes_por_s", "temp_C", "freq_MHz"])

        for p in procesos:
            p.start()
        t0 = time.perf_counter()
        fila(escritor, 0.0, "carga", 0, 0.0)
        t_prev, total_prev = t0, 0
        fase = "carga"

        try:
            while True:
                time.sleep(args.intervalo)
                ahora = time.perf_counter()
                t = ahora - t0
                total = sum(contadores)
                tasa = (total - total_prev) / (ahora - t_prev)
                temp, freq = fila(escritor, t, fase, total, tasa)
                archivo.flush()
                print(f"\r[{fase:12s}] t = {t:6.0f} s | {tasa:12,.0f} hash/s | "
                      f"T = {temp if temp is not None else '--'} °C | "
                      f"f = {freq if freq is not None else '--'} MHz   ", end="")
                t_prev, total_prev = ahora, total
                if fase == "carga" and t >= args.duracion:
                    parar.set()
                    for p in procesos:
                        p.join()
                    fase = "enfriamiento"
                    total_prev = sum(contadores)
                if t >= args.duracion + args.enfriamiento:
                    break
        except KeyboardInterrupt:
            print("\nInterrumpido; se guardó lo medido hasta ahora.")
        finally:
            parar.set()
            for p in procesos:
                p.join()

    print(f"\nListo: {salida}")


if __name__ == "__main__":
    main()
