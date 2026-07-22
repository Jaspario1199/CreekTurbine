"""
TRASH RACK / intake screen — sheds leaves, sticks, and debris.

Debris clogging and log strikes are the #1 field failure of small hydrokinetic
units (see docs/RESEARCH_ROTORS.md). This is a barred screen that mounts across
the intake: water passes between the bars, debris larger than RACK_GAP is shed by
the flow. Angle it downstream-leaning in the current so debris rides up and over
rather than pinning to it, and keep the open area generous so the screen doesn't
itself become the blockage (the model in siting.py sizes that).
"""

import cadquery as cq

from cad import params as P


def build():
    R = P.RACK_DIA / 2.0
    inner_r = R - P.RACK_RIM
    thk = P.RACK_THK

    # Solid outer rim.
    ring = cq.Workplane("XY").circle(R).circle(inner_r).extrude(thk)

    # Parallel bars spanning the opening.
    pitch = P.RACK_BAR + P.RACK_GAP
    n = max(1, int((2.0 * inner_r) // pitch))
    xs = [(-(n - 1) / 2.0 + i) * pitch for i in range(n)]
    bars = (cq.Workplane("XY").pushPoints([(x, 0.0) for x in xs])
            .box(P.RACK_BAR, 2.0 * R, thk, centered=(True, True, False)))
    bars = bars.intersect(cq.Workplane("XY").circle(R).extrude(thk))

    return ring.union(bars)


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "trash_rack.stl")
