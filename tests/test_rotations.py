"""
tests/test_rotations.py
=======================
Testes unitários para core/rotations.py.
"""

import numpy as np
import pytest
from core.rotations import (
    rot_x, rot_y, rot_z,
    dip_dipdirection_to_normal,
    normal_to_dip_dipdirection,
    euler_zxz_to_matrix,
    euler_xyz_to_matrix,
    matrix_to_euler_zxz,
    matrix_to_euler_xyz,
)

TOL = 1e-9


# ---------------------------------------------------------------------------
# Matrizes elementares de rotação
# ---------------------------------------------------------------------------

def test_rot_x_identity():
    """Rotação de 0° em torno de X deve ser matriz identidade."""
    assert np.allclose(rot_x(0), np.eye(3), atol=TOL)


def test_rot_y_identity():
    """Rotação de 0° em torno de Y deve ser matriz identidade."""
    assert np.allclose(rot_y(0), np.eye(3), atol=TOL)


def test_rot_z_identity():
    """Rotação de 0° em torno de Z deve ser matriz identidade."""
    assert np.allclose(rot_z(0), np.eye(3), atol=TOL)


def test_rot_x_90():
    """Rotação de 90° em torno de X: Y→Z, Z→-Y."""
    R = rot_x(90)
    expected = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=float)
    assert np.allclose(R, expected, atol=TOL)


def test_rot_z_90():
    """Rotação de 90° em torno de Z: X→Y, Y→-X."""
    R = rot_z(90)
    expected = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=float)
    assert np.allclose(R, expected, atol=TOL)


def test_rot_is_orthogonal():
    """Matrizes de rotação devem ser ortogonais (R^T · R = I)."""
    for angle in [0, 30, 45, 90, 135, 180, 270, 360]:
        for R in [rot_x(angle), rot_y(angle), rot_z(angle)]:
            assert np.allclose(R.T @ R, np.eye(3), atol=TOL)


def test_rot_determinant_is_one():
    """Matrizes de rotação devem ter determinante = 1."""
    for angle in [15, 45, 90, 180]:
        for R in [rot_x(angle), rot_y(angle), rot_z(angle)]:
            assert abs(np.linalg.det(R) - 1.0) < TOL


# ---------------------------------------------------------------------------
# dip_dipdirection_to_normal
# ---------------------------------------------------------------------------

def test_normal_horizontal():
    """Disco horizontal (dip=0): normal deve apontar para cima (0, 0, 1)."""
    n = dip_dipdirection_to_normal(0, 0)
    assert np.allclose(n, [0, 0, 1], atol=TOL)


def test_normal_vertical_north():
    """Disco vertical mergulhando para Norte (dip=90, dir=0): normal = (0, -1, 0)."""
    n = dip_dipdirection_to_normal(90, 0)
    assert np.allclose(n, [0, -1, 0], atol=TOL)


def test_normal_vertical_east():
    """Disco vertical mergulhando para Leste (dip=90, dir=90): normal = (-1, 0, 0) (oposta ao mergulho)."""
    n = dip_dipdirection_to_normal(90, 90)
    assert np.allclose(n, [-1, 0, 0], atol=TOL)


def test_normal_45_north():
    """Disco 45° para Norte: normal = (0, -sin45, cos45) — componente Y oposta ao mergulho Norte."""
    n = dip_dipdirection_to_normal(45, 0)
    # nx = -sin(45)*sin(0) = 0, ny = -sin(45)*cos(0) = -sin45, nz = cos45
    expected = np.array([0, -np.sin(np.radians(45)), np.cos(np.radians(45))])
    assert np.allclose(n, expected, atol=TOL)


def test_normal_unit_length():
    """Vetor normal deve ser unitário para qualquer dip/dip_direction."""
    for dip in [0, 30, 45, 60, 90]:
        for dd in [0, 45, 90, 180, 270]:
            n = dip_dipdirection_to_normal(dip, dd)
            assert abs(np.linalg.norm(n) - 1.0) < TOL


# ---------------------------------------------------------------------------
# Round-trip normal ↔ dip/dip_direction
# ---------------------------------------------------------------------------

def test_roundtrip_normal_to_dip():
    """Round-trip dip_dipdirection_to_normal → normal_to_dip_dipdirection."""
    test_cases = [(0, 0), (30, 45), (60, 90), (90, 180), (45, 270)]
    for dip_in, dd_in in test_cases:
        n = dip_dipdirection_to_normal(dip_in, dd_in)
        dip_out, dd_out = normal_to_dip_dipdirection(n)
        assert abs(dip_out - dip_in) < 1e-6, f"dip mismatch: {dip_out} != {dip_in}"
        # Para dip=0, dip_direction é indeterminado
        if dip_in > 0:
            dd_diff = abs((dd_out - dd_in + 360) % 360)
            dd_diff = min(dd_diff, 360 - dd_diff)
            assert dd_diff < 1e-4, f"dir mismatch: {dd_out} != {dd_in}"


# ---------------------------------------------------------------------------
# Euler ZXZ round-trip
# ---------------------------------------------------------------------------

def test_euler_zxz_roundtrip():
    """Round-trip euler_zxz_to_matrix → matrix_to_euler_zxz."""
    test_cases = [
        (0, 0, 0),
        (30, 45, 60),
        (90, 30, 45),
        (180, 90, 270),
        (45, 10, 300),
    ]
    for a, b, g in test_cases:
        R = euler_zxz_to_matrix(a, b, g)
        a2, b2, g2 = matrix_to_euler_zxz(R)
        R2 = euler_zxz_to_matrix(a2, b2, g2)
        assert np.allclose(R, R2, atol=1e-9), f"ZXZ roundtrip failed for ({a},{b},{g})"


# ---------------------------------------------------------------------------
# Euler XYZ round-trip
# ---------------------------------------------------------------------------

def test_euler_xyz_roundtrip():
    """Round-trip euler_xyz_to_matrix → matrix_to_euler_xyz."""
    test_cases = [
        (0, 0, 0),
        (30, 45, 60),
        (10, 20, 80),
        (-30, 45, -60),
    ]
    for a, b, g in test_cases:
        R = euler_xyz_to_matrix(a, b, g)
        a2, b2, g2 = matrix_to_euler_xyz(R)
        R2 = euler_xyz_to_matrix(a2, b2, g2)
        assert np.allclose(R, R2, atol=1e-9), f"XYZ roundtrip failed for ({a},{b},{g})"
