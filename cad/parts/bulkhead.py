"""
BULKHEAD / sealing plate — the wall the magnetic coupling drives through.

This is the sealed boundary between the wet (rotor) side and the dry (generator +
battery + electronics) side. The magnetic coupling's two discs run close on either
face; nothing penetrates the plate, so the dry side stays dry. It is:

  * THIN at the centre — that membrane thickness is part of the coupling gap, so
    keep it small (BULKHEAD_CENTER_THK); it only has to resist water pressure over
    a small span.
  * THICK and BOLTED at the rim, with an O-ring groove, so it clamps water-tight
    to the housing.

>>> PRINT/CUT THIS IN A NON-MAGNETIC MATERIAL ONLY <<< — polycarbonate,
fiberglass, aluminium, or 316 stainless. Plain steel shorts the magnetic flux and
the coupling dies. See docs/MAG_COUPLING.md.
"""

import cadquery as cq

from cad import params as P


def build():
    r_out = P.BULKHEAD_DIA / 2.0
    plate = cq.Workplane("XY").circle(r_out).extrude(P.BULKHEAD_FLANGE_THK)

    # Thin the centre: recess both faces down to the membrane thickness.
    recess = (P.BULKHEAD_FLANGE_THK - P.BULKHEAD_CENTER_THK) / 2.0
    if recess > 0:
        plate = (plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
                 .circle(P.BULKHEAD_MEMBRANE_DIA / 2.0).cutBlind(-recess))
        plate = (plate.faces("<Z").workplane(centerOption="CenterOfBoundBox")
                 .circle(P.BULKHEAD_MEMBRANE_DIA / 2.0).cutBlind(-recess))

    # Clamp bolt holes around the rim.
    plate = (plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
             .polarArray(radius=P.BULKHEAD_BOLT_CIRCLE / 2.0, startAngle=0,
                         angle=360, count=P.BULKHEAD_BOLTS)
             .hole(P.SCREW_M5))

    # O-ring groove on the top flange (annular pocket).
    ro = P.BULKHEAD_ORING_MEAN / 2.0
    plate = (plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
             .circle(ro + P.BULKHEAD_ORING_W / 2.0)
             .circle(ro - P.BULKHEAD_ORING_W / 2.0)
             .cutBlind(-P.BULKHEAD_ORING_DEPTH))
    return plate


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "bulkhead.stl")
