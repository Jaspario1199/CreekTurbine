"""
Siting & measurement — how to get honest numbers off a real creek.

You cannot size a turbine from a guess, because power goes as v^3 and a guess of
"eh, maybe half a meter per second" can be off by 8x in power. These helpers turn
a tape measure, a stick, and a stopwatch into the two numbers the rest of the
toolkit needs: mean velocity and channel cross-section. See docs/SITING.md for
the field procedure; `python -m scripts.measure_creek` runs it interactively.
"""

from __future__ import annotations

from dataclasses import dataclass

# A surface float travels at the fastest (surface, mid-channel) speed. The
# depth-and-width-averaged mean is slower. This is the standard correction for a
# small, rough-bottomed natural channel.
SURFACE_TO_MEAN = 0.85


def velocity_from_float(distance_m: float, seconds: float,
                        surface_correction: float = SURFACE_TO_MEAN) -> float:
    """Mean channel velocity (m/s) from the float method.

    Float a stick/orange down a measured straight reach, time it, average
    several runs, then multiply by ~0.85 to convert the surface speed to the
    depth-averaged mean. This is the field-standard cheap measurement.
    """
    if seconds <= 0:
        raise ValueError("seconds must be > 0")
    return (distance_m / seconds) * surface_correction


def channel_area(width_m: float, avg_depth_m: float) -> float:
    """Wetted cross-sectional area (m^2). Use AVERAGE depth, not the deepest."""
    return width_m * avg_depth_m


def flow_rate_m3s(area_m2: float, mean_velocity: float) -> float:
    """Volumetric flow (m^3/s) = area x mean velocity. Also called discharge, Q."""
    return area_m2 * mean_velocity


def flow_rate_lpm(area_m2: float, mean_velocity: float) -> float:
    """Flow in litres per minute — an easier number to picture than m^3/s."""
    return flow_rate_m3s(area_m2, mean_velocity) * 1000.0 * 60.0


def continuity_velocity(mean_velocity: float, area_from: float, area_to: float) -> float:
    """Speed the water reaches when a channel of area_from narrows to area_to.

    Conservation of flow (A1*v1 = A2*v2): squeeze the same water through a
    smaller opening and it speeds up. This is the physics behind building a
    narrowed chute to boost the v^3 power — halve the area, double the speed,
    ~8x the raw power (minus real-world losses). Returns the sped-up velocity.
    """
    if area_to <= 0:
        raise ValueError("area_to must be > 0")
    return mean_velocity * area_from / area_to


@dataclass
class CreekMeasurement:
    """A tidy record of one site measurement, with derived quantities."""

    width_m: float
    avg_depth_m: float
    float_distance_m: float
    float_seconds: float
    surface_correction: float = SURFACE_TO_MEAN

    @property
    def mean_velocity(self) -> float:
        return velocity_from_float(self.float_distance_m, self.float_seconds,
                                   self.surface_correction)

    @property
    def area(self) -> float:
        return channel_area(self.width_m, self.avg_depth_m)

    @property
    def flow_m3s(self) -> float:
        return flow_rate_m3s(self.area, self.mean_velocity)
