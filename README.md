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
- [ ] **Fase 2** — Frenado térmico f(T) (on/off vs. proporcional) y acoplamiento con el
      ataque: intentos y energía acumulados hasta cubrir 95^N combinaciones
- [ ] **Fase 3** — Medición propia con `benchmark.py` (los tres portátiles) y ajuste de τ
- [ ] **Fase 4** — Barridos (N, tipo de hash, R_th, T_amb), costo en kWh y pesos, Landauer
- [ ] **Fase 5** — Notebook como ensayo: limitaciones, conclusiones, declaración de IA;
      verificar que "Restart & Run All" corre sin errores
- [ ] **Fase 6** — Demo interactiva (ipywidgets), póster y ensayo de la sustentación
