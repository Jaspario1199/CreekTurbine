"""
Portable "power-station" model — a carry-anywhere creek turbine.

The concept: a rugged, sealed turbine you drop into *any* creek (backyard or
campsite), a **low-voltage DC** cable to shore, and a battery-buffered box on dry
land that runs your loads. Unlike solar it works **24/7 — at night, in rain, in
shade** — which is the whole reason to carry one.

This module models the three things that decide whether that's practical:

1. **Battery buffer** — you run loads off the battery and the turbine tops it up.
   That gives smooth, instant, full-power output even from a weak creek, and lets
   you *burst* a load bigger than the turbine's continuous output for a while.
2. **The cable** — the "waterproof extension cord" is the sneaky-hard part. Volt-
   drop over a long low-voltage run is brutal (P_loss = I²R), so the model sizes
   the conductor and shows why a longer run wants a *higher* bus voltage.
3. **Weight** — "slightly heavy" is fine, but let's put a number on the pack.

⚠️ SAFETY: the in-water cable carries LOW-VOLTAGE DC (12–48 V). Never run mains
AC in or near the water. Any 120/230 V AC inverter lives on DRY LAND, after the
battery. See docs/PORTABLE.md and docs/SAFETY.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import hydrokinetics as hk

COPPER_RESISTIVITY = 1.68e-8  # ohm·m, annealed copper near 20 °C


# ---------------------------------------------------------------------------
# Battery buffer: sustained vs. burst
# ---------------------------------------------------------------------------
def runtime_hours(battery_wh: float, load_w: float, usable_fraction: float = 0.9) -> float:
    """Hours a `load_w` runs off a `battery_wh` pack (turbine off / no flow)."""
    if load_w <= 0:
        return float("inf")
    return battery_wh * usable_fraction / load_w


def sustained_load_w(harvest_w: float, margin: float = 0.9) -> float:
    """The continuous load the turbine supports indefinitely (24/7).

    A little under the raw harvest so the battery trends up, not down. This is
    the honest "always-on" budget — small, but it never sleeps."""
    return harvest_w * margin


def burst_runtime_hours(harvest_w: float, battery_wh: float, load_w: float,
                        usable_fraction: float = 0.9) -> float:
    """Hours you can run a load BIGGER than the turbine's output.

    The battery covers the shortfall (load - harvest). Returns inf if the load
    is within the turbine's continuous output (sustainable forever)."""
    net = load_w - harvest_w
    if net <= 0:
        return float("inf")
    return battery_wh * usable_fraction / net


def recharge_hours(harvest_w: float, energy_used_wh: float,
                   charge_efficiency: float = 0.9) -> float:
    """Hours for the turbine alone to put `energy_used_wh` back into the pack."""
    if harvest_w <= 0:
        return float("inf")
    return energy_used_wh / (harvest_w * charge_efficiency)


# ---------------------------------------------------------------------------
# The cable ("waterproof extension cord") — low-voltage DC to shore
# ---------------------------------------------------------------------------
def cable_voltage_drop(current_a: float, length_m: float, area_mm2: float,
                       bus_voltage: float, resistivity: float = COPPER_RESISTIVITY):
    """Return (drop_percent, drop_volts) for a two-conductor DC run to shore.

    Accounts for BOTH conductors (out and back = 2·length). Keep the drop under
    ~3–5%; above that you're heating the cable instead of charging the battery.
    """
    if area_mm2 <= 0 or bus_voltage <= 0:
        raise ValueError("area_mm2 and bus_voltage must be > 0")
    area_m2 = area_mm2 * 1e-6
    r = resistivity * 2.0 * length_m / area_m2
    v = current_a * r
    return 100.0 * v / bus_voltage, v


def min_cable_area_mm2(current_a: float, length_m: float, bus_voltage: float,
                       max_drop_percent: float = 3.0,
                       resistivity: float = COPPER_RESISTIVITY) -> float:
    """Smallest copper conductor (mm²) to keep the drop within a limit.

    The punchline for a long "extension cord": area scales with current and
    length but *inversely* with bus voltage — so doubling the bus voltage (12→24
    →48 V) quarters the required copper (or the loss). For a long run to shore,
    use a higher-voltage generator and step down on land.
    """
    if bus_voltage <= 0 or max_drop_percent <= 0:
        raise ValueError("bus_voltage and max_drop_percent must be > 0")
    max_drop_v = bus_voltage * max_drop_percent / 100.0
    area_m2 = current_a * resistivity * 2.0 * length_m / max_drop_v
    return area_m2 * 1e6


# ---------------------------------------------------------------------------
# Weight budget
# ---------------------------------------------------------------------------
LIFEPO4_WH_PER_KG = 110.0  # realistic packaged LiFePO4 energy density


def battery_mass_kg(battery_wh: float, wh_per_kg: float = LIFEPO4_WH_PER_KG) -> float:
    """Approx packaged battery mass for a given capacity."""
    return battery_wh / wh_per_kg


def pack_weight_kg(battery_wh: float, rotor_frame_kg: float = 3.0,
                   generator_kg: float = 1.5, electronics_kg: float = 0.8,
                   cable_length_m: float = 15.0, cable_kg_per_m: float = 0.12) -> float:
    """Rough total carry weight of the portable kit (kg)."""
    return (battery_mass_kg(battery_wh) + rotor_frame_kg + generator_kg
            + electronics_kg + cable_length_m * cable_kg_per_m)


# ---------------------------------------------------------------------------
# The whole unit
# ---------------------------------------------------------------------------
@dataclass
class PortableUnit:
    """A carry-anywhere creek unit, tying harvest + battery + cable + weight."""

    rotor_area: float = 0.12       # m², a compact portable rotor
    cp: float = 0.18
    eta_generator: float = 0.65
    eta_drivetrain: float = 0.90
    battery_wh: float = 300.0      # onboard buffer
    bus_voltage: float = 24.0      # cable/charge voltage (higher = longer runs)
    cable_length_m: float = 15.0
    cable_area_mm2: float = 4.0
    rho: float = 1000.0

    def harvest_w(self, velocity: float) -> float:
        """Continuous electrical watts into the battery at a creek speed."""
        return hk.extractable_power(self.rotor_area, velocity, self.cp,
                                    self.eta_generator, self.eta_drivetrain, self.rho)

    def report(self, velocity: float) -> dict:
        h = self.harvest_w(velocity)
        current = h / self.bus_voltage if self.bus_voltage > 0 else 0.0
        drop_pct, drop_v = cable_voltage_drop(current, self.cable_length_m,
                                              self.cable_area_mm2, self.bus_voltage)
        return {
            "velocity": velocity,
            "harvest_w": h,
            "sustained_w": sustained_load_w(h),
            "daily_wh": h * 24.0,
            "cable_current_a": current,
            "cable_drop_percent": drop_pct,
            "pack_weight_kg": pack_weight_kg(self.battery_wh,
                                             cable_length_m=self.cable_length_m),
        }
