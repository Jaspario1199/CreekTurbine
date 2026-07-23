"""
Funnel / converging intake — make a mellow, shallow creek hit useful speed.

The idea: wall the creek into a **converging chute** so the flow squeezes through a
narrow throat at the rotor. By continuity (A₁v₁ = A₂v₂) the water speeds up, and
because power ∝ v³ that's a big win. Crucially, this reframes what you harvest:
instead of a small rotor sipping from a slow, shallow flow, the funnel routes the
creek's whole **flow rate Q** through the rotor at elevated speed —

    P_available = ½·ρ·A_throat·v_throat³ = ½·ρ·Q·v_throat²

so even a lazy creek with a decent Q becomes useful once v is raised.

THE HONEST CEILING (why this isn't free): an *open-channel* constriction can only
accelerate flow up to the **critical velocity** v_c = √(g·y) at the throat depth y.
Push harder (a narrower throat) and the flow "chokes" — it just backs water up
upstream instead of going faster. At 6 in (0.15 m) that ceiling is √(9.81·0.15) ≈
**1.2 m/s** — which, happily, is right where a 6-inch rotor starts charging a
laptop. To beat the critical cap you need a *closed, pressurized* duct with real
head (that's the [box-with-head design](../docs/BOX_AND_DUCT.md)), not an open funnel.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .hydrokinetics import RHO_WATER, extractable_power

G = 9.81


def critical_velocity(depth: float) -> float:
    """Open-channel critical velocity √(g·y) — the speed a funnel maxes out at."""
    if depth <= 0:
        raise ValueError("depth must be > 0")
    return math.sqrt(G * depth)


def froude_number(velocity: float, depth: float) -> float:
    """Fr = v/√(g·y). <1 subcritical (calm), =1 critical (choked), >1 supercritical."""
    return velocity / math.sqrt(G * depth)


def flow_rate(width: float, depth: float, velocity: float) -> float:
    """Volumetric flow Q = w·y·v (m³/s) — the creek's discharge."""
    return width * depth * velocity


@dataclass
class FunnelIntake:
    """A converging chute from the approach channel down to a throat at the rotor."""

    up_width: float          # m, approach channel width
    up_depth: float          # m, approach depth
    up_velocity: float       # m/s, approach (mellow) velocity
    throat_width: float      # m, narrowed width at the rotor
    throat_depth: float      # m, water depth at the throat (>= rotor submersion)
    cp: float = 0.19
    eta_generator: float = 0.65
    eta_drivetrain: float = 0.90
    # How much of the ideal (continuity/critical) speed-up is actually realized.
    # A bank-to-bank WEIR ponds the flow and approaches 1.0; a FREE-STANDING unit
    # in an open creek lets water bypass/spill around it, so it realizes less
    # (~0.7-0.85). This is the honest cost of "works in any creek" portability.
    confinement: float = 1.0
    rho: float = RHO_WATER

    @classmethod
    def universal(cls, creek_depth: float, up_velocity: float,
                  gather_width: float = 0.9, throat_width: float = 0.4,
                  throat_depth: float = 0.15, confinement: float = 0.82,
                  intake_height: float = 0.35, **kw):
        """A free-standing unit with a FIXED gather width, for any creek that's
        wider (and at least as deep) than it.

        Two honesty caps: the throat can't be deeper than the water (shallow
        creeks get a short rotor), and the unit can't gather water deeper than
        its own intake mouth (`intake_height`) — in a 3 ft creek a 0.35 m-tall
        mouth only captures the top/bottom 0.35 m; the rest flows past.

        NOTE `confinement` is an engineering ASSUMPTION, not a measured value —
        free-standing intakes shed flow around themselves and the literature has
        no clean number for this geometry. Field-calibrate it (measure the
        throat velocity with a float) before trusting absolute watts."""
        return cls(up_width=gather_width,
                   up_depth=min(creek_depth, intake_height),
                   up_velocity=up_velocity, throat_width=throat_width,
                   throat_depth=min(throat_depth, creek_depth),
                   confinement=confinement, **kw)

    @property
    def creek_flow(self) -> float:
        """The creek's total discharge Q (m³/s) — the resource you can tap."""
        return flow_rate(self.up_width, self.up_depth, self.up_velocity)

    @property
    def throat_area(self) -> float:
        return self.throat_width * self.throat_depth

    @property
    def critical_velocity(self) -> float:
        return critical_velocity(self.throat_depth)

    @property
    def ideal_throat_velocity(self) -> float:
        """Speed if the whole creek were forced through the throat (uncapped)."""
        return self.creek_flow / self.throat_area

    @property
    def choked(self) -> bool:
        """True if the throat hits the critical cap (excess flow backs up/bypasses)."""
        return self.ideal_throat_velocity > self.critical_velocity

    @property
    def capped_velocity(self) -> float:
        """Ideal throat speed after the critical-velocity cap (before confinement)."""
        return min(self.ideal_throat_velocity, self.critical_velocity)

    @property
    def throat_velocity(self) -> float:
        """Realized throat speed: the ideal speed-up scaled by confinement.

        confinement=1.0 (walled weir) gives the full continuity/critical value;
        a free-standing unit realizes only part of it as flow bypasses around it.
        """
        return self.up_velocity + self.confinement * (self.capped_velocity - self.up_velocity)

    @property
    def throat_froude(self) -> float:
        return froude_number(self.throat_velocity, self.throat_depth)

    @property
    def augmentation(self) -> float:
        """Velocity multiplier vs the ambient creek (feeds VELOCITY_AUGMENTATION)."""
        return self.throat_velocity / self.up_velocity

    @property
    def throughput(self) -> float:
        """Flow actually passing the throat (m³/s); < creek_flow when choked."""
        return self.throat_area * self.throat_velocity

    def available_power(self) -> float:
        """Kinetic power in the throat flow, ½·ρ·A·v³ (W)."""
        return 0.5 * self.rho * self.throat_area * self.throat_velocity ** 3

    def electrical_power(self) -> float:
        """Battery-side watts from a rotor filling the throat."""
        return extractable_power(self.throat_area, self.throat_velocity, self.cp,
                                 self.eta_generator, self.eta_drivetrain, self.rho)

    def bare_rotor_power(self) -> float:
        """For comparison: the same throat-area rotor in the un-funnelled creek."""
        return extractable_power(self.throat_area, self.up_velocity, self.cp,
                                 self.eta_generator, self.eta_drivetrain, self.rho)

    def power_gain(self) -> float:
        """How many times more power the funnel delivers vs a bare rotor."""
        bare = self.bare_rotor_power()
        return self.electrical_power() / bare if bare > 0 else math.inf


def throat_width_for_velocity(creek_flow: float, target_velocity: float,
                              throat_depth: float) -> float:
    """Throat width to reach a target throat velocity (won't exceed critical).

    If `target_velocity` is above the critical cap for `throat_depth`, the flow
    chokes there instead — you can't out-narrow physics in an open channel.
    """
    v = min(target_velocity, critical_velocity(throat_depth))
    if v <= 0:
        return math.inf
    return creek_flow / (v * throat_depth)
