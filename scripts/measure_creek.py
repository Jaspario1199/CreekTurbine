"""
measure_creek — turn a tape measure, a stick, and a stopwatch into real numbers.

Because power goes as velocity CUBED, a guessed velocity can be 8x wrong in
power. Spend twenty minutes measuring instead. This script both explains the
field procedure and does the arithmetic — pass your measurements as flags, or
run it with no flags to see the instructions and a worked example.

    python -m scripts.measure_creek
    python -m scripts.measure_creek --width 1.6 --depth 0.4 --distance 5 --seconds 9.5
"""

from __future__ import annotations

import argparse

from creekturbine import siting


INSTRUCTIONS = """\
HOW TO MEASURE YOUR CREEK (float method + cross-section)
--------------------------------------------------------
Pick a straight, roughly uniform reach a few meters long — not a pool, not a
waterfall. Then:

 1. WIDTH:  measure the water-surface width (m).
 2. DEPTH:  measure the depth at several points across the width and AVERAGE
            them (m). Use the average, not the deepest spot.
 3. VELOCITY (float method):
      a. Mark a start line and an end line a known DISTANCE apart (say 5 m).
      b. Drop a floating stick/orange upstream of the start line so it's up to
         speed, then time it from start to end. Do 3-5 runs and average.
      c. This gives SURFACE speed; the depth-averaged mean is ~0.85 of it.

Feed the four numbers below back into creekturbine/config.py:
      CREEK_VELOCITY  (this script's 'mean velocity')
      CREEK_WIDTH, CREEK_DEPTH

TIP: the fastest, narrowest, shallowest riffle is usually the best turbine spot,
and you can make it better with a chute — see docs/SITING.md.
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Measure creek velocity & flow")
    ap.add_argument("--width", type=float, help="water surface width (m)")
    ap.add_argument("--depth", type=float, help="AVERAGE depth across the width (m)")
    ap.add_argument("--distance", type=float, help="float-method reach length (m)")
    ap.add_argument("--seconds", type=float, help="seconds for the float to travel it")
    args = ap.parse_args()

    have_all = all(v is not None for v in (args.width, args.depth,
                                           args.distance, args.seconds))
    if not have_all:
        print(INSTRUCTIONS)
        print("WORKED EXAMPLE  (--width 1.6 --depth 0.4 --distance 5 --seconds 9.5):")
        args.width, args.depth, args.distance, args.seconds = 1.6, 0.4, 5.0, 9.5

    m = siting.CreekMeasurement(width_m=args.width, avg_depth_m=args.depth,
                                float_distance_m=args.distance,
                                float_seconds=args.seconds)
    surface_v = args.distance / args.seconds
    print("-" * 60)
    print(f" Surface speed:      {surface_v:.2f} m/s  ({args.distance} m in {args.seconds} s)")
    print(f" Mean velocity:      {m.mean_velocity:.2f} m/s  (×0.85 correction)")
    print(f" Channel area:       {m.area:.2f} m²  ({args.width} m × {args.depth} m)")
    print(f" Flow (discharge):   {m.flow_m3s:.3f} m³/s  "
          f"({siting.flow_rate_lpm(m.area, m.mean_velocity):,.0f} L/min)")
    print("-" * 60)
    print(" → Put CREEK_VELOCITY = %.2f, CREEK_WIDTH = %.2f, CREEK_DEPTH = %.2f"
          % (m.mean_velocity, args.width, args.depth))
    print("   into creekturbine/config.py, then run:  python -m scripts.size_turbine")


if __name__ == "__main__":
    main()
