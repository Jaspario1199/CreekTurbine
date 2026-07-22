"""
Regenerate every CreekTurbine CAD part as STEP + STL.

    pip install -r requirements-cad.txt
    python -m cad.export_all

Edit dimensions in cad/params.py first (especially SHAFT_DIA, GEN_SHAFT_DIA,
GEN_BODY_DIA to match the parts you actually buy). Outputs land in cad/step/
and cad/stl/. Always sanity-check the result in your slicer before printing.
"""

import importlib
import os

import cadquery as cq

PARTS = [
    "end_plate",
    "shaft_coupler",
    "generator_mount",
    "savonius_blade",
    "mag_coupling_disc",
]


def main() -> None:
    os.makedirs("cad/step", exist_ok=True)
    os.makedirs("cad/stl", exist_ok=True)
    for name in PARTS:
        mod = importlib.import_module(f"cad.parts.{name}")
        obj = mod.build()
        cq.exporters.export(obj, f"cad/step/{name}.step")
        cq.exporters.export(obj, f"cad/stl/{name}.stl")
        print(f"exported cad/step/{name}.step + cad/stl/{name}.stl")
    print("done — check the meshes in your slicer before printing.")


if __name__ == "__main__":
    main()
