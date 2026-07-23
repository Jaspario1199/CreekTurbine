"""
Generator matching — turning a slowly spinning shaft into battery charge.

This is the part most DIY creek builds get wrong, so the model is deliberately
explicit about the two things that actually bite you:

  1. CUT-IN. A permanent-magnet alternator (PMA) makes a voltage proportional
     to rpm.  Below the rpm where that voltage (after the rectifier) exceeds the
     battery voltage, ZERO current flows and you charge nothing.  So there is a
     minimum water velocity — the "cut-in velocity" — below which your creek
     does nothing.  You match the generator to the creek by choosing its
     voltage constant so cut-in lands at your creek's LOW flow, not its average.

  2. LOW RPM.  A Savonius turns at tens of rpm.  Most cheap motors/PMAs are wound
     to hit their rated voltage at thousands of rpm, so used bare they never cut
     in.  Fixes: pick a low-Kv (high pole-count) PMA, add a step-up (belt/gear),
     or accept a higher cut-in.  The model makes the trade-off visible.

We model the PMA by its voltage constant Ke (volts of DC bus per rpm, measured
AFTER the 3-phase rectifier).  If you know Kv (rpm per volt) instead, Ke = 1/Kv.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import hydrokinetics as hk


@dataclass
class Generator:
    """A permanent-magnet alternator described by the numbers that matter.

    ke_dc:      volts of rectified DC bus produced per shaft rpm (open circuit).
                e.g. 0.05 means 300 rpm -> ~15 V.  Ke = 1/Kv.
    resistance: total phase+rectifier resistance seen by the DC bus (ohms).
                Bigger = softer generator = less current at a given overspeed.
    efficiency: electrical efficiency at the operating point (0..1).
    max_power_w: rating above which you must divert to a dump load (0 = unknown).
    """

    ke_dc: float = 0.05
    resistance: float = 1.0
    efficiency: float = 0.65
    max_power_w: float = 0.0

    def open_circuit_voltage(self, rpm: float) -> float:
        """Rectified DC bus voltage with no load, at a given shaft rpm."""
        return self.ke_dc * rpm

    def cut_in_rpm(self, battery_voltage: float) -> float:
        """Lowest rpm at which the bus can exceed the battery and start charging."""
        if self.ke_dc <= 0:
            return math.inf
        return battery_voltage / self.ke_dc

    def charge_current(self, rpm: float, battery_voltage: float) -> float:
        """DC amps pushed into the battery at a given rpm (0 below cut-in).

        Simple, honest model: the generator is an EMF source ke*rpm behind an
        internal resistance, clamped to the battery voltage. Current is the
        excess voltage divided by resistance.
        """
        emf = self.open_circuit_voltage(rpm)
        if emf <= battery_voltage:
            return 0.0
        return (emf - battery_voltage) / self.resistance

    def charge_power(self, rpm: float, battery_voltage: float) -> float:
        """Electrical watts delivered INTO the battery at a given rpm."""
        return self.charge_current(rpm, battery_voltage) * battery_voltage


def cut_in_velocity(rotor, generator: Generator, battery_voltage: float) -> float:
    """Water velocity at which the rotor first reaches the generator's cut-in rpm.

    Below this creek speed you harvest nothing.  This is the single most useful
    number for judging a real build: compare it against your creek's LOW-season
    velocity, not its average.

    Returns math.inf if the generator can never cut in (ke_dc = 0).
    """
    rpm_needed = generator.cut_in_rpm(battery_voltage)
    if not math.isfinite(rpm_needed):
        return math.inf
    # rpm = tsr * v / R * (60 / 2pi)  ->  v = rpm_needed * R * 2pi / (tsr * 60)
    omega_needed = hk.omega_from_rpm(rpm_needed)
    return omega_needed * rotor.radius / rotor.optimal_tsr


def recommend_ke(rotor, cut_in_target_velocity: float, battery_voltage: float) -> float:
    """Pick a generator Ke so cut-in lands at a chosen (low) creek velocity.

    Feed this your creek's LOW-season speed and it returns the volts-per-rpm the
    PMA should have.  Use it to shop for a PMA or to size a step-up ratio.
    """
    rpm_at_target = hk.rpm_at_velocity(rotor.optimal_tsr, cut_in_target_velocity,
                                       rotor.radius)
    if rpm_at_target <= 0:
        return math.inf
    return battery_voltage / rpm_at_target


# The highest volts-per-rpm you can realistically BUY in a small PMA. Purpose-
# wound low-speed axial-flux PMAs reach ~0.10-0.15 V/rpm; the Ke this module
# often *recommends* for a slow Savonius (0.3-1.0 V/rpm) exceeds anything on the
# market. That gap is the classic dead-on-arrival DIY mistake, so we check it.
MAX_PRACTICAL_KE = 0.15


def practical_options(ke_recommended: float, practical_ke: float = 0.12) -> dict:
    """Reality-check a recommended Ke against buyable hardware.

    Returns {"buyable": bool, "step_up": ratio, "boost_mppt": bool}:
      - buyable:    the recommended Ke exists off the shelf — direct-drive works.
      - step_up:    belt/gear ratio that lets a realistic `practical_ke` PMA cut
                    in at the same rotor speed (ke_rec / practical_ke).
      - boost_mppt: True when the modern no-gears fix applies — a BOOST-type MPPT
                    charge controller steps a low PMA voltage (2-5 V+) UP to the
                    battery, so cut-in no longer requires beating battery voltage.
    """
    if ke_recommended <= 0:
        raise ValueError("ke_recommended must be > 0")
    buyable = ke_recommended <= MAX_PRACTICAL_KE
    return {
        "buyable": buyable,
        "step_up": ke_recommended / practical_ke,
        "boost_mppt": not buyable,
    }


def step_up_ratio_for_rpm(rotor, velocity: float, desired_generator_rpm: float) -> float:
    """Belt/gear ratio to bring a slow rotor up to a generator's happy rpm.

    Returns generator_rpm / rotor_rpm. A value near 1 means direct-drive is
    fine; a large value means you need a belt or gearbox (and will pay a few %
    efficiency for it). Savonius creeks often land at 5-15x.
    """
    rotor_rpm = hk.rpm_at_velocity(rotor.optimal_tsr, velocity, rotor.radius)
    if rotor_rpm <= 0:
        return math.inf
    return desired_generator_rpm / rotor_rpm
