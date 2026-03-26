"""
core/structural.py
==================
Funções de conversão entre representações de planos estruturais.

Representações suportadas:
    - Dip / Dip Direction (mergulho / azimute do mergulho) — convenção geológica
    - Strike / Dip — convenção RHR (regra da mão direita)
    - Polo (projeção estereográfica) — mesmo que vetor normal
    - Vetor normal unitário — sistema interno X=Leste, Y=Norte, Z=Cima

Sistema de coordenadas padrão interno: X=Leste, Y=Norte, Z=Cima (dextrogiro).
"""

import numpy as np
from core.rotations import dip_dipdirection_to_normal, normal_to_dip_dipdirection


def dip_dipdirection_to_strike_dip(dip: float, dip_direction: float) -> tuple[float, float]:
    """
    Converte dip/dip_direction para strike/dip (convenção RHR).

    Relação: strike = dip_direction - 90° (módulo 360°)

    Parâmetros
    ----------
    dip : float
        Ângulo de mergulho em graus (0–90°).
    dip_direction : float
        Azimute da direção de mergulho em graus (0–360°).

    Retorna
    -------
    strike : float
        Azimute do strike em graus (0–360°), convenção RHR:
        o plano mergulha para a direita de quem olha na direção do strike.
    dip : float
        Ângulo de mergulho (inalterado).
    """
    strike = (dip_direction - 90.0) % 360.0
    return float(strike), float(dip)


def strike_dip_to_dip_dipdirection(strike: float, dip: float) -> tuple[float, float]:
    """
    Converte strike/dip (convenção RHR) para dip/dip_direction.

    Relação: dip_direction = strike + 90° (módulo 360°)

    Parâmetros
    ----------
    strike : float
        Azimute do strike em graus (0–360°), convenção RHR.
    dip : float
        Ângulo de mergulho em graus (0–90°).

    Retorna
    -------
    dip : float
        Ângulo de mergulho (inalterado).
    dip_direction : float
        Azimute da direção de mergulho em graus (0–360°).
    """
    dip_direction = (strike + 90.0) % 360.0
    return float(dip), float(dip_direction)


def dip_dipdirection_to_pole(dip: float, dip_direction: float) -> np.ndarray:
    """
    Converte dip/dip_direction para vetor polo (vetor normal ao plano).

    O polo é idêntico ao vetor normal unitário no sistema X=Leste, Y=Norte, Z=Cima.

    Parâmetros
    ----------
    dip : float
        Ângulo de mergulho em graus.
    dip_direction : float
        Azimute da direção de mergulho em graus.

    Retorna
    -------
    np.ndarray, shape (3,)
        Vetor polo unitário [px, py, pz].
    """
    return dip_dipdirection_to_normal(dip, dip_direction)


def pole_to_dip_dipdirection(pole: np.ndarray) -> tuple[float, float]:
    """
    Converte vetor polo (vetor normal) de volta para dip/dip_direction.

    Parâmetros
    ----------
    pole : array-like, shape (3,)
        Vetor normal ao plano no sistema X=Leste, Y=Norte, Z=Cima.

    Retorna
    -------
    dip : float
        Ângulo de mergulho em graus.
    dip_direction : float
        Azimute da direção de mergulho em graus.
    """
    return normal_to_dip_dipdirection(pole)


def strike_dip_to_pole(strike: float, dip: float) -> np.ndarray:
    """
    Converte strike/dip para vetor polo (vetor normal).

    Parâmetros
    ----------
    strike : float
        Azimute do strike em graus (convenção RHR).
    dip : float
        Ângulo de mergulho em graus.

    Retorna
    -------
    np.ndarray, shape (3,)
        Vetor polo unitário.
    """
    dip_out, dip_dir = strike_dip_to_dip_dipdirection(strike, dip)
    return dip_dipdirection_to_normal(dip_out, dip_dir)


def pole_to_strike_dip(pole: np.ndarray) -> tuple[float, float]:
    """
    Converte vetor polo (vetor normal) para strike/dip.

    Parâmetros
    ----------
    pole : array-like, shape (3,)
        Vetor normal ao plano no sistema X=Leste, Y=Norte, Z=Cima.

    Retorna
    -------
    strike : float
        Azimute do strike em graus (convenção RHR).
    dip : float
        Ângulo de mergulho em graus.
    """
    dip, dip_direction = normal_to_dip_dipdirection(pole)
    strike, dip_out = dip_dipdirection_to_strike_dip(dip, dip_direction)
    return float(strike), float(dip_out)


def normal_to_strike_dip(normal_vector: np.ndarray) -> tuple[float, float]:
    """
    Alias de pole_to_strike_dip para clareza semântica.

    Parâmetros
    ----------
    normal_vector : array-like, shape (3,)
        Vetor normal ao plano no sistema X=Leste, Y=Norte, Z=Cima.

    Retorna
    -------
    strike : float
        Azimute do strike em graus.
    dip : float
        Ângulo de mergulho em graus.
    """
    return pole_to_strike_dip(normal_vector)
