# Rotor geometry research — maximizing Cp *and* surviving the creek

This is a synthesis of a multi-source, adversarially-verified literature pass on
experimental/optimized hydrokinetic rotor geometries, scoped to our goal: high
power coefficient (Cp) at **low creek speeds (~0.4–1.2 m/s)** in a **small,
self-contained, vertical-shaft unit** that must run **months unattended in
debris-laden water**. Claims marked ✅ passed 3-vote adversarial verification;
claims marked ⚠️ are reported by a source but were **not** verified in this pass
(the verification run was cut short by a usage limit) — treat those as leads, not
settled facts.

## The core tension

The geometries that maximize Cp and the ones that survive an unattended creek
pull in opposite directions:

- **Lift-type rotors** (Darrieus/H-rotor, axial propellers, thin hydrofoils) reach
  higher Cp but at **high tip-speed ratios**, generally **don't self-start**, and
  have thin, erosion-/debris-prone leading edges.
- **Drag/hybrid rotors** (Savonius family) sit lower on Cp but are blunt,
  **self-starting**, direction-agnostic, low-rpm, and debris-tolerant.

✅ **Savonius Cp ≈ 0.12–0.25 at TSR ≈ 0.35–1.0; Darrieus Cp ≈ 0.29–0.40 but only
at TSR ≈ 1.5–3.5.** [1] For an unattended creek where self-starting and robustness
matter more than peak efficiency, that points at an *optimized* Savonius — and the
research says "optimized" is worth a lot.

## (1) How to make a Savonius much better without losing its toughness

The classic semicircular Savonius is mediocre, but geometry tweaks nearly **double**
its Cp while keeping the blunt, self-starting, debris-shedding character:

- ✅ **Blade cross-section is the biggest lever.** A conventional semicircular
  scoop peaks at **Cp 0.166 @ TSR 0.78**; reshaping the blade lifts it. In one CFD
  study a **V-shaped** profile gave the best Cp 0.184 (U 0.172, W 0.160) vs 0.166
  conventional, all at TSR 0.78. [2]
- ✅ **A cambered *hydrofoil* Savonius blade roughly DOUBLES Cp at low speed:**
  **Cp ≈ 0.26 at a 140° camber angle vs 0.13 for the conventional design at
  0.4 m/s** (and 0.21 at 105°), at overlap ratio 0.15. [3][5] This is the single
  most striking result for our low-speed case.
- ✅ **Optimized "classic" geometry** (blade **arc angle ≈ 166°**, **aspect ratio
  1.4–2.0**, **overlap ratio 0.15–0.2**) reaches **Cp 0.194 at TSR 0.8**. [5]
  These are cheap, buildable parameters — pick them and you gain ~15–20% for free.
- ✅ **Self-starting improves with solidity; torque ripple falls as you add
  blades/stages.** [1] (Helical/twisted blades and multi-stage phase-shifting are
  the standard way to smooth torque and guarantee self-start at any angle — the
  twist also sheds debris, though this pass didn't return a clean Cp number for
  helical specifically. A broad "Gorlov helical reaches Cp ~0.45" claim was
  **refuted** 1-2 in verification, so don't count on helical for a Cp *gain* — its
  value is self-start, smoothness, and durability, not peak Cp.)

**Hybrid Savonius–Darrieus** — a Darrieus (for Cp) with a Savonius core (for
self-start):
- ✅ Hybrid yields **~9.9% higher Cp than a Darrieus alone**, [4]
- ✅ **~15.9% higher average torque with less fluctuation**, [4] and
- ✅ **much better self-starting** — a lone Darrieus makes negative (stalling)
  torque over three azimuth ranges; the hybrid only one. [4]

## (2) Flow augmentation (shrouds/diffusers) and axial blades

