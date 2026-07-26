"""
Hydrokinetics — the physics you must trust.

A creek turbine is a HYDROKINETIC device: it harvests the *kinetic* energy of
moving water, exactly like a wind turbine harvests moving air. It does NOT use
"head" (a vertical drop of water). That single fact drives everything:

    Kinetic power passing through an area A at speed v:

        P_available = 1/2 * rho * A * v^3          [watts]

    with rho = water density (~1000 kg/m^3). Note the v^3 — power scales with
    the CUBE of speed. This is why measuring (and, if possible, increasing) the
    water speed at the rotor matters more than anything else you can buy.

You cannot capture all of P_available. Two hard physical facts:

  * Betz limit: an open rotor can extract at most 16/27 = 59.3% of the kinetic
    power in the stream tube it intercepts, because the water has to keep
    moving to make room for the water behind it. Real rotors do worse.
  * The captured fraction is the power coefficient Cp (<= Betz). A conservative
    DIY Savonius is ~0.18; a good small propeller ~0.35-0.45.

Everything in this module is pure functions in SI units so it is trivial to
test (see tests/test_hydrokinetics.py) and to reason about.
"""

from __future__ import annotations

import math

RHO_WATER = 1000.0                 # kg/m^3, fresh water
BETZ_LIMIT = 16.0 / 27.0           # ~0.5926, the absolute ceiling on Cp


# ---------------------------------------------------------------------------
# Power in the water
# ---------------------------------------------------------------------------
def power_flux(velocity: float, rho: float = RHO_WATER) -> float:
    """Kinetic power per unit frontal area of the stream, in W/m^2.

    This is 1/2 * rho * v^3. Multiply by a rotor's frontal area to get the
    power available to that rotor. It is the cleanest way to feel the v^3 law:
    at 0.5 m/s water carries ~63 W/m^2; at 1.0 m/s it carries ~500 W/m^2.
    """
    if velocity < 0:
        raise ValueError("velocity must be >= 0")
    return 0.5 * rho * velocity ** 3


def available_power(area: float, velocity: float, rho: float = RHO_WATER) -> float:
    """Total kinetic power (W) passing through frontal area `area` (m^2).

    P = 1/2 * rho * A * v^3. This is the ceiling *before* the Betz limit and
    before any real losses — the raw resource, not what you'll get.
    """
    if area < 0:
        raise ValueError("area must be >= 0")
    return power_flux(velocity, rho) * area


def extractable_power(
    area: float,
    velocity: float,
    cp: float,
    eta_generator: float = 1.0,
    eta_drivetrain: float = 1.0,
    rho: float = RHO_WATER,
) -> float:
    """Realistic ELECTRICAL power delivered to the battery, in watts.

        P_elec = P_available * Cp * eta_generator * eta_drivetrain

    `cp` is silently capped at the Betz limit — asking for more is unphysical,
    and clamping keeps sizing math from returning fantasy numbers.
    """
    cp_eff = min(cp, BETZ_LIMIT)
    return available_power(area, velocity, rho) * cp_eff * eta_generator * eta_drivetrain


def swept_area_for_power(
    target_power_w: float,
    velocity: float,
    cp: float,
    eta_generator: float = 1.0,
    eta_drivetrain: float = 1.0,
    rho: float = RHO_WATER,
) -> float:
    """Invert `extractable_power`: frontal area (m^2) needed to hit a target.

    Returns math.inf if the velocity is (effectively) zero — no finite rotor
    can extract power from still water. This is the function that turns "I want
    10 W" into "you need a rotor this big", and it's where slow creeks reveal
    themselves: at 0.4 m/s the required area for even 10 W can be absurd.
    """
    if target_power_w <= 0:
        return 0.0
    denom = power_flux(velocity, rho) * min(cp, BETZ_LIMIT) * eta_generator * eta_drivetrain
    if denom <= 0:
        return math.inf
    return target_power_w / denom


# ---------------------------------------------------------------------------
# Flow speed-up (blockage, chutes, shrouds)
# ---------------------------------------------------------------------------
def blockage_ratio(rotor_area: float, channel_area: float) -> float:
    """Fraction of the wetted channel the rotor blocks (0..1).

    Some blockage HELPS a hydrokinetic rotor (it forces more water through the
    swept area instead of around it), but too much backs water up, scours the
    bed, and may need a permit. A common rule of thumb is to keep this below
    ~0.2-0.3 for a bare rotor in an open creek.
    """
    if channel_area <= 0:
        raise ValueError("channel_area must be > 0")
    return rotor_area / channel_area


def augmented_velocity(velocity: float, augmentation: float) -> float:
    """Effective velocity at the rotor after a chute/shroud speed-up factor.

    `augmentation` = 1.0 means a bare rotor in open water. A narrowed channel
    or a shroud/diffuser raises it. Because power ~ v^3, an augmentation of a
    is a power gain of a^3 (1.2x speed -> 1.73x power)."""
    if augmentation < 1.0:
        raise ValueError("augmentation must be >= 1.0 (a shroud cannot slow the water)")
    return velocity * augmentation


def power_gain_from_augmentation(augmentation: float) -> float:
    """The power multiplier for a given velocity augmentation (= augmentation^3)."""
    return augmentation ** 3


# ---------------------------------------------------------------------------
# Rotor speed / torque (ties the water to the generator)
# ---------------------------------------------------------------------------
def tip_speed_ratio(omega: float, radius: float, velocity: float) -> float:
    """TSR = (blade tip speed) / (water speed) = omega * R / v (dimensionless).

    Every rotor has a sweet-spot TSR where Cp peaks: drag rotors (Savonius)
    ~0.8-1.0, lift rotors (propellers) ~4-6. TSR sets how fast the shaft turns,
    which sets how you must match the generator.
    """
    if velocity <= 0:
        raise ValueError("velocity must be > 0")
    return omega * radius / velocity


def omega_from_tsr(tsr: float, velocity: float, radius: float) -> float:
    """Shaft angular speed (rad/s) for a target TSR at a given water speed."""
    if radius <= 0:
        raise ValueError("radius must be > 0")
    return tsr * velocity / radius


def rpm_from_omega(omega: float) -> float:
    """Convert rad/s to rev/min."""
    return omega * 60.0 / (2.0 * math.pi)


def omega_from_rpm(rpm: float) -> float:
    """Convert rev/min to rad/s."""
    return rpm * 2.0 * math.pi / 60.0


def rpm_at_velocity(tsr: float, velocity: float, radius: float) -> float:
    """Convenience: expected shaft rpm at the rotor's design TSR and a velocity.

    This is the number that decides your generator: a low-rpm Savonius (tens of
    rpm) wants a low-Kv PMA or a step-up; a faster propeller (hundreds of rpm)
    can often direct-drive a hub motor.
    """
    return rpm_from_omega(omega_from_tsr(tsr, velocity, radius))


def torque_from_power(power_w: float, omega: float) -> float:
    """Shaft torque (N*m) delivering `power_w` at angular speed `omega`.

    Torque = P / omega. Slow rotors make LOTS of torque for a given power,
    which is why a Savonius shaft and coupling must be beefy even at a few
    watts, and why its low rpm is the real generator-matching challenge.
    """
    if omega <= 0:
        raise ValueError("omega must be > 0")
    return power_w / omega
