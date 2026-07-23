"""Self-contained unit: geometry, drag, and base-ballast stability math."""

import pytest

from creekturbine import selfcontained as sc


def test_drag_force_hand_value():
    # 0.5 * 1000 * 1.0 * 0.1 * 0.8^2 = 32 N
    assert sc.drag_force_n(0.1, 0.8, cd=1.0) == pytest.approx(32.0)
    # grows with v^2
    assert sc.drag_force_n(0.1, 1.6, cd=1.0) == pytest.approx(4 * 32.0)


def test_drag_rejects_negative():
    with pytest.raises(ValueError):
        sc.drag_force_n(-0.1, 0.8)


def test_hold_mass_for_sliding():
    # need mu*W*g >= safety*drag -> W = safety*drag/(mu*g)
    # 2*32/(0.5*9.81) = 13.05 kg
    assert sc.hold_mass_for_sliding_kg(32.0, friction=0.5, safety=2.0) == pytest.approx(13.05, abs=0.05)


def test_hold_mass_for_tipping():
    # safety*drag*drag_height/(halfwidth*g) = 2*32*0.15/(0.15*9.81) = 6.52 kg
    m = sc.hold_mass_for_tipping_kg(32.0, drag_height_m=0.15, base_halfwidth_m=0.15,
                                    safety=2.0)
    assert m == pytest.approx(6.523, abs=0.01)


def test_wider_base_needs_less_tipping_ballast():
    narrow = sc.hold_mass_for_tipping_kg(32.0, 0.15, 0.10)
    wide = sc.hold_mass_for_tipping_kg(32.0, 0.15, 0.25)
    assert wide < narrow


def test_unit_geometry():
    u = sc.SelfContainedUnit(box_diameter=0.30, box_height=0.65, submerged_depth=0.30,
                             wall_clearance=0.02)
    assert u.rotor_diameter == pytest.approx(0.26)
    assert u.rotor_height == pytest.approx(0.25)
    assert u.frontal_area == pytest.approx(0.26 * 0.25)
    assert u.freeboard == pytest.approx(0.35)
    assert u.submerged_body_area == pytest.approx(0.30 * 0.30)


def test_unit_power_positive():
    u = sc.SelfContainedUnit(velocity=0.8)
    assert u.power_w() > 0
    assert u.report()["daily_wh"] == pytest.approx(u.power_w() * 24)


def test_required_ballast_zero_when_heavy_and_slow():
    # very slow creek + heavy unit -> no extra ballast needed
    u = sc.SelfContainedUnit(velocity=0.2, unit_dry_mass_kg=40.0)
    assert u.required_base_ballast_kg() == 0.0


def test_required_ballast_grows_with_velocity():
    slow = sc.SelfContainedUnit(velocity=0.5, unit_dry_mass_kg=5.0)
    fast = sc.SelfContainedUnit(velocity=1.4, unit_dry_mass_kg=5.0)
    assert fast.required_base_ballast_kg() > slow.required_base_ballast_kg()


def test_weight_breakdown_sums():
    wb = sc.estimate_weights(0.30, 0.65, 0.065, battery_wh=300)
    parts = sum(v for k, v in wb.items() if k != "dry_total")
    assert wb["dry_total"] == pytest.approx(parts)
    # battery mass = Wh / 110
    assert wb["battery"] == pytest.approx(300 / 110.0)


def test_bigger_battery_is_heavier():
    small = sc.estimate_weights(0.30, 0.65, 0.065, battery_wh=200)["dry_total"]
    big = sc.estimate_weights(0.30, 0.65, 0.065, battery_wh=500)["dry_total"]
    assert big - small == pytest.approx((500 - 200) / 110.0)


def test_computed_dry_mass_used_when_no_override():
    u = sc.SelfContainedUnit(battery_wh=300)  # no unit_dry_mass_kg override
    assert u.dry_mass_kg == pytest.approx(u.weight_breakdown()["dry_total"])
    # total = dry + ballast
    assert u.total_weight_kg() == pytest.approx(
        u.dry_mass_kg + u.required_base_ballast_kg())


def test_override_dry_mass_respected():
    u = sc.SelfContainedUnit(unit_dry_mass_kg=20.0)
    assert u.dry_mass_kg == 20.0


def test_flood_drag_dwarfs_operating_drag():
    u = sc.SelfContainedUnit(velocity=0.8)
    assert u.flood_drag_n(2.5) > 5 * u.drag_n()
    # hand value: 0.5*1000*1.1*(0.3*0.65)*2.5^2 = 670 N
    assert u.flood_drag_n(2.5) == pytest.approx(670.3, abs=1.0)
    assert u.flood_anchor_force_n(2.5, safety=1.5) == pytest.approx(
        u.flood_drag_n(2.5) * 1.5)
