"""
Central configuration for your CreekTurbine build.

Everything here uses SI units:
    - distances / lengths in METERS
    - velocities in METERS PER SECOND (m/s)
    - power in WATTS, energy in WATT-HOURS (Wh)
    - mass in KILOGRAMS, angles in RADIANS

============================================================================
  >>> YOU ONLY NEED TO EDIT THE THREE BLOCKS MARKED "EDIT ME" BELOW <<<
      (1) your creek's measured flow, (2) what you want to power,
      (3) your battery.  Everything else is computed for you.

  Don't have the numbers yet?  That's the whole point of
  `python -m scripts.measure_creek` — it walks you through measuring
  velocity and depth with a tape measure, a stick, and a stopwatch.
============================================================================

WHY VELOCITY IS EVERYTHING (read this once):
    Hydrokinetic power scales with the CUBE of water speed (v^3).  Double the
    speed -> 8x the power.  A sleepy 0.4 m/s creek and a brisk 0.8 m/s creek
    look similar to your eye but differ by 8x in harvestable power.  So the
    single most valuable thing you can do is measure your creek honestly and,
    if you can, speed the water up where the turbine sits (a narrowed chute or
    a shroud).  See docs/SITING.md.
"""

from dataclasses import dataclass, field


# ===========================================================================
#  EDIT ME (1/3) --- YOUR CREEK.  Measure it; don't guess. See scripts/measure_creek.py
# ===========================================================================
# Mean water speed at the spot the turbine will sit, in m/s.  Use the float
# method (time a floating stick over a measured distance) x 0.85 for the depth-
# averaged mean, OR a cheap flow meter.  Typical creeks:
#     ~0.2-0.4 m/s  lazy / low season   (marginal — expect a trickle)
#     ~0.5-0.8 m/s  healthy steady flow (a good trickle-charger)
#     ~1.0-1.5 m/s  brisk / after rain  (genuinely useful power)
CREEK_VELOCITY = 0.8          # m/s  <-- MEASURE THIS

# The wetted channel cross-section where the turbine sits.  Used to check the
# turbine isn't too big for the creek (blockage) and to estimate flow-speed-up.
CREEK_WIDTH = 1.5             # m, water surface width at the turbine spot
CREEK_DEPTH = 0.5            # m, average water depth at that spot (NOT the deepest)

# Water: fresh creek water. (Salt/brackish is ~1025; leave 1000 for a creek.)
WATER_DENSITY = 1000.0       # kg/m^3

# Seasonality: fraction of the year the creek runs at (roughly) CREEK_VELOCITY.
# Droughts and freezes count against you.  0.75 = flows usefully ~9 months/yr.
FLOW_AVAILABILITY = 0.75     # 0..1, used only for annual-energy estimates


# ===========================================================================
#  EDIT ME (2/3) --- WHAT YOU WANT TO POWER (your goal, be realistic)
# ===========================================================================
# A creek turbine is a TRICKLE CHARGER, not a generator set.  Aim to keep a
# battery topped up and run small always-on loads.  Set a target of CONTINUOUS
# electrical watts you'd like at the battery; the model will tell you what
# rotor size that needs at your measured velocity, and whether it's sane.
TARGET_POWER_W = 5.0         # W continuous, delivered to the battery (a realistic creek goal)


# ===========================================================================
#  EDIT ME (3/3) --- YOUR BATTERY / SYSTEM
# ===========================================================================
SYSTEM_VOLTAGE = 12.0        # V nominal battery bus (12 is easiest for USB/car gear)
BATTERY_CHEMISTRY = "LiFePO4"  # "LiFePO4" (recommended) or "lead-acid"
DAYS_AUTONOMY = 2.0          # days the battery should carry loads with zero flow
# Usable depth-of-discharge before you're stressing the battery.
DEPTH_OF_DISCHARGE = 0.8 if BATTERY_CHEMISTRY == "LiFePO4" else 0.5


# ---------------------------------------------------------------------------
# TURBINE CHOICE + realistic efficiencies (defaults are conservative on purpose)
# ---------------------------------------------------------------------------
# "savonius" = vertical-axis drag rotor.  RECOMMENDED for a DIY creek: self-
#     starts in slow water, doesn't care which way the flow points, tolerates
#     debris, spins slowly with lots of torque, and — crucially — its shaft is
#     vertical so the GENERATOR sits on top ABOVE the waterline. Lower Cp.
# "axial" = horizontal-axis propeller ("underwater wind turbine"). Higher Cp,
#     but needs faster flow to start, must face the current, and the generator
#     is harder to keep dry. Pick this only for a brisk, deeper creek.
TURBINE_TYPE = "savonius"    # "savonius" | "axial"

