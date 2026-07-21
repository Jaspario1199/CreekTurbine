"""
demo_sim — render the whole picture book from your config into ./output.

    python -m scripts.demo_sim
    python -m scripts.demo_sim --outdir some/dir

Produces power_vs_velocity.png, sizing_curve.png, energy_budget.png and (for a
Savonius) savonius_schematic.png. No display or hardware required.
"""

from __future__ import annotations

import argparse

from creekturbine.config import DEFAULT_CONFIG
from creekturbine import simulator


def main() -> None:
    ap = argparse.ArgumentParser(description="Render CreekTurbine figures")
    ap.add_argument("--outdir", default="output")
    args = ap.parse_args()
    paths = simulator.render_all(DEFAULT_CONFIG, args.outdir)
    print("Wrote:")
    for p in paths:
        print("  ", p)


if __name__ == "__main__":
    main()
