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
    ap.add_argument("--universal", action="store_true",
                    help="free-standing unit (fixed gather width): sweep across depth")
    ap.add_argument("--gather-width", type=float, default=0.9,
                    help="m, the unit's fixed intake/wing-wall span (fits creeks wider than this)")
    ap.add_argument("--confinement", type=float, default=0.82,
                    help="fraction of the ideal speed-up a free-standing unit realizes")
    args = ap.parse_args()

    if args.universal:
        _universal_sweep(args)
        return

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


def _universal_sweep(args) -> None:
    """A free-standing universal unit across the depth range it must handle."""
    min_creek_ft = (args.gather_width + 0.3) / 0.3048  # gather + margin, in feet
    print("=" * 70)
    print(" CreekTurbine — UNIVERSAL free-standing funnel unit")
    print("=" * 70)
    print(f" Fixed intake gather width: {args.gather_width:.2f} m "
          f"({args.gather_width/0.3048:.1f} ft) → fits any creek wider than "
          f"~{min_creek_ft:.0f} ft")
    print(f" Throat/rotor: {args.throat_width:.2f} m wide, {args.confinement:.2f} "
          f"confinement (free-standing, water can bypass — honest derate)")
    print(f" Mellow creek speed: {args.up_vel:.2f} m/s")
    print("-" * 70)
    print(f" {'water depth':>12} | {'throat v':>9} | {'power':>7} | {'per day':>8} | laptop charges/day")
    for depth in (0.15, 0.30, 0.45, 0.60, 0.90):
        fi = fn.FunnelIntake.universal(creek_depth=depth, up_velocity=args.up_vel,
                                       gather_width=args.gather_width,
                                       throat_width=args.throat_width,
                                       throat_depth=args.throat_depth,
                                       confinement=args.confinement, cp=cfg.cp,
                                       eta_generator=cfg.generator_efficiency,
                                       eta_drivetrain=cfg.drivetrain_efficiency)
        wh = fi.electrical_power() * 24 * cfg.flow_availability
        ft = depth / 0.3048
        note = "choked" if fi.choked else "continuity"
        print(f" {depth*100:4.0f} cm ({ft:.1f} ft) | {fi.throat_velocity:5.2f} m/s | "
              f"{fi.electrical_power():5.1f} W | {wh:5.0f} Wh | "
              f"{wh/args.laptop_wh:4.1f}   ({note})")
    print("-" * 70)
    print(" Reads: it works in every creek wider than its gather mouth; power grows")
    print(" with DEPTH (it funnels the full depth into the short throat and chokes).")
    print(" Charges a laptop daily in normal water; derates gracefully at 6 inches.")
    print(" Add temporary bank wing-walls at a chosen site to push toward the")
    print(" full-weir numbers (confinement → 1.0). See docs/FUNNEL.md.")
    print("=" * 70)


if __name__ == "__main__":
    main()
