"""
Energy accounting — from continuous watts to "what can I actually run?"

A creek turbine's superpower is that, unlike solar or wind, it runs 24/7. Even a
humble 8 W becomes 8 W x 24 h = 192 Wh/day, and a battery turns that steady
trickle into useful bursts. This module does the boring-but-essential arithmetic:
daily/annual energy, battery sizing for a run of cloudy... er, low-flow days, and
a reality-check table of common loads.
"""

from __future__ import annotations

from dataclasses import dataclass

HOURS_PER_DAY = 24.0
DAYS_PER_YEAR = 365.0


def daily_energy_wh(power_w: float, flow_availability: float = 1.0) -> float:
    """Watt-hours per day from a continuous `power_w`, derated by flow uptime.

    `flow_availability` (0..1) accounts for droughts/freezes when the creek
    isn't running at your design speed. 1.0 = flows all day every day.
    """
    return power_w * HOURS_PER_DAY * flow_availability


def annual_energy_kwh(power_w: float, flow_availability: float = 1.0) -> float:
    """kWh per year — the number to compare against your utility bill for fun."""
    return daily_energy_wh(power_w, flow_availability) * DAYS_PER_YEAR / 1000.0


def battery_capacity_ah(
    daily_wh: float,
    system_voltage: float,
    days_autonomy: float,
    depth_of_discharge: float,
) -> float:
    """Battery size (amp-hours) to carry your daily load through low-flow days.

    Sized so `days_autonomy` days of load fit within the usable depth of
    discharge. Returns amp-hours at `system_voltage`.
    """
    if system_voltage <= 0 or depth_of_discharge <= 0:
        raise ValueError("system_voltage and depth_of_discharge must be > 0")
    usable_wh_needed = daily_wh * days_autonomy
    total_wh = usable_wh_needed / depth_of_discharge
    return total_wh / system_voltage


# ---------------------------------------------------------------------------
# "What can I run?" — a small, honest catalogue of everyday loads.
# Values are typical daily energy budgets (Wh/day) for always-on or daily use.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Load:
    name: str
    wh_per_day: float
    note: str = ""


COMMON_LOADS = (
    Load("Phone charge (1/day)", 15, "one full top-up"),
    Load("Trail / security camera", 30, "cellular game cam, always on"),
    Load("LED area light (5 W, 5 h)", 25, "an evening's light"),
    Load("Wi-Fi router / repeater", 120, "10 W always on"),
    Load("Weather / IoT sensors", 24, "1 W always on"),
    Load("Laptop charge (1/day)", 70, "one full battery top-up via the pack"),
    Load("Laptop (2 h/day active)", 100, "using it while it charges"),
    Load("Starlink Mini (avg)", 600, "~25 W always on"),
    Load("12 V fridge/cooler", 480, "small, well-insulated"),
    Load("Well/sump pump (short daily)", 500, "brief high-power run"),
)


def what_it_runs(daily_wh: float, loads=COMMON_LOADS):
    """Return [(Load, runs_bool, fraction_of_budget)] for a daily energy budget.

    fraction_of_budget < 1 means the load fits with headroom; > 1 means it
    exceeds what the creek makes in a day. This is the table that turns an
    abstract wattage into "yes, this keeps my cameras and phone alive."
    """
    out = []
    for load in loads:
        frac = load.wh_per_day / daily_wh if daily_wh > 0 else float("inf")
        out.append((load, frac <= 1.0, frac))
    return out
