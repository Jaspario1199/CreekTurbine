"""Generator matching: cut-in, charge current, and Ke recommendation."""

import math

import pytest

from creekturbine import generator as gen_mod
from creekturbine import rotor as rotor_mod


def test_open_circuit_voltage_linear_in_rpm():
    g = gen_mod.Generator(ke_dc=0.05)
    assert g.open_circuit_voltage(300) == pytest.approx(15.0)


def test_cut_in_rpm():
    g = gen_mod.Generator(ke_dc=0.05)
    # need 12 V / 0.05 = 240 rpm to reach a 12 V bus
    assert g.cut_in_rpm(12.0) == pytest.approx(240.0)


def test_no_current_below_cut_in():
    g = gen_mod.Generator(ke_dc=0.05, resistance=1.0)
    assert g.charge_current(200, 12.0) == 0.0
    assert g.charge_power(200, 12.0) == 0.0


def test_current_above_cut_in():
    g = gen_mod.Generator(ke_dc=0.05, resistance=1.0)
    # at 300 rpm emf=15 V, over a 12 V battery, (15-12)/1 = 3 A -> 36 W
    assert g.charge_current(300, 12.0) == pytest.approx(3.0)
    assert g.charge_power(300, 12.0) == pytest.approx(36.0)


def test_cut_in_velocity_for_slow_rotor():
    r = rotor_mod.SavoniusRotor(diameter=0.5, height=0.8)  # slow, low rpm
    g = gen_mod.Generator(ke_dc=0.05)
    v_cut = gen_mod.cut_in_velocity(r, g, 12.0)
    # a bare 0.05 V/rpm PMA needs unrealistically fast water for this slow rotor
    assert v_cut > 1.0


def test_recommend_ke_places_cut_in_at_target():
    r = rotor_mod.SavoniusRotor(diameter=0.5, height=0.8)
    target_v = 0.5
    ke = gen_mod.recommend_ke(r, target_v, 12.0)
    g = gen_mod.Generator(ke_dc=ke)
    # with the recommended Ke, cut-in velocity should equal the target
    assert gen_mod.cut_in_velocity(r, g, 12.0) == pytest.approx(target_v, rel=1e-6)


def test_step_up_ratio_positive_for_slow_rotor():
    r = rotor_mod.SavoniusRotor(diameter=0.5, height=0.8)
    ratio = gen_mod.step_up_ratio_for_rpm(r, 0.7, 350.0)
    assert ratio > 1.0 and math.isfinite(ratio)


def test_zero_ke_never_cuts_in():
    g = gen_mod.Generator(ke_dc=0.0)
    assert g.cut_in_rpm(12.0) == math.inf
