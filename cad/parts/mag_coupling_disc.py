"""
Magnetic coupling DISC (print TWO — one per shaft).

A disc with a ring of blind pockets for cylindrical magnets and a central hub for
the shaft. Press magnets into the pockets in ALTERNATING polarity (N, S, N, S …).
Mount one disc on the wet rotor shaft (magnets facing UP to the bulkhead) and one
on the dry generator shaft (magnets facing DOWN), with the sealed non-magnetic
bulkhead in the small gap between them. Torque crosses the wall with no
penetration; overload just makes the magnets slip (built-in torque limiter).

Re-size for your rotor's torque with `python -m scripts.mag_coupling`, then set
MAG_COUNT / MAG_DIA / MAG_MEAN_RADIUS in cad/params.py. See docs/MAG_COUPLING.md.
"""

import cadquery as cq

from cad import params as P


def build(bore: float = None):
    bore = P.SHAFT_DIA if bore is None else bore
    r_disc = P.MAGDISC_DIA / 2.0

    disc = cq.Workplane("XY").circle(r_disc).extrude(P.MAGDISC_THK)

    # Blind magnet pockets in a ring on the top face.
    disc = (
        disc.faces(">Z").workplane(centerOption="CenterOfBoundBox")
        .polarArray(radius=P.MAG_MEAN_RADIUS, startAngle=0, angle=360, count=P.MAG_COUNT)
        .circle((P.MAG_DIA + P.MAG_POCKET_CLEAR) / 2.0)
        .cutBlind(-P.MAG_THK)
    )

    # Central hub, then the shaft bore.
    boss_h = max(0.0, P.HUB_THK - P.MAGDISC_THK)
    if boss_h > 0:
        disc = (disc.faces(">Z").workplane(centerOption="CenterOfBoundBox")
                .circle(P.HUB_DIA / 2.0).extrude(boss_h))
    disc = (disc.faces(">Z").workplane(centerOption="CenterOfBoundBox")
            .hole(bore + P.CLEARANCE))

    # Radial set screw into the hub (cut a horizontal cylinder along +Y).
    z = P.MAGDISC_THK + boss_h / 2.0 if boss_h > 0 else P.MAGDISC_THK / 2.0
    screw = (cq.Workplane("XZ").workplane(offset=-r_disc)
             .center(0, z).circle(P.SETSCREW_M5 / 2.0).extrude(r_disc))
    disc = disc.cut(screw)
    return disc


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "mag_coupling_disc.stl")
