"""
Ducted / low-head / submerged-box model — the "enclosed air box" idea, costed.

This module answers a specific design question: *can I put an enclosed, mostly
air-filled box in the creek, keep the generator dry inside it, and route water
through a channel past a turbine?* The answer is yes — it's a **ducted turbine
with a dry nacelle** — and this module makes the trade-offs quantitative.

Three honest ideas it captures:

1. **Velocity head is tiny.** A creek's *kinetic* energy is worth almost no
   "head": v²/2g. At 0.8 m/s that's ~3 cm of water. That is why a pure box
   around a kinetic rotor gains little on its own...

2. **...but adding real HEAD is transformative.** If you place the box's inlet a
   little higher/upstream and the outlet lower, you create a static head H across
   it and become a *low-head* turbine: P = ρ·g·Q·H·η. Even 0.3-0.5 m of drop
   beats pure kinetic for the same creek, often several-fold.

3. **A submerged air box is very buoyant** and must be ballasted/anchored, and
   the wet turbine must drive the dry generator through the wall — best done with
   a **magnetic coupling** (no shaft penetration, nothing to seal).

Everything is pure functions + one dataclass, SI units, tested against
hand-computable values (see tests/test_ducted.py).
"""

from __future__ import annotations

from dataclasses import dataclass

from .hydrokinetics import RHO_WATER

G = 9.81  # m/s^2


# ---------------------------------------------------------------------------
# Head / flow / power
# ---------------------------------------------------------------------------
def velocity_head(velocity: float, g: float = G) -> float:
    """Equivalent head (m) of a moving stream: v²/(2g).

    The eye-opener: at 0.8 m/s this is only ~0.033 m (3.3 cm). A creek's speed
    is worth almost nothing as head — which is exactly why enclosing a kinetic
    rotor in a box gains little *unless* you also add a real elevation drop.
    """
    if velocity < 0:
        raise ValueError("velocity must be >= 0")
    return velocity ** 2 / (2.0 * g)


def low_head_power(flow_q: float, head_h: float, efficiency: float = 1.0,
                   rho: float = RHO_WATER, g: float = G) -> float:
    """Hydraulic power (W) of a low-head turbine: P = ρ·g·Q·H·η.

    `flow_q` is volumetric flow through the turbine (m³/s), `head_h` is the head
    across it (m). This is the bedrock micro-hydro equation, and the reason even
    a small deliberate drop across the box is worth chasing.
    """
    if flow_q < 0 or head_h < 0:
        raise ValueError("flow and head must be >= 0")
    return rho * g * flow_q * head_h * efficiency


def throat_velocity(driving_head: float, cd: float = 0.85, g: float = G) -> float:
    """Water speed through the box throat, driven by `driving_head` (Torricelli).

    v = Cd·√(2·g·H). The discharge coefficient Cd (~0.6-0.9) lumps entry, exit,
    and duct friction losses. This is what couples head to flow: raise the head
    and the throat runs faster; a lossy duct (low Cd) bleeds it back.
    """
    if driving_head < 0:
        raise ValueError("driving_head must be >= 0")
    return cd * (2.0 * g * driving_head) ** 0.5


# ---------------------------------------------------------------------------
# The submerged / ducted box
# ---------------------------------------------------------------------------
@dataclass
class DuctedBox:
    """An enclosed box that routes creek water through a throat past a turbine.

    throat_area:        m², the wetted opening the flow passes through
    static_head:        m, elevation drop you build between inlet and outlet
                        (0 = purely kinetic; even 0.2-0.5 m changes everything)
    diffuser_gain:      effective-head multiplier from a flared outlet/diffuser
                        that recovers exit velocity as suction (1.0 = none, a
                        good diffuser ~1.3-1.8; treat as optimistic-approximate)
    cd:                 discharge coefficient (losses) for the throat flow
    efficiency:         overall water→electrical efficiency for a low-head DIY
                        turbine (~0.30-0.50)
    """

    throat_area: float = 0.05
    static_head: float = 0.30
    diffuser_gain: float = 1.0
    cd: float = 0.85
    efficiency: float = 0.40

    def driving_head(self, approach_velocity: float, g: float = G) -> float:
        """Total head pushing water through the box, including the creek's own
        velocity head at the inlet, boosted by any diffuser."""
        return (self.static_head + velocity_head(approach_velocity, g)) * self.diffuser_gain

    def flow(self, approach_velocity: float, g: float = G) -> float:
        """Volumetric flow through the throat (m³/s)."""
        v = throat_velocity(self.driving_head(approach_velocity, g), self.cd, g)
        return self.throat_area * v

    def report(self, approach_velocity: float, rho: float = RHO_WATER, g: float = G) -> dict:
        """Everything you need to judge the box, in one dict.

        `gross_w` is the hydraulic power available across the box (ρgQH);
        `electrical_w` applies the overall efficiency. Both use the *driving*
        head so a diffuser and any static drop are reflected.
        """
        h = self.driving_head(approach_velocity, g)
        v_t = throat_velocity(h, self.cd, g)
        q = self.throat_area * v_t
        gross = low_head_power(q, h, 1.0, rho, g)
        elec = gross * self.efficiency
        return {
            "approach_velocity": approach_velocity,
            "driving_head_m": h,
            "throat_velocity": v_t,
            "flow_m3s": q,
            "gross_hydraulic_w": gross,
            "electrical_w": elec,
        }


# ---------------------------------------------------------------------------
# Buoyancy — an air box wants to float; how much ballast to sink & hold it
# ---------------------------------------------------------------------------
def buoyancy_force_n(air_volume_m3: float, rho: float = RHO_WATER, g: float = G) -> float:
    """Upward buoyant force (N) on a fully submerged air volume: ρ·g·V."""
    if air_volume_m3 < 0:
        raise ValueError("air_volume must be >= 0")
    return rho * g * air_volume_m3


def ballast_mass_kg(air_volume_m3: float, structure_mass_kg: float = 0.0,
                    ballast_density: float = 2400.0, safety_factor: float = 1.5,
                    rho: float = RHO_WATER, g: float = G) -> float:
    """Dry mass of ballast (kg) needed to sink AND hold a submerged air box.

    Ballast loses some of its own weight to buoyancy underwater, so we divide by
    (1 - ρ_water/ρ_ballast). Concrete ballast_density ≈ 2400, steel ≈ 7850.
    `structure_mass_kg` is the box's own dry mass (it helps sink itself). A
    safety factor pads against currents trying to lift/roll the box.

    Returns 0 if the structure already outweighs the buoyancy.
    """
    if not (0 < rho < ballast_density):
        raise ValueError("need 0 < rho < ballast_density (ballast must sink)")
    buoy_n = buoyancy_force_n(air_volume_m3, rho, g) * safety_factor
    structure_hold_n = structure_mass_kg * g  # dry-weight hold-down (approx)
    needed_n = max(0.0, buoy_n - structure_hold_n)
    effective = g * (1.0 - rho / ballast_density)  # N of hold-down per kg ballast
    return needed_n / effective
