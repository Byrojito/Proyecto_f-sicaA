"""
Parámetros del modelo, con unidades y origen.

Son los mismos valores de la celda de parámetros del notebook (sección 3) y de las
secciones 9 a 12. Las funciones del paquete los usan como valores por defecto, pero
todas aceptan otros valores como argumento.
"""

# --- GPU de referencia (RTX 4090) ---
P_MAX = 450.0      # W    potencia máxima (especificación del fabricante)
T_AMB = 25.0       # °C   temperatura del cuarto
T_LIM = 83.0       # °C   temperatura a partir de la cual el chip frena

# --- Parámetros térmicos (estimaciones) ---
C_TH = 600.0       # J/K  disipador de ~0.67 kg de aluminio y cobre, c ≈ 900 J/(kg·K)
R_BUENO = 0.10     # K/W  disipador bueno
R_MALO = 0.18      # K/W  disipador malo (polvo, pasta térmica seca)

# --- Voltaje contra frecuencia (medido en el portátil de Felipe, sección 9.1) ---
A_DVFS = 0.311     # V(f = 0) / V(f_máx), sale de la recta V = 0.320 V + 0.199 V/GHz · f

# --- Freno térmico (sección 9.2) ---
PHI_MIN = 0.5      # frecuencia relativa mínima
K_FRENO = 0.10     # 1/°C: la frecuencia baja 10 % por cada grado sobre T_LIM

# --- Ataque (secciones 10 y 11) ---
ALFABETO = 95                                  # caracteres imprimibles
VEL_HASH = {                                   # intentos/s de una RTX 4090 a φ = 1 (hashcat 6.2.6, Chick3nman 2022)
    "NTLM": 3e11,                              # 288.5 GH/s redondeado
    "bcrypt costo 5": 2e5,                     # 184 kH/s redondeado; costo 5 = 32 iteraciones
    "bcrypt costo 12": 2e5 / 2**7,             # lo que usaría un sitio bien configurado
}
COP = 3.0                                      # aire acondicionado real
TARIFA = 863.61                                # COP/kWh, Enel Colombia, estrato 4, agosto de 2026
AÑO = 3.156e7                                  # s

# --- Constantes físicas (sección 12) ---
K_B = 1.380649e-23   # J/K   constante de Boltzmann (valor exacto del SI)
T_L = 300.0          # K     temperatura ambiente para Landauer
L_SOL = 3.828e26     # W     luminosidad del Sol
E_HUMANIDAD = 6.0e20 # J     energía primaria que usa la humanidad en un año (> 600 EJ en 2025)
