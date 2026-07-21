"""
box_turbine — cost out the "enclosed underwater air box" idea for YOUR creek.

Compares a purely-kinetic box against one where you build in a little head, shows
the flow and power through the throat, and tells you how much ballast a submerged
air box needs (it wants to float — hard). Reads the creek velocity from
creekturbine/config.py; the box geometry comes from flags.

    python -m scripts.box_turbine
    python -m scripts.box_turbine --static-head 0.4 --throat 0.06 --diffuser 1.4 \
                                  --air-volume 0.12 --structure-mass 25 --eta 0.4
"""

from __future__ import annotations

import argparse

from creekturbine.config import DEFAULT_CONFIG as cfg
from creekturbine import ducted as d


def main() -> None:
    ap = argparse.ArgumentParser(description="Model an enclosed underwater box turbine")
    ap.add_argument("--static-head", type=float, default=0.30,
                    help="m of elevation drop you build between inlet and outlet")
    ap.add_argument("--throat", type=float, default=0.05,
                    help="m^2 throat area the flow passes through")
    ap.add_argument("--diffuser", type=float, default=1.0,
                    help="effective-head multiplier from a flared outlet (1.0 = none)")
    ap.add_argument("--cd", type=float, default=0.85, help="throat discharge coefficient")
    ap.add_argument("--eta", type=float, default=0.40, help="overall water->electrical eff")
    ap.add_argument("--air-volume", type=float, default=0.08,
                    help="m^3 of air inside the box (buoyancy/ballast)")
    ap.add_argument("--structure-mass", type=float, default=15.0,
                    help="kg dry mass of the box itself (helps it sink)")
    args = ap.parse_args()

    v0 = cfg.effective_velocity

    print("=" * 68)
    print(" CreekTurbine — enclosed underwater box (ducted / low-head) model")
    print("=" * 68)
    print(f" Creek speed at the box: {v0:.2f} m/s")
    print(f" A creek's speed is worth almost no HEAD: v²/2g = "
          f"{d.velocity_head(v0)*100:.1f} cm.")
    print(f" That's why a box helps most when you also build in a real drop.")
    print("-" * 68)

    kinetic = d.DuctedBox(args.throat, static_head=0.0, diffuser_gain=args.diffuser,
                          cd=args.cd, efficiency=args.eta)
    withdrop = d.DuctedBox(args.throat, static_head=args.static_head,
                           diffuser_gain=args.diffuser, cd=args.cd, efficiency=args.eta)

    rk = kinetic.report(v0)
    rd = withdrop.report(v0)
    print(f" Throat: {args.throat:.3f} m²   diffuser gain: {args.diffuser:.2f}   "
          f"Cd: {args.cd:.2f}   η: {args.eta:.2f}")
    print(f"  • Purely kinetic box (0 m drop):")
    print(f"      driving head {rk['driving_head_m']*100:.1f} cm → throat "
          f"{rk['throat_velocity']:.2f} m/s, {rk['flow_m3s']*1000:.0f} L/s "
          f"→ ~{rk['electrical_w']:.1f} W")
    print(f"  • With a {args.static_head:.2f} m built-in drop:")
    print(f"      driving head {rd['driving_head_m']*100:.1f} cm → throat "
          f"{rd['throat_velocity']:.2f} m/s, {rd['flow_m3s']*1000:.0f} L/s "
          f"→ ~{rd['electrical_w']:.1f} W")
    if rk['electrical_w'] > 0:
        print(f"      → the drop is worth ~{rd['electrical_w']/rk['electrical_w']:.1f}× "
              f"the power of the kinetic-only box.")
    print("-" * 68)

    buoy = d.buoyancy_force_n(args.air_volume)
    ballast = d.ballast_mass_kg(args.air_volume, structure_mass_kg=args.structure_mass)
    print(f" BUOYANCY (the catch with a submerged air box):")
    print(f"  {args.air_volume:.2f} m³ of air ⇒ {buoy:.0f} N of lift "
          f"(~{buoy/9.81:.0f} kg trying to float up).")
    print(f"  To sink & hold it (concrete ballast, 1.5× safety, crediting a "
          f"{args.structure_mass:.0f} kg box):")
    print(f"      ≈ {ballast:.0f} kg of ballast — or just keep the dry housing "
          f"AT/ABOVE the surface instead.")
    print("-" * 68)
    print(" Wet turbine → dry generator: use a MAGNETIC COUPLING through the box")
    print(" wall (no shaft hole, nothing to seal). See docs/BOX_AND_DUCT.md.")
    print("=" * 68)


if __name__ == "__main__":
    main()
