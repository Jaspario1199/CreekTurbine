# Safety — water + electricity + a spinning machine

This is a device that combines a creek, stored electrical energy, and a rotor
that never wants to stop. Read this before the build, not after.

## Electrical

- **A hydro source runs 24/7 and can't be "switched off" like a panel in the
  dark.** You MUST give the generated power somewhere to go at all times, or the
  turbine free-spins to destruction and the rectifier/voltage spikes.
  → Install a **charge controller with a dump/diversion load** (a resistor bank
  or a heating element) that soaks up power when the battery is full. This is not
  optional on a turbine.
- **Fuse everything.** A fuse at the battery **+** terminal (sized to the wiring)
  is the single most important safety part in the box. A shorted lead-acid or
  LiFePO4 battery can deliver hundreds of amps and start a fire.
- **Battery chemistry.** LiFePO4 is the safest practical chemistry (no thermal
  runaway like other lithium types) and tolerates cold better than most —
  recommended. Whatever you use, add a **BMS**. Vent lead-acid (hydrogen gas).
- **Ground fault + wet hands.** Even 12 V systems can deliver dangerous currents
  through wet skin, and corrosion is relentless near water. Keep all electronics
  in a **sealed, elevated enclosure**, use marine-grade tinned wire and heat-
  shrink/gel connectors, and add a **GFCI/RCD** on any AC (inverter) output.
- **Never work on the wiring with the rotor free to spin.** Physically **block
  or lift the rotor** (or short the three generator phases together, which brakes
  a PMA) before touching anything.

## Mechanical

- **Overspeed is the enemy.** In a flood the water speeds up and, if the load
  drops out, the rotor can run away. The dump load handles the electrical side;
  also design a **mechanical furling/lift-out** plan and beefy bearings.
- **Pinch & entanglement.** A slow Savonius still has real torque — enough to
  catch fingers, hair, a pet, or a curious kid. Add a **guard/cage**, especially
  if the site is accessible.
- **Anchoring & floods.** Assume the worst storm in your area. Anchor to bed AND
  bank; make the unit removable; never stand downstream of a loaded frame under
  high flow.

## Environmental & legal

- **No dam.** Keep it hydrokinetic and removable. Don't block fish passage.
- **Fluids.** Use food-grade / non-toxic grease on wet bearings; never let oil
  enter the creek.
- **Permits.** See [SITING.md](SITING.md#4-permits--neighbors-do-this-before-you-build) —
  check water rights and environmental rules **before** building.

## A pre-power checklist

- [ ] Battery **fused** at the positive terminal, correct amp rating
- [ ] **Charge controller + dump load** wired and tested (fill the battery and
      confirm the diversion load gets warm)
- [ ] All electronics in a **sealed, elevated** enclosure; marine-grade connectors
- [ ] Rotor **guard** fitted; a way to **brake/lift** the rotor for service
- [ ] Frame anchored to **bed and bank**; **removable** before storms
- [ ] Permits/authority checked; downstream neighbors informed
