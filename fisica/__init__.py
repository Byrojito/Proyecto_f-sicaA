"""
Física del proyecto «¿Cuánta energía cuesta romper una contraseña?» como paquete de Python.

Cada función traduce una ecuación del notebook; ver docs/ECUACIONES_A_CODIGO.md.

    from fisica import ataque, VEL_HASH, R_BUENO
    ataque(8, VEL_HASH["NTLM"], R_BUENO)   # 8 caracteres en una RTX 4090
"""

from .ataque import (ataque, bits, cop_carnot, costo_pesos, energia_con_aire, pesos,
                     tamaño_alfabeto, tiempo_legible)
from .frenado import (biseccion, equilibrio, phi_por_tope, regla_frenado, simular,
                      T_equilibrio_frenado, tau_efectivo)
from .landauer import bits_alcanzables, energia_bit, energia_minima
from .parametros import *  # noqa: F401,F403
from .potencia import ajuste_dvfs, capacitancia_efectiva, energia_por_intento_relativa, potencia
from .termico import (F_sin_frenado, T_analitica, T_equilibrio, calentamiento, enfriamiento, euler,
                      factor_euler, resistencia_termica)
