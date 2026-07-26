"""
DRY HOUSING — the sealed upper canister.

Holds everything that must stay dry: generator + dry coupling disc (just above
the floor), boost-MPPT controller, battery, and the outlet panel. Features:

  * sealed FLOOR with a central opening over the bulkhead membrane; the
    bulkhead clamps flat UNDER this floor (its O-ring against the floor's
    underside) on the shared 8-bolt circle,
  * cylindrical shell (HOUSING_ID bore clears nothing — the rotor is below;
    the bore simply matches the printed/cut shell stock),
  * top LID FLANGE with 6 bolts,
  * a rectangular side cutout for a commercial USB/12 V outlet panel (mount the
    panel with its own gasket, above the waterline by design).

Print in sections or roll from HDPE/PVC pipe of matching diameter — for pipe,
this STEP is the drilling/cutting template.
"""

import cadquery as cq

from cad import params as P


def build():
    ri = P.HOUSING_ID / 2.0
    ro = P.HOUSING_OD / 2.0
    h = P.HOUSING_DRY_H

    # Shell + integral floor.
    shell = cq.Workplane("XY").circle(ro).circle(ri).extrude(h)
    floor = cq.Workplane("XY").circle(ro).extrude(P.HOUSING_FLOOR_THK)
    body = shell.union(floor)

    # Coupling window + bulkhead bolt circle in the floor.
    body = (body.faces("<Z").workplane(centerOption="CenterOfBoundBox")
            .hole(P.HOUSING_FLOOR_OPEN))
    body = (body.faces("<Z").workplane(centerOption="CenterOfBoundBox")
            .polarArray(radius=P.BULKHEAD_BOLT_CIRCLE / 2.0, startAngle=0,
                        angle=360, count=P.BULKHEAD_BOLTS)
            .hole(P.SCREW_M5))

    # Top lid flange.
    flange = (cq.Workplane("XY").workplane(offset=h - 6.0)
              .circle(P.HOUSING_FLANGE_OD / 2.0).circle(ri).extrude(6.0))
    body = body.union(flange)
    body = (body.faces(">Z").workplane(centerOption="CenterOfBoundBox")
            .polarArray(radius=P.HOUSING_LID_BC / 2.0, startAngle=0,
                        angle=360, count=P.HOUSING_LID_BOLTS)
            .hole(P.SCREW_M5))

    # Outlet-panel cutout through the shell wall, high on the +Y side.
    cut = (cq.Workplane("XZ")
           .workplane(offset=-(ro + 5.0))
           .center(0, h - 90.0)
           .rect(P.PANEL_CUT_W, P.PANEL_CUT_H)
           .extrude(2 * (ro + 5.0)))
    # only remove the far-side wall once: intersect the cut with the +Y half
    halfspace = (cq.Workplane("XY").center(0, ro).rect(2 * ro, 2 * ro)
                 .extrude(h))
    body = body.cut(cut.intersect(halfspace))
    return body


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "housing_upper.stl")
