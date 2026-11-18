# De las ecuaciones al código

Cada ecuación del proyecto, la función que la implementa en el paquete `fisica/` y la prueba
automática que la verifica. Las secciones son las del notebook `proyecto.ipynb`.

Las pruebas se corren con `pytest` y GitHub las corre solas en cada push (ver la pestaña *Actions*).
Hay dos tipos:

- **Pruebas de física** (`tests/test_fisica.py`): comprueban algo que tiene que cumplirse por la física o
  por el método, sin depender de nuestras mediciones. Ejemplo: que Euler sea de orden 1.
- **Pruebas de reproducción** (`tests/test_resultados_notebook.py`): comprueban que el paquete da los mismos
  números que imprime el notebook. Ejemplo: 8 caracteres en NTLM tardan 6.1 h y gastan 3.69 kWh.

## 1. Termodinámica: el chip como un cuerpo que se calienta

| Ecuación | Qué es | Código | Prueba |
| --- | --- | --- | --- |
| C_th·dT/dt = P − (T − T_amb)/R_th | Primera ley + conducción de Fourier (sec. 2.1) | `termico.F_sin_frenado` | `test_euler_sigue_la_solucion_analitica` |
| T(t) = T_amb + P·R_th·(1 − e^(−t/τ)), τ = R_th·C_th | Solución exacta, carga RC (sec. 2.1 y 5) | `termico.T_analitica` | `test_tau_es_el_63_por_ciento` |
| T_eq = T_amb + P·R_th | Equilibrio, dT/dt = 0 | `termico.T_equilibrio` | `test_equilibrio_no_depende_de_la_capacidad` |
| T(t) = T_∞ + A·e^(−t/τ) | Enfriamiento de Newton (sec. 8.3) | `termico.enfriamiento`, `mediciones.ajustar_tau` | `test_medicion_felipe_silencio` (τ = 44 s) |
| R_th = ΔT/ΔP | Resistencia térmica medida (sec. 8.3) | `termico.resistencia_termica` | `test_medicion_felipe_silencio` (1.22 K/W) |

## 2. Método numérico: Euler

| Ecuación | Qué es | Código | Prueba |
| --- | --- | --- | --- |
| T_{k+1} = T_k + Δt·F(t_k, T_k) | Euler explícito (sec. 4) | `termico.euler` | `test_euler_sigue_la_solucion_analitica` |
| error ∝ Δt | Orden 1 (sec. 6) | — | `test_euler_es_de_orden_uno` (pendiente log-log ≈ 1) |
| u_{k+1} = (1 − Δt/τ)·u_k | Estabilidad (sec. 7) | `termico.factor_euler` | `test_euler_estable_oscila_diverge` |

## 3. Electricidad: la potencia del chip

| Ecuación | Qué es | Código | Prueba |
| --- | --- | --- | --- |
| U = ½CV² → P = C·V²·f | Energía del condensador por ciclo (sec. 8.6) | `potencia.capacitancia_efectiva` | `test_capacitancia_recupera_C_conocida`, `test_capacitancia_efectiva_felipe` (12.0 nF, R² = 0.986) |
| V = V₀ + m·f, a = V(0)/V(f_máx) | Voltaje contra frecuencia (sec. 9.1) | `potencia.ajuste_dvfs` | `test_a_dvfs_sale_de_los_datos` (a = 0.311) |
| P(φ) = P_máx·φ·(a + (1 − a)φ)² | Potencia de la GPU con φ = f/f_máx (sec. 9.1) | `potencia.potencia` | `test_potencia_maxima_y_monotona` |
| E/intento ∝ V² | Por qué Turbo gasta más por hash (sec. 8.5) | `potencia.energia_por_intento_relativa` | `test_turbo_mas_rapido_pero_mas_caro` (+22 % velocidad, +30 % energía) |

## 4. Frenado: un sistema no lineal

| Ecuación | Qué es | Código | Prueba |
| --- | --- | --- | --- |
| φ = mín(φ_tope, 1 − K·(T − T_lím)) | Los dos frenos (sec. 9.2) | `frenado.regla_frenado`, `frenado.phi_por_tope` | `test_freno_respeta_sus_limites` |
| C_th·dT/dt = P(φ(T)) − (T − T_amb)/R_th | Balance no lineal, con Euler (sec. 9.3) | `frenado.simular` | `test_escenarios_de_frenado` (84.2 °C, φ = 0.875) |
| P(φ(T_eq)) = (T_eq − T_amb)/R_th | Equilibrio por bisección (sec. 9.4) | `frenado.biseccion`, `frenado.T_equilibrio_frenado` | `test_simulacion_llega_al_equilibrio_de_biseccion` |
| 1/τ_ef = (1/R_th + K·dP/dφ)/C_th | Linealización: el freno acelera la respuesta (sec. 9.5) | `frenado.tau_efectivo` | `test_tau_efectivo` (6.5 s), `test_freno_acelera_la_respuesta` |

## 5. El ataque y su costo

| Ecuación | Qué es | Código | Prueba |
| --- | --- | --- | --- |
| dn/dt = r_máx·φ(T), dE/dt = P(φ(T)) | Ataque acoplado al modelo térmico (sec. 10.1) | `ataque.ataque` | `test_tabla_8_caracteres_ntlm` (6.1 h, 3.69 kWh) |
| Extrapolar tras 20τ | El transitorio que queda es e^(−20) (sec. 10.2) | `ataque.ataque` (`n_tau`) | `test_extrapolar_en_equilibrio_no_cambia_el_resultado` |
| 95^N combinaciones, N·log₂ 95 bits | Tamaño del problema | `ataque.bits`, `ataque.tamaño_alfabeto` | `test_cada_caracter_multiplica_el_tiempo_por_95`, `test_alfabeto` |
| E_total = E·(1 + 1/COP) | Aire acondicionado y factura (sec. 10.1 y 11.1) | `ataque.energia_con_aire`, `ataque.costo_pesos` | `test_costo_8_caracteres` ($3.183) |

## 6. Segunda ley

| Ecuación | Qué es | Código | Prueba |
| --- | --- | --- | --- |
| COP ≤ T_c/(T_h − T_c) | Refrigerador de Carnot (sec. 2.4 y 10.1) | `ataque.cop_carnot` | `test_carnot` (≈ 30) |
| E_bit ≥ k_B·T·ln 2 | Principio de Landauer (sec. 12) | `landauer.energia_bit` | `test_landauer` (2.87×10⁻²¹ J) |
| E_mín = 2ⁿ·k_B·T·ln 2 | Recorrer n bits | `landauer.energia_minima`, `landauer.bits_alcanzables` | — |

## Cómo usarlo

```python
from fisica import ataque, VEL_HASH, R_BUENO, tiempo_legible

res = ataque(8, VEL_HASH["NTLM"], R_BUENO)
print(tiempo_legible(res["t"]))     # 6.1 h
```

```bash
pip install -r requirements.txt
pytest -v                           # 32 pruebas
```

El notebook sigue teniendo su propio código, porque es el ensayo que se entrega y debe leerse solo.
El paquete es la misma física organizada por tema, documentada y verificada; las pruebas de
reproducción garantizan que los dos dan los mismos resultados.
