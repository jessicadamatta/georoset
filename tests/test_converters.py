"""
tests/test_converters.py
========================
Testes de conversão entre softwares.

Casos obrigatórios:
    - Disco horizontal (dip=0): normal = (0, 0, 1)
    - Disco vertical para Norte (dip=90, dir=0): normal = (0, -1, 0)
    - Round-trip Leapfrog → Vulcan → Leapfrog: tolerância 1e-6
    - Round-trip variograma e modelo de blocos
"""

import numpy as np
import pytest
from converters.cross_converters import (
    leapfrog_to_vulcan_disc,
    vulcan_to_leapfrog_disc,
    leapfrog_to_isatis_disc,
    isatis_to_leapfrog_disc,
    vulcan_to_isatis_disc,
    isatis_to_vulcan_disc,
    leapfrog_to_vulcan_vario,
    vulcan_to_leapfrog_vario,
    leapfrog_to_vulcan_block,
    vulcan_to_leapfrog_block,
)
from converters import vulcan, leapfrog

TOL = 1e-6


# ===========================================================================
# Casos obrigatórios de discos
# ===========================================================================

def test_horizontal_disc_normal():
    """Disco horizontal (dip=0): normal deve ser (0, 0, 1)."""
    n = leapfrog.disc_to_normal(0, 0)
    assert np.allclose(n, [0, 0, 1], atol=TOL)


def test_vertical_north_disc_normal():
    """Disco vertical para Norte (dip=90, dir=0): normal deve ser (0, -1, 0)."""
    n = leapfrog.disc_to_normal(90, 0)
    assert np.allclose(n, [0, -1, 0], atol=TOL)


def test_vulcan_disc_horizontal():
    """Disco horizontal no Vulcan: bearing=qualquer, plunge=90°."""
    bearing, plunge = leapfrog_to_vulcan_disc(0, 0)
    assert abs(plunge - 90) < TOL


def test_vulcan_disc_vertical_north():
    """Disco vertical para Norte: bearing=180°, plunge=0° no Vulcan."""
    bearing, plunge = leapfrog_to_vulcan_disc(90, 0)
    assert abs(plunge - 0) < TOL
    assert abs((bearing - 180) % 360) < TOL


def test_vulcan_disc_vertical_east():
    """Disco vertical para Leste (dip=90, dir=90): bearing=270°, plunge=0° no Vulcan."""
    bearing, plunge = leapfrog_to_vulcan_disc(90, 90)
    assert abs(plunge - 0) < TOL
    assert abs((bearing - 270) % 360) < TOL


# ===========================================================================
# Round-trip Leapfrog → Vulcan → Leapfrog (discos)
# ===========================================================================

@pytest.mark.parametrize("dip,dip_dir", [
    (0, 0),
    (30, 45),
    (45, 90),
    (60, 135),
    (90, 0),
    (90, 180),
    (90, 270),
    (45, 315),
])
def test_roundtrip_leapfrog_vulcan_disc(dip, dip_dir):
    """Round-trip Leapfrog → Vulcan → Leapfrog para discos."""
    bearing, plunge = leapfrog_to_vulcan_disc(dip, dip_dir)
    dip_out, dd_out = vulcan_to_leapfrog_disc(bearing, plunge)
    assert abs(dip_out - dip) < TOL, f"dip mismatch: {dip_out} != {dip}"
    if dip > 0:
        dd_diff = abs((dd_out - dip_dir + 360) % 360)
        dd_diff = min(dd_diff, 360 - dd_diff)
        assert dd_diff < TOL, f"dir mismatch: {dd_out} != {dip_dir}"


# ===========================================================================
# Round-trip Leapfrog ↔ Isatis.neo (discos — convenções idênticas)
# ===========================================================================

@pytest.mark.parametrize("dip,dip_dir", [
    (0, 0), (30, 45), (90, 270)
])
def test_roundtrip_leapfrog_isatis_disc(dip, dip_dir):
    """Round-trip Leapfrog → Isatis.neo → Leapfrog para discos."""
    dip_i, az_i = leapfrog_to_isatis_disc(dip, dip_dir)
    dip_out, dd_out = isatis_to_leapfrog_disc(dip_i, az_i)
    assert abs(dip_out - dip) < TOL
    if dip > 0:
        dd_diff = abs((dd_out - dip_dir + 360) % 360)
        dd_diff = min(dd_diff, 360 - dd_diff)
        assert dd_diff < TOL


# ===========================================================================
# Round-trip variograma
# ===========================================================================

@pytest.mark.parametrize("bearing,plunge,rake", [
    (0, 0, 0),
    (30, 20, 10),
    (90, 45, 30),
    (180, 0, 90),
])
def test_roundtrip_vario_leapfrog_vulcan(bearing, plunge, rake):
    """Round-trip variograma Leapfrog → Vulcan → Leapfrog."""
    from converters.leapfrog import vario_to_matrix
    R_orig = vario_to_matrix(bearing, plunge, rake)
    b_v, p_v, d_v = leapfrog_to_vulcan_vario(bearing, plunge, rake)
    b_lf, p_lf, r_lf = vulcan_to_leapfrog_vario(b_v, p_v, d_v)
    from converters.leapfrog import vario_to_matrix as v2m
    R_roundtrip = v2m(b_lf, p_lf, r_lf)
    assert np.allclose(R_orig, R_roundtrip, atol=TOL), (
        f"Variograma roundtrip falhou para ({bearing},{plunge},{rake})"
    )


# ===========================================================================
# Round-trip modelo de blocos
# ===========================================================================

@pytest.mark.parametrize("bearing,plunge,dip", [
    (0, 0, 0),
    (45, 30, 15),
    (90, 45, 30),
    (180, 0, 90),
])
def test_roundtrip_block_leapfrog_vulcan(bearing, plunge, dip):
    """Round-trip modelo de blocos Leapfrog → Vulcan → Leapfrog."""
    from converters.leapfrog import block_to_matrix
    R_orig = block_to_matrix(bearing, plunge, dip)
    b_v, p_v, d_v = leapfrog_to_vulcan_block(bearing, plunge, dip)
    b_lf, p_lf, d_lf = vulcan_to_leapfrog_block(b_v, p_v, d_v)
    R_roundtrip = block_to_matrix(b_lf, p_lf, d_lf)
    assert np.allclose(R_orig, R_roundtrip, atol=TOL), (
        f"Bloco roundtrip falhou para ({bearing},{plunge},{dip})"
    )
