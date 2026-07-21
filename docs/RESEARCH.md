# Research — the physics behind the numbers

The toolkit is deliberately built on textbook fluid mechanics, not vendor claims.
This page records *why* the equations and default coefficients are what they are,
so you can push back on them for your own site.

## Core equations

- **Kinetic power flux.** A stream of density ρ moving at speed v carries kinetic
  energy ½mv²; the mass flow through area A is ρAv, so the power is
  **P = ½·ρ·A·v³**. This is the same equation used for wind, with water's density
  (~1000 kg/m³) instead of air's (~1.2). Water is ~800× denser than air, which is
  why a slow, small water rotor rivals a big wind turbine — but the **v³** term
  means slow water is still stingy.
- **Betz limit.** An open (unshrouded) rotor cannot extract more than
  **16/27 ≈ 59.3%** of that kinetic power, because the water it slows must still
  move on to make room for the water behind it. Derived by Betz (1919) for a
  actuator-disc in an unbounded flow. It is a hard ceiling on Cp; every real
  number in this repo sits well below it. (A *shroud/diffuser* can beat the bare-
  rotor Betz value for a given swept area by drawing in extra flow — that's why
  augmentation is modeled separately.)
- **Power coefficient Cp.** The captured fraction, `P_rotor = Cp · P_available`.
- **Tip-speed ratio TSR = ωR/v.** Cp peaks at a rotor-specific TSR.

## Default coefficients (conservative on purpose)

| Quantity | Default | Why |
|----------|---------|-----|
| Cp, Savonius | 0.18 | Drag-type VAWTs typically test at Cp ≈ 0.15–0.25; lab-optimized profiles reach ~0.25–0.30. A DIY cut-pipe rotor lives at the low end — 0.18 is honest, not rosy. |
| Optimal TSR, Savonius | ~0.9 | Drag rotors peak just below TSR = 1 (the scoops can't outrun the water). |
| Cp, axial | 0.35 | Small hydrokinetic propellers report Cp ≈ 0.35–0.45; good tidal rotors approach the mid-0.4s. 0.35 is a safe DIY assumption. |
| Optimal TSR, axial | ~5 | Lift-type rotors run fast (TSR 4–7). |
| Generator efficiency | 0.65 | A small PMA at low rpm plus a diode rectifier: 60–75% is realistic; big claims are for the rated point, not creek rpm. |
| Drivetrain efficiency | 0.90 | Bearings, seal drag, coupling/belt. |
| Surface→mean velocity | 0.85 | Standard correction: a surface float reads faster than the depth-averaged mean in a small natural channel. |

The result — an end-to-end "water→battery" efficiency around **10–11%** for a
Savonius, **~20%** for an axial — is deliberately on the pessimistic side so real
builds *beat* the estimate rather than disappoint. Tune the values in
`config.py` if you have measured data for your own parts.

## Why hydrokinetic (no dam)

Conventional micro-hydro multiplies **head × flow** and wants a vertical drop
(a pipe/penstock from higher ground). A flat creek has almost no head, so the
kinetic route — an "underwater wind turbine" — is the honest match. It's also the
low-impact, usually-more-legal choice: no dam, no diversion, removable.

## Good places to read further

- Betz's law and actuator-disc theory (any wind-energy textbook; the derivation
  is identical for water).
- Savonius rotor performance studies (aspect ratio, overlap ratio, end plates,
  2- vs 3-bucket) — these set the geometry defaults in `cad/params.py`.
- Hydrokinetic / micro-hydro guides from small-turbine communities for the
  generator-matching, rectifier, and dump-load practice.
- Your local water authority and fish & wildlife office for the rules that
  actually apply to your creek.

*(This file intentionally cites principles rather than specific pages/prices,
which drift. The equations are stable; verify coefficients against your own
bench measurements in Phase 2.)*
