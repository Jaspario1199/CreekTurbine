"""
CreekTurbine — an honest engineering toolkit for a DIY hydrokinetic ("underwater
wind") turbine you can drop into a creek to trickle-charge a battery.

The public surface is intentionally small; everything is plain functions and
dataclasses operating in SI units. Start with:

    from creekturbine import config
    from creekturbine.hydrokinetics import extractable_power, swept_area_for_power
    from creekturbine.rotor import SavoniusRotor, AxialRotor
    from creekturbine.generator import Generator, cut_in_velocity
    from creekturbine.energy import daily_energy_wh, what_it_runs

See README.md for the one-paragraph reality check, then run
`python -m scripts.size_turbine` to size a turbine for YOUR creek.
"""

from . import (config, hydrokinetics, rotor, generator, energy, siting, ducted,
               portable, selfcontained, magnetics)

__all__ = ["config", "hydrokinetics", "rotor", "generator", "energy", "siting",
           "ducted", "portable", "selfcontained", "magnetics"]

__version__ = "0.1.0"
