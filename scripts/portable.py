"""
portable — model a carry-anywhere creek power station for YOUR trip.

Shows the continuous harvest, what it sustains 24/7, how long the onboard battery
bursts a bigger load, the cable volt-drop to shore (and why a long run wants a
higher bus voltage), and the pack weight. Creek speed comes from
creekturbine/config.py; the kit specs come from flags.

    python -m scripts.portable
    python -m scripts.portable --rotor-area 0.15 --battery-wh 500 --bus 48 \
                               --cable-length 25 --cable-area 4 --burst-load 60
"""

from __future__ import annotations

import argparse
import math

from creekturbine.config import DEFAULT_CONFIG as cfg
from creekturbine import portable as p


def _fmt_h(h: float) -> str:
    return "∞ (sustainable)" if math.isinf(h) else f"{h:.1f} h"


def main() -> None:
    ap = argparse.ArgumentParser(description="Model a portable creek power station")
    ap.add_argument("--rotor-area", type=float, default=0.12, help="m² frontal area")
    ap.add_argument("--battery-wh", type=float, default=300.0, help="onboard battery Wh")
    ap.add_argument("--bus", type=float, default=24.0, help="cable/charge DC voltage")
    ap.add_argument("--cable-length", type=float, default=15.0, help="m to shore")
    ap.add_argument("--cable-area", type=float, default=4.0, help="mm² copper conductor")
    ap.add_argument("--burst-load", type=float, default=60.0, help="W of a device to burst")
    args = ap.parse_args()

    v = cfg.effective_velocity
    unit = p.PortableUnit(rotor_area=args.rotor_area, cp=cfg.cp,
                          eta_generator=cfg.generator_efficiency,
                          eta_drivetrain=cfg.drivetrain_efficiency,
                          battery_wh=args.battery_wh, bus_voltage=args.bus,
                          cable_length_m=args.cable_length, cable_area_mm2=args.cable_area,
                          rho=cfg.water_density)
    r = unit.report(v)

    print("=" * 68)
    print(" CreekTurbine — portable power station")
    print("=" * 68)
    print(f" Creek {v:.2f} m/s · rotor {args.rotor_area:.2f} m² · "
          f"battery {args.battery_wh:.0f} Wh · {args.bus:.0f} V bus")
    print("-" * 68)
    print(f" Continuous harvest:  {r['harvest_w']:.1f} W  "
          f"({r['daily_wh']:.0f} Wh/day — and it runs at NIGHT, unlike solar)")
    print(f" Sustains 24/7:       ~{r['sustained_w']:.1f} W continuous "
          f"(phones, lights, sensors, a power bank topped up)")

    # Burst: run a bigger device off the pre-charged battery + turbine
    burst = p.burst_runtime_hours(r['harvest_w'], args.battery_wh, args.burst_load)
    if math.isinf(burst):
        print(f" Burst a {args.burst_load:.0f} W device: {_fmt_h(burst)} "
              f"(within continuous output)")
    else:
        # over the burst the pack gives up ~90% of its capacity; the turbine
        # then refills that same energy
        recover = p.recharge_hours(r['harvest_w'], args.battery_wh * 0.9)
        print(f" Burst a {args.burst_load:.0f} W device: {_fmt_h(burst)}, then "
              f"~{_fmt_h(recover)} for the turbine to refill the pack")
    print(f" Off battery alone (no flow): a {args.burst_load:.0f} W load runs "
          f"{_fmt_h(p.runtime_hours(args.battery_wh, args.burst_load))}")
    print("-" * 68)

    # Cable
    print(f" CABLE to shore ({args.cable_length:.0f} m, {args.cable_area:.0f} mm² Cu, "
          f"low-voltage DC):")
    print(f"   {r['cable_current_a']:.1f} A → {r['cable_drop_percent']:.1f}% volt-drop", end="")
    print("  ✓ fine" if r['cable_drop_percent'] <= 5 else "  ✗ too much — fatter cable or higher voltage")
    for bus in (12.0, 24.0, 48.0):
        i = r['harvest_w'] / bus
        area = p.min_cable_area_mm2(i, args.cable_length, bus, max_drop_percent=3.0)
        print(f"     at {bus:>2.0f} V: {i:4.1f} A, needs ≥ {area:5.2f} mm² for <3% drop")
    print("   → a longer run wants a HIGHER bus voltage (¼ the copper per voltage doubling).")
    print("-" * 68)
    print(f" PACK WEIGHT (carryable): ~{r['pack_weight_kg']:.1f} kg "
          f"(battery {p.battery_mass_kg(args.battery_wh):.1f} kg + rotor/gen/cable)")
    print("-" * 68)
    print(" TOPOLOGY:  rotor → sealed generator → [low-voltage DC cable] → shore box:")
    print("            charge controller → LiFePO4 battery → USB / 12V / (inverter on land)")
    print(" Multi-input controller lets the SAME battery also charge from solar or a")
    print(" wall outlet — that's your 'switch between sources'. See docs/PORTABLE.md.")
    print("=" * 68)


if __name__ == "__main__":
    main()
