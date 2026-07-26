"""
ROTOR CAGE — BOTTOM RING / BASE DISC.

The lower half of the wet cage: a disc that

  * sockets the four aluminium columns (same pockets as the top ring, opening
    UPWARD here),
  * carries the rotor's LOWER BEARING in a raised centre boss (seat sized for a
    flanged stainless bearing, BEARING_OD) — raised so silt has to climb before
    it reaches the bearing,
  * bolts down to the skid/ballast base (4x M5 at CAGE_BOLT_R),
  * is perforated with drain/wash-through holes so sediment flushes instead of
    accumulating.
"""

import cadquery as cq

from cad import params as P


def build():
    ro = P.CAGE_RING_OD / 2.0
    thk = P.CAGE_RING_THK
    pocket = P.CAGE_COL + P.CAGE_SOCKET_CLEAR
    boss = pocket + 2 * P.WALL

    disc = cq.Workplane("XY").circle(ro).extrude(thk)

    # Raised centre boss with the lower-bearing seat (blind, so grit can't pass).
    disc = (disc.faces(">Z").workplane(centerOption="CenterOfBoundBox")
            .circle((P.BEARING_OD + 2 * P.WALL + 8.0) / 2.0).extrude(14.0))
    disc = (disc.faces(">Z").workplane(centerOption="CenterOfBoundBox")
            .hole(P.BEARING_OD + P.CLEARANCE, depth=10.0))

    # Drain / wash-through holes so sediment flushes.
    disc = (disc.faces("<Z").workplane(centerOption="CenterOfBoundBox")
            .polarArray(radius=ro * 0.55, startAngle=22.5, angle=360, count=8)
            .hole(18.0))

    # Skid hold-down bolts.
    disc = (disc.faces("<Z").workplane(centerOption="CenterOfBoundBox")
            .polarArray(radius=P.CAGE_BOLT_R, startAngle=0, angle=360, count=4)
            .hole(P.SCREW_M5))

    # Column sockets: bosses standing UP from the disc, pockets opening upward.
    for i in range(P.CAGE_COL_COUNT):
        ang = 45.0 + i * 360.0 / P.CAGE_COL_COUNT
        b = (cq.Workplane("XY").workplane(offset=thk)
             .center(P.CAGE_COL_R, 0).rect(boss, boss)
             .extrude(P.CAGE_SOCKET_DEPTH + 4.0)
             .rotate((0, 0, 0), (0, 0, 1), ang))
        disc = disc.union(b)
        p = (cq.Workplane("XY").workplane(offset=thk + 4.0)
             .center(P.CAGE_COL_R, 0).rect(pocket, pocket)
             .extrude(P.CAGE_SOCKET_DEPTH)
             .rotate((0, 0, 0), (0, 0, 1), ang))
        disc = disc.cut(p)
        s = (cq.Workplane("YZ").workplane(offset=P.CAGE_COL_R - boss)
             .center(0, thk + 4.0 + P.CAGE_SOCKET_DEPTH / 2.0)
             .circle(P.SETSCREW_M5 / 2.0).extrude(2 * boss)
             .rotate((0, 0, 0), (0, 0, 1), ang))
        disc = disc.cut(s)
    return disc


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "cage_ring_bottom.stl")
