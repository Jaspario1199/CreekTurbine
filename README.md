# CreekTurbine 🌊⚡

A DIY **hydrokinetic** turbine you can drop into a creek — an "underwater wind
turbine" that harvests the *kinetic* energy of the moving stream to trickle-charge
a battery. No dam, no vertical drop, removable before floods.

> **Status: Phase 0 — the honest-numbers toolkit.** A config-driven physics
> engine sizes a turbine for *your* creek, matches a generator, sizes a battery,
> and tells you what it can actually run — today, with **zero hardware**. You only
> fill in three things you measure with a tape and a stopwatch. Parametric CAD for
> the printed parts is included and exports clean STEP/STL.

```bash
pip install -r requirements.txt
python -m scripts.measure_creek        # how to measure your creek (float method)
python -m scripts.size_turbine --figs  # size the turbine + render figures to ./output
python -m pytest                       # 46 checks on the physics
```

---

## Read this first: a creek is a *trickle-charger*, not a generator set

The power in moving water is `P = ½·ρ·A·v³`. That **v³** is the whole story:
double the water speed and you get **8×** the power. Two creeks that look the same
to your eye can differ 8× in what they'll make. So:

![Creek power scales with velocity cubed](docs/images/power_vs_velocity.png)

- **Measure your creek's speed honestly** — it dominates everything else.
- A gentle 0.5 m/s creek yields a few watts; a brisk 1 m/s creek, tens of watts.
- **A few watts, 24/7, is genuinely useful.** 5 W around the clock ≈ **90 Wh/day**
  — enough to keep phones, trail/security cameras, LED lights, and IoT sensors
  alive indefinitely (a ~10 W always-on Wi-Fi router or a laptop needs a bit more
  creek). It is **not** going to run a fridge or a house.

The toolkit's job is to tell you the truth for *your* water before you spend a
dollar — and to show you the two free levers that beat buying bigger gear:
**measure the fastest spot**, and **speed the water up** with a chute or shroud
(since power ∝ v³, a 1.2× speed-up is a ~1.7× power gain).

---

## What it tells you (real output for the default creek)

`python -m scripts.size_turbine` on the placeholder creek (0.8 m/s, 1.5 m × 0.5 m
channel, 5 W target):

```
 TARGET: 5.0 W continuous at the battery
   → Savonius rotor: Ø 0.34 m × 0.54 m tall  (frontal area 0.19 m²)
   Blocks 25% of the wetted channel — comfortable.
   At 0.80 m/s: shaft ≈ 40 rpm, torque ≈ 2.0 N·m, mechanical ≈ 8.5 W → battery ≈ 5.0 W
 GENERATOR MATCH (the part people get wrong):
   Rotor turns ~40 rpm — that's SLOW. For a 12 V bus to cut in at your low-season
   ~0.48 m/s, pick a PMA with Ke ≈ 0.5 V/rpm (≈ 2 rpm/V).
 ENERGY: 5.0 W × 24 h × 75% uptime ≈ 90 Wh/day  (33 kWh/year)
 BATTERY: 19 Ah at 12 V (LiFePO4) for 2 days autonomy
 WHAT IT RUNS:  ✓ phone  ✓ security cam  ✓ LED light  ✓ sensors  ✗ Wi-Fi  ✗ laptop  ✗ fridge
```

It also renders these:

| Size vs. velocity | Daily energy budget | Recommended rotor |
|---|---|---|
| ![sizing](docs/images/sizing_curve.png) | ![energy](docs/images/energy_budget.png) | ![savonius](docs/images/savonius_schematic.png) |

---

## Why a Savonius (vertical-axis) turbine

The default design is a **Savonius** — a vertical-axis drag rotor (think two
scoops making an S). Its power coefficient isn't the best (a propeller wins on
paper), but it's the best *system* for a real DIY creek:

