"""Portable power-station math: battery buffer, cable volt-drop, weight."""

import math

import pytest

from creekturbine import portable as p


def test_runtime_hours():
    # 300 Wh, 90% usable, 10 W load -> 27 h
    assert p.runtime_hours(300, 10) == pytest.approx(27.0)
    assert p.runtime_hours(300, 0) == math.inf


def test_sustained_load():
    assert p.sustained_load_w(10.0) == pytest.approx(9.0)


def test_burst_runtime_infinite_when_within_output():
    # load below harvest -> sustainable forever
    assert p.burst_runtime_hours(20, 300, 15) == math.inf


def test_burst_runtime_finite_above_output():
    # harvest 10, load 60, net 50 W drain, 300 Wh * 0.9 / 50 = 5.4 h
    assert p.burst_runtime_hours(10, 300, 60) == pytest.approx(5.4)


def test_recharge_hours():
    # refill 270 Wh at 10 W and 90% charge eff: 270 / 9 = 30 h
    assert p.recharge_hours(10, 270) == pytest.approx(30.0)
    assert p.recharge_hours(0, 270) == math.inf


def test_cable_voltage_drop_hand_value():
    # 10 A, 20 m, 4 mm^2 Cu, 12 V bus: R = 1.68e-8*40/4e-6 = 0.168 ohm
    # Vdrop = 1.68 V -> 14% of 12 V
    pct, v = p.cable_voltage_drop(10, 20, 4.0, 12.0)
    assert v == pytest.approx(1.68, abs=1e-2)
    assert pct == pytest.approx(14.0, abs=0.2)


def test_higher_voltage_needs_less_copper():
    """The key result: quadruple the voltage -> ~1/16 the copper for same drop%
    at the same POWER (current scales as 1/V, area scales as I/V)."""
    # same power 240 W: at 12 V -> 20 A, at 48 V -> 5 A
    a12 = p.min_cable_area_mm2(240 / 12, 20, 12, max_drop_percent=3.0)
    a48 = p.min_cable_area_mm2(240 / 48, 20, 48, max_drop_percent=3.0)
    assert a12 / a48 == pytest.approx(16.0, rel=1e-3)


def test_min_cable_area_rejects_bad_inputs():
    with pytest.raises(ValueError):
        p.min_cable_area_mm2(10, 20, 0.0)
    with pytest.raises(ValueError):
        p.cable_voltage_drop(10, 20, 0.0, 12)


def test_battery_and_pack_weight():
    # 330 Wh at 110 Wh/kg = 3 kg battery
    assert p.battery_mass_kg(330) == pytest.approx(3.0)
    w = p.pack_weight_kg(330, rotor_frame_kg=3, generator_kg=1.5, electronics_kg=0.8,
                         cable_length_m=15, cable_kg_per_m=0.12)
    # 3 + 3 + 1.5 + 0.8 + 1.8 = 10.1 kg
    assert w == pytest.approx(10.1, abs=1e-6)


def test_portable_unit_report():
    unit = p.PortableUnit(rotor_area=0.12, battery_wh=300, bus_voltage=24,
                          cable_length_m=15, cable_area_mm2=4.0)
    r = unit.report(0.8)
    assert r["harvest_w"] > 0
    assert r["daily_wh"] == pytest.approx(r["harvest_w"] * 24)
    assert r["sustained_w"] == pytest.approx(r["harvest_w"] * 0.9)
    assert r["cable_current_a"] == pytest.approx(r["harvest_w"] / 24)
    assert r["pack_weight_kg"] > 0
