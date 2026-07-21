"""
self_contained — model the all-in-one "box with a handle" for YOUR creek.

One carriable housing you set in the stream: rotor at the bottom (wet), generator
+ battery + outlets stacked above the waterline (dry). No cable, no shore box —
plug-and-play. Prints the rotor that fits the box, the power, the freeboard, and
the base ballast the current's drag demands. Creek speed comes from config.py.

    python -m scripts.self_contained
    python -m scripts.self_contained --box-dia 0.35 --box-height 0.7 \
                                     --submerged 0.35 --battery-wh 400 --figs
"""

from __future__ import annotations

import argparse

from creekturbine.config import DEFAULT_CONFIG as cfg
from creekturbine import selfcontained as sc


def main() -> None:
    ap = argparse.ArgumentParser(description="Model the self-contained creek unit")
    ap.add_argument("--box-dia", type=float, default=0.30, help="m, box outer diameter")
    ap.add_argument("--box-height", type=float, default=0.65, help="m, total height")
    ap.add_argument("--submerged", type=float, default=0.30, help="m, wet depth in creek")
    ap.add_argument("--battery-wh", type=float, default=300.0)
    ap.add_argument("--unit-mass", type=float, default=None,
                    help="kg, override the computed unit mass (default: compute it)")
    ap.add_argument("--max-weight-lb", type=float, default=40.0,
                    help="your carry-weight budget (lb) to check against")
    ap.add_argument("--figs", action="store_true", help="render a schematic to ./output")
    args = ap.parse_args()

    unit = sc.SelfContainedUnit(
        box_diameter=args.box_dia, box_height=args.box_height,
        submerged_depth=args.submerged, velocity=cfg.effective_velocity,
        battery_wh=args.battery_wh, unit_dry_mass_kg=args.unit_mass,
        cp=cfg.cp, eta_generator=cfg.generator_efficiency,
        eta_drivetrain=cfg.drivetrain_efficiency, rho=cfg.water_density)
    r = unit.report()
    LB = 2.2046

    print("=" * 66)
    print(" CreekTurbine — self-contained all-in-one unit")
    print("=" * 66)
    print(f" Box: Ø {args.box_dia*100:.0f} cm × {args.box_height*100:.0f} cm tall, "
          f"sitting {args.submerged*100:.0f} cm deep in a {cfg.effective_velocity:.2f} m/s creek")
    print("-" * 66)
    print(f" Rotor that fits: Ø {r['rotor_diameter']*100:.0f} cm × "
          f"{r['rotor_height']*100:.0f} cm  ({r['frontal_area']:.3f} m² frontal)")
    print(f" Power: ~{r['power_w']:.1f} W continuous  ({r['daily_wh']:.0f} Wh/day, "
          f"buffered by the {args.battery_wh:.0f} Wh battery)")
    print(f" Needs ≥ {r['min_water_depth']*100:.0f} cm of water; top stays "
          f"{r['freeboard']*100:.0f} cm dry (outlets above water). ", end="")
    print("✓" if r['freeboard'] > 0.12 else "✗ raise the box / shallower submersion")
    print("-" * 66)
    print(f" STABILITY (the real catch for a free-standing box):")
    print(f"   current drag ≈ {r['drag_n']:.0f} N pushing it downstream/over")
    if r['required_base_ballast_kg'] <= 0:
        print(f"   the {r['dry_mass_kg']:.0f} kg unit is heavy enough on its own. ✓")
    else:
        print(f"   add ≈ {r['required_base_ballast_kg']:.0f} kg of base ballast "
              f"(or a stake/tether) beyond the {r['dry_mass_kg']:.0f} kg unit.")
    print(f"   → a wide, weighted base + one stake makes it 'set-and-forget'.")
    print("-" * 66)
    wb = unit.weight_breakdown()
    print(" WEIGHT (computed from components):")
    for k in ("housing", "rotor", "shaft_bearings", "generator", "battery",
              "electronics", "misc"):
        print(f"     {k:<15} {wb[k]:5.1f} kg  ({wb[k]*LB:4.1f} lb)")
    print(f"     {'—'*13}")
    print(f"     unit dry        {r['dry_mass_kg']:5.1f} kg  ({r['dry_mass_kg']*LB:4.1f} lb)")
    print(f"     + base ballast  {r['required_base_ballast_kg']:5.1f} kg  "
          f"({r['required_base_ballast_kg']*LB:4.1f} lb)")
    tot = r['total_weight_kg']
    budget_kg = args.max_weight_lb / LB
    print(f"     {'='*13}")
    print(f"     TOTAL           {tot:5.1f} kg  ({tot*LB:4.1f} lb)", end="")
    if tot <= budget_kg:
        head = budget_kg - tot
        print(f"   ✓ under {args.max_weight_lb:.0f} lb, ~{head*LB:.0f} lb to spare")
        print(f"   → spend the headroom on a bigger battery (more buffer) or more")
        print(f"     base ballast (stability in a faster creek).")
    else:
        print(f"   ✗ over {args.max_weight_lb:.0f} lb by {(tot-budget_kg)*LB:.0f} lb "
              f"— shrink the box/battery or lighten the ballast (stake instead).")
    print("-" * 66)
    print(" Wet rotor → dry generator via a MAGNETIC COUPLING through the bulkhead")
    print(" (no seal to leak). Outlets/battery/controller live in the dry top.")
    print("=" * 66)

    if args.figs:
        from creekturbine import simulator
        p = simulator.self_contained_schematic(unit, "output")
        print("Schematic:", p)


if __name__ == "__main__":
    main()
