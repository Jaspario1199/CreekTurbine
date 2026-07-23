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


def test_confinement_derates_free_standing_unit():
    # confinement=1.0 gives the full (walled) speed-up; <1 realizes less
    walled = f.FunnelIntake(1.5, 0.3, 0.4, 0.4, 0.15, confinement=1.0)
    free = f.FunnelIntake(1.5, 0.3, 0.4, 0.4, 0.15, confinement=0.8)
    assert free.throat_velocity < walled.throat_velocity
    assert free.throat_velocity > free.up_velocity  # still faster than ambient
    # confinement=0 collapses to the bare ambient speed
    none = f.FunnelIntake(1.5, 0.3, 0.4, 0.4, 0.15, confinement=0.0)
    assert none.throat_velocity == pytest.approx(none.up_velocity)


def test_universal_unit_fixed_gather_and_depth_cap():
    # throat can't be deeper than the water
    shallow = f.FunnelIntake.universal(creek_depth=0.15, up_velocity=0.4)
    assert shallow.throat_depth == pytest.approx(0.15)
    assert shallow.up_width == pytest.approx(0.9)   # fixed gather width
    deep = f.FunnelIntake.universal(creek_depth=0.6, up_velocity=0.4)
    assert deep.throat_depth == pytest.approx(0.15)  # short rotor, capped nominal
    # deeper water gathers more flow -> more power from the same unit
    assert deep.electrical_power() > shallow.electrical_power()


def test_throat_width_for_velocity_respects_critical():
    q = 0.18
    # ask for 3 m/s at 0.15 m depth — impossible (critical ~1.21), so it sizes
    # for the critical velocity instead
    w = f.throat_width_for_velocity(q, 3.0, 0.15)
    w_crit = q / (f.critical_velocity(0.15) * 0.15)
    assert w == pytest.approx(w_crit)


def test_universal_caps_gather_at_intake_height():
    # a 0.9 m-deep creek can't all be gathered by a 0.35 m-tall mouth
    deep = f.FunnelIntake.universal(creek_depth=0.9, up_velocity=0.4,
                                    intake_height=0.35)
    assert deep.up_depth == pytest.approx(0.35)
    shallow = f.FunnelIntake.universal(creek_depth=0.15, up_velocity=0.4,
                                       intake_height=0.35)
    assert shallow.up_depth == pytest.approx(0.15)
