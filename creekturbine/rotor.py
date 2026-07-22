"""
Rotor models: Savonius (recommended) and Axial (for brisk creeks).

Each rotor knows three things:
  * its FRONTAL AREA (what the water "sees" — this drives available power),
  * its design power coefficient Cp and design tip-speed ratio (TSR),
  * how to turn a water velocity into a shaft rpm and torque.

That is exactly the interface the generator model needs, so the two rotor types
are interchangeable everywhere downstream (same trick RoomCleaner used for its
detectors: one interface, swappable implementations).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import hydrokinetics as hk


# Research-backed Savonius blade profiles and their peak Cp at low creek speed.
# Sources & full discussion in docs/RESEARCH_ROTORS.md (all adversarially verified):
#   conventional  semicircular scoop, Cp ~0.166 @ TSR 0.78            [2]
#   optimized     arc ~166°, aspect 1.4-2.0, overlap 0.15-0.2,        [5]
#                 end plates -> Cp ~0.194 @ TSR 0.8
#   hydrofoil     cambered-hydrofoil blade -> Cp ~0.21-0.26 @ 0.4 m/s [3]
# Defaults stay conservative; opt into a better profile for the researched gain.
SAVONIUS_PROFILES = {
    "conventional": 0.16,
    "optimized": 0.19,
    "hydrofoil": 0.24,
}


@dataclass
class RotorPerformance:
    """What a rotor does at one water velocity — the full picture in one object."""

    velocity: float          # m/s seen by the rotor
    frontal_area: float      # m^2
    cp: float                # power coefficient used
    available_w: float       # kinetic power in the intercepted stream
    mechanical_w: float      # power on the shaft (available * cp)
    rpm: float               # shaft speed at design TSR
    torque_nm: float         # shaft torque delivering mechanical_w at that rpm


class _RotorBase:
    #: design tip-speed ratio where Cp peaks (set by subclass)
    optimal_tsr: float = 1.0
    #: default power coefficient (set by subclass / overridden per instance)
    cp: float = 0.2

    @property
    def frontal_area(self) -> float:  # pragma: no cover - overridden
        raise NotImplementedError

    @property
    def radius(self) -> float:  # pragma: no cover - overridden
        raise NotImplementedError

    def performance(
        self,
        velocity: float,
        eta_generator: float = 1.0,
        eta_drivetrain: float = 1.0,
        rho: float = hk.RHO_WATER,
    ) -> RotorPerformance:
        """Full mechanical picture at `velocity` (electrical is a separate step)."""
        area = self.frontal_area
        available = hk.available_power(area, velocity, rho)
        mechanical = available * min(self.cp, hk.BETZ_LIMIT)
        rpm = hk.rpm_at_velocity(self.optimal_tsr, velocity, self.radius)
        omega = hk.omega_from_rpm(rpm)
        torque = hk.torque_from_power(mechanical, omega) if omega > 0 else 0.0
        return RotorPerformance(
            velocity=velocity,
            frontal_area=area,
            cp=min(self.cp, hk.BETZ_LIMIT),
            available_w=available,
            mechanical_w=mechanical,
            rpm=rpm,
            torque_nm=torque,
        )

    def electrical_power(
        self,
        velocity: float,
        eta_generator: float,
        eta_drivetrain: float,
        rho: float = hk.RHO_WATER,
    ) -> float:
        """Battery-side watts at `velocity` for this rotor."""
        return hk.extractable_power(
            self.frontal_area, velocity, self.cp, eta_generator, eta_drivetrain, rho
        )


@dataclass
class SavoniusRotor(_RotorBase):
    """Vertical-axis drag rotor (two/three scoops). The DIY creek workhorse.

    Frontal area is simply diameter x height (the projected rectangle the water
    pushes on). Its shaft is vertical, so the generator lives on top, above the
    waterline — the single biggest reason to pick it for a creek.

    Geometry note: for a classic two-bucket rotor built from buckets of
    diameter `bucket_dia` with an overlap `overlap`, the rotor diameter is
    `2*bucket_dia - overlap`. You can either pass the rotor `diameter` directly
    or build one from buckets with `from_buckets(...)`.
    """

    diameter: float = 0.5     # m, rotor diameter (tip to tip across the scoops)
    height: float = 0.6       # m, rotor height (submerged depth of the scoops)
    cp: float = 0.18          # conservative DIY value
    optimal_tsr: float = 0.9  # drag rotors peak just below TSR = 1
    profile: str = "custom"   # which SAVONIUS_PROFILES entry set the cp (or "custom")
    helical: bool = False     # twisted blades: better self-start/torque/debris shedding

    @classmethod
    def from_buckets(cls, bucket_dia: float, height: float, overlap_ratio: float = 0.15,
                     **kw) -> "SavoniusRotor":
        overlap = overlap_ratio * bucket_dia
        diameter = 2.0 * bucket_dia - overlap
        return cls(diameter=diameter, height=height, **kw)

    @classmethod
    def from_profile(cls, diameter: float, height: float, profile: str = "optimized",
                     helical: bool = True, **kw) -> "SavoniusRotor":
        """Build a rotor with a research-backed Cp for a named blade profile.

        See SAVONIUS_PROFILES / docs/RESEARCH_ROTORS.md. `helical` is metadata (it
        aids self-start, torque smoothness, and debris shedding without a reliable
        Cp change), used by the CAD to twist the blades.
        """
        if profile not in SAVONIUS_PROFILES:
            raise ValueError(f"unknown profile {profile!r}; "
                             f"choose from {sorted(SAVONIUS_PROFILES)}")
        return cls(diameter=diameter, height=height, cp=SAVONIUS_PROFILES[profile],
                   profile=profile, helical=helical, **kw)

    @property
    def frontal_area(self) -> float:
        return self.diameter * self.height

    @property
    def radius(self) -> float:
        return self.diameter / 2.0

    @property
    def aspect_ratio(self) -> float:
        """Height / diameter. ~1.5-2.0 gives good stability and Cp for Savonius."""
        return self.height / self.diameter


@dataclass
class AxialRotor(_RotorBase):
    """Horizontal-axis propeller — an 'underwater wind turbine'.

    Higher Cp, but needs faster water to self-start, must be yawed into the
    current, and its horizontal shaft makes keeping the generator dry harder.
    Frontal area is the swept circle, pi/4 * D^2.
    """

    diameter: float = 0.4     # m, propeller (swept-circle) diameter
    cp: float = 0.35          # conservative small-prop value
    optimal_tsr: float = 5.0  # lift rotors run fast

    @property
    def frontal_area(self) -> float:
        return math.pi / 4.0 * self.diameter ** 2

    @property
    def radius(self) -> float:
        return self.diameter / 2.0


# ---------------------------------------------------------------------------
# Sizing helpers — turn a power goal + velocity into rotor dimensions
# ---------------------------------------------------------------------------
def size_savonius_for_power(
    target_power_w: float,
    velocity: float,
    aspect_ratio: float = 1.6,
    cp: float = 0.18,
    eta_generator: float = 0.65,
    eta_drivetrain: float = 0.90,
    rho: float = hk.RHO_WATER,
) -> SavoniusRotor:
    """Smallest Savonius (at the given aspect ratio) that meets a power target.

    Solves swept_area_for_power for area = D*H with H = aspect_ratio*D, so
    D = sqrt(area / aspect_ratio). Returns math.inf dimensions if the velocity
    is too low to ever reach the target — which is the honest answer for a very
    slow creek and a greedy target.
    """
    area = hk.swept_area_for_power(target_power_w, velocity, cp, eta_generator,
                                   eta_drivetrain, rho)
    if not math.isfinite(area):
        return SavoniusRotor(diameter=math.inf, height=math.inf, cp=cp)
    diameter = math.sqrt(area / aspect_ratio)
    return SavoniusRotor(diameter=diameter, height=aspect_ratio * diameter, cp=cp)


def size_axial_for_power(
    target_power_w: float,
    velocity: float,
    cp: float = 0.35,
    eta_generator: float = 0.65,
    eta_drivetrain: float = 0.90,
    rho: float = hk.RHO_WATER,
) -> AxialRotor:
    """Smallest axial propeller diameter that meets a power target."""
    area = hk.swept_area_for_power(target_power_w, velocity, cp, eta_generator,
                                   eta_drivetrain, rho)
    if not math.isfinite(area):
        return AxialRotor(diameter=math.inf, cp=cp)
    diameter = math.sqrt(4.0 * area / math.pi)
    return AxialRotor(diameter=diameter, cp=cp)


def make_rotor_from_config(cfg) -> _RotorBase:
    """Build the rotor the config asks for, sized to hit its target power.

    Uses the config's effective (augmented) velocity so a chute/shroud in the
    config actually shrinks the rotor the model recommends.
    """
    v = cfg.effective_velocity
    if cfg.turbine_type == "axial":
        return size_axial_for_power(cfg.target_power_w, v, cfg.cp_axial,
                                    cfg.generator_efficiency, cfg.drivetrain_efficiency,
                                    cfg.water_density)
    # cfg.cp already reflects the selected Savonius profile (or the custom Cp).
    rot = size_savonius_for_power(cfg.target_power_w, v, 1.6, cfg.cp,
                                  cfg.generator_efficiency, cfg.drivetrain_efficiency,
                                  cfg.water_density)
    profile = getattr(cfg, "savonius_profile", "custom")
    rot.profile = profile
    rot.helical = profile in SAVONIUS_PROFILES  # named profiles ship helical CAD
    return rot
