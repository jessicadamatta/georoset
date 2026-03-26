"""
converters/cross_converters.py
================================
Funções de conversão direta entre pares de softwares.

Todas as conversões passam pelo vetor normal unitário (sistema interno GeoRoset)
ou pela matriz de rotação como formato intermediário.

Funções disponíveis:
    Discos estruturais:
        leapfrog_to_vulcan_disc, vulcan_to_leapfrog_disc
        leapfrog_to_isatis_disc, isatis_to_leapfrog_disc
        vulcan_to_isatis_disc,   isatis_to_vulcan_disc

    Variograma:
        leapfrog_to_vulcan_vario, vulcan_to_leapfrog_vario
        leapfrog_to_isatis_vario, isatis_to_leapfrog_vario
        vulcan_to_isatis_vario,   isatis_to_vulcan_vario

    Modelo de blocos:
        leapfrog_to_vulcan_block, vulcan_to_leapfrog_block
        leapfrog_to_isatis_block, isatis_to_leapfrog_block
        vulcan_to_isatis_block,   isatis_to_vulcan_block
"""

import numpy as np
from converters import leapfrog, isatis_neo, vulcan


# ===========================================================================
# Discos estruturais
# ===========================================================================

def leapfrog_to_vulcan_disc(dip: float, dip_direction: float) -> tuple[float, float]:
    """
    Converte disco estrutural do Leapfrog para o formato Vulcan.

    Leapfrog: dip + dip_direction (azimute do mergulho)
    Vulcan:   bearing + plunge (azimute e inclinação da NORMAL ao plano)

    Relações:
        plunge_vulcan    = 90° − dip
        bearing_vulcan   = (dip_direction + 180°) mod 360°

    Parâmetros
    ----------
    dip : float
        Ângulo de mergulho em graus.
    dip_direction : float
        Azimute do mergulho em graus.

    Retorna
    -------
    bearing : float
        Azimute da normal (Vulcan) em graus.
    plunge : float
        Inclinação da normal (Vulcan) em graus.
    """
    normal = leapfrog.disc_to_normal(dip, dip_direction)
    return vulcan.normal_to_disc(normal)


def vulcan_to_leapfrog_disc(bearing: float, plunge: float) -> tuple[float, float]:
    """
    Converte disco estrutural do Vulcan para o formato Leapfrog.

    Parâmetros
    ----------
    bearing : float
        Azimute da normal (Vulcan) em graus.
    plunge : float
        Inclinação da normal (Vulcan) em graus.

    Retorna
    -------
    dip : float
        Ângulo de mergulho (Leapfrog) em graus.
    dip_direction : float
        Azimute do mergulho (Leapfrog) em graus.
    """
    normal = vulcan.disc_to_normal(bearing, plunge)
    return leapfrog.normal_to_disc(normal)


def leapfrog_to_isatis_disc(dip: float, dip_direction: float) -> tuple[float, float]:
    """
    Converte disco estrutural do Leapfrog para o Isatis.neo.

    Como as convenções de disco são idênticas, esta é uma passagem direta.

    Parâmetros
    ----------
    dip : float
        Ângulo de mergulho em graus.
    dip_direction : float
        Azimute do mergulho em graus.

    Retorna
    -------
    dip : float
        Ângulo de mergulho (Isatis.neo).
    azimuth : float
        Azimute (Isatis.neo).
    """
    normal = leapfrog.disc_to_normal(dip, dip_direction)
    return isatis_neo.normal_to_disc(normal)


def isatis_to_leapfrog_disc(dip: float, azimuth: float) -> tuple[float, float]:
    """
    Converte disco estrutural do Isatis.neo para o Leapfrog.

    Parâmetros
    ----------
    dip : float
        Ângulo de mergulho (Isatis.neo) em graus.
    azimuth : float
        Azimute (Isatis.neo) em graus.

    Retorna
    -------
    dip : float
        Ângulo de mergulho (Leapfrog).
    dip_direction : float
        Azimute do mergulho (Leapfrog).
    """
    normal = isatis_neo.disc_to_normal(dip, azimuth)
    return leapfrog.normal_to_disc(normal)


