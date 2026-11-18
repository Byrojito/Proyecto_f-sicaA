"""
Sirve el panel en http://localhost:8000 con el modo EN VIVO activado.

Mientras gpu_benchmark.py (o benchmark.py) escribe su CSV en medicion/datos/,
el panel lo lee cada segundo y muestra la medición real junto al modelo.

    Terminal 1:  python presentacion/servidor.py
    Navegador:   http://localhost:8000
    Terminal 2:  python medicion/gpu_benchmark.py --hashcat C:\\hashcat\\hashcat.exe --duracion 900 --nombre demo

Solo escucha en este computador (127.0.0.1); nadie más en la red lo puede abrir.
"""
import glob
import os
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, "..", "medicion", "datos")
RECIENTE = 120  # s: un CSV modificado hace menos de esto se considera "en curso"


class Manejador(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=AQUI, **k)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/panel.html"
        if self.path.startswith("/en_vivo.csv"):
            return self.en_vivo()
        return super().do_GET()

    def en_vivo(self):
        csvs = [c for c in glob.glob(os.path.join(DATOS, "*.csv")) if not c.endswith("_hwinfo.csv")]
        csvs = [c for c in csvs if time.time() - os.path.getmtime(c) < RECIENTE]
        if not csvs:
            self.send_error(404, "No hay una medición en curso")
            return
        ruta = max(csvs, key=os.path.getmtime)
        cuerpo = open(ruta, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("X-Archivo", os.path.basename(ruta))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("Panel en http://localhost:8000  (Ctrl+C para salir)")
    HTTPServer(("127.0.0.1", 8000), Manejador).serve_forever()
