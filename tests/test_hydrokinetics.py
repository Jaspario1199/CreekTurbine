"""The physics we must trust — tested against hand-computable ground truth."""

import math

import pytest

from creekturbine import hydrokinetics as hk


def test_power_flux_hand_value():
    # 1/2 * 1000 * 1.0^3 = 500 W/m^2 at 1 m/s
    assert hk.power_flux(1.0) == pytest.approx(500.0)
    # 1/2 * 1000 * 0.5^3 = 62.5 W/m^2 at 0.5 m/s
    assert hk.power_flux(0.5) == pytest.approx(62.5)


def test_cube_law():
    """Doubling velocity must give 8x the power (the whole point)."""
    p1 = hk.available_power(0.25, 0.5)
    p2 = hk.available_power(0.25, 1.0)
    assert p2 / p1 == pytest.approx(8.0)


def test_available_power_scales_with_area():
    assert hk.available_power(2.0, 0.8) == pytest.approx(2.0 * hk.available_power(1.0, 0.8))


def test_extractable_never_exceeds_betz():
    # Even a greedy Cp request is clamped to the Betz limit.
    greedy = hk.extractable_power(1.0, 1.0, cp=0.99)
    ceiling = hk.available_power(1.0, 1.0) * hk.BETZ_LIMIT
    assert greedy == pytest.approx(ceiling)


def test_betz_limit_value():
    assert hk.BETZ_LIMIT == pytest.approx(16.0 / 27.0)
    assert hk.BETZ_LIMIT == pytest.approx(0.5926, abs=1e-4)


def test_extractable_efficiency_chain():
    p = hk.extractable_power(1.0, 1.0, cp=0.2, eta_generator=0.65, eta_drivetrain=0.9)
    assert p == pytest.approx(500.0 * 0.2 * 0.65 * 0.9)


def test_swept_area_round_trips_with_extractable_power():
    """Area sizing is the exact inverse of the power calculation."""
    target = 12.0
    area = hk.swept_area_for_power(target, 0.8, cp=0.18, eta_generator=0.65,
                                   eta_drivetrain=0.9)
    back = hk.extractable_power(area, 0.8, cp=0.18, eta_generator=0.65,
                                eta_drivetrain=0.9)
    assert back == pytest.approx(target)


def test_swept_area_infinite_at_zero_velocity():
    assert hk.swept_area_for_power(10.0, 0.0, cp=0.2) == math.inf


def test_swept_area_zero_for_zero_target():
    assert hk.swept_area_for_power(0.0, 0.8, cp=0.2) == 0.0


def test_augmentation_cubes_power():
    assert hk.power_gain_from_augmentation(1.2) == pytest.approx(1.728)
    assert hk.augmented_velocity(0.5, 2.0) == pytest.approx(1.0)


def test_augmentation_rejects_slowdown():
    with pytest.raises(ValueError):
        hk.augmented_velocity(0.5, 0.9)


def test_blockage_ratio():
    assert hk.blockage_ratio(0.2, 1.0) == pytest.approx(0.2)
    with pytest.raises(ValueError):
        hk.blockage_ratio(0.2, 0.0)


def test_tsr_and_rpm_consistency():
    # TSR and its inverse must round-trip.
    omega = hk.omega_from_tsr(0.9, 0.8, 0.25)
    tsr = hk.tip_speed_ratio(omega, 0.25, 0.8)
    assert tsr == pytest.approx(0.9)


def test_rpm_omega_round_trip():
    assert hk.omega_from_rpm(hk.rpm_from_omega(3.7)) == pytest.approx(3.7)


def test_rpm_at_velocity_hand_value():
    # tsr=1, v=1, R=0.25 -> omega=4 rad/s -> 4*60/2pi = 38.2 rpm
    assert hk.rpm_at_velocity(1.0, 1.0, 0.25) == pytest.approx(38.197, abs=1e-2)


def test_torque_from_power():
    # 100 W at 10 rad/s = 10 N*m
    assert hk.torque_from_power(100.0, 10.0) == pytest.approx(10.0)
    with pytest.raises(ValueError):
        hk.torque_from_power(100.0, 0.0)


def test_negative_inputs_rejected():
    with pytest.raises(ValueError):
        hk.power_flux(-1.0)
    with pytest.raises(ValueError):
        hk.available_power(-1.0, 1.0)