- ✅ A **diffuser-augmented (shrouded) rotor** designed by a cascade-based method
  hit **Cp 0.415 — but normalized by the diffuser's *outer* area**, not the rotor
  swept area. [6] That normalization is the catch: a shroud's honest win is more
  power *per rotor*, at the cost of a much bigger structure.
- ⚠️ Reported diffuser gains: a flanged "wind-lens" flange alone gave **+28% Cp**
  (at TSR 5.6, 10° flange), [7] and wind-lens shrouds are claimed at **2–5×** a
  bare rotor (water-lens ~2.5×) — ⚠️ unverified here. [8] Ties directly to our
  [BOX_AND_DUCT.md](BOX_AND_DUCT.md) design.
- Axial propellers reach the highest bare-rotor Cp (~0.35–0.45) but need higher
  flow to self-start and have erosion-prone blades — better suited to a *ducted*
  unit than an open drop-in.

## (3) Frontier / experimental (worth watching, not yet buildable)

All ⚠️ **unverified in this pass** — promising leads, but treat as research-stage:

- **Oscillating / flapping hydrofoils:** an optimized *tandem* flapping foil
  reported ~66.8% energy-extraction efficiency in CFD, aimed at ~1 m/s currents. [12]
- **Vortex-induced vibration (VIVACE):** reported ~98 W/m³ at ~1.03 m/s and
  operation across ~0.4–1.1 m/s — squarely our speed band. [9]
- **Flow-induced-oscillation harvesters** with passive turbulence control claimed
  to generate down to **0.2 m/s**, below the usual turbine floor. [11]
- Among flow-induced-vibration types, reviews rank **galloping** (high power) and
  **VIV** (high efficiency) differently, with **wake-induced vibration** proposed
  as a best-of-both. [10]

These have **no moving airfoil-free simplicity, no field-proven durability, and no
DIY path** yet. Keep an eye on them; don't build your creek unit around them.

## (4) Durability — the "withstand the long term" half

Verification of the durability sources was cut short, so these are ⚠️ **reported,
unverified** — but they match established tidal-turbine field experience:

- ⚠️ Dominant blade-degradation mechanisms are **cavitation, abrasion, and
  suspended-sediment impact**, hitting both structure *and* power over time. [13]
- ⚠️ **Leading-edge erosion is the most performance-critical** location — it
  wrecks the flow behavior that lift blades depend on. [13] → the thin,
  high-Cp lift blades are exactly the ones that degrade; blunt Savonius scoops
  have far less to lose.
- Field failures on small units are dominated by **floating debris/log strikes and
  clogging** (from the debris-mitigation literature) — which is why a blunt,
  self-clearing rotor + an upstream **trash rack** matters more than a few points
  of Cp. See [SITING.md](SITING.md) and [SAFETY.md](SAFETY.md).

## Ranked recommendation for a buildable self-contained creek unit

1. **Optimized Savonius — the pick.** Cambered/hydrofoil (or ≥160° arc) blades,
   **overlap 0.15–0.2, aspect ratio 1.5–2.0, end plates**, ideally **helical**.
   Buys ~0.19–0.26 Cp (vs ~0.16 conventional) *and* keeps self-start, low rpm,
   direction-agnosticism, and debris tolerance. Best Cp-per-durability for our case.
2. **Add a shroud/diffuser** if you want more from the same rotor — real gains, but
   a bigger structure; folds into the [box/head design](BOX_AND_DUCT.md).
3. **Hybrid Savonius–Darrieus** if you have brisker, cleaner flow and want more Cp
   while keeping self-start — more complex to build.
4. **Watch, don't build:** flapping-foil / VIV / galloping harvesters. Exciting at
   low speed on paper; not field-proven or DIY-ready.

**What we did in the code:** `rotor.py` now carries these as selectable
`SAVONIUS_PROFILES` (conventional / optimized / hydrofoil) with Cp values from the
sources above, and `cad/` includes a **helical, cambered Savonius** blade so the
recommended geometry is actually printable. Defaults stay conservative; opt into
`hydrofoil` for the researched upgrade.

