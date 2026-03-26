"""
core/rotations.py
=================
Funções de rotação 3D para o sistema GeoRoset.

Sistema de coordenadas interno padrão:
    X = Leste, Y = Norte, Z = Cima (dextrogiro, mão direita)

Ângulos em graus são convertidos para radianos internamente.
Todas as funções retornam numpy arrays ou tuplas de floats.
"""

import numpy as np


def rot_x(angle_deg: float) -> np.ndarray:
    """
    Matriz de rotação 3x3 em torno do eixo X (positivo = sentido anti-horário
    quando visto do eixo X positivo apontando para o observador).

    Parâmetros
    ----------
    angle_deg : float
        Ângulo de rotação em graus.

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação Rx(θ).

    Notas
    -----
    Rx(θ) = [[1,   0,        0     ],
             [0,  cos(θ), -sin(θ) ],
             [0,  sin(θ),  cos(θ) ]]
    """
    theta = np.radians(angle_deg)
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [1,  0,  0],
        [0,  c, -s],
        [0,  s,  c],
    ], dtype=float)


def rot_y(angle_deg: float) -> np.ndarray:
    """
    Matriz de rotação 3x3 em torno do eixo Y (positivo = sentido anti-horário
    quando visto do eixo Y positivo apontando para o observador).

    Parâmetros
    ----------
    angle_deg : float
        Ângulo de rotação em graus.

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação Ry(θ).

    Notas
    -----
    Ry(θ) = [[ cos(θ),  0,  sin(θ) ],
             [  0,      1,    0    ],
             [-sin(θ),  0,  cos(θ) ]]
    """
    theta = np.radians(angle_deg)
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [ c,  0,  s],
        [ 0,  1,  0],
        [-s,  0,  c],
    ], dtype=float)


def rot_z(angle_deg: float) -> np.ndarray:
    """
    Matriz de rotação 3x3 em torno do eixo Z (positivo = sentido anti-horário
    quando visto de cima, i.e., do eixo Z positivo).

    Parâmetros
    ----------
    angle_deg : float
        Ângulo de rotação em graus.

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação Rz(θ).

    Notas
    -----
    Rz(θ) = [[cos(θ), -sin(θ), 0],
             [sin(θ),  cos(θ), 0],
             [  0,       0,    1]]
    """
    theta = np.radians(angle_deg)
    c, s = np.cos(theta), np.sin(theta)
    return np.array([
        [c, -s,  0],
        [s,  c,  0],
        [0,  0,  1],
    ], dtype=float)


def dip_dipdirection_to_normal(dip: float, dip_direction: float) -> np.ndarray:
    """
    Converte dip e dip direction para vetor normal unitário ao plano.

    Convenção de entrada (geológica padrão):
        - dip_direction: azimute da direção de mergulho máximo (0–360°, CW from N)
        - dip: ângulo de mergulho abaixo da horizontal (0° = horizontal, 90° = vertical)

    Sistema de coordenadas de saída: X = Leste, Y = Norte, Z = Cima.

    A normal aponta para o hemisfério superior (Z ≥ 0 para dip ≤ 90°).

    Parâmetros
    ----------
    dip : float
        Ângulo de mergulho em graus (0–90°).
    dip_direction : float
        Azimute da direção de mergulho em graus (0–360°, sentido horário a partir do Norte).

    Retorna
    -------
    np.ndarray, shape (3,)
        Vetor normal unitário [nx, ny, nz] onde:
            nx = sin(dip) * sin(dip_direction)   (componente Leste)
            ny = -sin(dip) * cos(dip_direction)  (componente Norte — negativa por convenção)
            nz = cos(dip)                         (componente vertical)

    Exemplos
    --------
    >>> dip_dipdirection_to_normal(0, 0)    # plano horizontal → normal para cima
    array([0., 0., 1.])
    >>> dip_dipdirection_to_normal(90, 0)   # plano vertical para Norte → normal aponta para Sul
    array([ 0., -1.,  0.])
    """
    dip_rad = np.radians(dip)
    dd_rad = np.radians(dip_direction)
    nx = -np.sin(dip_rad) * np.sin(dd_rad)
    ny = -np.sin(dip_rad) * np.cos(dd_rad)
    nz = np.cos(dip_rad)
    return np.array([nx, ny, nz], dtype=float)


def normal_to_dip_dipdirection(normal_vector: np.ndarray) -> tuple[float, float]:
    """
    Converte vetor normal unitário ao plano para dip e dip direction.

    Inverte a operação de dip_dipdirection_to_normal. O vetor de entrada
    não precisa ser unitário — é normalizado internamente.

    Parâmetros
    ----------
    normal_vector : array-like, shape (3,)
        Vetor normal ao plano no sistema X=Leste, Y=Norte, Z=Cima.

    Retorna
    -------
    dip : float
        Ângulo de mergulho em graus (0–90°).
    dip_direction : float
        Azimute da direção de mergulho em graus (0–360°).
    """
    n = np.asarray(normal_vector, dtype=float)
    n = n / np.linalg.norm(n)
    nx, ny, nz = n

    # Clip para evitar erros numéricos em arccos/arctan2
    nz = np.clip(nz, -1.0, 1.0)
    dip = np.degrees(np.arccos(nz))

    # dip direction: a horizontal component of the normal is (-sin(dip)*sin(dd), -sin(dip)*cos(dd))
    # so arctan2(-nx, -ny) recovers dd = arctan2(sin(dd), cos(dd))
    dip_direction = np.degrees(np.arctan2(-nx, -ny)) % 360.0

    return float(dip), float(dip_direction)


