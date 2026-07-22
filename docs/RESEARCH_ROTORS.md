# Rotor geometry research — maximizing Cp *and* surviving the creek

A multi-source, **adversarially-verified** literature pass on experimental and
optimized hydrokinetic rotor geometries, scoped to our goal: high power
coefficient (Cp) at **low creek speeds (~0.4–1.2 m/s)** in a **small,
self-contained, vertical-shaft unit** that must run **months unattended in
debris-laden water**.

**Method / confidence:** 5 search angles → 23 sources → 75 extracted claims → the
top 25 verified by 3 independent skeptics each (a claim needs 2/3 to survive).
Result: **22 confirmed ✅, 3 refuted ❌, 0 unverified.** Confidence is noted per
claim. Several headline Cp figures are **CFD/numerical only** — flagged, and to be
discounted for simulation optimism (real built rotors land lower).

## Bottom line

For an unattended low-speed creek unit, the peer-reviewed evidence points to an
**optimized drag-type Savonius** (optionally helical, with end plates) as the best
balance of Cp and robustness. The high-Cp lift geometries win on paper and lose on
self-start and durability — exactly the wrong trade for water you can't babysit.

## The core tension (✅ high confidence)

✅ **Savonius Cp ≈ 0.12–0.25 at TSR ≈ 0.35–1.0 and self-starts; Darrieus Cp ≈
0.29–0.40 but only at TSR ≈ 1.5–3.5 and struggles to self-start at low speed.
Self-start improves with solidity; torque ripple falls as blade count rises.** [1]
For water you can't restart by hand, the higher-solidity Savonius end is the safe
choice. (A broad "Gorlov helical reaches Cp ~0.45" claim from the same review was
**❌ refuted** — do not rely on it.)

## (1) Making a Savonius much better without losing its toughness

✅ **Blade-shape optimization is the biggest low-cost lever.** An ANN/CFD-optimized
semicircular rotor — **arc angle ≈ 166°, aspect ratio 1.4–2.0, overlap 0.15–0.2,
end plates** — reaches **Cp 0.194 at TSR 0.8** (experimentally validated to ~1.6%).
[5] Among novel cross-sections, a **V-shaped** blade gave the best Cp 0.184 (U
0.172, conventional 0.166, **W 0.160 — worse than stock**), all at TSR 0.78. [2]
Profile choice can help *or* hurt.

✅ **A cambered-hydrofoil Savonius blade nearly DOUBLES Cp at very low flow:
Cp 0.21 at 105° camber → 0.26 at 140°, vs 0.13 conventional, at 0.4 m/s and
overlap 0.15.** [3] ⚠️ **Caveat:** 3D RANS **CFD only**, and the 0.13 baseline is
low — expect real numbers below 0.26. This is the strongest low-speed Cp lever
found, but an accurate cambered section is harder to fabricate than a plain bucket.

✅ **Helical/twisted blades** don't reliably raise peak Cp (that's why we set
`helical` as a self-start/robustness feature, not a Cp bump), but they remove the
Savonius's angular dead-spots, **smooth torque ripple, and shed debris** — all
gold for an unattended creek unit.

✅ **Hybrid Savonius–Darrieus:** in one experiment-validated CFD study, **~9.9%
higher Cp and ~15.9% higher torque than a lone Darrieus, with less ripple**, and
the Savonius stage shrinks the Darrieus negative-torque "dead band" from three
azimuth ranges to one (big self-start win). [4] ⚠️ **Caveat:** that Cp *gain* is
configuration-specific — much of the hybrid literature finds an added Savonius
stage *reduces* peak Cp (you buy self-start at the cost of efficiency). Trust the
self-start/ripple benefit more than the +10% Cp.

## (2) Flow augmentation (shrouds/diffusers) — real but conditional

