"""
SHAFT COUPLER — joins the rotor shaft (bottom) to the generator shaft (top).

Two coaxial bores of different diameters, each locked by radial set screws.
Print in a strong material (PETG/ABS/nylon) or, better for a wet load path,
use a metal coupler and treat this as the fit reference. Keep the bores a snug
slip fit; the set screws (ideally onto flats you file on the shafts) carry the
torque.
"""

import cadquery as cq

from cad import params as P


def build():
    body = cq.Workplane("XY").circle(P.COUPLER_DIA / 2.0).extrude(P.COUPLER_LEN)

    bore_depth = P.COUPLER_LEN / 2.0 - 3.0
    # rotor shaft bore up from the bottom
    body = (
        body.faces("<Z").workplane(centerOption="CenterOfBoundBox")
        .hole(P.SHAFT_DIA + P.CLEARANCE, depth=bore_depth)
    )
    # generator shaft bore down from the top
    body = (
        body.faces(">Z").workplane(centerOption="CenterOfBoundBox")
        .hole(P.GEN_SHAFT_DIA + P.CLEARANCE, depth=bore_depth)
    )

    # Radial set-screw holes into each bore (cut horizontal cylinders along +Y).
    for frac in (0.22, 0.78):
        z = P.COUPLER_LEN * frac
        screw = (
            cq.Workplane("XZ").workplane(offset=-P.COUPLER_DIA / 2.0)
            .center(0, z).circle(P.SETSCREW_M5 / 2.0)
            .extrude(P.COUPLER_DIA)
        )
        body = body.cut(screw)
    return body


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "shaft_coupler.stl")
