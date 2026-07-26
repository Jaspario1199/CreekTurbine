"""
FULL-UNIT ASSEMBLY — the base CAD model of everything, in one file.

Positions every part (printed, cut, and bought) into the Mk1 stack and exports:

    python -m cad.assembly
      -> cad/step/_assembly.step   (named parts — open in FreeCAD/Fusion/any viewer)
      -> cad/stl/_assembly.stl     (single mesh, for quick 3D preview)

Bought items (columns, shaft, generator, battery) are modeled as simple solids
so the assembly is complete; their specs live in docs/HARDWARE.md. Positions
mirror docs/SPEC.md's stack: skid → cage → rotor → coupling → bulkhead → dry
canister → lid, with the funnel wings and trash rack on the intake side.
"""

import importlib
import math
import os

import cadquery as cq

from cad import params as P

# --- the vertical stack (mm), bottom of skid runners = z 0 -------------------
Z_SKID = 15.0                       # skid plate bottom (runners below)
Z_CAGE_BOT = Z_SKID + P.SKID_THK    # 23
Z_COL0, Z_COL1 = 35.0, 35.0 + P.CAGE_COL_LEN            # column span
Z_PLATE_BOT = 45.0                  # lower end plate
Z_BLADE0 = Z_PLATE_BOT + 6.0 - P.PLATE_GROOVE_DEPTH     # blades seat in grooves
Z_PLATE_TOP = Z_BLADE0 + P.ROTOR_HEIGHT + P.PLATE_GROOVE_DEPTH
Z_CAGE_TOP = Z_COL1 + 4.0           # ring blind-top sits on the columns
Z_BULKHEAD = Z_CAGE_TOP + P.CAGE_RING_THK
Z_FLOOR = Z_BULKHEAD + P.BULKHEAD_FLANGE_THK
Z_LID = Z_FLOOR + P.HOUSING_DRY_H


def _part(name):
    return importlib.import_module(f"cad.parts.{name}").build()


def _loc(x=0.0, y=0.0, z=0.0, axis=None, angle=0.0):
    if axis is None:
        return cq.Location(cq.Vector(x, y, z))
    return cq.Location(cq.Vector(x, y, z), cq.Vector(*axis), angle)


def build():
    asm = cq.Assembly(name="creekturbine_mk1")

    # Base & cage
    asm.add(_part("skid_base"), name="skid_base", loc=_loc(z=Z_SKID))
    asm.add(_part("cage_ring_bottom"), name="cage_ring_bottom", loc=_loc(z=Z_CAGE_BOT))
    col = (cq.Workplane("XY").rect(P.CAGE_COL, P.CAGE_COL)
           .extrude(P.CAGE_COL_LEN))
    for i in range(P.CAGE_COL_COUNT):
        a = math.radians(45.0 + i * 360.0 / P.CAGE_COL_COUNT)
        asm.add(col, name=f"column_{i+1} (buy: 20mm Al tube)",
                loc=_loc(P.CAGE_COL_R * math.cos(a), P.CAGE_COL_R * math.sin(a),
                         Z_COL0))
    asm.add(_part("cage_ring_top"), name="cage_ring_top", loc=_loc(z=Z_CAGE_TOP))

    # Rotor: shaft, plates (top one flipped), 2 blades x segments
    shaft = cq.Workplane("XY").circle(P.SHAFT_DIA / 2.0).extrude(
        Z_BULKHEAD - 11.0 - 30.0)
    asm.add(shaft, name="shaft (buy: 16mm stainless)", loc=_loc(z=30.0))
    plate = _part("end_plate")
    asm.add(plate, name="end_plate_bottom", loc=_loc(z=Z_PLATE_BOT))
    asm.add(plate, name="end_plate_top",
            loc=_loc(z=Z_PLATE_TOP + 12.0, axis=(1, 0, 0), angle=180.0))
    blade = _part("savonius_blade")
    for phase in (0.0, 180.0):
        for k in range(P.BLADE_SEGMENTS):
            asm.add(blade, name=f"blade{int(phase//180)+1}_seg{k+1}",
                    loc=_loc(z=Z_BLADE0 + k * P.BLADE_SEG_H, axis=(0, 0, 1),
                             angle=phase + k * P.BLADE_SEG_TWIST))

    # Sealed drivetrain
    disc = _part("mag_coupling_disc")
    asm.add(disc, name="mag_disc_wet", loc=_loc(z=Z_BULKHEAD - P.HUB_THK - 1.0))
    asm.add(_part("magnet_cover"), name="magnet_cover",
            loc=_loc(z=Z_BULKHEAD - 1.0 - P.MAGCOVER_THK))
    asm.add(_part("bulkhead"), name="bulkhead (cut: 3mm PC sheet)",
            loc=_loc(z=Z_BULKHEAD))
    asm.add(disc, name="mag_disc_dry",
            loc=_loc(z=Z_FLOOR + 1.0 + P.HUB_THK, axis=(1, 0, 0), angle=180.0))

    # Dry canister
    asm.add(_part("housing_upper"), name="housing_upper", loc=_loc(z=Z_FLOOR))
    gen = cq.Workplane("XY").circle(P.GEN_BODY_DIA / 2.0).extrude(70.0)
    asm.add(gen, name="generator (buy: low-Kv PMA)",
            loc=_loc(z=Z_FLOOR + P.HOUSING_FLOOR_THK + 26.0))
    asm.add(_part("generator_mount"), name="generator_mount",
            loc=_loc(z=Z_FLOOR + P.HOUSING_FLOOR_THK + 96.0))
    battery = cq.Workplane("XY").box(160, 100, 120, centered=(True, True, False))
    asm.add(battery, name="battery (buy: 12V LiFePO4)",
            loc=_loc(x=70.0, z=Z_FLOOR + 160.0))
    asm.add(_part("lid_handle"), name="lid_handle", loc=_loc(z=Z_LID))

    # Intake: two wings (one mirrored via 180° X flip) + angled trash rack
    wing = _part("funnel_wing")
    asm.add(wing, name="funnel_wing_L (cut: 6mm HDPE)",
            loc=_loc(-141.0, 141.0, Z_CAGE_BOT, axis=(0, 0, 1), angle=150.0))
    asm.add(wing, name="funnel_wing_R (cut: 6mm HDPE)",
            loc=_loc(-141.0, -141.0, Z_CAGE_BOT + P.WING_H, axis=(1, 0, 0),
                     angle=180.0) * _loc(axis=(0, 0, 1), angle=-150.0))
    asm.add(_part("trash_rack"), name="trash_rack",
            loc=_loc(-320.0, 0.0, 180.0, axis=(1, 0, 0), angle=75.0))
    return asm


def main():
    os.makedirs("cad/step", exist_ok=True)
    os.makedirs("cad/stl", exist_ok=True)
    asm = build()
    asm.save("cad/step/_assembly.step")
    cq.exporters.export(asm.toCompound(), "cad/stl/_assembly.stl")
    n = len(asm.children)
    print(f"exported cad/step/_assembly.step + cad/stl/_assembly.stl ({n} parts)")


if __name__ == "__main__":
    main()
