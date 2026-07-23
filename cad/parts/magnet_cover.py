"""
MAGNET COVER — the marine seal for the WET coupling disc.

Bare NdFeB rusts through pinholes; a dab of glue is not sealing. Procedure:
pot the magnets in their pockets with epoxy, wet a layer of epoxy over the
whole face, and press this thin cover disc on — it becomes a continuous bonded
barrier over every magnet. 1.2 mm thickness costs ~0.1 mm of extra coupling gap
per the model's derating; buy it back by seating magnets 1 mm proud... no —
keep them flush and accept the tiny loss; sealing beats 2 % of torque.
"""

import cadquery as cq

from cad import params as P


def build():
    cover = (cq.Workplane("XY").circle(P.MAGCOVER_DIA / 2.0)
             .extrude(P.MAGCOVER_THK))
    cover = (cover.faces(">Z").workplane(centerOption="CenterOfBoundBox")
             .hole(P.MAGCOVER_HOLE))
    return cover


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "magnet_cover.stl")