def vulcan_to_isatis_disc(bearing: float, plunge: float) -> tuple[float, float]:
    """
    Converte disco estrutural do Vulcan para o Isatis.neo.

    Parâmetros
    ----------
    bearing : float
        Azimute da normal (Vulcan) em graus.
    plunge : float
        Inclinação da normal (Vulcan) em graus.

    Retorna
    -------
    dip : float
        Ângulo de mergulho (Isatis.neo) em graus.
    azimuth : float
        Azimute (Isatis.neo) em graus.
    """
    normal = vulcan.disc_to_normal(bearing, plunge)
    return isatis_neo.normal_to_disc(normal)


def isatis_to_vulcan_disc(dip: float, azimuth: float) -> tuple[float, float]:
    """
    Converte disco estrutural do Isatis.neo para o Vulcan.

    Parâmetros
    ----------
    dip : float
        Ângulo de mergulho (Isatis.neo) em graus.
    azimuth : float
        Azimute (Isatis.neo) em graus.

    Retorna
    -------
    bearing : float
        Azimute da normal (Vulcan) em graus.
    plunge : float
        Inclinação da normal (Vulcan) em graus.
    """
    normal = isatis_neo.disc_to_normal(dip, azimuth)
    return vulcan.normal_to_disc(normal)


# ===========================================================================
# Variograma
# ===========================================================================

