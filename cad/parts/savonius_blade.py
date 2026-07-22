"""
Helical Savonius BLADE (print SCOOP_COUNT of these).

Research (docs/RESEARCH_ROTORS.md) points at an optimized Savonius as the best
Cp-vs-durability balance for an unattended creek unit, with a HELICAL twist for
self-start-at-any-angle, smooth torque, and debris shedding. This part is one
twisted scoop: a curved (C-section) blade twist-extruded about the rotor axis.

Assembly: print SCOOP_COUNT blades, phase them evenly (2 blades → 180° apart),
overlap them by SCOOP_OVERLAP at the center, and clamp top and bottom between the
`end_plate` discs on the shaft. Set BLADE_TWIST_DEG = 0 in params for a straight
(non-helical) rotor.
"""

import cadquery as cq

from cad import params as P


def build():
    # Bucket geometry derived from the rotor diameter and overlap.
    bucket_dia = P.ROTOR_DIA / (2.0 - P.SCOOP_OVERLAP)   # mm
    outer = bucket_dia / 2.0
    inner = max(1.0, outer - P.BLADE_THK)
    # Offset the bucket centre from the rotor axis so the twist wraps the shaft.
    off = bucket_dia * (1.0 - P.SCOOP_OVERLAP) / 2.0

    # C-shaped (half-annulus) cross-section: an outer semicircle out and an inner
    # semicircle back, closed into a thin curved shell.
    profile = (
        cq.Workplane("XY")
        .moveTo(off + outer, 0)
        .threePointArc((off, outer), (off - outer, 0))    # outer arc (bulges +y)
        .lineTo(off - inner, 0)
        .threePointArc((off, inner), (off + inner, 0))    # inner arc back
        .close()
    )

    blade = profile.twistExtrude(P.ROTOR_HEIGHT, P.BLADE_TWIST_DEG)
    return blade


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "savonius_blade.stl")
