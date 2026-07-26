"""
FUNNEL WING WALL (make 2 — same part, one flipped).

The converging intake that makes a mellow creek useful (docs/FUNNEL.md): two
angled panels gather a ~0.9 m swath and squeeze it toward the rotor cage. Each
wing is a stiffened flat panel with:

  * an L-return MOUNTING FLANGE that bolts to a cage column (4x M5),
  * a horizontal STIFFENING RIB at mid-height,
  * two STAKE SLOTS near the outer end (drive rebar through into the bed; slots
    not holes, so the panel can sit on uneven bottom).

Print in sections if longer than your bed — or, better, cut the panel from 6 mm
HDPE sheet and print only nothing: this STEP is then your cutting/drilling
template. Angle the pair ~25-35° off the flow for a smooth contraction.
"""

import cadquery as cq

from cad import params as P


def build():
    L, H, T = P.WING_LEN, P.WING_H, P.WING_THK

    # Main panel: X = length, Y = thickness, Z = height.
    panel = cq.Workplane("XY").box(L, T, H, centered=(False, False, False))

    # L-return mounting flange at the cage end (x = 0).
    flange = (cq.Workplane("XY")
              .box(T, P.WING_FLANGE_W + T, H, centered=(False, False, False))
              .translate((-T, -P.WING_FLANGE_W, 0)))
    panel = panel.union(flange)
    # 4 M5 holes through the flange (bolt to the cage column / top-bottom rings)
    for z in (H * 0.15, H * 0.38, H * 0.62, H * 0.85):
        h = (cq.Workplane("YZ").workplane(offset=-T - 1.0)
             .center(-(P.WING_FLANGE_W / 2.0), z)
             .circle(P.SCREW_M5 / 2.0).extrude(T + 2.0))
        panel = panel.cut(h)

    # Horizontal stiffening rib at mid-height on the outer face.
    rib_w, rib_t = P.WING_RIB
    rib = (cq.Workplane("XY")
           .box(L * 0.9, rib_t, rib_w, centered=(False, False, False))
           .translate((L * 0.05, T, H / 2.0 - rib_w / 2.0)))
    panel = panel.union(rib)

    # Stake slots near the outer end (through the panel, vertical slots).
    sw, sh = P.WING_STAKE_SLOT
    for z in (H * 0.25, H * 0.7):
        slot = (cq.Workplane("XZ").workplane(offset=-(T + rib_t + 1.0))
                .center(L - 45.0, z)
                .slot2D(sh, sw, 90.0)
                .extrude(T + rib_t + 2.0))
        panel = panel.cut(slot)
    return panel


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "funnel_wing.stl")
