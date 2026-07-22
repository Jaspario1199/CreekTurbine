"""
mag_coupling — size the sealed magnetic coupling to YOUR rotor's torque.

The coupling must carry the rotor's shaft torque (with margin) through the sealed
bulkhead. This reads the rotor torque from config.py, checks the default coupling,
and tells you the magnet count / grade / gap you actually need.

    python -m scripts.mag_coupling
    python -m scripts.mag_coupling --gap 2 --magnet-dia 20 --grade N52 --safety 2.5
"""

from __future__ import annotations

import argparse
import math

from creekturbine.config import DEFAULT_CONFIG as cfg
from creekturbine import rotor as rotor_mod
from creekturbine import magnetics as mag


def main() -> None:
    ap = argparse.ArgumentParser(description="Size the sealed magnetic coupling")
    ap.add_argument("--gap", type=float, default=3.0, help="mm, bulkhead + clearances")
    ap.add_argument("--magnet-dia", type=float, default=15.0, help="mm")
    ap.add_argument("--magnet-thk", type=float, default=6.0, help="mm")
    ap.add_argument("--mean-radius", type=float, default=55.0, help="mm")
    ap.add_argument("--grade", default="N42", choices=sorted(mag.MAGNET_GRADES))
    ap.add_argument("--safety", type=float, default=2.0)
    args = ap.parse_args()

    # Rotor operating torque at the config's velocity.
    rot = rotor_mod.make_rotor_from_config(cfg)
    v = cfg.effective_velocity
    torque = rot.performance(v, rho=cfg.water_density).torque_nm if math.isfinite(
        rot.frontal_area) else 0.0

    print("=" * 66)
    print(" CreekTurbine — sealed magnetic coupling (wet shaft → dry generator)")
    print("=" * 66)
    print(f" Rotor torque to transmit: {torque:.2f} N·m at {v:.2f} m/s "
          f"({rot.performance(v).rpm:.0f} rpm)")
    print(f" Target: hold that with a {args.safety:.1f}× margin "
          f"(= {torque*args.safety:.2f} N·m capacity)")
    print("-" * 66)

    n = mag.magnets_needed(torque, args.magnet_dia, args.mean_radius, args.gap,
                           args.magnet_thk, args.grade, args.safety)
    coupling = mag.AxialMagCoupling(n_magnets=n, magnet_dia=args.magnet_dia,
                                    magnet_thickness=args.magnet_thk,
                                    mean_radius=args.mean_radius, gap=args.gap,
                                    grade=args.grade)
    cap = coupling.max_torque()
    print(f" DESIGN: {n} × Ø{args.magnet_dia:.0f}×{args.magnet_thk:.0f} mm {args.grade} "
          f"magnets per disc, on a {args.mean_radius*2:.0f} mm ring, {args.gap:.1f} mm gap")
    print(f"   → capacity ≈ {cap:.2f} N·m  (shear stress ≈ "
          f"{coupling.shear_stress_pa/1000:.0f} kPa, effective field "
          f"{coupling.b_gap:.2f} T)")
    print(f"   → {'✓ holds' if cap >= torque*args.safety else '✗ short'} the "
          f"{torque*args.safety:.2f} N·m target.")
    print("-" * 66)
    print(" Design levers (in order of impact):")
    print("   • SMALLER GAP is king — field ~ t/(t+gap); a thin bulkhead matters most")
    print("   • bigger mean radius (torque ∝ R) and more/bigger magnets")
    print("   • stronger grade (N52 > N42 > N35; ferrite needs many more)")
    print(" Overload just makes the magnets SLIP — a built-in torque limiter that")
    print(" protects the drivetrain in a jam or flood. Print two discs (cad/), press")
    print(" magnets in ALTERNATING polarity. Bench-test before trusting the estimate.")
    print("=" * 66)


if __name__ == "__main__":
    main()
