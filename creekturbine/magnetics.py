"""
Magnetic coupling — transmit rotor torque through a SEALED wall, no shaft seal.

This is how the box/self-contained designs cross the wet→dry boundary without a
hole to leak: a ring of magnets on the wet turbine shaft drives a matching ring on
the dry generator shaft *through* a solid non-magnetic bulkhead. Nothing
penetrates the wall; if you overload it, the magnets simply **slip** — a built-in
torque limiter that protects the drivetrain in a flood or a jam.

We model an **axial (face-to-face)** coupling — two coaxial magnet discs separated
by a flat bulkhead — because that's the natural fit for a vertical shaft with a
flat sealing plate at the waterline.

The torque a magnetic coupling can transmit is, to first order,

    T_max ≈ τ · A_active · R_mean

where `A_active` is the total magnet face area, `R_mean` the magnets' mean radius,
and `τ` a magnetic *shear stress*. τ ≈ tangential_factor · (B_gap² / 2μ₀); for
real NdFeB couplings at small gaps τ lands around **10–40 kPa**, which the default
coefficients reproduce. Treat the numbers as a **sizing estimate to bench-test**,
not a guarantee — magnetics is unforgiving and gap-sensitive.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

MU0 = 4.0e-7 * math.pi          # T·m/A, permeability of free space

# Residual flux density B_r by NdFeB grade (tesla), roughly.
MAGNET_GRADES = {
    "N35": 1.17,
    "N42": 1.30,
    "N52": 1.45,
    "ferrite": 0.40,            # cheap ceramic — much weaker, needs many/large
}


def magnetic_pressure(b: float) -> float:
    """Peak normal magnetic pressure between two facing poles: B²/(2μ₀) [Pa]."""
    return b ** 2 / (2.0 * MU0)


def gap_field(b_r: float, thickness_m: float, gap_m: float) -> float:
    """Rough effective flux density reaching the opposing magnet across a gap.

    A crude but monotonic derating B_gap ≈ B_r · t/(t+gap): the field weakens as
    the gap grows relative to magnet thickness. Good enough to show the dominant
    lever (keep the gap SMALL — a thick bulkhead kills a coupling), not exact.
    """
    if thickness_m <= 0:
        raise ValueError("thickness must be > 0")
    return b_r * thickness_m / (thickness_m + gap_m)


def shear_stress(b_gap: float, tangential_factor: float = 0.12) -> float:
    """Magnetic shear (torque-producing) stress at the coupling face [Pa].

    `tangential_factor` (~0.08–0.2) is the fraction of the normal magnetic
    pressure that shows up as usable tangential stress for a simple block/disc
    magnet array; 0.12 lands τ in the empirical 10–40 kPa band.
    """
    return tangential_factor * magnetic_pressure(b_gap)


def coupling_max_torque(active_area_m2: float, mean_radius_m: float, b_gap: float,
                        tangential_factor: float = 0.12) -> float:
    """Peak transmissible torque of an axial magnetic coupling [N·m]."""
    return shear_stress(b_gap, tangential_factor) * active_area_m2 * mean_radius_m


@dataclass
class AxialMagCoupling:
    """Two coaxial magnet discs across a flat bulkhead. All lengths in mm."""

    n_magnets: int = 12          # per disc (alternating polarity around the ring)
    magnet_dia: float = 15.0     # mm, cylindrical magnet diameter
    magnet_thickness: float = 6.0  # mm
    mean_radius: float = 55.0    # mm, ring radius the magnets sit on
    gap: float = 3.0             # mm, TOTAL wet-face to dry-face (bulkhead + clearances)
    grade: str = "N42"
    tangential_factor: float = 0.12

    @property
    def b_r(self) -> float:
        return MAGNET_GRADES[self.grade]

    @property
    def b_gap(self) -> float:
        return gap_field(self.b_r, self.magnet_thickness * 1e-3, self.gap * 1e-3)

    @property
    def active_area(self) -> float:
        """Total magnet face area on one disc (m²)."""
        a_one = math.pi / 4.0 * (self.magnet_dia * 1e-3) ** 2
        return self.n_magnets * a_one

    @property
    def shear_stress_pa(self) -> float:
        return shear_stress(self.b_gap, self.tangential_factor)

    def max_torque(self) -> float:
        """Peak transmissible torque before the magnets slip (N·m)."""
        return coupling_max_torque(self.active_area, self.mean_radius * 1e-3,
                                   self.b_gap, self.tangential_factor)

    def axial_force_n(self, attraction_factor: float = 0.6) -> float:
        """Static axial ATTRACTION between the two discs (newtons).

        The same magnets that make torque also pull the discs together with
        F ≈ k · (B_gap²/2μ₀) · A_active — for the default coupling that's a very
        real ~350-400 N (~35-40 kg!). This force is constant, rides on the SHAFT
        BEARINGS of both discs (the non-magnetic bulkhead itself feels none of
        it), and will grind plain radial bearings flat. Fit THRUST bearings (or
        angular-contact bearings) on both shafts, rated above this with margin.
        `attraction_factor` (~0.5-0.7) accounts for pole alternation and leakage.
        """
        return attraction_factor * magnetic_pressure(self.b_gap) * self.active_area

    def holds(self, required_torque_nm: float, safety: float = 2.0) -> bool:
        """True if the coupling carries `required_torque` with the safety margin."""
        return self.max_torque() >= required_torque_nm * safety


def magnets_needed(required_torque_nm: float, magnet_dia_mm: float,
                   mean_radius_mm: float, gap_mm: float = 3.0,
                   magnet_thickness_mm: float = 6.0, grade: str = "N42",
                   safety: float = 2.0, tangential_factor: float = 0.12) -> int:
    """Smallest magnet count (per disc) to carry a torque with a safety margin.

    Slipping is a *feature* (overload protection), but you still want the coupling
    to hold the rotor's normal operating torque comfortably — hence the margin.
    """
    b_gap = gap_field(MAGNET_GRADES[grade], magnet_thickness_mm * 1e-3, gap_mm * 1e-3)
    tau = shear_stress(b_gap, tangential_factor)
    a_one = math.pi / 4.0 * (magnet_dia_mm * 1e-3) ** 2
    per_magnet_torque = tau * a_one * (mean_radius_mm * 1e-3)
    if per_magnet_torque <= 0:
        return math.inf
    return max(2, math.ceil(required_torque_nm * safety / per_magnet_torque))
