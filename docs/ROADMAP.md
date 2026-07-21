# Roadmap — de-risk in software, then build

The philosophy: prove the numbers work for *your* creek (free) before spending on
parts, and tackle the genuinely hard bits (the generator, waterproofing, floods)
deliberately rather than by surprise.

| Phase | What | Cost |
|------|------|------|
| **0** ✅ | Physics & sizing engine, rotor/generator/energy models, simulator, tests, parametric CAD | Free (software) |
| **1** | Measure your creek in 2+ seasons; lock rotor size & generator Ke; dry-fit the CAD | ~$0 |
| **2** | Bench build: rotor + generator on a stand, spin it (drill/by hand), confirm cut-in & charging into a battery | 💰 the generator + battery |
| **3** | Wet install: frame, anchoring, trash rack, dump load, sealed electronics; measure real output | 💰 the full build (~$250–450) |
| **4** | Flow augmentation (chute/shroud) + survival hardening for floods & winter | 💰 iteration |

## What's built today (Phase 0)

- **`hydrokinetics.py`** — `½·ρ·A·v³`, the Betz limit, rotor sizing, rpm/torque,
  and flow-augmentation math, all tested against hand-computed values.
- **`rotor.py`** — Savonius and axial rotor models behind one interface; sizing
  helpers that turn a power target into rotor dimensions.
- **`generator.py`** — PMA cut-in rpm/velocity, charge current/power, and a Ke
  recommender so the generator matches your low-season flow.
- **`energy.py`** — daily/annual energy, battery Ah sizing, and a "what it runs"
  table (phone → fridge).
- **`siting.py`** — the float-method + cross-section measurement math.
- **`simulator.py`** + `scripts/` — the sizing report and the figures.
- **`cad/`** — parametric end plates, shaft coupler, generator mount (STEP+STL).

## The genuinely hard parts (called out honestly)

1. **Generator matching** (Phase 2). Low creek rpm vs. a generator's cut-in is
   *the* classic failure. The model makes it visible; the bench test in Phase 2
   is where you prove it with a real part before getting wet.
2. **Keeping the generator dry** (Phase 3). The vertical-axis choice mostly
   solves this — generator on top, only bearings wet — but the shaft, bearings,
   and enclosure sealing still need care.
3. **Surviving the creek** (Phase 3–4). Floods, debris, silt, ice, corrosion.
   Design for removal; over-build the frame and anchors.
4. **Legal & environmental** (Phase 1, ongoing). Water rights and fish passage —
   settle these *before* building. See [SITING.md](SITING.md) and [SAFETY.md](SAFETY.md).

## Ideas for later

- A live logger (ESP32 + INA226 current/voltage sensor) to record real Wh/day
  and validate the model against your creek.
- A 3-scoop Savonius option (smoother torque) and a proper shrouded-rotor model.
- A tuned Cp-vs-TSR curve per rotor instead of a single design-point Cp.
