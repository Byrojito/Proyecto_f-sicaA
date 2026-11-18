"""
Medición de una GPU NVIDIA haciendo un ataque real de fuerza bruta con hashcat.

Corre hashcat contra un hash NTLM inventado (imposible de romper en el tiempo de la
prueba) durante un tiempo fijo y, en paralelo, lee de nvidia-smi la temperatura,
la potencia, la frecuencia y los motivos de frenado de la GPU. Guarda una fila por
segundo en CSV:

    hora, t_s, fase, hashes_por_s, temp_C, potencia_W, freq_MHz, mem_MHz,
    vent_pct, uso_pct, freno_potencia, freno_termico, motivos_freno

Al terminar la carga sigue registrando en reposo (fase "enfriamiento") para ajustar
tau con la curva de enfriamiento, igual que en benchmark.py.

La columna "hora" permite unir este CSV con el de HWiNFO64, que además da el VOLTAJE
de la GPU (nvidia-smi no lo da en tarjetas de consumo). Con voltaje se puede probar
P = C V^2 f en la GPU, como en la sección 8.6 del notebook.

Requisitos (Windows, fuera de cualquier máquina virtual):
- Driver de NVIDIA instalado (trae nvidia-smi).
- hashcat descargado de https://hashcat.net/hashcat/ y descomprimido.

Uso (portátil ENCHUFADO, modo de rendimiento que quieras medir, todo lo demás cerrado):

    python medicion/gpu_benchmark.py --hashcat C:\\hashcat-6.2.6\\hashcat.exe --duracion 60 --nombre prueba
    python medicion/gpu_benchmark.py --hashcat C:\\hashcat-6.2.6\\hashcat.exe --duracion 900 --nombre samuel_omen_gpu

Primero haz la prueba de 60 s para comprobar que todo se lee bien.
"""

import argparse
import csv
import json
import os
import secrets
import subprocess
import threading
import time
from datetime import datetime

# Bits de "clocks_throttle_reasons.active" de nvidia-smi (documentación de NVML)
FRENO_POTENCIA = 0x04 | 0x80   # tope de potencia por software / freno de potencia por hardware
FRENO_TERMICO = 0x20 | 0x40    # freno térmico por software / por hardware
NOMBRES_FRENO = {
    0x01: "reposo", 0x02: "reloj_app", 0x04: "tope_potencia", 0x08: "hw_lento",
    0x20: "termico_sw", 0x40: "termico_hw", 0x80: "freno_potencia_hw", 0x100: "reloj_pantalla",
}

CAMPOS_SMI = ["temperature.gpu", "power.draw", "clocks.sm", "clocks.mem",
              "fan.speed", "utilization.gpu"]


def numero(texto):
    """Convierte la salida de nvidia-smi a float; '[N/A]' y similares dan None."""
    try:
        return float(texto)
    except (TypeError, ValueError):
        return None


