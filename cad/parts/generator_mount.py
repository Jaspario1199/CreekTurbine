"""
GENERATOR MOUNT — the top plate the PMA bolts onto, standing above the water.

The generator hangs face-down from this plate; its shaft drops through the
center bore to the coupler. Legs (threaded rod or printed posts through the
corner holes) carry the plate on the frame, well ABOVE the waterline so the
generator never gets wet. Size the center bore and bolt circle to YOUR PMA in
cad/params.py.
"""

import cadquery as cq

from cad import params as P


def build():
    plate = cq.Workplane("XY").rect(P.MOUNT_PLATE, P.MOUNT_PLATE).extrude(P.MOUNT_THK)

    # Center clearance for the PMA shaft / register boss.
    plate = (
        plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
        .hole(P.GEN_SHAFT_DIA + 6.0)
    )

    # PMA face bolt circle.
    plate = (
        plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
        .polarArray(radius=P.GEN_BOLT_CIRCLE / 2.0, startAngle=45, angle=360,
                    count=P.GEN_BOLT_COUNT)
        .hole(P.SCREW_M5)
    )

    # Leg holes near the corners (threaded rod down to the frame).
    off = P.MOUNT_PLATE / 2.0 - 14.0
    corners = [(off, off), (-off, off), (-off, -off), (off, -off)]
    pts = corners[: max(3, min(4, P.MOUNT_LEG_COUNT))]
    plate = (
        plate.faces(">Z").workplane(centerOption="CenterOfBoundBox")
        .pushPoints(pts).hole(P.SCREW_M5)
    )
    return plate


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "generator_mount.stl")
