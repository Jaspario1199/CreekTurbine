"""
Helical Savonius BLADE — one printable SEGMENT.

Research (docs/RESEARCH_ROTORS.md) picks an optimized Savonius with a HELICAL
twist for self-start-at-any-angle, smooth torque, and debris shedding. A full
blade is ROTOR_HEIGHT tall (too tall for any consumer printer), so this part is
ONE stackable segment of it:

  * Print SCOOP_COUNT x BLADE_SEGMENTS copies of this ONE part — segments of a
    helix are identical; each sits on the last rotated by BLADE_SEG_TWIST.
  * Register segments with 3 mm pins (a scrap of filament) in the end-face pin
    holes, epoxy the joints, and seat the finished blade ends in the end plates'
    profile-matched grooves (see end_plate.py).

Set BLADE_TWIST_DEG = 0 in params for a straight (non-helical) rotor; the
segmenting and pins still apply. The cross-section itself lives in cad/lib.py so
the blade and the end-plate grooves can never drift apart.
"""

import cadquery as cq

from cad import params as P
from cad import lib


def build():
    # One segment: the shared C-profile twist-extruded by the per-segment twist.
    blade = lib.savonius_profile(
        cq.Workplane("XY"), P.ROTOR_DIA, P.SCOOP_OVERLAP, P.BLADE_THK
    ).twistExtrude(P.BLADE_SEG_H, P.BLADE_SEG_TWIST)

    # Alignment pin holes: bottom face at 0°, top face rotated by the segment
    # twist (where the profile has arrived). 2 pins per interface.
    for z0, height, ang in ((0.0, P.BLADE_PIN_DEPTH, 0.0),
                            (P.BLADE_SEG_H - P.BLADE_PIN_DEPTH, P.BLADE_PIN_DEPTH,
                             P.BLADE_SEG_TWIST)):
        pts = lib.blade_pin_points(P.ROTOR_DIA, P.SCOOP_OVERLAP, P.BLADE_THK, ang)
        pins = (cq.Workplane("XY").workplane(offset=z0)
                .pushPoints(pts).circle(P.BLADE_PIN_DIA / 2.0).extrude(height))
        blade = blade.cut(pins)
    return blade


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "savonius_blade.stl")