class LectorGPU(threading.Thread):
    """Mantiene la última lectura de nvidia-smi, que se lanza una sola vez en modo bucle."""

    def __init__(self, intervalo_ms):
        super().__init__(daemon=True)
        # Los drivers nuevos renombraron el campo; probamos los dos nombres.
        campo_freno = "clocks_event_reasons.active"
        ayuda = subprocess.run(["nvidia-smi", "--help-query-gpu"], capture_output=True, text=True).stdout
        if campo_freno not in ayuda:
            campo_freno = "clocks_throttle_reasons.active"
        consulta = ",".join(CAMPOS_SMI + [campo_freno])
        self.proc = subprocess.Popen(
            ["nvidia-smi", f"--query-gpu={consulta}", "--format=csv,noheader,nounits",
             f"-lms={intervalo_ms}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.ultima = None
        self.error = None

    def run(self):
        for linea in self.proc.stdout:
            partes = [p.strip() for p in linea.split(",")]
            if len(partes) != len(CAMPOS_SMI) + 1:
                self.error = linea.strip()
                continue
            *valores, freno = partes
            try:
                mascara = int(freno, 16)
            except ValueError:
                mascara = None
            self.ultima = [numero(v) for v in valores] + [mascara]

    def parar(self):
        self.proc.terminate()


class LectorHashcat(threading.Thread):
    """Lanza hashcat y guarda la última velocidad reportada (hashes/s sumando dispositivos)."""

    def __init__(self, exe, duracion, temp_abortar):
        super().__init__(daemon=True)
        hash_falso = secrets.token_hex(16)  # 32 hex = formato NTLM; nadie conoce su contraseña
        self.cmd = [exe, "-m", "1000", "-a", "3", hash_falso, "?a?a?a?a?a?a?a?a?a?a",
                    "-O", "-w", "3", f"--runtime={int(duracion)}",
                    "--status", "--status-json", "--status-timer=1",
                    "--potfile-disable", "--restore-disable", "--quiet",
                    f"--hwmon-temp-abort={temp_abortar}"]
        # hashcat en Windows necesita correr desde su propia carpeta (busca OpenCL/ y modules/)
        self.proc = subprocess.Popen(self.cmd, cwd=os.path.dirname(os.path.abspath(exe)) or None,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.velocidad = None
        self.dispositivo = None
        self.otras = []

    def run(self):
        for linea in self.proc.stdout:
            linea = linea.strip()
            if not linea.startswith("{"):
                if linea:
                    self.otras.append(linea)
                continue
            try:
                estado = json.loads(linea)
            except json.JSONDecodeError:
                continue
            disp = estado.get("devices", [])
            self.velocidad = sum(d.get("speed", 0) for d in disp)
            if disp and self.dispositivo is None:
                self.dispositivo = disp[0].get("device_name")

    def termino(self):
        return self.proc.poll() is not None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--hashcat", required=True, help="ruta a hashcat.exe")
    p.add_argument("--duracion", type=float, default=900, help="segundos de ataque (por defecto 900)")
    p.add_argument("--enfriamiento", type=float, default=300, help="segundos en reposo al final")
    p.add_argument("--nombre", default="gpu", help="etiqueta para el archivo")
    p.add_argument("--temp-abortar", type=int, default=90,
                   help="hashcat se detiene si la GPU pasa de esta temperatura (°C)")
    args = p.parse_args()

    carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
    os.makedirs(carpeta, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    salida = os.path.join(carpeta, f"{args.nombre}_{marca}.csv")

    gpu = LectorGPU(intervalo_ms=500)
    gpu.start()
    time.sleep(1.5)
    if gpu.ultima is None:
        print(f"No pude leer nvidia-smi: {gpu.error or 'sin respuesta'}")
        gpu.parar()
        return

    print(f"Reposo inicial: T = {gpu.ultima[0]} °C, P = {gpu.ultima[1]} W")
    print(f"Guardando en {salida}\n")

    with open(salida, "w", newline="") as archivo:
        esc = csv.writer(archivo)
        esc.writerow(["hora", "t_s", "fase", "hashes_por_s", "temp_C", "potencia_W", "freq_MHz",
                      "mem_MHz", "vent_pct", "uso_pct", "freno_potencia", "freno_termico",
                      "motivos_freno"])

        hc = LectorHashcat(args.hashcat, args.duracion, args.temp_abortar)
        hc.start()
        t0 = time.perf_counter()
        fase = "carga"
        try:
            while True:
                time.sleep(1.0)
                t = time.perf_counter() - t0
                if fase == "carga" and hc.termino():
                    fase = "enfriamiento"
                    t_fin = t
                    if t < args.duracion - 5:
                        print("\nhashcat terminó antes de tiempo. Sus últimos mensajes:")
                        print("\n".join(hc.otras[-10:]))
                temp, pot, f, fm, vent, uso, mascara = gpu.ultima
                tasa = hc.velocidad if fase == "carga" else 0
                fp = ft = motivos = None
                if mascara is not None:
                    fp, ft = int(bool(mascara & FRENO_POTENCIA)), int(bool(mascara & FRENO_TERMICO))
                    motivos = "+".join(n for b, n in NOMBRES_FRENO.items() if mascara & b) or "ninguno"
                hora = datetime.now().isoformat(sep=" ", timespec="milliseconds")
                esc.writerow([hora, round(t, 3), fase, tasa, temp, pot, f, fm, vent, uso, fp, ft, motivos])
                archivo.flush()
                print(f"\r[{fase:12s}] t = {t:5.0f} s | {(tasa or 0) / 1e9:7.2f} GH/s | T = {temp} °C | "
                      f"P = {pot} W | f = {f} MHz | freno: {motivos}      ", end="")
                if fase == "enfriamiento" and t >= t_fin + args.enfriamiento:
                    break
        except KeyboardInterrupt:
            print("\nInterrumpido; se guardó lo medido hasta ahora.")
        finally:
            if not hc.termino():
                hc.proc.terminate()
            gpu.parar()

    print(f"\nGPU: {hc.dispositivo} | Listo: {salida}")


if __name__ == "__main__":
    main()
