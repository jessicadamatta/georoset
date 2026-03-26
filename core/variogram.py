"""
core/variogram.py
=================
Funções utilitárias para construção e decomposição de elipsoides de anisotropia
de variograma, independente da convenção de software.

Sistema de coordenadas padrão interno: X=Leste, Y=Norte, Z=Cima.

A elipsoide é definida pela matriz de rotação R e pelos semieixos (a1, a2, a3),
onde a1 ≥ a2 ≥ a3 por convenção (maior → menor alcance).
"""

import numpy as np
from core.rotations import euler_zxz_to_matrix, euler_xyz_to_matrix


def build_anisotropy_matrix(
    R: np.ndarray,
    a1: float,
    a2: float,
    a3: float,
) -> np.ndarray:
    """
    Constrói a matriz de anisotropia A = R · diag(a1, a2, a3) · R^T.

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação que alinha os eixos da elipsoide com os eixos globais.
    a1, a2, a3 : float
        Semieixos (alcances) da elipsoide de anisotropia.

    Retorna
    -------
    np.ndarray, shape (3, 3)
        Matriz de anisotropia simétrica positiva-definida.
    """
    D = np.diag([a1, a2, a3])
    return R @ D @ R.T


def ellipsoid_surface(R: np.ndarray, a1: float, a2: float, a3: float, n: int = 30):
    """
    Gera pontos na superfície da elipsoide de anisotropia para plotagem 3D.

    Parâmetros
    ----------
    R : np.ndarray, shape (3, 3)
        Matriz de rotação da elipsoide.
    a1, a2, a3 : float
        Semieixos da elipsoide.
    n : int
        Número de pontos por ângulo paramétrico (resolução da malha).

    Retorna
    -------
    X, Y, Z : np.ndarray, shape (n, n)
        Coordenadas dos pontos na superfície, no sistema global X=E, Y=N, Z=Cima.
    """
    u = np.linspace(0, 2 * np.pi, n)
    v = np.linspace(0, np.pi, n)
    # Esfera unitária parametrizada
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))

    # Escalar pelos semieixos e rotacionar
    pts = np.stack([xs * a1, ys * a2, zs * a3], axis=-1)  # (n, n, 3)
    rotated = pts @ R.T  # aplica R a cada ponto
    return rotated[..., 0], rotated[..., 1], rotated[..., 2]