## Comparison table

| Geometry | Typical Cp | Optimal TSR | Self-start | Durability (creek) | DIY-buildable |
|---|---|---|---|---|---|
| Conventional Savonius | ~0.16 [2] | ~0.8 | Excellent | Excellent (blunt) | Easy |
| **Optimized Savonius** (arc 166°, AR 1.5–2, overlap 0.15–0.2, end plates) | **~0.19** [5] | ~0.8 | Excellent | Excellent | Easy–moderate |
| **Hydrofoil/cambered Savonius** | **~0.21–0.26** [3] | ~0.8–1.0 | Very good | Very good | Moderate |
| Helical Savonius | ~0.16–0.20 (Cp≈conv.) | ~0.8–1.0 | Excellent | Excellent (sheds debris) | Moderate |
| Hybrid Savonius–Darrieus | ~0.32–0.44 (+~10% vs Darrieus) [4] | ~1.5–2.5 | Good (Savonius-assisted) | Moderate | Hard |
| Darrieus / H-rotor | ~0.29–0.40 [1] | ~1.5–3.5 | Poor | Moderate (thin blades) | Hard |
| Axial propeller | ~0.35–0.45 | ~4–6 | Poor–fair | Low (leading-edge erosion) | Hard |
| Shrouded/diffuser rotor | rotor Cp ×~1.3–2.5 ⚠️ [7][8] | (rotor-dependent) | inherits rotor | adds a big structure | Moderate–hard |
| Flapping foil / VIV (frontier) ⚠️ | lab-stage [9][12] | n/a | n/a | unproven | Not yet |

## Sources

1. Recent advances in vertical-axis hydrokinetic turbines (review) — sciencedirect.com/science/article/pii/S235248472500695X ✅
2. Savonius blade-profile CFD (U/V/W vs conventional) — sciencedirect.com/science/article/abs/pii/S0029801821009926 ✅
3. Cambered-hydrofoil Savonius blade — sciencedirect.com/science/article/abs/pii/S0029801823029451 ✅
4. Hybrid Savonius–Darrieus hydrokinetic rotor — sciencedirect.com/science/article/pii/S235248471930962X ✅
5. Optimized Savonius (arc/AR/overlap) — sciencedirect.com/science/article/abs/pii/S0960148122015142 ✅
6. Cascade-based diffuser-augmented hydrokinetic rotor (Cp 0.415, outer-area normalized) — sciencedirect.com/science/article/abs/pii/S0960148123005219 ✅
7. Flanged diffuser (wind-lens) flange effect (+28%) — sciencedirect.com/science/article/abs/pii/S0960148118302441 ⚠️
8. Wind-lens / water-lens (2–5×) — researchgate.net/publication/312564963 ⚠️
9. VIVACE (vortex-induced vibration) — asmedigitalcollection.asme.org/.../471896 ⚠️
10. Flow-induced-vibration harvester comparison — sciencedirect.com/science/article/abs/pii/S0960148121018565 ⚠️
11. Flow-induced-oscillation at very low speed (0.2 m/s) — sciencedirect.com/science/article/abs/pii/S0960148123007437 ⚠️
12. Tandem flapping-hydrofoil optimization — sciencedirect.com/science/article/abs/pii/S0029801824020110 ⚠️
13. Tidal-blade erosion mechanisms & leading-edge criticality — sciencedirect.com/science/article/pii/S1350630725007861 ⚠️
14. Field-testing of model helical-bladed hydrokinetic turbines — sciencedirect.com/science/article/abs/pii/S0960148118304609

*Verification note: 25 extracted claims were adversarially checked (3 independent
skeptic votes each); 12 confirmed, 1 refuted, and 12 (mostly frontier/durability)
left unverified when the run hit a usage limit. The Savonius/hybrid/diffuser Cp
numbers above are the confirmed set; frontier and durability items are flagged ⚠️.*
