"""
Savonius END PLATE (print two: top and bottom).

The two end plates seat the blade ends and carry the shaft through a thickened
central hub. Overhanging the blades slightly (PLATE_DIA > ROTOR_DIA) measurably
raises a Savonius's Cp by suppressing flow spill off the scoop ends.

Blade attachment: each plate carries SCOOP_COUNT **profile-matched grooves**
(cut from the same cross-section definition the blade extrudes, cad/lib.py) —
the blade end drops into its groove and is epoxied/clamped, because a twisted
blade edge cannot take a vertical bolt. The bolt rings remain as clamping /
through-rod holes. The two plates are IDENTICAL: at assembly, rotate the top
plate about the shaft until its grooves meet the twisted blade tops (any
BLADE_TWIST_DEG works, since the groove pattern is SCOOP_COUNT-fold symmetric).
"""

import cadquery as cq

from cad import params as P
from cad import lib


def build():
    r_plate = P.PLATE_DIA / 2.0

    plate = cq.Workplane("XY").circle(r_plate).extrude(P.PLATE_THK)

    # Scoop mounting holes: an inner and an outer ring so each half-pipe scoop
    # can be through-bolted at both of its edges.
    n = P.SCOOP_BOLTS_PER_SIDE * 2
    for r in (P.ROTOR_DIA * 0.25, P.ROTOR_DIA * 0.48):
        plate = (
            plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
            .polarArray(radius=r, startAngle=0, angle=360, count=n)
            .hole(P.SCREW_M5)
        )

    # Lightening holes to save plastic and shed weight/buoyancy.
    if P.PLATE_LIGHTENING:
        plate = (
            plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
            .polarArray(radius=P.ROTOR_DIA * 0.36, startAngle=30, angle=360, count=6)
            .hole(P.PLATE_DIA * 0.10)
        )

    # Blade-seat grooves: the shared C-profile, one per scoop, evenly phased.
    # (They may graze a lightening hole — cosmetic, not structural.)
    for i in range(P.SCOOP_COUNT):
        ang = i * 360.0 / P.SCOOP_COUNT
        wp = (plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
              .transformed(rotate=(0, 0, ang)))
        plate = lib.savonius_profile(wp, P.ROTOR_DIA, P.SCOOP_OVERLAP,
                                     P.BLADE_THK + 2 * P.CLEARANCE
                                     ).cutBlind(-P.PLATE_GROOVE_DEPTH)

    # Central hub boss (extra meat around the shaft) then the shaft bore.
    boss_h = max(0.0, P.HUB_THK - P.PLATE_THK)
    if boss_h > 0:
        plate = (
            plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
            .circle(P.HUB_DIA / 2.0).extrude(boss_h)
        )
    plate = (
        plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
        .hole(P.SHAFT_DIA + P.CLEARANCE)
    )
    return plate


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "end_plate.stl")
