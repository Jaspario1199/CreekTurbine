"""
ROTOR CAGE — TOP RING.

The wet section is an open cage: two printed rings joined by four BOUGHT 20 mm
aluminium square-tube columns (a one-piece 600 mm cage is unprintable; tube is
stiffer and cheaper). This top ring:

  * sockets the four columns (blind pockets hanging below the ring, with radial
    M5 clamp screws),
  * carries the bulkhead bolt circle, so the stack CAGE RING -> BULKHEAD ->
    HOUSING FLOOR clamps with one ring of 8 M5 bolts,
  * leaves a central opening for the coupling's wet disc to run just below the
    bulkhead membrane.

Water and debris pass freely through the cage; the rotor spins inside it.
"""

import cadquery as cq

from cad import params as P


def build():
    ro = P.CAGE_RING_OD / 2.0
    ri = P.HOUSING_FLOOR_OPEN / 2.0 - 3.0  # slight overlap under the bulkhead rim
    thk = P.CAGE_RING_THK
    pocket = P.CAGE_COL + P.CAGE_SOCKET_CLEAR
    boss = pocket + 2 * P.WALL              # socket boss outer square
    boss_h = P.CAGE_SOCKET_DEPTH + 4.0      # hangs below the ring; 4 mm blind top

    ring = cq.Workplane("XY").circle(ro).circle(ri).extrude(thk)

    # Bulkhead clamp circle (shared with the dry housing floor).
    ring = (ring.faces(">Z").workplane(centerOption="CenterOfBoundBox")
            .polarArray(radius=P.BULKHEAD_BOLT_CIRCLE / 2.0, startAngle=0,
                        angle=360, count=P.BULKHEAD_BOLTS)
            .hole(P.SCREW_M5))

    for i in range(P.CAGE_COL_COUNT):
        ang = 45.0 + i * 360.0 / P.CAGE_COL_COUNT
        # socket boss hanging below the ring at radius CAGE_COL_R on this diagonal
        b = (cq.Workplane("XY").center(P.CAGE_COL_R, 0)
             .rect(boss, boss).extrude(-boss_h)
             .rotate((0, 0, 0), (0, 0, 1), ang))
        ring = ring.union(b)
        # blind square pocket, open downward, SOCKET_DEPTH deep
        p = (cq.Workplane("XY").workplane(offset=-boss_h)
             .center(P.CAGE_COL_R, 0).rect(pocket, pocket)
             .extrude(P.CAGE_SOCKET_DEPTH)
             .rotate((0, 0, 0), (0, 0, 1), ang))
        ring = ring.cut(p)
        # radial M5 clamp screw into the pocket (cylinder along the local X axis)
        s = (cq.Workplane("YZ").workplane(offset=P.CAGE_COL_R - boss)
             .center(0, -boss_h + P.CAGE_SOCKET_DEPTH / 2.0)
             .circle(P.SETSCREW_M5 / 2.0).extrude(2 * boss)
             .rotate((0, 0, 0), (0, 0, 1), ang))
        ring = ring.cut(s)
    return ring


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "cage_ring_top.stl")
