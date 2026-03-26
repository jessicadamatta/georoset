"""
converters/isatis_neo.py
========================
Convenções do Isatis.neo para discos estruturais, variograma e modelo de blocos.

Flag de incerteza de convenção:
    ISATIS_NEO_SIGN_CONVENTION = -1  # TODO: validar com documentação oficial
"""

import numpy as np

# TODO: validar com documentação oficial Isatis.neo
ISATIS_NEO_SIGN_CONVENTION = -1  # TODO: validar com documentação oficial

"""
Convenções do Isatis.neo:
-------------------------
Discos estruturais:
    - Azimute (dip direction): 0–360°, CW from N — idêntico ao Leapfrog
    - Dip: 0–90° — idêntico ao Leapfrog

Variograma (anisotropia):
    - Azimute (α), Mergulho (β), Rake (ω)
    - Sequência: Z-X-X
    - R = Rz(−α) · Rx(ISATIS_NEO_SIGN_CONVENTION · β) · Rx(ω)
    ⚠️ Sinal de β a confirmar com documentação oficial.

Modelo de blocos:
    - Azimute, Mergulho, Rake
    - Ordem Z-X-Z (mesma do Leapfrog, verificar sinais)
    # TODO: validar sinais com documentação oficial Isatis.neo

Sistema de coordenadas interno GeoRoset: X=Leste, Y=Norte, Z=Cima (dextrogiro).
"""

from core.rotations import (
    rot_x, rot_z,
    dip_dipdirection_to_normal,
    normal_to_dip_dipdirection,
    matrix_to_euler_zxz,
)


# ---------------------------------------------------------------------------
# Discos estruturais (idêntico ao Leapfrog)
# ---------------------------------------------------------------------------

def disc_to_normal(dip: float, azimuth: float) -> np.ndarray:
    """
    Converte parâmetros de disco do Isatis.neo para vetor normal unitário.

    Convenção idêntica ao Leapfrog: azimute = dip direction, dip = mergulho.

    Parâmetros
    ----------
    dip : float
        Ângulo de mergulho (0–90°).
    azimuth : float
        Azimute do dip direction (0–360°, CW from N).

    Retorna
    -------
    np.ndarray, shape (3,)
        Vetor normal no sistema X=Leste, Y=Norte, Z=Cima.
    """
    return dip_dipdirection_to_normal(dip, azimuth)


def normal_to_disc(normal: np.ndarray) -> tuple[float, float]:
    """
    Converte vetor normal unitário para parâmetros de disco do Isatis.neo.

    Parâmetros
    ----------
    normal : array-like, shape (3,)
        Vetor normal no sistema X=Leste, Y=Norte, Z=Cima.

    Retorna
    -------
    dip : float
        Ângulo de mergulho em graus.
    azimuth : float
        Azimute do dip direction em graus.
    """
    return normal_to_dip_dipdirection(normal)


# ---------------------------------------------------------------------------
# Variograma
# ---------------------------------------------------------------------------

def vario_to_matrix(azimuth: float, dip: float, rake: float) -> np.ndarray:
    """
    Constrói a matriz de rotação do variograma no formato Isatis.neo.

    Convenção: R = Rz(−azimuth) · Rx(ISATIS_NEO_SIGN_CONVENTION · dip) · Rx(rake)

    ⚠️ O sinal de dip (β) é incerto — ver flag ISATIS_NEO_SIGN_CONVENTION no topo.
    # TODO: validar com documentação oficial Isatis.neo

    Parâmetros
    ----------
    azimuth : float
        Azimute (α) em graus — rotação em torno de Z.
    dip : float
        Mergulho (β) em graus — rotação em torno de X.
    rake : float
        Rake (ω) em graus — rotação adicional em torno de X.

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação da elipsoide de anisotropia.
    """
    return rot_z(-azimuth) @ rot_x(ISATIS_NEO_SIGN_CONVENTION * dip) @ rot_x(rake)


def matrix_to_vario(R: np.ndarray) -> tuple[float, float, float]:
    """
    Decompõe matriz de rotação nos ângulos de variograma do Isatis.neo.

    Inverte aproximadamente: R = Rz(−α) · Rx(−β) · Rx(ω) = Rz(−α) · Rx(−β+ω)

    ⚠️ A separação de dip e rake é indeterminada sem informação adicional.
    Retorna o ângulo combinado como dip, rake=0.

    # TODO: validar decomposição com documentação oficial Isatis.neo

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação.

    Retorna
    -------
    azimuth, dip, rake : float
        Ângulos em graus. A decomposição de dip e rake é aproximada.
    """
    # Rz(-α)·Rx(θ) onde θ = combinação de -β e ω
    # Terceira coluna de R: [sin(θ)·sin(α), -sin(θ)·cos(α), cos(θ)]
    col2 = R[:, 2]
    theta = np.degrees(np.arccos(np.clip(col2[2], -1.0, 1.0)))
    sin_theta = np.sin(np.radians(theta))
    if abs(sin_theta) < 1e-9:
        azimuth = 0.0
    else:
        azimuth = np.degrees(np.arctan2(col2[0], -col2[1])) % 360.0

    dip = theta * ISATIS_NEO_SIGN_CONVENTION
    rake = 0.0  # indeterminado sem informação adicional
    return float(azimuth), float(dip), float(rake)


# ---------------------------------------------------------------------------
# Modelo de blocos
# ---------------------------------------------------------------------------

def block_to_matrix(azimuth: float, dip: float, rake: float) -> np.ndarray:
    """
    Constrói a matriz de rotação do modelo de blocos no formato Isatis.neo.

    Convenção Z-X-Z (mesma ordem do Leapfrog, sinais a confirmar).
    # TODO: validar sinais com documentação oficial Isatis.neo

    Parâmetros
    ----------
    azimuth : float
        Azimute (α) em graus.
    dip : float
        Mergulho (β) em graus.
    rake : float
        Rake (γ) em graus.

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação do modelo de blocos.
    """
    # TODO: validar sinais com documentação oficial Isatis.neo
    return rot_z(azimuth) @ rot_x(dip) @ rot_z(rake)


def matrix_to_block(R: np.ndarray) -> tuple[float, float, float]:
    """
    Decompõe matriz de rotação nos ângulos de modelo de blocos do Isatis.neo.

    # TODO: validar com documentação oficial Isatis.neo

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação.

    Retorna
    -------
    azimuth, dip, rake : float
        Ângulos em graus no formato Isatis.neo.
    """
    return matrix_to_euler_zxz(R)
