"""
Principio de Landauer (sección 12 del notebook).

Borrar un bit lleva la memoria de 2 estados a 1: su entropía baja en k_B·ln 2. Por la
segunda ley ese calor tiene que salir al ambiente:

    E_bit ≥ k_B · T · ln 2

Recorrer un espacio de n bits exige al menos 2ⁿ·k_B·T·ln 2 (cota para un computador
irreversible perfecto).
"""

import numpy as np

from .parametros import K_B, T_L


def energia_bit(T=T_L):
    """Mínimo de Landauer por bit borrado (J): k_B·T·ln 2."""
    return K_B * T * np.log(2)


def energia_minima(n_bits, T=T_L):
    """Energía mínima para recorrer 2ⁿ claves (J)."""
    return 2.0 ** n_bits * energia_bit(T)


def bits_alcanzables(E, energia_por_intento):
    """Cuántos bits se pueden recorrer con una energía E: log₂(E / energía por intento)."""
    return np.log2(E / energia_por_intento)