def euler_zxz_to_matrix(alpha: float, beta: float, gamma: float) -> np.ndarray:
    """
    Matriz de rotação composta pela sequência de Euler Z-X-Z.

    Ordem de aplicação: primeiro Rz(alpha), depois Rx(beta), depois Rz(gamma).

    R = Rz(alpha) · Rx(beta) · Rz(gamma)

    Parâmetros
    ----------
    alpha : float
        Ângulo da primeira rotação em torno de Z (em graus).
    beta : float
        Ângulo da segunda rotação em torno de X (em graus).
    gamma : float
        Ângulo da terceira rotação em torno de Z (em graus).

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação composta.
    """
    return rot_z(alpha) @ rot_x(beta) @ rot_z(gamma)


def euler_xyz_to_matrix(alpha: float, beta: float, gamma: float) -> np.ndarray:
    """
    Matriz de rotação composta pela sequência X-Y-Z (ângulos de Tait-Bryan).

    Ordem de aplicação: primeiro Rx(alpha), depois Ry(beta), depois Rz(gamma).

    R = Rx(alpha) · Ry(beta) · Rz(gamma)

    Parâmetros
    ----------
    alpha : float
        Ângulo da primeira rotação em torno de X (em graus).
    beta : float
        Ângulo da segunda rotação em torno de Y (em graus).
    gamma : float
        Ângulo da terceira rotação em torno de Z (em graus).

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de rotação composta.
    """
    return rot_x(alpha) @ rot_y(beta) @ rot_z(gamma)


def matrix_to_euler_zxz(R: np.ndarray) -> tuple[float, float, float]:
    """
    Decompõe uma matriz de rotação nos ângulos de Euler Z-X-Z.

    Resolve: R = Rz(alpha) · Rx(beta) · Rz(gamma)

    Trata o gimbal lock (singularidade quando beta = 0° ou beta = 180°):
        - Se sin(beta) ≈ 0, define alpha = 0 e calcula gamma como rotação única em Z.

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação ortogonal.

    Retorna
    -------
    alpha, beta, gamma : float
        Ângulos em graus. beta ∈ [0°, 180°], alpha e gamma ∈ [0°, 360°).

    Notas
    -----
    Para a decomposição Z-X-Z padrão, as fórmulas analíticas são:
        beta  = arccos(R[2, 2])
        alpha = atan2(R[0, 2], -R[1, 2])   quando sin(beta) ≠ 0
        gamma = atan2(R[2, 0],  R[2, 1])   quando sin(beta) ≠ 0
    """
    R = np.asarray(R, dtype=float)
    r33 = np.clip(R[2, 2], -1.0, 1.0)
    beta = np.degrees(np.arccos(r33))
    sin_beta = np.sin(np.radians(beta))

    if abs(sin_beta) < 1e-9:
        # Gimbal lock: beta ≈ 0° ou 180° → alpha + gamma ou alpha - gamma é definido
        alpha = 0.0
        if r33 > 0:
            # beta ≈ 0°: R ≈ Rz(alpha + gamma)
            gamma = np.degrees(np.arctan2(R[1, 0], R[0, 0])) % 360.0
        else:
            # beta ≈ 180°: R ≈ Rz(alpha - gamma)
            gamma = np.degrees(np.arctan2(-R[1, 0], R[0, 0])) % 360.0
    else:
        alpha = np.degrees(np.arctan2(R[0, 2], -R[1, 2])) % 360.0
        gamma = np.degrees(np.arctan2(R[2, 0],  R[2, 1])) % 360.0

    return float(alpha), float(beta), float(gamma)


def matrix_to_euler_xyz(R: np.ndarray) -> tuple[float, float, float]:
    """
    Decompõe uma matriz de rotação nos ângulos de Tait-Bryan X-Y-Z.

    Resolve: R = Rx(alpha) · Ry(beta) · Rz(gamma)

    Trata o gimbal lock (singularidade quando beta = ±90°):
        - Se cos(beta) ≈ 0, define gamma = 0 e calcula alpha como rotação única em X.

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação ortogonal.

    Retorna
    -------
    alpha, beta, gamma : float
        Ângulos em graus. beta ∈ (-90°, 90°], alpha e gamma ∈ (-180°, 180°].

    Notas
    -----
    Para a decomposição X-Y-Z:
        beta  = arcsin(-R[2, 0])
        alpha = atan2(R[2, 1], R[2, 2])   quando cos(beta) ≠ 0
        gamma = atan2(R[1, 0], R[0, 0])   quando cos(beta) ≠ 0
    """
    # Para R = Rx(α)·Ry(β)·Rz(γ), o elemento R[0,2] = sin(β).
    # α = arctan2(-R[1,2], R[2,2]),  γ = arctan2(-R[0,1], R[0,0])
    R = np.asarray(R, dtype=float)
    val = np.clip(R[0, 2], -1.0, 1.0)
    beta = np.degrees(np.arcsin(val))
    cos_beta = np.cos(np.radians(beta))

    if abs(cos_beta) < 1e-9:
        # Gimbal lock: beta ≈ ±90°
        gamma = 0.0
        if val > 0:
            alpha = np.degrees(np.arctan2(R[1, 0], R[1, 1]))
        else:
            alpha = np.degrees(np.arctan2(-R[1, 0], R[1, 1]))
    else:
        alpha = np.degrees(np.arctan2(-R[1, 2], R[2, 2]))
        gamma = np.degrees(np.arctan2(-R[0, 1], R[0, 0]))

    return float(alpha), float(beta), float(gamma)
