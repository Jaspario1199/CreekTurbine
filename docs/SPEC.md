# CreekTurbine Mk1 — frozen design specification

**Status: DESIGN FROZEN** (rev 1). Every decision below is locked with its
rationale; the short list of parameters *deliberately* left to prototype
calibration is at the end. The complete unit is modeled — open
**`cad/step/_assembly.step`** in any CAD tool for the base model, or regenerate
everything from `cad/params.py` (one dimensional chain).

![Full unit assembly](images/cad_assembly.png)

## Identity & envelope

| | |
|---|---|
| Concept | Self-contained hydrokinetic creek turbine — "a box with a handle you set in the stream" |
| Deploys in | any creek **≥ 4 ft wide**, **6 in – 3 ft deep**, mellow flow (~0.4 m/s+) |
| Footprint | skid 460 × 460 mm; funnel wings gather a ~0.9 m swath |
| Height | ~1.02 m (skid → handle) |
| Carry weight | **~15 kg (33 lb) dry** — under the 40 lb budget; ballast is **creek rocks added on-site** into the skid tray, so you never carry it |
| Output | 12 V LiFePO₄ buffer → USB-C PD (laptop), USB, 12 V |
| Performance | ~1.7–4 W continuous (mellow creek, universal funnel): **~1 laptop charge/day in ≥1 ft of water**, derating to ~0.4/day at 6 in. Brisker water or site wing-walls raise it substantially (v³) |

## Frozen decisions (the design record)

| # | Decision | Frozen choice | Why (full rationale linked) |
|---|----------|---------------|------------------------------|
| D1 | Energy principle | **Hydrokinetic** (no dam) | legal/eco footprint, removable — [ARCHITECTURE](ARCHITECTURE.md) |
| D2 | Rotor type | **Vertical-axis Savonius** | self-starts in slow water, direction-agnostic, debris-tolerant, vertical shaft puts the generator above water — [RESEARCH_ROTORS](RESEARCH_ROTORS.md) |
| D3 | Blade geometry | **Helical (180° twist), arc-optimized scoop, overlap 0.15, aspect ~1.6, end plates** | verified Cp levers; helix adds self-start smoothness + debris shedding — [RESEARCH_ROTORS](RESEARCH_ROTORS.md) |
| D4 | Sizing basis | **Cp 0.18 (conservative)** for all sizing; optimized geometry's 0.19–0.25 is *margin*, not promise | lab-vs-field honesty — [CRITIQUE #16](CRITIQUE.md) |
| D5 | Rotor size | **Ø 340 × 540 mm** (3 printed segments/blade × 2 blades) | 5 W target at 0.8 m/s; segments fit a 240 mm printer Z — [CRITIQUE #3](CRITIQUE.md) |
| D6 | Blade↔plate joint | **Profile-matched grooves** in the end plates + through-rod clamps + epoxy | a twisted edge can't take a bolt; shared profile source `cad/lib.py` — [CRITIQUE #4](CRITIQUE.md) |
| D7 | Intake | **Universal free-standing funnel**, 0.9 m gather mouth, 0.35 m tall wings | works in any ≥4 ft creek without bank works; speed-up capped honestly at √(g·y) — [FUNNEL](FUNNEL.md) |
| D8 | Wet→dry crossing | **Axial magnetic coupling** (12 × Ø15×6 N42 per disc, R55, 3 mm gap → ~4.2 N·m, slips on overload) through a **cut-from-sheet non-magnetic bulkhead** | no shaft seal to leak; built-in torque limiter — [MAG_COUPLING](MAG_COUPLING.md) |
| D9 | Coupling thrust | **Thrust/angular-contact bearings both shafts** (≥570 N) | ~380 N constant axial pull — [CRITIQUE #2](CRITIQUE.md) |
| D10 | Generator + charge path | Low-Kv PMA → 3-phase rectifier → **boost-MPPT** (low quiescent <10 mA) → 12 V LiFePO₄ (BMS w/ low-temp cutoff) | the *buyable* fix for slow-rotor cut-in — [CRITIQUE #1](CRITIQUE.md) |
| D11 | Overspeed safety | **Dump/clamp on the generator side, before the BMS** + fuse at battery + | BMS disconnect must never orphan the PMA — [SAFETY](SAFETY.md), [CRITIQUE #9](CRITIQUE.md) |
| D12 | Bus voltage | **12 V** | no shore cable in the self-contained form; richest USB/12 V ecosystem ([PORTABLE](PORTABLE.md) covers the 24–48 V cable variant) |
| D13 | Structure | Printed rings/plates (PETG/ASA) + **bought 20 mm Al tube columns** + stainless Ø16 shaft, Ø22 flanged bearings | print what's complex, buy what's long/structural — [cad/README](../cad/README.md) |
| D14 | Outer durability | **HDPE/UHMW shell** (or ASA + bed-liner), **sacrificial UHMW skid runners**, TPU bumpers | scuff resistance with cheap replaceable wear parts |
| D15 | Debris strategy | Blunt drag rotor + **angled trash rack** + open cage + drain holes + raised bearing boss | debris is the #1 field failure — [RESEARCH_ROTORS §4](RESEARCH_ROTORS.md) |
| D16 | Flood strategy | **Retrieval line + pull before storms**; stakes/ballast as backstop (~670 N flood drag computed) | you don't out-anchor a flood — [CRITIQUE #5](CRITIQUE.md) |
| D17 | Loads philosophy | Battery-buffered: loads always run off the pack; turbine trickles it back | smooth output, burst capability, source-agnostic charging |

## Key interfaces (for anyone extending the CAD)

- **Main clamp stack:** cage top ring → bulkhead → housing floor, **8 × M5 on Ø161** — one bolt circle seals and structures the wet/dry joint
- **Shaft:** Ø16 stainless; lower bearing Ø22 flanged in the cage boss; coupling discs bore Ø16 w/ M5 set screws
- **Cage columns:** 4 × 20 mm square tube, 604 mm, socketed ±15 mm with radial M5 clamps
- **Skid bolts:** 4 × M5 on Ø406; stake holes Ø10 at corners
- **Lid:** 6 × M5 on Ø394, gasketed, lip-registered

## Deliberately NOT frozen (calibrate on the prototype — [TEST_PROTOCOL](TEST_PROTOCOL.md))

| Parameter | Current assumption | Calibrated by |
|---|---|---|
| Funnel `confinement` | 0.82 | **F2** float test through the throat |
| Real rotor Cp | 0.18 sizing / 0.19–0.25 geometry | **F3** logged watts |
| Generator Ke & cut-in | catalog value | **B1** drill test |
| Coupling slip torque | ~4.2 N·m (τ·A·R model) | **B2** lever + scale |
| Maintenance interval | unknown | **F4** 72 h soak |

## Cost & verification

- **BOM band:** ~$300–480 ([HARDWARE](HARDWARE.md)) + ~2 kg filament
- **Software verification:** 115 physics/model tests passing; 14 parts + assembly export clean; 19-finding red-team audit closed ([CRITIQUE](CRITIQUE.md))
- **Research basis:** 22 adversarially-verified literature claims ([RESEARCH_ROTORS](RESEARCH_ROTORS.md))
