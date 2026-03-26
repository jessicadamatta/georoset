"""
tests/test_structural.py
========================
Testes unitários para core/structural.py.
"""

import numpy as np
import pytest
from core.structural import (
    dip_dipdirection_to_strike_dip,
    strike_dip_to_dip_dipdirection,
    dip_dipdirection_to_pole,
    pole_to_dip_dipdirection,
    strike_dip_to_pole,
    pole_to_strike_dip,
)

TOL = 1e-9


def test_strike_from_dip_direction():
    """Strike deve ser dip_direction - 90°."""
    strike, dip = dip_dipdirection_to_strike_dip(45, 180)
    assert abs(strike - 90) < TOL
    assert abs(dip - 45) < TOL


def test_dip_direction_from_strike():
    """dip_direction deve ser strike + 90°."""
    dip, dd = strike_dip_to_dip_dipdirection(90, 45)
    assert abs(dd - 180) < TOL
    assert abs(dip - 45) < TOL


def test_roundtrip_strike_dip():
    """Round-trip dip_dipdirection → strike_dip → dip_dipdirection."""
    cases = [(30, 0), (45, 90), (60, 270), (0, 180)]
    for dip_in, dd_in in cases:
        strike, dip_s = dip_dipdirection_to_strike_dip(dip_in, dd_in)
        dip_out, dd_out = strike_dip_to_dip_dipdirection(strike, dip_s)
        assert abs(dip_out - dip_in) < TOL
        dd_diff = abs((dd_out - dd_in + 360) % 360)
        assert min(dd_diff, 360 - dd_diff) < 1e-6


def test_pole_horizontal():
    """Polo de disco horizontal = (0, 0, 1)."""
    pole = dip_dipdirection_to_pole(0, 0)
    assert np.allclose(pole, [0, 0, 1], atol=TOL)


def test_pole_vertical_north():
    """Polo de disco vertical para Norte = (0, -1, 0)."""
    pole = dip_dipdirection_to_pole(90, 0)
    assert np.allclose(pole, [0, -1, 0], atol=TOL)


def test_roundtrip_pole():
    """Round-trip dip_dipdirection → pole → dip_dipdirection."""
    cases = [(30, 45), (60, 135), (90, 270)]
    for dip_in, dd_in in cases:
        pole = dip_dipdirection_to_pole(dip_in, dd_in)
        dip_out, dd_out = pole_to_dip_dipdirection(pole)
        assert abs(dip_out - dip_in) < 1e-6
        dd_diff = abs((dd_out - dd_in + 360) % 360)
        assert min(dd_diff, 360 - dd_diff) < 1e-4
