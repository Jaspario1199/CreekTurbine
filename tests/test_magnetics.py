"""Magnetic coupling model: pressure, gap derating, torque, sizing."""

import math

import pytest

from creekturbine import magnetics as m


def test_magnetic_pressure_hand_value():
    # B²/(2μ0) at 1 T = 1/(2*4πe-7) ≈ 397,887 Pa
    assert m.magnetic_pressure(1.0) == pytest.approx(397887, rel=1e-3)
    # scales with B²
    assert m.magnetic_pressure(2.0) == pytest.approx(4 * m.magnetic_pressure(1.0))


def test_gap_field_derating():
    # B_r * t/(t+gap): 1.3 * 6/9 = 0.8667
    assert m.gap_field(1.3, 0.006, 0.003) == pytest.approx(0.86667, abs=1e-4)
    # zero gap -> full B_r
    assert m.gap_field(1.3, 0.006, 0.0) == pytest.approx(1.3)
    # bigger gap -> weaker field
    assert m.gap_field(1.3, 0.006, 0.010) < m.gap_field(1.3, 0.006, 0.003)


def test_shear_stress_in_empirical_band():
    # a well-designed NdFeB coupling at a small gap sits ~10-40 kPa
    tau = m.shear_stress(m.gap_field(1.3, 0.006, 0.003))
    assert 10_000 < tau < 40_000


def test_default_coupling_torque():
    c = m.AxialMagCoupling()
    # 12 x 15mm N42 magnets at R=55mm, 3mm gap -> ~4.2 N·m
    assert c.max_torque() == pytest.approx(4.18, abs=0.1)


def test_more_magnets_more_torque():
    small = m.AxialMagCoupling(n_magnets=8)
    big = m.AxialMagCoupling(n_magnets=16)
    assert big.max_torque() == pytest.approx(2 * small.max_torque())


def test_bigger_gap_less_torque():
    tight = m.AxialMagCoupling(gap=2.0)
    loose = m.AxialMagCoupling(gap=6.0)
    assert loose.max_torque() < tight.max_torque()


def test_holds_with_margin():
    c = m.AxialMagCoupling()          # ~4.18 N·m
    assert c.holds(2.0, safety=2.0)   # needs 4.0, has 4.18 -> ok
    assert not c.holds(3.0, safety=2.0)  # needs 6.0 -> no


def test_magnets_needed_scales_with_torque():
    few = m.magnets_needed(1.0, magnet_dia_mm=15, mean_radius_mm=55)
    many = m.magnets_needed(4.0, magnet_dia_mm=15, mean_radius_mm=55)
    assert many > few
    assert few >= 2  # never fewer than a 2-pole pair


def test_stronger_grade_needs_fewer_magnets():
    n42 = m.magnets_needed(3.0, 15, 55, grade="N42")
    n52 = m.magnets_needed(3.0, 15, 55, grade="N52")
    assert n52 <= n42


def test_axial_force_is_large_and_scales():
    c = m.AxialMagCoupling()
    f = c.axial_force_n()
    # the default coupling pulls with hundreds of newtons — the point of the check
    assert 200 < f < 600
    # hand value: 0.6 * B^2/(2mu0) * A
    expect = 0.6 * m.magnetic_pressure(c.b_gap) * c.active_area
    assert f == pytest.approx(expect)
    # a bigger gap relaxes the pull
    assert m.AxialMagCoupling(gap=6.0).axial_force_n() < f
