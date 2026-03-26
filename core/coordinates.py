"""
core/coordinates.py
===================
Funções para manipulação de coordenadas de pontos e sondagens
entre os softwares Leapfrog, Isatis.neo e Vulcan.

Sistema de referência padrão: X=Leste, Y=Norte, Z=Cota (altitude positiva para cima).

Diferença crítica — convenção de Z do Vulcan para sondagens:
    Vulcan armazena profundidade de sondagem como Z positivo para baixo.
    Para converter para coordenadas geográficas: Z_geo = -Z_profundidade

Nota sobre reprojeção geodésica:
    Conversões entre fusos UTM ou entre datum SAD69/SIRGAS 2000 requerem
    a biblioteca pyproj (não incluída neste módulo por ser opcional).
"""

import numpy as np
import pandas as pd


def vulcan_depth_to_elevation(depth_z: float, collar_z: float) -> float:
    """
    Converte profundidade de sondagem do Vulcan para cota geográfica.

    No Vulcan, a profundidade é positiva para baixo a partir da boca do furo.
    A cota geográfica é: Z_geo = Z_boca - profundidade

    Parâmetros
    ----------
    depth_z : float
        Profundidade acumulada ao longo do furo (Z positivo para baixo), em metros.
    collar_z : float
        Cota da boca do furo (Z geográfico, positivo para cima), em metros.

    Retorna
    -------
    float
        Cota geográfica do ponto (positivo para cima).
    """
    return float(collar_z - depth_z)


def elevation_to_vulcan_depth(elevation: float, collar_z: float) -> float:
    """
    Converte cota geográfica para profundidade de sondagem no formato Vulcan.

    Parâmetros
    ----------
    elevation : float
        Cota geográfica do ponto (positivo para cima), em metros.
    collar_z : float
        Cota da boca do furo (positivo para cima), em metros.

    Retorna
    -------
    float
        Profundidade acumulada (positivo para baixo), em metros.
    """
    return float(collar_z - elevation)


def standardize_columns(
    df: pd.DataFrame,
    x_col: str = "X",
    y_col: str = "Y",
    z_col: str = "Z",
) -> pd.DataFrame:
    """
    Renomeia colunas de um DataFrame para o padrão interno X, Y, Z.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame com colunas de coordenadas.
    x_col, y_col, z_col : str
        Nomes atuais das colunas X, Y, Z no DataFrame de entrada.

    Retorna
    -------
    pd.DataFrame
        Cópia do DataFrame com colunas renomeadas para X, Y, Z.
    """
    df = df.copy()
    df = df.rename(columns={x_col: "X", y_col: "Y", z_col: "Z"})
    return df


def flip_z_sign(df: pd.DataFrame, z_col: str = "Z") -> pd.DataFrame:
    """
    Inverte o sinal da coluna Z — útil para converter entre
    profundidade (Vulcan, positivo para baixo) e cota (positivo para cima).

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame com coluna Z.
    z_col : str
        Nome da coluna Z.

    Retorna
    -------
    pd.DataFrame
        Cópia do DataFrame com Z negado.
    """
    df = df.copy()
    df[z_col] = -df[z_col]
    return df