def leapfrog_to_vulcan_vario(
    bearing: float, plunge: float, rake: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de variograma do Leapfrog para o Vulcan.

    Estratégia: montar R no formato Leapfrog, depois decompor no formato Vulcan.

    Parâmetros
    ----------
    bearing, plunge, rake : float
        Ângulos do variograma no formato Leapfrog (em graus).

    Retorna
    -------
    bearing_v, plunge_v, dip_v : float
        Ângulos do variograma no formato Vulcan (em graus).
    """
    R = leapfrog.vario_to_matrix(bearing, plunge, rake)
    return vulcan.matrix_to_vario(R)


def vulcan_to_leapfrog_vario(
    bearing: float, plunge: float, dip: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de variograma do Vulcan para o Leapfrog.

    Parâmetros
    ----------
    bearing, plunge, dip : float
        Ângulos do variograma no formato Vulcan (em graus).

    Retorna
    -------
    bearing_lf, plunge_lf, rake_lf : float
        Ângulos do variograma no formato Leapfrog (em graus).
    """
    R = vulcan.vario_to_matrix(bearing, plunge, dip)
    return leapfrog.matrix_to_vario(R)


def leapfrog_to_isatis_vario(
    bearing: float, plunge: float, rake: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de variograma do Leapfrog para o Isatis.neo.

    ⚠️ Conversão sujeita à incerteza de sinal do Isatis.neo.
    # TODO: validar com documentação oficial Isatis.neo

    Parâmetros
    ----------
    bearing, plunge, rake : float
        Ângulos do variograma no formato Leapfrog (em graus).

    Retorna
    -------
    azimuth, dip, rake_out : float
        Ângulos do variograma no formato Isatis.neo (em graus).
    """
    R = leapfrog.vario_to_matrix(bearing, plunge, rake)
    return isatis_neo.matrix_to_vario(R)


def isatis_to_leapfrog_vario(
    azimuth: float, dip: float, rake: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de variograma do Isatis.neo para o Leapfrog.

    ⚠️ Conversão sujeita à incerteza de sinal do Isatis.neo.
    # TODO: validar com documentação oficial Isatis.neo

    Parâmetros
    ----------
    azimuth, dip, rake : float
        Ângulos do variograma no formato Isatis.neo (em graus).

    Retorna
    -------
    bearing_lf, plunge_lf, rake_lf : float
        Ângulos do variograma no formato Leapfrog (em graus).
    """
    R = isatis_neo.vario_to_matrix(azimuth, dip, rake)
    return leapfrog.matrix_to_vario(R)


def vulcan_to_isatis_vario(
    bearing: float, plunge: float, dip: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de variograma do Vulcan para o Isatis.neo.

    ⚠️ Conversão sujeita à incerteza de sinal do Isatis.neo.
    # TODO: validar com documentação oficial Isatis.neo

    Parâmetros
    ----------
    bearing, plunge, dip : float
        Ângulos do variograma no formato Vulcan (em graus).

    Retorna
    -------
    azimuth, dip_out, rake : float
        Ângulos do variograma no formato Isatis.neo (em graus).
    """
    R = vulcan.vario_to_matrix(bearing, plunge, dip)
    return isatis_neo.matrix_to_vario(R)


def isatis_to_vulcan_vario(
    azimuth: float, dip: float, rake: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de variograma do Isatis.neo para o Vulcan.

    ⚠️ Conversão sujeita à incerteza de sinal do Isatis.neo.
    # TODO: validar com documentação oficial Isatis.neo

    Parâmetros
    ----------
    azimuth, dip, rake : float
        Ângulos do variograma no formato Isatis.neo (em graus).

    Retorna
    -------
    bearing_v, plunge_v, dip_v : float
        Ângulos do variograma no formato Vulcan (em graus).
    """
    R = isatis_neo.vario_to_matrix(azimuth, dip, rake)
    return vulcan.matrix_to_vario(R)


# ===========================================================================
# Modelo de blocos
# ===========================================================================

def leapfrog_to_vulcan_block(
    bearing: float, plunge: float, dip: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de modelo de blocos do Leapfrog para o Vulcan.

    Parâmetros
    ----------
    bearing, plunge, dip : float
        Ângulos no formato Leapfrog (em graus).

    Retorna
    -------
    bearing_v, plunge_v, dip_v : float
        Ângulos no formato Vulcan (em graus).
    """
    R = leapfrog.block_to_matrix(bearing, plunge, dip)
    return vulcan.matrix_to_block(R)


def vulcan_to_leapfrog_block(
    bearing: float, plunge: float, dip: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de modelo de blocos do Vulcan para o Leapfrog.

    Parâmetros
    ----------
    bearing, plunge, dip : float
        Ângulos no formato Vulcan (em graus).

    Retorna
    -------
    bearing_lf, plunge_lf, dip_lf : float
        Ângulos no formato Leapfrog (em graus).
    """
    R = vulcan.block_to_matrix(bearing, plunge, dip)
    return leapfrog.matrix_to_block(R)


def leapfrog_to_isatis_block(
    bearing: float, plunge: float, dip: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de modelo de blocos do Leapfrog para o Isatis.neo.

    # TODO: validar sinais com documentação oficial Isatis.neo

    Parâmetros
    ----------
    bearing, plunge, dip : float
        Ângulos no formato Leapfrog (em graus).

    Retorna
    -------
    azimuth, dip_out, rake : float
        Ângulos no formato Isatis.neo (em graus).
    """
    R = leapfrog.block_to_matrix(bearing, plunge, dip)
    return isatis_neo.matrix_to_block(R)


def isatis_to_leapfrog_block(
    azimuth: float, dip: float, rake: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de modelo de blocos do Isatis.neo para o Leapfrog.

    # TODO: validar sinais com documentação oficial Isatis.neo

    Parâmetros
    ----------
    azimuth, dip, rake : float
        Ângulos no formato Isatis.neo (em graus).

    Retorna
    -------
    bearing_lf, plunge_lf, dip_lf : float
        Ângulos no formato Leapfrog (em graus).
    """
    R = isatis_neo.block_to_matrix(azimuth, dip, rake)
    return leapfrog.matrix_to_block(R)


def vulcan_to_isatis_block(
    bearing: float, plunge: float, dip: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de modelo de blocos do Vulcan para o Isatis.neo.

    # TODO: validar sinais com documentação oficial Isatis.neo

    Parâmetros
    ----------
    bearing, plunge, dip : float
        Ângulos no formato Vulcan (em graus).

    Retorna
    -------
    azimuth, dip_out, rake : float
        Ângulos no formato Isatis.neo (em graus).
    """
    R = vulcan.block_to_matrix(bearing, plunge, dip)
    return isatis_neo.matrix_to_block(R)


def isatis_to_vulcan_block(
    azimuth: float, dip: float, rake: float
) -> tuple[float, float, float]:
    """
    Converte ângulos de modelo de blocos do Isatis.neo para o Vulcan.

    # TODO: validar sinais com documentação oficial Isatis.neo

    Parâmetros
    ----------
    azimuth, dip, rake : float
        Ângulos no formato Isatis.neo (em graus).

    Retorna
    -------
    bearing_v, plunge_v, dip_v : float
        Ângulos no formato Vulcan (em graus).
    """
    R = isatis_neo.block_to_matrix(azimuth, dip, rake)
    return vulcan.matrix_to_block(R)
