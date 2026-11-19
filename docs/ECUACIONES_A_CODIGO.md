# De las ecuaciones al código

Cada ecuación del proyecto y la función que la implementa en el paquete `fisica/`. Las secciones son
las del notebook `proyecto.ipynb`.

## 1. Termodinámica: el chip como un cuerpo que se calienta

| Ecuación | Qué es | Código |
| --- | --- | --- |
| C_th·dT/dt = P − (T − T_amb)/R_th | Primera ley + conducción de Fourier (sec. 2.1) | `termico.F_sin_frenado` |
| T(t) = T_amb + P·R_th·(1 − e^(−t/τ)), τ = R_th·C_th | Solución exacta, carga RC (sec. 2.1 y 5) | `termico.T_analitica` |
| T_eq = T_amb + P·R_th | Equilibrio, dT/dt = 0 | `termico.T_equilibrio` |
| T(t) = T_∞ + A·e^(−t/τ) | Enfriamiento de Newton (sec. 8.3) | `termico.enfriamiento`, `mediciones.ajustar_tau` |
| R_th = ΔT/ΔP | Resistencia térmica medida (sec. 8.3) | `termico.resistencia_termica` |

## 2. Método numérico: Euler

| Ecuación | Qué es | Código |
| --- | --- | --- |
| T_{k+1} = T_k + Δt·F(t_k, T_k) | Euler explícito (sec. 4) | `termico.euler` |
| error ∝ Δt | Orden 1 (sec. 6) | — |
| u_{k+1} = (1 − Δt/τ)·u_k | Estabilidad (sec. 7) | `termico.factor_euler` |

## 3. Electricidad: la potencia del chip

| Ecuación | Qué es | Código |
| --- | --- | --- |
| U = ½CV² → P = C·V²·f | Energía del condensador por ciclo (sec. 8.6) | `potencia.capacitancia_efectiva` |
| V = V₀ + m·f, a = V(0)/V(f_máx) | Voltaje contra frecuencia (sec. 9.1) | `potencia.ajuste_dvfs` |
| P(φ) = P_máx·φ·(a + (1 − a)φ)² | Potencia de la GPU con φ = f/f_máx (sec. 9.1) | `potencia.potencia` |
| E/intento ∝ V² | Por qué Turbo gasta más por hash (sec. 8.5) | `potencia.energia_por_intento_relativa` |

## 4. Frenado: un sistema no lineal

| Ecuación | Qué es | Código |
| --- | --- | --- |
| φ = mín(φ_tope, 1 − K·(T − T_lím)) | Los dos frenos (sec. 9.2) | `frenado.regla_frenado`, `frenado.phi_por_tope` |
| C_th·dT/dt = P(φ(T)) − (T − T_amb)/R_th | Balance no lineal, con Euler (sec. 9.3) | `frenado.simular` |
| P(φ(T_eq)) = (T_eq − T_amb)/R_th | Equilibrio por bisección (sec. 9.4) | `frenado.biseccion`, `frenado.T_equilibrio_frenado` |
| 1/τ_ef = (1/R_th + K·dP/dφ)/C_th | Linealización: el freno acelera la respuesta (sec. 9.5) | `frenado.tau_efectivo` |

## 5. El ataque y su costo

| Ecuación | Qué es | Código |
| --- | --- | --- |
| dn/dt = r_máx·φ(T), dE/dt = P(φ(T)) | Ataque acoplado al modelo térmico (sec. 10.1) | `ataque.ataque` |
| Extrapolar tras 20τ | El transitorio que queda es e^(−20) (sec. 10.2) | `ataque.ataque` (`n_tau`) |
| 95^N combinaciones, N·log₂ 95 bits | Tamaño del problema | `ataque.bits`, `ataque.tamaño_alfabeto` |
| E_total = E·(1 + 1/COP) | Aire acondicionado y factura (sec. 10.1 y 11.1) | `ataque.energia_con_aire`, `ataque.costo_pesos` |

## 6. Segunda ley

| Ecuación | Qué es | Código |
| --- | --- | --- |
| COP ≤ T_c/(T_h − T_c) | Refrigerador de Carnot (sec. 2.4 y 10.1) | `ataque.cop_carnot` |
| E_bit ≥ k_B·T·ln 2 | Principio de Landauer (sec. 12) | `landauer.energia_bit` |
| E_mín = 2ⁿ·k_B·T·ln 2 | Recorrer n bits | `landauer.energia_minima`, `landauer.bits_alcanzables` |

## Cómo usarlo

```python
from fisica import ataque, VEL_HASH, R_BUENO, tiempo_legible

res = ataque(8, VEL_HASH["NTLM"], R_BUENO)
print(tiempo_legible(res["t"]))     # 6.1 h
```

El notebook sigue teniendo su propio código, porque es el ensayo que se entrega y debe leerse solo.
El paquete es la misma física organizada por tema, para consultarla por partes.
