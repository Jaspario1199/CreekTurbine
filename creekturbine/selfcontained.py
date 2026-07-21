"""
Self-contained all-in-one unit — "a box with a handle you set in the creek."

This is the plug-and-play form: ONE carriable housing, no cable to a shore box.
It works because the rotor is VERTICAL-AXIS, so the unit is a vertical stack:

        ┌─ handle ─┐
        │ outlets  │   ← DRY: battery + charge controller + USB/12V + display
        │ battery  │      (stays above the waterline — the "freeboard")
   ~~~~~├──────────┤~~~~~ waterline
        │ generator│   ← DRY, sealed (magnetic-coupled to the rotor below)
        │  ┌────┐  │
        │  │rotor│ │   ← WET: Savonius in the flow (self-starts, any direction)
        └──┴────┴──┘
         weighted base

You set it in the stream, the rotor charges the internal battery, and the outlets
on top are live — no wiring on site. The physics is unchanged (small rotor → a few
watts, buffered by the battery), so the two things that actually decide whether a
free-standing box works are modeled here:

1. **Does the rotor fit the box, and does the top stay dry?** (geometry/freeboard)
2. **Will the current push it over or wash it downstream?** A bluff body in
   flowing water feels a drag force ½·ρ·Cd·A·v²; a tall box on a creek bed must
   out-weigh that in both SLIDING and TIPPING. This sizes the base ballast — the
   real reason a "just drop it in" unit needs a heavy/anchored base.

See docs/SELF_CONTAINED.md.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import hydrokinetics as hk

G = 9.81


def drag_force_n(frontal_area: float, velocity: float, cd: float = 1.0,
                 rho: float = hk.RHO_WATER) -> float:
    """Hydrodynamic drag on the submerged body: F = ½·ρ·Cd·A·v² (newtons).

    This is the downstream push the current exerts. Cd ≈ 1.0–1.3 for a bluff
    body / Savonius. It grows with v², so a brisk creek needs a much heavier or
    staked base than a lazy one.
    """
    if frontal_area < 0 or velocity < 0:
        raise ValueError("area and velocity must be >= 0")
    return 0.5 * rho * cd * frontal_area * velocity ** 2


def hold_mass_for_sliding_kg(drag_n: float, friction: float = 0.5,
                             safety: float = 2.0, g: float = G) -> float:
    """Net weight (kg) needed so bed friction resists the drag without sliding.

    Requires μ·W ≥ safety·drag. `friction` μ ≈ 0.4–0.6 on a rocky/gravel bed.
    'Net' = dry weight minus buoyancy (an air-filled dry compartment lightens it).
    """
    if friction <= 0:
        raise ValueError("friction must be > 0")
    return safety * drag_n / (friction * g)


def hold_mass_for_tipping_kg(drag_n: float, drag_height_m: float,
                             base_halfwidth_m: float, safety: float = 2.0,
                             g: float = G) -> float:
    """Weight (kg) needed so the unit doesn't tip about its downstream base edge.

    Overturning moment = drag·(height of the drag centroid above the base);
    restoring moment = weight·(base half-width). Requires
    weight·halfwidth ≥ safety·drag·drag_height.
    """
    if base_halfwidth_m <= 0:
        raise ValueError("base_halfwidth must be > 0")
    return safety * drag_n * drag_height_m / (base_halfwidth_m * g)


@dataclass
class SelfContainedUnit:
    """A single carriable box that stands in the creek. All-in-one, plug-and-play."""

    box_diameter: float = 0.30    # m, outer footprint you carry
    box_height: float = 0.65      # m, total height
    submerged_depth: float = 0.30  # m, how deep the lower (wet) box sits
    velocity: float = 0.8         # m/s creek speed
    battery_wh: float = 300.0     # onboard buffer
    unit_dry_mass_kg: float = 8.0  # mass of the unit itself (before base ballast)
    cp: float = 0.18
    eta_generator: float = 0.65
    eta_drivetrain: float = 0.90
    cd_drag: float = 1.1
    bed_friction: float = 0.5
    rho: float = hk.RHO_WATER
    wall_clearance: float = 0.02  # m, rotor-to-wall gap

    # --- geometry -------------------------------------------------------
    @property
    def rotor_diameter(self) -> float:
        return max(0.0, self.box_diameter - 2 * self.wall_clearance)

    @property
    def rotor_height(self) -> float:
        # rotor occupies the submerged depth minus a little for the base/bearing
        return max(0.0, self.submerged_depth - 0.05)

    @property
    def frontal_area(self) -> float:
        return self.rotor_diameter * self.rotor_height

    @property
    def freeboard(self) -> float:
        """Dry height of the box standing above the water (must be > 0)."""
        return self.box_height - self.submerged_depth

    @property
    def submerged_body_area(self) -> float:
        """Frontal area of the whole submerged box (for the drag calc)."""
        return self.box_diameter * self.submerged_depth

    # --- performance & stability ---------------------------------------
    def power_w(self) -> float:
        return hk.extractable_power(self.frontal_area, self.velocity, self.cp,
                                    self.eta_generator, self.eta_drivetrain, self.rho)

    def drag_n(self) -> float:
        return drag_force_n(self.submerged_body_area, self.velocity, self.cd_drag,
                            self.rho)

    def required_base_ballast_kg(self, safety: float = 2.0) -> float:
        """Extra ballast (kg) the base needs beyond the unit's own weight.

        Takes the worse of the sliding and tipping requirements and subtracts the
        unit's own dry mass. Returns 0 if the unit is already heavy enough.
        """
        drag = self.drag_n()
        sliding = hold_mass_for_sliding_kg(drag, self.bed_friction, safety)
        tipping = hold_mass_for_tipping_kg(drag, self.submerged_depth / 2.0,
                                           self.box_diameter / 2.0, safety)
        needed = max(sliding, tipping)
        return max(0.0, needed - self.unit_dry_mass_kg)

    def report(self) -> dict:
        return {
            "rotor_diameter": self.rotor_diameter,
            "rotor_height": self.rotor_height,
            "frontal_area": self.frontal_area,
            "power_w": self.power_w(),
            "daily_wh": self.power_w() * 24.0,
            "freeboard": self.freeboard,
            "min_water_depth": self.submerged_depth,
            "drag_n": self.drag_n(),
            "required_base_ballast_kg": self.required_base_ballast_kg(),
        }
