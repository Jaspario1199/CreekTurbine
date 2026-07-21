"""Ducted / low-head / submerged-box math, against hand-computed ground truth."""

import pytest

from creekturbine import ducted as d


def test_velocity_head_is_tiny_for_a_creek():
    # v^2/2g at 0.8 m/s = 0.64/19.62 = 0.0326 m (~3.3 cm) — the key teaching point
    assert d.velocity_head(0.8) == pytest.approx(0.03262, abs=1e-4)
    assert d.velocity_head(0.0) == 0.0


def test_velocity_head_rejects_negative():
    with pytest.raises(ValueError):
        d.velocity_head(-1.0)


def test_low_head_power_hand_value():
    # rho*g*Q*H*eta = 1000*9.81*0.1*1.0*1.0 = 981 W
    assert d.low_head_power(0.1, 1.0) == pytest.approx(981.0)
    # scales linearly in Q, H, eta
    assert d.low_head_power(0.2, 1.0) == pytest.approx(2 * 981.0)
    assert d.low_head_power(0.1, 1.0, efficiency=0.4) == pytest.approx(0.4 * 981.0)


def test_low_head_power_rejects_negative():
    with pytest.raises(ValueError):
        d.low_head_power(-0.1, 1.0)


def test_throat_velocity_torricelli():
    # Cd=1 -> sqrt(2*9.81*1) = 4.429 m/s
    assert d.throat_velocity(1.0, cd=1.0) == pytest.approx(4.429, abs=1e-3)
    # Cd scales it linearly
    assert d.throat_velocity(1.0, cd=0.85) == pytest.approx(0.85 * 4.429, abs=1e-3)


def test_ducted_box_report_is_self_consistent():
    box = d.DuctedBox(throat_area=0.05, static_head=0.3, diffuser_gain=1.0,
                      cd=0.85, efficiency=0.4)
    r = box.report(0.8)
    # driving head = static + velocity head (no diffuser)
    assert r["driving_head_m"] == pytest.approx(0.3 + d.velocity_head(0.8))
    # flow = throat_area * throat velocity
    assert r["flow_m3s"] == pytest.approx(0.05 * r["throat_velocity"])
    # electrical = gross * efficiency
    assert r["electrical_w"] == pytest.approx(r["gross_hydraulic_w"] * 0.4)


def test_static_head_dominates_velocity_head():
    """Adding a real drop should beat a purely kinetic box by a lot."""
    kinetic = d.DuctedBox(throat_area=0.05, static_head=0.0)
    with_drop = d.DuctedBox(throat_area=0.05, static_head=0.4)
    assert with_drop.report(0.8)["electrical_w"] > 5 * kinetic.report(0.8)["electrical_w"]


def test_diffuser_gain_increases_power():
    plain = d.DuctedBox(throat_area=0.05, static_head=0.3, diffuser_gain=1.0)
    shrouded = d.DuctedBox(throat_area=0.05, static_head=0.3, diffuser_gain=1.6)
    assert shrouded.report(0.8)["electrical_w"] > plain.report(0.8)["electrical_w"]


def test_buoyancy_force_hand_value():
    # 1 m^3 of air submerged -> 1000*9.81*1 = 9810 N up (~1 tonne of lift)
    assert d.buoyancy_force_n(1.0) == pytest.approx(9810.0)


def test_ballast_mass_for_concrete():
    # 1 m^3 air, no structure, concrete (2400), SF=1.0:
    # effective hold-down = 9.81*(1-1000/2400) = 5.7225 N/kg; 9810/5.7225 = 1714 kg
    m = d.ballast_mass_kg(1.0, structure_mass_kg=0.0, ballast_density=2400.0,
                          safety_factor=1.0)
    assert m == pytest.approx(1714.2, abs=1.0)


def test_ballast_mass_credits_structure_weight():
    heavy = d.ballast_mass_kg(0.1, structure_mass_kg=0.0, safety_factor=1.0)
    with_struct = d.ballast_mass_kg(0.1, structure_mass_kg=50.0, safety_factor=1.0)
    assert with_struct < heavy


def test_ballast_requires_sinkable_ballast():
    with pytest.raises(ValueError):
        d.ballast_mass_kg(1.0, ballast_density=500.0)  # lighter than water
