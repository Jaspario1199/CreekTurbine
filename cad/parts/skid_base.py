"""
SKID / BALLAST BASE — what the whole unit stands on.

A square base plate with:

  * two SACRIFICIAL RUNNERS underneath (bolt-on wear strips — print them, or
    better, cut from UHMW; they drag on gravel so the housing never does),
  * a shallow BALLAST TRAY on top (perimeter wall) that takes bricks/steel/
    concrete to the mass `scripts.self_contained` computes,
  * the cage hold-down bolt circle,
  * corner STAKE holes (Ø10 rebar/stake) and tether holes — the flood plan
    ([SELF_CONTAINED.md](../docs/SELF_CONTAINED.md)) assumes these are used.
"""

import cadquery as cq

from cad import params as P


def build():
    s = P.SKID_SIZE
    plate = cq.Workplane("XY").rect(s, s).extrude(P.SKID_THK)

    # Runners underneath (full length, near the two edges).
    for sy in (-1.0, 1.0):
        r = (cq.Workplane("XY").workplane(offset=-P.SKID_RUNNER_H)
             .center(0, sy * (s / 2.0 - P.SKID_RUNNER_W))
             .rect(s, P.SKID_RUNNER_W).extrude(P.SKID_RUNNER_H))
        plate = plate.union(r)

    # Ballast tray wall around the top perimeter.
    wall_out = (cq.Workplane("XY").workplane(offset=P.SKID_THK)
                .rect(s, s).extrude(P.TRAY_WALL_H))
    wall_in = (cq.Workplane("XY").workplane(offset=P.SKID_THK)
               .rect(s - 2 * P.TRAY_WALL_T, s - 2 * P.TRAY_WALL_T)
               .extrude(P.TRAY_WALL_H))
    plate = plate.union(wall_out.cut(wall_in))

    # Central clearance under the cage's drain holes + bearing boss.
    plate = (plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
             .hole(60.0))

    # Cage hold-down bolts.
    plate = (plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
             .polarArray(radius=P.CAGE_BOLT_R, startAngle=0, angle=360, count=4)
             .hole(P.SCREW_M5))

    # Corner stake holes + two tether holes.
    off = s / 2.0 - 18.0
    plate = (plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
             .pushPoints([(off, off), (-off, off), (-off, -off), (off, -off)])
             .hole(P.STAKE_HOLE))
    plate = (plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
             .pushPoints([(0, off), (0, -off)]).hole(8.0))
    return plate


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "skid_base.stl")
