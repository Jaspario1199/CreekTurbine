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