# Savonius blade profile — see docs/RESEARCH_ROTORS.md + rotor.SAVONIUS_PROFILES.
#   "custom"       use the explicit CP_SAVONIUS below (conservative default)
#   "conventional" ~0.16   classic semicircular scoop
#   "optimized"    ~0.19   arc ~166°, aspect 1.5-2, overlap 0.15-0.2, end plates
#   "hydrofoil"    ~0.24   cambered-hydrofoil blade (best low-speed Cp, harder build)
# A named profile OVERRIDES CP_SAVONIUS. Lab Cp exceeds real DIY, so stay humble.
SAVONIUS_PROFILE = "custom"

# Power coefficient Cp = fraction of the water's kinetic power the ROTOR
# captures. Hard ceiling is the Betz limit 16/27 = 0.593. Real DIY numbers:
CP_SAVONIUS = 0.18           # conservative DIY Savonius (used when profile = "custom")
CP_AXIAL = 0.35              # conservative small hydrokinetic prop (good ones ~0.40-0.45)

# Everything downstream of the rotor that eats power before the battery:
GENERATOR_EFFICIENCY = 0.65  # small PMA at low rpm + 3-phase rectifier losses
DRIVETRAIN_EFFICIENCY = 0.90  # bearings, shaft seal drag, coupling/belt

# What the charge controller itself eats, 24/7, even with zero flow. A typical
# small MPPT idles at 15-30 mA on a 12 V bus (~0.2-0.4 W) — at trickle-charger
# power levels that is a real tax, so it's counted in the energy budget. Shop
# for low-quiescent controllers (<10 mA) at the small end.
CONTROLLER_IDLE_W = 0.25     # W, controller quiescent draw

# Flow speed-up you actually achieve at the rotor. 1.0 = none (bare rotor in
# open water). A narrowed chute or a shroud/diffuser can raise the effective
# velocity; because power ~ v^3 even a modest 1.2x is a ~1.7x power gain.
# Keep at 1.0 until you've actually built the channel — see docs/SITING.md.
VELOCITY_AUGMENTATION = 1.0  # dimensionless multiplier on CREEK_VELOCITY

GRAVITY = 9.81               # m/s^2


@dataclass
class CreekConfig:
    """Bundles the site + goal so we can pass one object around."""

    velocity: float = CREEK_VELOCITY
    width: float = CREEK_WIDTH
    depth: float = CREEK_DEPTH
    water_density: float = WATER_DENSITY
    flow_availability: float = FLOW_AVAILABILITY

    target_power_w: float = TARGET_POWER_W

    system_voltage: float = SYSTEM_VOLTAGE
    battery_chemistry: str = BATTERY_CHEMISTRY
    days_autonomy: float = DAYS_AUTONOMY
    depth_of_discharge: float = DEPTH_OF_DISCHARGE

    turbine_type: str = TURBINE_TYPE
    savonius_profile: str = SAVONIUS_PROFILE
    cp_savonius: float = CP_SAVONIUS
    cp_axial: float = CP_AXIAL
    generator_efficiency: float = GENERATOR_EFFICIENCY
    drivetrain_efficiency: float = DRIVETRAIN_EFFICIENCY
    velocity_augmentation: float = VELOCITY_AUGMENTATION
    controller_idle_w: float = CONTROLLER_IDLE_W

    @property
    def channel_area(self) -> float:
        """Wetted cross-section of the creek at the turbine (m^2)."""
        return self.width * self.depth

    @property
    def effective_velocity(self) -> float:
        """Velocity actually seen by the rotor after any chute/shroud speed-up."""
        return self.velocity * self.velocity_augmentation

    @property
    def cp(self) -> float:
        """Rotor power coefficient for the selected turbine type (+ Savonius profile)."""
        if self.turbine_type == "savonius":
            from .rotor import SAVONIUS_PROFILES  # lazy: avoid import cycle
            if self.savonius_profile in SAVONIUS_PROFILES:
                return SAVONIUS_PROFILES[self.savonius_profile]
            return self.cp_savonius
        return self.cp_axial

    @property
    def system_efficiency(self) -> float:
        """Cp x generator x drivetrain: water kinetic power -> battery watts."""
        return self.cp * self.generator_efficiency * self.drivetrain_efficiency


DEFAULT_CONFIG = CreekConfig()
