# Assembly guide — from parts to a running creek turbine

This stitches every part and subsystem into a build order. It's written for the
**self-contained unit** (the most complete form — one box, handle on top); the
steps generalize to the drop-in and box-with-head forms too. Do the **planning**
and **bench** phases before you get anywhere near the water.

> ⚠️ Read [SAFETY.md](SAFETY.md) first. A hydro source runs 24/7, can't be
> "switched off," and needs a dump load, a fused battery, and sealed, elevated
> electronics. And settle water rights / fish-passage rules ([SITING.md](SITING.md))
> before you build.

---

## Phase 0 — Plan it in software (free, no parts)

1. **Measure your creek:** `python -m scripts.measure_creek` → velocity, width, depth.
2. **Fill in `creekturbine/config.py`** (the three EDIT-ME blocks). Pick a
   `SAVONIUS_PROFILE` (`optimized` is the sweet spot — see
   [RESEARCH_ROTORS.md](RESEARCH_ROTORS.md)).
3. **Size the rotor & system:** `python -m scripts.size_turbine --figs` → rotor
   diameter/height, expected watts, generator Ke, battery Ah, what it runs.
4. **Size the enclosure & stability:** `python -m scripts.self_contained --figs`
   → box size, freeboard, base ballast, total weight.
5. **Size the sealed coupling:** `python -m scripts.mag_coupling` → magnet count/
   grade/gap for your rotor torque.
6. If chasing more power, model the head option: `python -m scripts.box_turbine`
   ([BOX_AND_DUCT.md](BOX_AND_DUCT.md)).

Copy the resulting dimensions into `cad/params.py`.

## Phase 1 — Make the parts

**3D-print** (`pip install -r requirements-cad.txt && python -m cad.export_all`):

| Part | Qty | Notes |
|------|----:|-------|
| `savonius_blade` (helical) | `SCOOP_COUNT` (2) | PETG/ASA, print upright, 4+ walls |
| `end_plate` | 2 | clamp the blades top & bottom |
| `mag_coupling_disc` | 2 | one wet, one dry |
| `bulkhead` | 1 | **non-magnetic material only** |
| `generator_mount` | 1 | carries the PMA in the dry top |
| `shaft_coupler` | 1 | only if not using the magnetic coupling end-to-end |
| `trash_rack` | 1+ | intake screen |

**Buy** (see [HARDWARE.md](HARDWARE.md) BOM): stainless shaft + marine bearings,
low-Kv PMA, NdFeB magnets (~24 for the coupling), 3-phase rectifier, MPPT charge
controller **+ dump load**, LiFePO4 battery + BMS, main fuse, marine wire/
connectors, ballast, fasteners, O-ring, sealed enclosure.

## Phase 2 — Rotor assembly

1. **Stack each blade from its segments**: `BLADE_SEGMENTS` identical printed
   pieces per blade, each rotated by `BLADE_SEG_TWIST`, registered on 3 mm pins
   (filament offcuts) in the end-face holes, joints epoxied.
2. Fit the **shaft** through both `end_plate` hubs (the lower plate carries the
   wet coupling disc).
3. **Seat the blade ends in the plates' profile-matched grooves** (epoxy in the
   groove), phased evenly (2 blades → 180° apart); clock the top plate to the
   blade twist. Run the through-rods/bolts in the plate rings as clamps.
4. Check it spins **true and free** on its bearings before going further.

## Phase 3 — The sealed drivetrain (the clever bit)

1. Press magnets into **both** `mag_coupling_disc` parts in **alternating
   polarity** (N,S,N,S…); the two rings must mirror so N faces S. Epoxy them in.
   **Seal/pot the WET disc's magnets** (bare NdFeB rusts fast). Mind your fingers.
2. Mount the **wet disc** on the rotor shaft (below the bulkhead), the **dry disc**
   on the generator shaft (above it) — **each shaft on a THRUST (or angular-
   contact) bearing**: the discs pull toward each other with ~350–400 N,
   constantly ([MAG_COUPLING.md](MAG_COUPLING.md)). Secure against axial creep
   (collars/circlips) so neither disc can walk into the bulkhead.
3. Clamp the **`bulkhead`** (cut from 3 mm non-magnetic sheet) between them with
   its O-ring, magnets running close on each face. Keep the **gap small** — it
   sets the coupling strength. Confirm the dry side turns when you turn the wet
   side, and that it **slips** cleanly past the design torque.

## Phase 4 — Dry stack (generator + electronics)

1. Bolt the **PMA** to the `generator_mount`, coupled to the dry disc.
2. Wire **PMA → 3-phase rectifier → BOOST-MPPT charge controller → battery**,
   with the **dump/clamp on the generator side, BEFORE the BMS** (a full/cold
   battery opens the BMS — the dump must survive that) and a **fuse at the
   battery +**. Add outputs (USB-C PD module for the laptop / 12 V / a land-side
   inverter).
3. Everything except the generator lives in the **dry, sealed, elevated** part of
   the housing, above the waterline.

## Phase 5 — Housing, intake, ballast

1. Assemble the housing so the **rotor is submerged** and the **outlets stay
   above water** (the freeboard from `self_contained`).
2. Fit the **`trash_rack`** across the intake, angled to shed debris; keep the
   open area generous (the `siting.screen_*` helpers).
3. Add **base ballast** to the computed mass and a **stake/tether** so the current
   can't slide or tip it.

## Phase 6 — Bench test BEFORE the creek

Spin the rotor shaft with a drill/by hand and confirm, dry:

- [ ] Generator reaches **cut-in** and **charges the battery** at your creek's rpm
      (the number from `size_turbine`).
- [ ] The **dump load** heats up when the battery is full (fill it and check).
- [ ] The coupling transmits torque and **slips** at overload, not before.
- [ ] Nothing binds; bearings run free; the enclosure is **water-tight** (submerge
      the empty sealed housing and check for ingress).

## Phase 7 — Wet commissioning

1. Physically **block/lift the rotor** while you place and anchor the unit.
2. Set it so the rotor is submerged, outlets dry; secure ballast + stake.
3. Release the rotor; confirm it **self-starts** and the battery begins charging.
4. Walk the [SAFETY.md](SAFETY.md) pre-power checklist. Plan to **pull it before
   floods/freezes**.

---

## Where each piece is documented

- Sizing & physics: [ARCHITECTURE.md](ARCHITECTURE.md), [RESEARCH.md](RESEARCH.md)
- Rotor choice: [RESEARCH_ROTORS.md](RESEARCH_ROTORS.md)
- Enclosure forms: [SELF_CONTAINED.md](SELF_CONTAINED.md),
  [PORTABLE.md](PORTABLE.md), [BOX_AND_DUCT.md](BOX_AND_DUCT.md)
- Sealed drivetrain: [MAG_COUPLING.md](MAG_COUPLING.md)
- Parts & printing: [../cad/README.md](../cad/README.md)
- Shopping: [HARDWARE.md](HARDWARE.md) · Plan/phases: [ROADMAP.md](ROADMAP.md)
- Siting, permits, survival: [SITING.md](SITING.md) · Hazards: [SAFETY.md](SAFETY.md)
