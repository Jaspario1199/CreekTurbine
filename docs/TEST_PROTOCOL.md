# Test protocol — from "modeled" to "trusted"

Every number the toolkit prints is a *prediction*. This protocol is how you turn
predictions into measurements — on the bench first (cheap, dry, reversible),
then in the creek — and **feed each measurement back into `config.py`** so the
model converges on *your* hardware. It closes the open items at the end of
[CRITIQUE.md](CRITIQUE.md).

**Equipment (~$40 beyond the build):** cordless drill with speed control,
multimeter (with 10 A range or a shunt), cheap luggage/fish scale, stopwatch,
tape measure, a floating stick, zip ties, desiccant packs, paper towel.

**Rule for every test:** write the number down (template at the bottom). A test
without a recorded number didn't happen.

---

## Bench tests (do ALL before the creek)

### B1 — Generator curve & cut-in ✻ the most important test
**Why:** cut-in is where DIY builds die (CRITIQUE #1).
1. Chuck the generator shaft (or its coupler) in the drill. Run at 3–4 set
   speeds; measure speed (mark the shaft, count flashes against a stopwatch, or
   use a phone tachometer app) and **open-circuit DC volts** after the rectifier.
2. **Ke = volts ÷ rpm** (it's a straight line — 2 points confirm, 4 points prove).
3. Connect rectifier → controller → battery. Slowly raise rpm until **charge
   current > 0**: that's your real **cut-in rpm**.
4. Convert to water speed: `v_cutin = cut-in rpm ÷ (rpm printed by size_turbine
   per m/s)`. **PASS: v_cutin ≤ your creek's low-season speed.**
5. If using a boost-MPPT: verify it charges with the drill at the rotor's real
   ~40 rpm equivalent. **PASS: charging at working rpm, not just at drill max.**

→ **Feed back:** measured Ke into your generator notes; if cut-in fails, change
the controller (boost) or the pulley ratio — not your hopes.

### B2 — Coupling slip torque & axial pull
**Why:** the τ·A·R estimate must be verified (CRITIQUE open item 4); the axial
force is large (#2).
1. Lock the generator-side disc. Zip-tie a lever (known length L, e.g. 0.3 m) to
   the rotor-side disc. Pull the lever tip with the luggage scale, perpendicular,
   until the coupling **slips**. **Slip torque = scale reading (kg) × 9.81 × L.**
2. **PASS: slip torque ≥ 2× the rotor operating torque** from `size_turbine`
   (default ~2 N·m → need ≥ 4 N·m). Repeat 3×; take the lowest.
3. Axial: with the bulkhead clamped, spin the drivetrain by hand for 5 minutes.
   **PASS: no rubbing sounds, no gap closure, thrust bearings turning freely.**

→ **Feed back:** if slip is low, add magnets / close the gap and re-run
`scripts.mag_coupling`; record the measured vs predicted ratio.

### B3 — Drivetrain drag (the silent power thief)
1. With the generator **disconnected** (open circuit), measure the torque to
   *just keep the drivetrain turning*: lever + scale again, slow steady pull.
2. **PASS: drag torque < 10 % of operating torque** (~0.2 N·m for the default).
   Higher means bearing preload, seal rub, or coupling eccentricity — find it
   now; in the creek it just looks like "less power."

### B4 — Watertightness (the dry canister earns its name)
1. Assemble the dry housing + bulkhead + lid with gaskets, **empty** except a
   paper towel and a desiccant pack taped inside. Weight it and submerge in a
   tub/barrel, deeper than creek depth (≥ 0.5 m of water above the lid).
2. 30 min first, inspect. Then a full **24 h**. **PASS: towel bone-dry twice.**
3. Re-test after every re-opening of the housing. Seals fail on the re-assembly
   you didn't test, not the one you did.

### B5 — Controller idle draw
1. Battery connected, turbine input disconnected, loads off. Measure the DC
   current out of the battery. `P_idle = V × I`.
2. **PASS: ≤ 0.3 W** (25 mA @ 12 V). → **Feed back: `CONTROLLER_IDLE_W`.**

---

## Field tests (in the creek, staged)

### F1 — Site numbers (before anything gets wet)
`python -m scripts.measure_creek` at the actual spot: width, average depth,
float-timed velocity ×0.85. → **Feed back: `CREEK_VELOCITY / WIDTH / DEPTH`.**

### F2 — Funnel confinement calibration ✻ the model's known unknown
**Why:** `confinement = 0.82` is an assumption (CRITIQUE #7).
1. Install the wings + cage, **no rotor yet** (open throat).
2. Float-time the stick through the **throat** over a marked ~1 m, several runs.
3. Compute what the model calls ideal: run `scripts.funnel` with your F1 numbers
   and read `capped_velocity` (or: min(Q/A_throat, √(g·y_throat))).
4. **`confinement = (v_throat_measured − v_ambient) / (v_ideal − v_ambient)`.**
→ **Feed back:** `confinement` in your funnel runs; re-run the sizing. Expect
0.6–0.9; below 0.5 means water is escaping under/around — seal the wing bottoms
to the bed with rocks/sandbags and re-measure.

### F3 — Real rotor Cp (one number that grades the whole rotor)
1. Full unit running, battery charging. Log **battery-side watts** (V × I) over
   ≥ 10 min of steady flow; note the throat velocity (F2 method).
2. **Cp_real = P_elec ÷ (½·ρ·A_rotor·v³ · η_gen · η_drive)** with η_gen from B1's
   curve (or 0.65 default) and η_drive ≈ 0.9.
3. Compare to your selected profile (0.16 / 0.19 / 0.24). **Expect 20–30 % below
   the preset** (lab-vs-field, CRITIQUE #16). → **Feed back: `CP_SAVONIUS` =
   measured, profile = `custom`.** The model now predicts *your* build.

### F4 — 72-hour unattended soak (the graduation exam)
Leave it running three days, visit daily:
- [ ] Net Wh gained per day ≈ model prediction (within the F2/F3-calibrated model)
- [ ] Trash rack shedding, throat clear (note debris per day — sets your
      maintenance interval, CRITIQUE open item 3)
- [ ] No water in the dry canister (towel check), no bearing noise/heat
- [ ] Stakes/ballast unmoved; retrieval line intact
- [ ] Battery not over-full (dump load working) and not draining overnight

**PASS on all five → the unit has earned unattended deployment.** Any failure:
fix, and restart the 72 h clock.

---

## Data log (copy per test session)

| Date | Test | Measured | Model predicted | Ratio | Fed back to |
|------|------|----------|-----------------|-------|-------------|
| | B1 Ke (V/rpm) | | | | notes |
| | B1 cut-in (rpm / m/s) | | | | controller/pulley choice |
| | B2 slip torque (N·m) | | ~4.2 | | magnets/gap |
| | B3 drag torque (N·m) | | <0.2 | | bearings/seals |
| | B5 idle draw (W) | | 0.25 | | `CONTROLLER_IDLE_W` |
| | F1 velocity (m/s) | | — | | `CREEK_VELOCITY` |
| | F2 confinement | | 0.82 | | funnel runs |
| | F3 Cp | | profile value | | `CP_SAVONIUS` |
| | F4 net Wh/day | | report value | | sanity |

Two calibration passes (bench, then field) typically bring the model within
~15 % of reality — from there on, `size_turbine` is telling you the truth about
*your* creek and *your* machine.
