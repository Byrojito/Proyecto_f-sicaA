# ¿Cuánta energía cuesta romper una contraseña por fuerza bruta?

Proyecto final de **Física A: Hardware e Información** (Universidad de los Andes).
Profesor: Andrés Flórez.

**Integrantes:** Felipe Rojas Díaz · Alejandra Rodríguez · Samuel Fonseca

Simulamos una GPU que prueba contraseñas por fuerza bruta: el chip se calienta según un
balance de energía, se frena cuando supera su temperatura límite, y eso cambia cuánto
tiempo, energía y dinero cuesta el ataque. Al final comparamos con el límite
termodinámico de Landauer.

## Cómo correrlo

```bash
pip install -r requirements.txt
jupyter notebook proyecto.ipynb      # luego: Kernel -> Restart & Run All
```

Medición propia (portátil enchufado, unos 15 minutos):

```bash
python medicion/benchmark.py --duracion 900 --nombre <tu_nombre>
```

Guarda un CSV en `medicion/datos/` con hora, hashes por segundo, temperatura y
frecuencia contra el tiempo. Después de la carga sigue registrando 5 minutos en reposo
(fase de enfriamiento). En Linux la temperatura se lee sola; en Windows hay que
registrarla en paralelo con HWiNFO64 y en macOS con `sudo powermetrics`. Los dos
archivos se unen por la columna `hora`.

Protocolo para que las mediciones sean comparables:

1. Cerrar todo (navegador, juegos, Discord) y dejar el equipo en reposo unos 5 minutos.
2. En HWiNFO: *Settings → Scan interval = 1000 ms*; abrir *Sensors-only* e iniciar el
   registro a CSV.
3. Esperar 30 s y correr `python medicion/benchmark.py --duracion 900 --nombre <nombre>_<modo>`.
4. No tocar el equipo hasta que termine (unos 20 min). Detener el registro de HWiNFO.
5. Guardar los dos archivos en `medicion/datos/` como `<nombre>_<modo>_benchmark.csv` y
   `<nombre>_<modo>_hwinfo.csv`.

## Estructura

```
proyecto.ipynb        Entregable: ensayo computacional (texto + código + interpretación)
medicion/
  benchmark.py        Bucle de hashes en paralelo que registra velocidad vs. tiempo
  datos/              CSV medidos por nosotros
figuras/              Gráficas exportadas para el póster
requirements.txt      Librerías: numpy, matplotlib, ipywidgets, psutil (opcional)
```

Todo el modelo y el integrador están dentro del notebook, para que cada ecuación
esté junto a su código y su interpretación.

## Plan

- [x] **Fase 1** — Balance de energía, Euler propio, validación con solución analítica,
      convergencia (orden 1) y estabilidad (Δt > τ oscila, Δt > 2τ diverge)
- [x] **Fase 2** — Frenado con dos frenos (tope de potencia y límite térmico, on/off vs.
      proporcional), P(φ) calibrada con la medición, validación del equilibrio por bisección,
      τ efectivo con freno, y acoplamiento con el ataque (T, intentos y energía con Euler)
- [ ] **Fase 3** — Medición propia con `benchmark.py` y HWiNFO, ajuste de τ con la curva de
      enfriamiento
  - [x] Felipe, modo Silencio (τ ≈ 44 s, R_th ≈ 1.2 K/W)
  - [x] Felipe, modos Rendimiento y Turbo (Turbo: +22 % velocidad, +30 % energía por hash;
        P = C·V²·f confirmado con C ≈ 12 nF en los tres modos)
  - [x] Alejandra, modos Silencio y Rendimiento (5.9 µJ/hash, C ≈ 9.5 nF, R_th ≈ 2 K/W,
        freno térmico observado; τ de calentamiento ≈ 10 s vs. enfriamiento ≈ 33 s)
  - [ ] Samuel
- [ ] **Fase 4** — Barridos de R_th y T_amb, costo en pesos, Landauer
- [ ] **Fase 5** — Notebook como ensayo: limitaciones, conclusiones, declaración de IA;
      verificar que "Restart & Run All" corre sin errores
- [ ] **Fase 6** — Demo interactiva (ipywidgets), póster y ensayo de la sustentación
