"""
funnel — can a converging chute make a mellow, shallow creek useful?

Model a wall-to-the-banks funnel that squeezes the creek into a narrow throat at
the rotor. Shows the throat velocity (capped at the open-channel critical speed),
the power gain vs a bare rotor, and whether it charges a laptop.

    python -m scripts.funnel
    python -m scripts.funnel --up-width 2 --up-depth 0.3 --up-vel 0.4 \
                             --throat-width 0.4 --throat-depth 0.15
"""

from __future__ import annotations

import argparse

from creekturbine import funnel as fn
from creekturbine.config import DEFAULT_CONFIG as cfg


def main() -> None:
    ap = argparse.ArgumentParser(description="Model a converging-intake funnel")
    ap.add_argument("--up-width", type=float, default=1.5, help="m, approach width")
    ap.add_argument("--up-depth", type=float, default=0.30, help="m, approach depth")
    ap.add_argument("--up-vel", type=float, default=0.40, help="m/s, mellow creek speed")
    ap.add_argument("--throat-width", type=float, default=0.40, help="m, throat width")
    ap.add_argument("--throat-depth", type=float, default=0.15, help="m, throat depth")
    ap.add_argument("--laptop-wh", type=float, default=70.0, help="Wh per laptop charge")
    args = ap.parse_args()

    fi = fn.FunnelIntake(up_width=args.up_width, up_depth=args.up_depth,
                         up_velocity=args.up_vel, throat_width=args.throat_width,
                         throat_depth=args.throat_depth, cp=cfg.cp,
                         eta_generator=cfg.generator_efficiency,
                         eta_drivetrain=cfg.drivetrain_efficiency)
    daily = fi.electrical_power() * 24 * cfg.flow_availability

    print("=" * 66)
    print(" CreekTurbine — converging-intake funnel")
    print("=" * 66)
    print(f" Mellow creek: {args.up_vel:.2f} m/s, {args.up_width:.1f} m wide × "
          f"{args.up_depth:.2f} m deep  →  Q = {fi.creek_flow*1000:.0f} L/s")
    print(f" Throat at the rotor: {args.throat_width:.2f} m wide × "
          f"{args.throat_depth:.2f} m deep ({fi.throat_area:.3f} m²)")
    print("-" * 66)
    print(f" Open-channel critical cap here: √(g·y) = {fi.critical_velocity:.2f} m/s")
    print(f" Throat velocity: {fi.throat_velocity:.2f} m/s "
          f"({'CHOKED at critical — extra flow backs up/bypasses' if fi.choked else 'set by continuity (not choked)'})")
    print(f"   → {fi.augmentation:.1f}× the mellow speed  ⇒  {fi.power_gain():.0f}× "
          f"the power of a bare rotor (v³ law)")
    print("-" * 66)
    print(f" Bare rotor in the open creek: {fi.bare_rotor_power():.1f} W")
    print(f" Funnelled rotor:              {fi.electrical_power():.1f} W  "
          f"→ {daily:.0f} Wh/day  = {daily/args.laptop_wh:.1f} laptop charges/day")
    print("-" * 66)
    print(" Reality check: this is a small WEIR/wing-wall structure spanning the")
    print(" creek (walls to both banks so water can't bypass), which ponds the")
    print(" upstream level a little and edges toward 'diverting' the creek —")
    print(" bigger permit/fish-passage footprint than a drop-in. A trash rack is")
    print(" essential; the narrowed throat clogs faster. To beat the critical cap")
    print(" you need a CLOSED pressurized duct with head — see docs/BOX_AND_DUCT.md.")
    print("=" * 66)


if __name__ == "__main__":
    main()
