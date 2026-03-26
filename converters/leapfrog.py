"""
converters/leapfrog.py
======================
Convenções do Leapfrog Geo para discos estruturais, variograma e modelo de blocos.

Convenções do Leapfrog:
-----------------------
Discos estruturais:
    - Dip Direction: azimute do mergulho máximo (0–360°, CW from N)
    - Dip: ângulo de mergulho abaixo do horizontal (0–90°)
    → Idêntico à convenção geológica padrão (sistema interno GeoRoset)

Variograma (anisotropia):
    - Bearing (azimute, α): rotação em torno de Z
    - Plunge (β): rotação em torno de X
    - Rake (γ): rotação em torno de Z
    - Sequência: Z-X-Z
    - R = Rz(−α) · Rx(−β) · Rz(γ)

Modelo de blocos:
    - Bearing (α), Plunge (β), Dip (γ)
    - Sequência: Z-X-Z
    - R = Rz(α) · Rx(β) · Rz(γ)

Sistema de coordenadas interno GeoRoset: X=Leste, Y=Norte, Z=Cima (dextrogiro).
"""

import numpy as np
from core.rotations import (
    rot_x, rot_z,
    dip_dipdirection_to_normal,
    normal_to_dip_dipdirection,
    matrix_to_euler_zxz,
    matrix_to_euler_xyz,
)


# ---------------------------------------------------------------------------
# Discos estruturais
# ---------------------------------------------------------------------------

def disc_to_normal(dip: float, dip_direction: float) -> np.ndarray:
    """
    Converte parâmetros de disco do Leapfrog para vetor normal unitário.

    Parâmetros
    ----------
    dip : float
        Ângulo de mergulho (0–90°).
    dip_direction : float
        Azimute do mergulho (0–360°, CW from N).

    Retorna
    -------
    np.ndarray, shape (3,)
        Vetor normal no sistema X=Leste, Y=Norte, Z=Cima.
    """
    return dip_dipdirection_to_normal(dip, dip_direction)


def normal_to_disc(normal: np.ndarray) -> tuple[float, float]:
    """
    Converte vetor normal unitário para parâmetros de disco do Leapfrog.

    Parâmetros
    ----------
    normal : array-like, shape (3,)
        Vetor normal no sistema X=Leste, Y=Norte, Z=Cima.

    Retorna
    -------
    dip : float
        Ângulo de mergulho em graus.
    dip_direction : float
        Azimute do mergulho em graus.
    """
    return normal_to_dip_dipdirection(normal)


# ---------------------------------------------------------------------------
# Variograma
# ---------------------------------------------------------------------------

def vario_to_matrix(bearing: float, plunge: float, rake: float) -> np.ndarray:
    """
    Constrói a matriz de rotação do variograma no formato Leapfrog.

    Convenção: R = Rz(−bearing) · Rx(−plunge) · Rz(rake)

    Parâmetros
    ----------
    bearing : float
        Azimute (α) em graus — rotação em torno de Z.
    plunge : float
        Mergulho (β) em graus — rotação em torno de X.
    rake : float
        Rake (γ) em graus — rotação final em torno de Z.

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação da elipsoide de anisotropia.
    """
    return rot_z(-bearing) @ rot_x(-plunge) @ rot_z(rake)


def matrix_to_vario(R: np.ndarray) -> tuple[float, float, float]:
    """
    Decompõe matriz de rotação nos ângulos de variograma do Leapfrog.

    Inverte: R = Rz(−bearing) · Rx(−plunge) · Rz(rake)

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação da elipsoide.

    Retorna
    -------
    bearing, plunge, rake : float
        Ângulos em graus no formato Leapfrog.
    """
    # R = Rz(-a) * Rx(-b) * Rz(c)  →  decompor Rz(a) * R * Rz(-c) = Rx(b)
    # Estratégia: R_lf = Rz(-α)·Rx(-β)·Rz(γ)
    # Equivalente a euler Z-X-Z com sinais negados nos dois primeiros
    # Decompomos: R = Rz(-α)·Rx(-β)·Rz(γ)
    # Seja α'=-α, β'=-β: R = Rz(α')·Rx(β')·Rz(γ) → usar matrix_to_euler_zxz
    alpha_p, beta_p, gamma = matrix_to_euler_zxz(R)
    bearing = (-alpha_p) % 360.0
    plunge = (-beta_p) % 360.0
    return float(bearing), float(plunge), float(gamma)


# ---------------------------------------------------------------------------
# Modelo de blocos
# ---------------------------------------------------------------------------

def block_to_matrix(bearing: float, plunge: float, dip: float) -> np.ndarray:
    """
    Constrói a matriz de rotação do modelo de blocos no formato Leapfrog.

    Convenção: R = Rz(bearing) · Rx(plunge) · Rz(dip)

    Parâmetros
    ----------
    bearing : float
        Azimute (α) em graus.
    plunge : float
        Mergulho (β) em graus.
    dip : float
        Ângulo de dip final (γ) em graus.

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação do modelo de blocos.
    """
    return rot_z(bearing) @ rot_x(plunge) @ rot_z(dip)


def matrix_to_block(R: np.ndarray) -> tuple[float, float, float]:
    """
    Decompõe matriz de rotação nos ângulos de modelo de blocos do Leapfrog.

    Inverte: R = Rz(bearing) · Rx(plunge) · Rz(dip)

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação.

    Retorna
    -------
    bearing, plunge, dip : float
        Ângulos em graus no formato Leapfrog.
    """
    return matrix_to_euler_zxz(R)
