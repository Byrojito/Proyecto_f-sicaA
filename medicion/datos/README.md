# Datos medidos

Cada medición tiene dos archivos con el mismo prefijo `<persona>_<modo>`, tomados al mismo tiempo:

- `_benchmark.csv`: lo escribe `medicion/benchmark.py` (la carga y su velocidad).
- `_hwinfo.csv`: lo escribe HWiNFO64 (los sensores del chip, cada 1 o 2 s).

Se unen por la hora del reloj del computador: la columna `hora` del benchmark y las columnas `Date` y `Time` de HWiNFO.
El hardware de cada equipo está en [`../EQUIPOS.md`](../EQUIPOS.md).

| Prefijo | Equipo | Modo de energía | Uso en el notebook |
| --- | --- | --- | --- |
| `felipe_silencio` | ASUS TUF F15 (i5-10300H) | Silencio | Secciones 8.1 a 8.4: τ, R_th y energía por hash |
| `felipe_rendimiento` | ASUS TUF F15 | Rendimiento | Secciones 8.5 y 8.6 |
| `felipe_turbo` | ASUS TUF F15 | Turbo | Secciones 8.5, 8.6 y 9.1 (recta V contra f) |
| `alejandra_silencio` | ASUS VivoBook 15 (i5-1135G7) | Silencio | Sección 8.7: freno térmico observado |
| `alejandra_rendimiento` | ASUS VivoBook 15 | Rendimiento | Sección 8.7: τ de calentamiento y de enfriamiento |
| `felipe_gpu_turbo` | GPU GTX 1650 del ASUS TUF F15 | Turbo | Sección 8.9: GPU atacando con hashcat (`_benchmark.csv` de `gpu_benchmark.py`, `_hwinfo.csv` y `_hashcat.log`) |

`pruebas/` guarda corridas de prueba (60 s e interrumpida) que no se usan en el análisis.

## Columnas de `_benchmark.csv`

| Columna | Unidad | Significado |
| --- | --- | --- |
| `hora` | fecha y hora | Reloj del computador, para unir con HWiNFO |
| `t_s` | s | Tiempo desde el inicio de la prueba |
| `fase` | — | `carga` (15 min calculando hashes) o `enfriamiento` (5 min en reposo) |
| `hashes_total` | — | Hashes SHA-256 acumulados |
| `hashes_por_s` | hashes/s | Velocidad en ese intervalo |
| `temp_C`, `freq_MHz` | °C, MHz | Lectura de psutil; suele venir vacía en Windows, por eso se usa HWiNFO |

## Columnas de HWiNFO que usa el análisis

HWiNFO registra cientos de sensores. El código busca estas columnas por nombre, en español o inglés
(`fisica/mediciones.py`, `COLUMNAS_HWINFO`):

| Variable | Columna (español / inglés) | Unidad |
| --- | --- | --- |
| Temperatura | `CPU Entera` / `CPU Package` | °C |
| Potencia | `Potencia total de CPU` / `CPU Package Power` | W |
| Frecuencia | `Relojes efectivos núcleo (avg)` / `Core Effective Clocks (avg)` | MHz |
| Voltaje | `Core VIDs (avg)` | V |
| Ventilador | `CPU [RPM]` | rpm |
| Freno térmico | `Desaceleración térmica del núcleo (avg)` / `Core Thermal Throttling (avg)` | Sí/No |

## Medidas de la GPU

`medicion/gpu_benchmark.py` escribe un solo archivo con todo junto (hashcat y nvidia-smi):
`hora, t_s, fase, hashes_por_s, temp_C, potencia_W, freq_MHz, mem_MHz, vent_pct, uso_pct,
freno_potencia, freno_termico, motivos_freno`. Para el voltaje de la GPU se graba HWiNFO en paralelo.
