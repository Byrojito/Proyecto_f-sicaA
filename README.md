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

## Panel de la presentación

`presentacion/panel.html` es una sola página con tres columnas que comparten el mismo reloj:

1. **El ataque:** escribes una contraseña de prueba y calcula el espacio de búsqueda, el tiempo, los kWh, el costo en pesos y el piso de Landauer.
2. **El modelo:** la GPU simulada con el mismo Euler y los mismos frenos del notebook. Tiene controles para R_th, T_amb, tope de potencia y tipo de freno.
3. **La realidad:** nuestras mediciones de HWiNFO reproducidas al mismo ritmo, con el freno térmico y el tope de potencia marcados.

Se abre con doble clic, sin internet. Para el **modo en vivo** (la GPU atacando durante la sustentación):

```bash
python presentacion/servidor.py            # luego abrir http://localhost:8000
python medicion/gpu_benchmark.py --hashcat C:\hashcat\hashcat.exe --duracion 900 --nombre demo
```

Si se cambian los datos o la plantilla, se regenera con `python presentacion/generar_panel.py`.

## Medición de la GPU

`medicion/gpu_benchmark.py` corre hashcat (NTLM, `-m 1000`) contra un hash inventado y registra cada segundo
la velocidad, la temperatura, la potencia, la frecuencia y el motivo de frenado (nvidia-smi). Se usa en Windows,
fuera de cualquier máquina virtual, con HWiNFO registrando en paralelo para obtener el voltaje de la GPU.
Primero conviene hacer una prueba con `--duracion 60`.

## Material para la sustentación

- `docs/Chuleta_fisica.docx`: 4 páginas, una ficha por ecuación del curso (qué dice, cómo la usamos, nuestro número). Es lo que hay que tener a mano frente al póster.
- `docs/Fisica_del_proyecto_completo.docx`: 11 páginas con las derivaciones completas y las figuras, por si preguntan de dónde sale una ecuación.

## Estructura

```
proyecto.ipynb        Entregable: ensayo computacional (texto + código + interpretación)
medicion/
  benchmark.py        Bucle de hashes en paralelo que registra velocidad vs. tiempo
  gpu_benchmark.py    Ataque real con hashcat en una GPU NVIDIA + registro de nvidia-smi
  EQUIPOS.md          Hardware de cada integrante y qué medición puede hacer cada equipo
  datos/              CSV medidos por nosotros
figuras/              Gráficas exportadas para el póster
docs/                 Chuleta de física y documento completo para la sustentación
presentacion/
  panel.html          Panel de tres columnas para la sustentación (se abre solo)
  panel_plantilla.html  Fuente del panel (sin datos)
  generar_panel.py    Incrusta las mediciones en la plantilla
  servidor.py         Sirve el panel con modo en vivo en http://localhost:8000
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
  - [ ] Samuel: ThinkPad T14 (i7-1185G7, solo CPU) en dos modos
  - [ ] GPU NVIDIA con `gpu_benchmark.py`: Omen de Samuel (RTX 4060 Laptop) y/o TUF de Felipe
- [x] **Fase 4** — Costo en pesos (Enel, estrato 4), barridos de R_th y T_amb, límite de
      Landauer (≈ 215 bits / 33 caracteres aleatorios superan la energía del Sol en su vida)
- [ ] **Fase 5** — Notebook como ensayo
  - [x] Limitaciones y conclusiones (borrador para revisar entre los tres)
  - [ ] Declaración de uso de IA: completar qué hizo cada integrante
  - [x] "Restart & Run All" corre sin errores
- [ ] **Fase 6** — Presentación
  - [x] Demo interactiva (sección 13)
  - [x] Panel de tres columnas con modo en vivo (`presentacion/`)
  - [ ] Póster
  - [ ] Ensayo de la sustentación