✅ A cascade-designed **diffuser-augmented rotor reached ducted Cp ≈ 0.415**
(normalized to the diffuser's outer area, CFD), [6] and ✅ the brimmed "wind-lens"
mechanism **transfers to water — a water-lens turbine shows ~2.5× power** vs a bare
rotor. [7][8] **But:** ❌ the generic **"2–5× for any bare rotor" claim was
refuted**, and the blockage-correction literature warns diffuser gains are
"significantly overestimated in a confined [test-tank] domain" — an open,
low-blockage creek sees **less**. And a shroud is a **debris-clog and biofouling
liability**. Net: a real lever (folds into our [BOX_AND_DUCT.md](BOX_AND_DUCT.md)
head design), not a free win. Axial propellers reach the highest bare-rotor Cp
(~0.35–0.45) but need fast flow to start and have erosion-prone blades.

## (3) Frontier / experimental — real low-speed promise, "watch, don't build"

Now **verified but heavily caveated** — genuinely interesting, not yet buildable:

✅ **VIV harvesters (VIVACE):** ~**98 W/m³ at 1.03 m/s** (including dead space
between cylinders), with experiments across **0.4–1.1 m/s** — squarely our window.
[9] ✅ Among flow-induced-vibration types, **galloping gives higher power, VIV
higher efficiency, and a wake-induced-vibration** circular oscillator is the
balanced optimum. [10] ✅ Low spring stiffness + passive turbulence control push
power **onset down to 0.2 m/s**. [11] ✅ **Tandem flapping hydrofoils** are
optimized for ~1 m/s currents at ~**66.8% CFD efficiency**. [12]

⚠️ **Why these stay on the watch list:** (a) power ∝ v³, so *net* harvest at
0.2–0.4 m/s is tiny; (b) the 66.8% is swept-area-defined and **exceeds the Betz
limit** — it is not comparable to rotor Cp and not a field number; (c) all are
lab/CFD-stage with moving linkages and no long-term field record. (One FIV ranking
sub-claim — "a fluttering foil ranks third" — was ❌ **refuted 0-3**.)

## (4) Durability — and why it *reinforces* the Savonius choice

✅ **The dominant blade-degradation mechanisms are suspended-sediment abrasion,
debris impact, fatigue, and biofouling; leading-edge erosion is the most
performance-critical location — on LIFT-based blades**, because it disrupts the
flow separation/stall that lift depends on. [13]

⚠️ **Crucial scope caveat (from verification):** that source is a *tidal* study at
**2–4 m/s**. At creek speeds (0.4–1.2 m/s), **cavitation is negligible**, and a
**drag-based Savonius has no lift-critical leading edge** to erode — its torque
comes from the concave/convex drag difference of a thick, blunt scoop. So the
scary failure modes hit exactly the high-Cp lift rotors, **not** the Savonius. For
our unit the real risks are **bearing/seal wear, sediment abrasion, biofouling,
debris strikes, and fatigue** — addressed by a blunt self-shedding rotor, an
upstream trash rack ([SITING.md](SITING.md)), and robust materials.

## Ranked recommendation for a buildable self-contained creek unit

1. **Optimized Savonius — the pick.** Helical/twisted blades, **end plates**,
   **aspect ratio 1.4–2.0, overlap 0.15–0.2, arc ~166°** (or a cambered profile if
   you can build it). Self-starts, debris-tolerant, easiest to build; Cp ~0.19–0.25.
2. **Hybrid Savonius–Darrieus** — more Cp/torque with retained self-start, more
   parts. Good if your flow is brisker and cleaner.
3. **Cambered-hydrofoil / V-profile Savonius** — highest low-speed Cp (CFD to 0.26)
   *if* you can fabricate the section accurately.
4. **Watch, don't build:** VIV/VIVACE/galloping and flapping-foil harvesters —
   real low-speed promise, but lab/CFD, tiny net power, moving parts.
5. **Avoid for unattended low speed:** bare Darrieus/H-rotor (poor self-start) and
   tight shrouds (debris/fouling liability; tank-inflated numbers).

**What we did in the code:** `rotor.py` carries these as selectable
`SAVONIUS_PROFILES` (conventional 0.16 / optimized 0.19 / hydrofoil 0.24 — the
hydrofoil value deliberately sits *below* the CFD 0.26 peak), `from_profile()`
tags a `helical` flag, and `cad/` ships a printable **helical Savonius blade**.
Defaults stay conservative; opt into a profile for the researched gain.

## Comparison table (from the verified synthesis)

| Geometry | Typical Cp | Optimal TSR | Self-start | Durability (creek) | DIY-buildable |
|---|---|---|---|---|---|
| Conventional Savonius | 0.12–0.19 | 0.7–1.0 | Excellent | High (blunt, drag) | Easy |
| **Optimized Savonius** (arc/AR/overlap, end plates) | **0.19–0.25** | ~0.8 | Excellent | High | Easy–Moderate |
| **Helical/twisted Savonius** | ~0.18–0.25 | ~0.8 | Excellent (no dead angle) | High + self-shedding | Moderate |
| Cambered-hydrofoil / V-profile Savonius | 0.18–0.26 (CFD) | 0.78–0.8 | Good–Excellent | High | Moderate–Hard |
| Hybrid Savonius–Darrieus | ~0.25–0.35 | ~1–2 | Good (dead band shrunk) | Moderate–High | Moderate |
| Darrieus / H-rotor | 0.29–0.40 | 1.5–3.5 | Poor at low speed | Moderate (thin-LE erosion) | Moderate |
| Diffuser/shroud (DAWT) | up to ~0.42 ducted (~2.5×, blockage-inflated) | rotor-dependent | inherits rotor | **Low** (debris clog/foul) | Hard |
| Axial propeller | 0.35–0.45 | 4–7 | Poor at low speed | Moderate (LE erosion) | Hard |
| FIV/VIV/VIVACE, flapping foil | n/a (lab/CFD) | n/a | onset ~0.2 m/s, tiny net power | Unproven | Not yet |

## Caveats worth remembering

- **CFD optimism:** the 0.26 hydrofoil Cp, 0.415 ducted Cp, and 66.8% flapping-foil
  efficiency are simulations; real builds land lower. Swept-area efficiencies that
  exceed the Betz limit (0.593) are defined differently and aren't comparable to Cp.
- **Shroud numbers are tank-inflated;** open-creek gain is smaller and comes with a
  debris/fouling maintenance burden.
- **Hybrid's +9.9% Cp is one config;** the reliable benefit is self-start + ripple.
- **The durability study is tidal (2–4 m/s);** its cavitation/leading-edge emphasis
  does **not** transfer to a low-speed drag Savonius.
- **Almost no source reports true months-long unattended field endurance** for a
  small DIY rotor — durability conclusions are extrapolated from larger tidal work
  and erosion physics, not directly comparable creek trials.

## Open questions (good next experiments)

1. Measured (not CFD) Cp and multi-month endurance of an optimized helical or
   cambered Savonius at 0.4–1.2 m/s in a real debris-laden creek, including
   bearing/seal wear and fouling-driven Cp decay.
2. True open-channel (blockage-corrected) shroud multiplier — does the net gain
   survive the added clogging/fouling maintenance?
3. Trash-rack / blockage-ratio / blade-edge geometry that minimizes jamming while
   preserving self-start torque — and how much Cp that costs.
4. Low-cost DIY materials/coatings (HDPE/UHMW, epoxy-glass, antifouling) that best
   resist sediment abrasion, biofouling, and fatigue at this scale.

## Sources

1. Vertical-axis hydrokinetic turbines review — sciencedirect.com/science/article/pii/S235248472500695X ✅
2. Savonius blade-profile CFD (U/V/W) — sciencedirect.com/science/article/abs/pii/S0029801821009926 ✅
3. Cambered-hydrofoil Savonius (Ocean Eng. 292, 2024) — sciencedirect.com/science/article/abs/pii/S0029801823029451 ✅
4. Hybrid Savonius–Darrieus — sciencedirect.com/science/article/pii/S235248471930962X ✅
5. Optimized semicircular Savonius (Renewable Energy 200, 2022) — sciencedirect.com/science/article/abs/pii/S0960148122015142 ✅
6. Cascade diffuser-augmented rotor (Cp 0.415) — sciencedirect.com/science/article/abs/pii/S0960148123005219 ✅
7. Flanged diffuser (wind-lens flange effect) — sciencedirect.com/science/article/abs/pii/S0960148118302441 ✅
8. Wind-lens / water-lens (~2.5×) — researchgate.net/publication/312564963 ✅ (generic 2–5× ❌ refuted)
9. VIVACE (vortex-induced vibration) — asmedigitalcollection.asme.org/.../471896 ✅
10. Flow-induced-vibration harvester comparison — sciencedirect.com/science/article/abs/pii/S0960148121018565 ✅ (one sub-claim ❌ refuted)
11. Flow-induced oscillation at 0.2 m/s — sciencedirect.com/science/article/abs/pii/S0960148123007437 ✅
12. Tandem flapping-hydrofoil optimization — sciencedirect.com/science/article/abs/pii/S0029801824020110 ✅
13. Tidal-blade erosion mechanisms (Eng. Failure Analysis, 2025) — sciencedirect.com/science/article/pii/S1350630725007861 ✅
14. Field-testing of model helical-bladed hydrokinetic turbines — sciencedirect.com/science/article/abs/pii/S0960148118304609

**Refuted (do not cite as fact):** Gorlov helical Cp ~0.45 [1]; generic wind-lens
2–5× multiplier [8]; "fluttering foil ranks third among FIV harvesters" [10].

*Full run: 25 claims verified (3 votes each) → 22 confirmed, 3 refuted, 0 unverified.*
