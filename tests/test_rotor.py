"""Rotor geometry, performance, and sizing round-trips."""

import math

import pytest

from creekturbine import rotor as rotor_mod
from creekturbine import hydrokinetics as hk


def test_savonius_frontal_area_is_d_times_h():
    r = rotor_mod.SavoniusRotor(diameter=0.5, height=0.8)
    assert r.frontal_area == pytest.approx(0.4)
    assert r.radius == pytest.approx(0.25)
    assert r.aspect_ratio == pytest.approx(1.6)


def test_axial_frontal_area_is_swept_circle():
    r = rotor_mod.AxialRotor(diameter=0.4)
    assert r.frontal_area == pytest.approx(math.pi / 4 * 0.16)


def test_savonius_from_buckets_geometry():
    # rotor diameter = 2*bucket - overlap; overlap = 0.15*bucket
    r = rotor_mod.SavoniusRotor.from_buckets(bucket_dia=0.3, height=0.6, overlap_ratio=0.15)
    assert r.diameter == pytest.approx(2 * 0.3 - 0.15 * 0.3)


def test_performance_matches_extractable_power():
    r = rotor_mod.SavoniusRotor(diameter=0.5, height=0.8, cp=0.18)
    perf = r.performance(0.8)
    expected_mech = hk.available_power(r.frontal_area, 0.8) * 0.18
    assert perf.mechanical_w == pytest.approx(expected_mech)
    assert perf.rpm > 0 and perf.torque_nm > 0


def test_electrical_power_uses_efficiencies():
    r = rotor_mod.AxialRotor(diameter=0.4, cp=0.35)
    p = r.electrical_power(1.0, eta_generator=0.65, eta_drivetrain=0.9)
    expected = hk.extractable_power(r.frontal_area, 1.0, 0.35, 0.65, 0.9)
    assert p == pytest.approx(expected)


def test_size_savonius_hits_target():
    target = 10.0
    r = rotor_mod.size_savonius_for_power(target, 0.8, aspect_ratio=1.6, cp=0.18,
                                          eta_generator=0.65, eta_drivetrain=0.9)
    p = r.electrical_power(0.8, 0.65, 0.9)
    assert p == pytest.approx(target, rel=1e-6)
    assert r.aspect_ratio == pytest.approx(1.6)


def test_size_axial_hits_target():
    target = 25.0
    r = rotor_mod.size_axial_for_power(target, 1.2, cp=0.35, eta_generator=0.65,
                                       eta_drivetrain=0.9)
    p = r.electrical_power(1.2, 0.65, 0.9)
    assert p == pytest.approx(target, rel=1e-6)


def test_slow_creek_gives_infinite_size():
    r = rotor_mod.size_savonius_for_power(50.0, 0.0, cp=0.18)
    assert not math.isfinite(r.diameter)


def test_make_rotor_from_config_respects_type():
    from creekturbine.config import CreekConfig
    sav = rotor_mod.make_rotor_from_config(CreekConfig(turbine_type="savonius"))
    ax = rotor_mod.make_rotor_from_config(CreekConfig(turbine_type="axial"))
    assert isinstance(sav, rotor_mod.SavoniusRotor)
    assert isinstance(ax, rotor_mod.AxialRotor)


def test_savonius_profiles_ordered():
    p = rotor_mod.SAVONIUS_PROFILES
    assert p["conventional"] < p["optimized"] < p["hydrofoil"]


def test_from_profile_sets_cp_and_metadata():
    r = rotor_mod.SavoniusRotor.from_profile(0.4, 0.6, profile="hydrofoil")
    assert r.cp == rotor_mod.SAVONIUS_PROFILES["hydrofoil"]
    assert r.profile == "hydrofoil"
    assert r.helical is True


def test_from_profile_rejects_unknown():
    with pytest.raises(ValueError):
        rotor_mod.SavoniusRotor.from_profile(0.4, 0.6, profile="banana")


def test_config_cp_reflects_profile():
    from creekturbine.config import CreekConfig
    custom = CreekConfig(turbine_type="savonius", savonius_profile="custom", cp_savonius=0.18)
    hydro = CreekConfig(turbine_type="savonius", savonius_profile="hydrofoil")
    assert custom.cp == pytest.approx(0.18)
    assert hydro.cp == pytest.approx(rotor_mod.SAVONIUS_PROFILES["hydrofoil"])


def test_hydrofoil_profile_shrinks_rotor_vs_conventional():
    from creekturbine.config import CreekConfig
    conv = rotor_mod.make_rotor_from_config(
        CreekConfig(savonius_profile="conventional"))
    hydro = rotor_mod.make_rotor_from_config(
        CreekConfig(savonius_profile="hydrofoil"))
    # higher Cp -> smaller rotor for the same target power
    assert hydro.frontal_area < conv.frontal_area
    assert hydro.helical is True


def test_augmentation_shrinks_rotor():
    from creekturbine.config import CreekConfig
    base = rotor_mod.make_rotor_from_config(CreekConfig(velocity_augmentation=1.0))
    shrouded = rotor_mod.make_rotor_from_config(CreekConfig(velocity_augmentation=1.3))
    assert shrouded.frontal_area < base.frontal_area
