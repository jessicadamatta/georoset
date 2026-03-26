"""
converters/vulcan.py
====================
Convenções do Vulcan (Maptek) para discos estruturais, variograma e modelo de blocos.

Convenções do Vulcan:
---------------------
Discos estruturais:
    - Bearing: azimute da NORMAL ao plano (não do mergulho!)
    - Plunge: inclinação da normal (0° = horizontal, 90° = vertical)
    ⚠️ DIFERENTE do Leapfrog: Vulcan usa a normal, não o vetor de mergulho.

    Relação com dip/dip_direction:
        plunge_normal = 90° − dip
        bearing_normal = (dip_direction + 180°) mod 360°

Variograma (anisotropia):
    - Bearing, Plunge, Dip
    - Sequência: X-Y-Z
    - R = Rx(bearing) · Ry(plunge) · Rz(dip)

Modelo de blocos:
    - Bearing, Plunge, Dip
    - Sequência: X-Y-Z (mesma do variograma)
    - R = Rx(bearing) · Ry(plunge) · Rz(dip)

Sistema de coordenadas interno GeoRoset: X=Leste, Y=Norte, Z=Cima (dextrogiro).
"""

import numpy as np
from core.rotations import (
    rot_x, rot_y, rot_z,
    dip_dipdirection_to_normal,
    normal_to_dip_dipdirection,
    matrix_to_euler_xyz,
)


# ---------------------------------------------------------------------------
# Discos estruturais
# ---------------------------------------------------------------------------

def disc_to_normal(bearing: float, plunge: float) -> np.ndarray:
    """
    Converte parâmetros de disco do Vulcan para vetor normal unitário.

    O Vulcan define o disco pelo bearing e plunge da NORMAL ao plano.

    Parâmetros
    ----------
    bearing : float
        Azimute da normal ao plano (0–360°, CW from N).
    plunge : float
        Inclinação da normal abaixo do horizontal (0–90°).

    Retorna
    -------
    np.ndarray, shape (3,)
        Vetor normal unitário no sistema X=Leste, Y=Norte, Z=Cima.

    Notas
    -----
    A normal no Vulcan é equivalente ao polo geológico. O vetor é calculado como:
        nx = cos(plunge) · sin(bearing)
        ny = cos(plunge) · cos(bearing)   (Norte positivo)
        nz = sin(plunge)                  (para cima positivo)

    Note que o plunge da normal é complementar ao dip do plano:
        dip = 90° − plunge_normal
    """
    plunge_rad = np.radians(plunge)
    bearing_rad = np.radians(bearing)
    nx = np.cos(plunge_rad) * np.sin(bearing_rad)
    ny = np.cos(plunge_rad) * np.cos(bearing_rad)
    nz = np.sin(plunge_rad)
    return np.array([nx, ny, nz], dtype=float)


def normal_to_disc(normal: np.ndarray) -> tuple[float, float]:
    """
    Converte vetor normal unitário para parâmetros de disco do Vulcan.

    Parâmetros
    ----------
    normal : array-like, shape (3,)
        Vetor normal no sistema X=Leste, Y=Norte, Z=Cima.

    Retorna
    -------
    bearing : float
        Azimute da normal em graus (0–360°).
    plunge : float
        Inclinação da normal em graus (0–90°).
    """
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    nx, ny, nz = n
    nz = np.clip(nz, -1.0, 1.0)
    plunge = np.degrees(np.arcsin(nz))
    bearing = np.degrees(np.arctan2(nx, ny)) % 360.0
    return float(bearing), float(plunge)


# ---------------------------------------------------------------------------
# Variograma
# ---------------------------------------------------------------------------

def vario_to_matrix(bearing: float, plunge: float, dip: float) -> np.ndarray:
    """
    Constrói a matriz de rotação do variograma no formato Vulcan.

    Convenção: R = Rx(bearing) · Ry(plunge) · Rz(dip)

    Parâmetros
    ----------
    bearing : float
        Bearing (α) em graus — rotação em torno de X.
    plunge : float
        Plunge (β) em graus — rotação em torno de Y.
    dip : float
        Dip (γ) em graus — rotação em torno de Z.

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação da elipsoide de anisotropia.
    """
    return rot_x(bearing) @ rot_y(plunge) @ rot_z(dip)


def matrix_to_vario(R: np.ndarray) -> tuple[float, float, float]:
    """
    Decompõe matriz de rotação nos ângulos de variograma do Vulcan.

    Inverte: R = Rx(bearing) · Ry(plunge) · Rz(dip)

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação.

    Retorna
    -------
    bearing, plunge, dip : float
        Ângulos em graus no formato Vulcan.
    """
    return matrix_to_euler_xyz(R)


# ---------------------------------------------------------------------------
# Modelo de blocos
# ---------------------------------------------------------------------------

def block_to_matrix(bearing: float, plunge: float, dip: float) -> np.ndarray:
    """
    Constrói a matriz de rotação do modelo de blocos no formato Vulcan.

    Convenção: R = Rx(bearing) · Ry(plunge) · Rz(dip)

    Parâmetros
    ----------
    bearing : float
        Bearing (α) em graus.
    plunge : float
        Plunge (β) em graus.
    dip : float
        Dip (γ) em graus.

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação do modelo de blocos.
    """
    return rot_x(bearing) @ rot_y(plunge) @ rot_z(dip)


def matrix_to_block(R: np.ndarray) -> tuple[float, float, float]:
    """
    Decompõe matriz de rotação nos ângulos de modelo de blocos do Vulcan.

    Inverte: R = Rx(bearing) · Ry(plunge) · Rz(dip)

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação.

    Retorna
    -------
    bearing, plunge, dip : float
        Ângulos em graus no formato Vulcan.
    """
    return matrix_to_euler_xyz(R)
