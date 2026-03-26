"""
core/blockmodel.py
==================
Funções para rotação de modelos de blocos.

A rotação do modelo de blocos define a orientação dos eixos locais U, V, W
em relação ao sistema global X=Leste, Y=Norte, Z=Cima.

A matriz de rotação R transforma coordenadas do sistema local para o global:
    p_global = R · p_local
"""

import numpy as np
from core.rotations import euler_zxz_to_matrix, euler_xyz_to_matrix


def block_axes(R: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Extrai os vetores dos eixos locais U, V, W a partir da matriz de rotação.

    Os vetores são as colunas da matriz R (representam as direções dos eixos
    locais no sistema global).

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação do modelo de blocos.

    Retorna
    -------
    u, v, w : np.ndarray, shape (3,)
        Vetores unitários dos eixos locais U (vermelho), V (verde), W (azul)
        no sistema global.
    """
    return R[:, 0], R[:, 1], R[:, 2]


def unit_block_corners(R: np.ndarray) -> np.ndarray:
    """
    Calcula os 8 cantos de um bloco unitário centrado na origem,
    após rotação pela matriz R.

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação.

    Retorna
    -------
    np.ndarray, shape (8, 3)
        Coordenadas dos 8 cantos no sistema global.
    """
    corners_local = np.array([
        [-0.5, -0.5, -0.5],
        [ 0.5, -0.5, -0.5],
        [ 0.5,  0.5, -0.5],
        [-0.5,  0.5, -0.5],
        [-0.5, -0.5,  0.5],
        [ 0.5, -0.5,  0.5],
        [ 0.5,  0.5,  0.5],
        [-0.5,  0.5,  0.5],
    ], dtype=float)
    return (R @ corners_local.T).T