- **Self-starts in slow water**, where a propeller just stalls.
- **Doesn't care which way the flow points** — creeks meander and eddy.
- **Vertical shaft ⇒ the generator sits on top, above the water.** This turns the
  single hardest problem — keeping a generator dry — into "bolt it to a plate in
  the air." Only the bearings get wet.
- **Debris-tolerant, low-rpm/high-torque, buildable from a barrel or PVC pipe.**

The costs — a bigger rotor per watt and a slow shaft that needs careful generator
matching — are shown explicitly, never hidden. Got a brisk, deep creek? Set
`TURBINE_TYPE = "axial"` and the model sizes the higher-efficiency propeller
instead. Details in **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

---

## How it works (the modules)

1. **`hydrokinetics.py`** — the physics you must trust: `½·ρ·A·v³`, the Betz limit
   (16/27), rotor sizing, rpm/torque, flow-augmentation. Tested against
   hand-computed values.
2. **`rotor.py`** — Savonius & axial rotors behind one interface; turns a power
   target into rotor dimensions.
3. **`generator.py`** — the part people get wrong: **cut-in velocity** (below which
   you make *nothing*) and a Ke recommender to match your low-season flow.
4. **`energy.py`** — daily/annual Wh, battery Ah sizing, and the "what it runs" table.
5. **`siting.py`** — float-method + cross-section math to measure your creek.
6. **`simulator.py`** — renders all of it to PNGs (headless).

---

## Repository layout

```
creekturbine/
  config.py          # ← the ONLY file you edit: your creek, your goal, your battery
  hydrokinetics.py   # ½·ρ·A·v³, Betz, sizing, rpm/torque, augmentation
  rotor.py           # Savonius + axial rotor models (one interface)
  generator.py       # PMA cut-in velocity + Ke matching (the classic failure point)
  energy.py          # daily/annual energy, battery sizing, what-it-runs
  siting.py          # measure-your-creek math (float method, cross-section)
  simulator.py       # renders the figures (matplotlib, headless)
scripts/
  measure_creek.py   # walk through measuring velocity & flow
  size_turbine.py    # end-to-end sizing report (+ --figs)
  demo_sim.py        # render the whole picture book to ./output
cad/
  params.py          # printed-part dimensions (mm) — edit to match your hardware
  parts/             # end plate ×2, shaft coupler, generator mount (parametric)
  export_all.py      # -> cad/step/*.step + cad/stl/*.stl
tests/               # 46 checks on the physics/energy/generator/siting math
docs/
  ARCHITECTURE.md    # how the pieces fit + design decisions
  SITING.md          # measure first, then make the water faster (+ permits)
  SAFETY.md          # water + electricity + a spinning rotor: read this
  HARDWARE.md        # BOM + the generator problem (cut-in, low rpm)
  ROADMAP.md         # phase-by-phase build plan
  RESEARCH.md        # the physics & why the default coefficients
```

---

## Where this is going

| Phase | What | Cost |
|------|------|------|
| **0** ✅ | Physics/sizing engine, rotor+generator+energy models, simulator, tests, CAD | Free |
| **1** | Measure your creek (2+ seasons), lock rotor size & generator Ke | ~$0 |
| **2** | Bench-build rotor + generator, prove **cut-in** and charging | 💰 generator + battery |
| **3** | Wet install: frame, anchoring, trash rack, **dump load**, sealed electronics | 💰 ~$250–450 |
| **4** | Flow augmentation (chute/shroud) + flood/winter survival | 💰 iteration |

The genuinely hard, risky parts are called out honestly: **matching a generator
to a slow shaft**, **keeping it dry and alive in a creek**, and the **legal/
environmental** rules you must settle *before* building. See
**[docs/ROADMAP.md](docs/ROADMAP.md)**.

> ⚠️ **Before you build, read [docs/SAFETY.md](docs/SAFETY.md).** A hydro source
> runs 24/7 and can't be switched off like a solar panel — it *needs* a charge
> controller with a dump load, a fused battery, and sealed, elevated electronics.
> And check your **water rights and fish-passage rules** first
> ([docs/SITING.md](docs/SITING.md)).
