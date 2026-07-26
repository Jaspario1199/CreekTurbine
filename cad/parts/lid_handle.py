"""
LID with carry HANDLE — the top of the dry canister.

A gasketed disc that bolts to the housing flange, with a registration lip that
drops inside the shell bore and the carry handle the whole "box with a handle"
concept hangs from (literally — it takes the unit's full ~15-18 kg, so it's a
thick bar on wide posts, not a printed afterthought). Underside carries a
shallow O-ring/gasket groove facing the flange.
"""

import cadquery as cq

from cad import params as P


def build():
    ro = P.HOUSING_FLANGE_OD / 2.0
    lid = cq.Workplane("XY").circle(ro).extrude(P.LID_THK)

    # Registration lip that drops inside the shell bore.
    lip_r = P.HOUSING_ID / 2.0 - 0.3
    lid = (lid.faces("<Z").workplane(centerOption="CenterOfBoundBox")
           .circle(lip_r).extrude(P.LID_LIP_DEPTH))

    # Gasket groove on the underside, over the flange land.
    gr = (P.HOUSING_OD + 2.0) / 2.0
    lid = (lid.faces("<Z").workplane(centerOption="CenterOfBoundBox")
           .circle(gr + 1.5).circle(gr - 1.5).cutBlind(-1.5))

    # Lid bolt circle.
    lid = (lid.faces(">Z").workplane(centerOption="CenterOfBoundBox")
           .polarArray(radius=P.HOUSING_LID_BC / 2.0, startAngle=0, angle=360,
                       count=P.HOUSING_LID_BOLTS)
           .hole(P.SCREW_M5))

    # Handle: two posts + a horizontal grip bar (takes the full unit weight).
    post_w, post_t = 26.0, 18.0
    post_h = P.HANDLE_CLEAR
    for sx in (-1.0, 1.0):
        post = (cq.Workplane("XY").workplane(offset=P.LID_THK)
                .center(sx * P.HANDLE_SPAN / 2.0, 0)
                .rect(post_w, post_t).extrude(post_h))
        lid = lid.union(post)
    bar = (cq.Workplane("YZ")
           .workplane(offset=-(P.HANDLE_SPAN / 2.0 + post_w / 2.0))
           .center(0, P.LID_THK + post_h)
           .circle(P.HANDLE_BAR_DIA / 2.0)
           .extrude(P.HANDLE_SPAN + post_w))
    lid = lid.union(bar)
    return lid


if __name__ == "__main__":  # pragma: no cover
    cq.exporters.export(build(), "lid_handle.stl")
