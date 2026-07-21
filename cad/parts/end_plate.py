"""
Savonius END PLATE (print two: top and bottom).

The two end plates clamp the cut-PVC scoops top and bottom and carry the shaft
through a thickened central hub. Overhanging the scoops slightly (PLATE_DIA >
ROTOR_DIA) measurably raises a Savonius's Cp by suppressing flow spill off the
scoop ends. The bolt rings are a starting pattern — a scoop's leading and
trailing edges bolt through the inner and outer rings; adjust to your pipe.
"""

import cadquery as cq

from cad import params as P


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
