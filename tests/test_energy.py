"""Energy accounting and battery sizing."""

import pytest

from creekturbine import energy as en


def test_daily_energy_wh():
    assert en.daily_energy_wh(10.0) == pytest.approx(240.0)
    assert en.daily_energy_wh(10.0, flow_availability=0.75) == pytest.approx(180.0)


def test_annual_energy_kwh():
    # 10 W continuous ~ 87.6 kWh/yr at 100% availability
    assert en.annual_energy_kwh(10.0) == pytest.approx(87.6, abs=0.1)


def test_battery_capacity_ah():
    # 240 Wh/day, 2 days, 80% DoD, 12 V -> 240*2/0.8/12 = 50 Ah
    ah = en.battery_capacity_ah(240.0, 12.0, 2.0, 0.8)
    assert ah == pytest.approx(50.0)


def test_battery_capacity_rejects_bad_inputs():
    with pytest.raises(ValueError):
        en.battery_capacity_ah(240.0, 0.0, 2.0, 0.8)
    with pytest.raises(ValueError):
        en.battery_capacity_ah(240.0, 12.0, 2.0, 0.0)


def test_what_it_runs_flags_fit():
    rows = en.what_it_runs(200.0)
    by_name = {ld.name: (ok, frac) for ld, ok, frac in rows}
    # a 15 Wh/day phone charge fits in a 200 Wh/day budget
    ok, frac = by_name["Phone charge (1/day)"]
    assert ok and frac == pytest.approx(15 / 200)
    # a 480 Wh/day fridge does not
    ok_fridge, frac_fridge = by_name["12 V fridge/cooler"]
    assert not ok_fridge and frac_fridge > 1.0


def test_what_it_runs_zero_budget():
    rows = en.what_it_runs(0.0)
    assert all(not ok for _, ok, _ in rows)


def test_net_daily_energy_subtracts_idle():
    # (5 W * 0.75 - 0.25 W) * 24 = 84 Wh
    assert en.net_daily_energy_wh(5.0, 0.25, 0.75) == pytest.approx(84.0)
    # zero idle == gross
    assert en.net_daily_energy_wh(5.0, 0.0, 0.75) == pytest.approx(
        en.daily_energy_wh(5.0, 0.75))


def test_net_daily_energy_can_go_negative():
    # controller eats more than the harvest -> battery drains (warned, not hidden)
    assert en.net_daily_energy_wh(0.2, 0.3, 1.0) < 0
    with pytest.raises(ValueError):
        en.net_daily_energy_wh(1.0, -0.1)
