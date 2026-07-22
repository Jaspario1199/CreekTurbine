"""Funnel / converging-intake model: continuity, critical-velocity choke, power."""

import math

import pytest

from creekturbine import funnel as f


def test_critical_velocity_hand_value():
    # √(9.81 * 0.15) ≈ 1.213 m/s at 6 inches
    assert f.critical_velocity(0.15) == pytest.approx(1.2131, abs=1e-3)
    with pytest.raises(ValueError):
        f.critical_velocity(0.0)


def test_froude_is_one_at_critical():
    vc = f.critical_velocity(0.2)
    assert f.froude_number(vc, 0.2) == pytest.approx(1.0)


def test_flow_rate():
    assert f.flow_rate(1.5, 0.3, 0.4) == pytest.approx(0.18)


def test_funnel_chokes_at_critical():
    fi = f.FunnelIntake(up_width=1.5, up_depth=0.3, up_velocity=0.4,
                        throat_width=0.4, throat_depth=0.15)
    assert fi.creek_flow == pytest.approx(0.18)
    assert fi.ideal_throat_velocity == pytest.approx(3.0)   # if uncapped
    assert fi.choked is True
    assert fi.throat_velocity == pytest.approx(f.critical_velocity(0.15))
    assert fi.throat_froude == pytest.approx(1.0)


def test_unchoked_funnel_uses_continuity():
    # a wide throat that doesn't reach critical -> velocity = Q/A
    fi = f.FunnelIntake(up_width=1.5, up_depth=0.3, up_velocity=0.4,
                        throat_width=1.2, throat_depth=0.3)
    assert not fi.choked
    assert fi.throat_velocity == pytest.approx(fi.creek_flow / fi.throat_area)


def test_augmentation_and_power_gain_are_cube_related():
    fi = f.FunnelIntake(up_width=1.5, up_depth=0.3, up_velocity=0.4,
                        throat_width=0.4, throat_depth=0.15)
    # power scales with velocity cubed, so gain ≈ augmentation³
    assert fi.power_gain() == pytest.approx(fi.augmentation ** 3, rel=1e-6)
    assert fi.electrical_power() > 10 * fi.bare_rotor_power()


def test_throughput_below_creek_flow_when_choked():
    fi = f.FunnelIntake(up_width=1.5, up_depth=0.3, up_velocity=0.4,
                        throat_width=0.4, throat_depth=0.15)
    assert fi.throughput < fi.creek_flow   # excess backs up / bypasses


def test_throat_width_for_velocity_respects_critical():
    q = 0.18
    # ask for 3 m/s at 0.15 m depth — impossible (critical ~1.21), so it sizes
    # for the critical velocity instead
    w = f.throat_width_for_velocity(q, 3.0, 0.15)
    w_crit = q / (f.critical_velocity(0.15) * 0.15)
    assert w == pytest.approx(w_crit)
