"""
Shared CAD geometry helpers.

The Savonius blade cross-section lives HERE so that the blade (which extrudes it)
and the end plates (which cut a seating groove shaped like it) can never drift
apart — one definition, two consumers. That groove-seat is how a twisted blade
attaches to a flat plate: the blade end drops into a profile-matched recess and
is clamped/epoxied, instead of pretending a helical edge can take a bolt.
"""

import math


def savonius_geometry(rotor_dia: float, overlap_ratio: float, blade_thk: float):
    """The derived numbers everything shares: (bucket_dia, offset, outer_r, inner_r).

    bucket_dia: diameter of one scoop's semicircle
    offset:     scoop centre's distance from the rotor axis
    outer_r/inner_r: outer/inner radii of the C-shaped wall section
    Rotor tip radius = offset + outer_r = rotor_dia/2 (checked by tests-by-use).
    """
    bucket_dia = rotor_dia / (2.0 - overlap_ratio)
    outer = bucket_dia / 2.0
    inner = max(1.0, outer - blade_thk)
    offset = bucket_dia * (1.0 - overlap_ratio) / 2.0
    return bucket_dia, offset, outer, inner


def savonius_profile(wp, rotor_dia: float, overlap_ratio: float, blade_thk: float):
    """Draw the closed C-section blade profile on workplane `wp` (not extruded).

    An outer semicircular arc out, an inner arc back, closed at the tips — the
    thin curved shell of one scoop, bulging toward +y.
    """
    _, off, outer, inner = savonius_geometry(rotor_dia, overlap_ratio, blade_thk)
    return (
        wp.moveTo(off + outer, 0)
        .threePointArc((off, outer), (off - outer, 0))
        .lineTo(off - inner, 0)
        .threePointArc((off, inner), (off + inner, 0))
        .close()
    )


def blade_pin_points(rotor_dia: float, overlap_ratio: float, blade_thk: float,
                     angle_deg: float = 0.0):
    """Two (x, y) alignment-pin centres on the blade's mid-wall arc.

    Used to register stacked blade segments: pins at 60° and 120° along the arc,
    optionally rotated about the rotor axis by `angle_deg` (for a segment's
    twisted top face).
    """
    _, off, outer, inner = savonius_geometry(rotor_dia, overlap_ratio, blade_thk)
    r_mid = (outer + inner) / 2.0
    pts = []
    for theta in (60.0, 120.0):
        t = math.radians(theta)
        x, y = off + r_mid * math.cos(t), r_mid * math.sin(t)
        a = math.radians(angle_deg)
        pts.append((x * math.cos(a) - y * math.sin(a),
                    x * math.sin(a) + y * math.cos(a)))
    return pts
