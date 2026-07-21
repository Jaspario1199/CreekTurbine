# Architecture — how the pieces fit

CreekTurbine is a small, honest engineering toolkit. Everything is driven from
**one file you edit** (`creekturbine/config.py`) and computed from there, so you
can answer "is this worth building for MY creek?" before spending a dollar.

## The energy chain (and where power is lost)

```
  creek flow                                                    your loads
  (v, depth) ──► ROTOR ──► SHAFT ──► GENERATOR ──► RECTIFIER ──► CHARGE ──► BATTERY ──► USB / 12V
                 (Cp)      (bearings) (PMA, η)     (3-phase)     CONTROLLER   (store)     / inverter
                  │          │          │                          │
             capture at    torque    volts ∝ rpm               MPPT/PWM +
             most Betz     & rpm      (cut-in!)                 DUMP LOAD
             (16/27)                                           (overspeed safety)
```

Each stage is a module:

| Stage | Module | The one thing it tells you |
|------|--------|----------------------------|
| Resource | `hydrokinetics.py` | how much power is in the water (`½·ρ·A·v³`) and the Betz ceiling |
| Rotor | `rotor.py` | Savonius vs axial geometry, Cp, and the rotor **size** to hit a target |
| Shaft | `hydrokinetics.py` | rpm & torque from velocity + TSR (this is what the generator sees) |
| Generator | `generator.py` | the **cut-in velocity** below which you make nothing, and how to match Ke |
| Storage | `energy.py` | daily/annual Wh, battery Ah, and **what it actually runs** |
| Siting | `siting.py` | how to *measure* v and A honestly (float method, cross-section) |
| Picture | `simulator.py` | renders all of the above to PNGs |

## Design decisions (and why)

**Hydrokinetic, not "dam-and-drop."** A creek is a low-head, flowing resource.
Building a dam to make head is a permitting/ecological nightmare and usually
illegal on a natural creek. We harvest the *kinetic* energy of the moving
water — an "underwater wind turbine." No dam, removable, low impact.

**Vertical-axis Savonius is the default.** Not because its Cp is best (it
isn't — a propeller wins there), but because it's the best *system* for a DIY
creek:

- **Self-starting in slow water** (drag-driven), where a propeller stalls.
- **Flow-direction agnostic** — creeks meander and back-eddy; it doesn't care.
- **Vertical shaft ⇒ the generator lives on top, above the water.** This turns
  the single hardest problem (keeping a generator dry) into "bolt it to a plate
  in the air." Only bearings get wet.
- **Low rpm, high torque, debris-tolerant, buildable from a barrel/PVC.**

The cost is a bigger rotor for the same watts, and a low shaft rpm that forces
careful generator matching. The toolkit makes both costs explicit instead of
hiding them. If your creek is genuinely brisk and deep, `TURBINE_TYPE = "axial"`
models the higher-Cp propeller alternative.

**Cut-in is a first-class citizen.** The most common DIY failure is a generator
that never reaches charging voltage at creek rpm. `generator.py` computes the
cut-in *velocity* and recommends a Ke so it lands at your creek's **low-season**
flow, not its average.

**One interface for both rotors.** `SavoniusRotor` and `AxialRotor` share the
same `_RotorBase` surface (`frontal_area`, `performance()`, `electrical_power()`),
so everything downstream — sizing, generator matching, energy, the simulator —
works unchanged when you switch types. (Same "one interface, swappable
implementations" trick a good perception stack uses for its detectors.)

## Coordinate & unit conventions

Pure SI throughout the Python (`m`, `m/s`, `W`, `Wh`, `kg`, `rad`); the CAD is
in millimeters (parametric, `cad/params.py`). No hidden globals — every function
takes what it needs and returns a number or a dataclass, which is why the whole
thing is trivially testable (`tests/`, 46 checks against hand-computed values).
