# Magnetic coupling — sealing the wet→dry shaft crossing

The turbine is wet; the generator and electronics are dry. Something has to carry
torque across that boundary. A shaft seal (lip/mechanical) is the classic answer —
and the classic **#1 leak point** on any submerged machine. A **magnetic coupling**
removes the problem entirely: it transmits torque **through a solid, unbroken
wall** with nothing penetrating it.

```
   generator shaft ──┬── [ dry magnet disc ]        DRY
                     │        ↕ magnets            (sealed housing)
   ══════════════════╪══════════════════════  sealed non-magnetic bulkhead
                     │        ↕ magnets            WET
   rotor shaft ──────┴── [ wet magnet disc ]      (in the water)
```

Two coaxial discs each carry a ring of magnets in **alternating polarity**. Turn
the wet disc and the dry disc follows in lock-step. **Bonus safety feature:** if
you overload it (a jam, a flood), the magnets simply **slip** past each other
instead of breaking anything — a built-in torque limiter.

Size it for your rotor with:

```bash
python -m scripts.mag_coupling            # sizes to the rotor torque from config.py
python -m scripts.mag_coupling --gap 2 --magnet-dia 20 --grade N52
```

## How much coupling you need

The torque a magnetic coupling transmits is, to first order:

> **T_max ≈ τ · A_active · R_mean**

— magnetic shear stress τ, total magnet face area A_active, and mean radius R_mean.
For NdFeB at a small gap, τ lands around **10–40 kPa**. For our default rotor
(~2 N·m at 40 rpm), a coupling of **12 × Ø15×6 mm N42 magnets per disc on a 110 mm
ring at a 3 mm gap** gives ~**4.2 N·m** — holding the rotor torque with a 2× margin
(τ ≈ 36 kPa, effective field 0.87 T). The model is in `creekturbine/magnetics.py`.

⚠️ **Treat the number as a sizing estimate to bench-test, not a guarantee.**
Magnetics is gap-sensitive and the shear coefficient is approximate; build it and
confirm the slip torque before you rely on it.

## ⚠ The axial pull nobody warns you about

The same magnets that make torque **attract the two discs toward each other with
a constant ~350–400 N (~35–40 kg)** for the default coupling
(`AxialMagCoupling.axial_force_n()`, printed by `scripts.mag_coupling`). This
force rides on the **shaft bearings of both discs** — the non-magnetic bulkhead
between them feels none of it — and it will grind plain radial bearings flat in
weeks. **Fit thrust bearings (or angular-contact bearings) on both shafts**,
rated ≥1.5× the printed pull, and make sure the shaft retention (circlips/collars)
carries the load without letting a disc creep into the bulkhead.

## Design levers (in order of impact)

1. **Keep the GAP small.** Field falls off as ~`t/(t+gap)`, so a thick bulkhead
   quietly kills the coupling. Use a **thin, strong, non-magnetic** bulkhead
   (2–3 mm polycarbonate, fiberglass, or aluminium/316 stainless — *not* ordinary
   steel, which shorts the flux). Practical tip: **don't print the bulkhead** —
   it's a flat disc, so **cut it from 3 mm PC/acrylic/FR4 sheet** and use the
   STEP file as the drill template.
2. **Bigger mean radius** — torque scales linearly with R, so spread the magnets
   out on a larger ring.
3. **More / bigger magnets** — active area scales the torque directly.
4. **Stronger grade** — N52 > N42 > N35; ferrite works but needs many more.

## Building it

- Print **two** `mag_coupling_disc` parts (`cad/`). One goes on the wet rotor
  shaft (magnets facing **up** to the bulkhead), one on the dry generator shaft
  (magnets facing **down**).
- Press cylindrical magnets into the pockets in **alternating polarity**
  (N, S, N, S …) — the two discs' rings must mirror each other so N faces S.
  A dab of epoxy keeps them seated; **mind your fingers**, these snap together hard.
- Set the running gap with the bulkhead thickness + a small clearance each side.
- Corrosion: the **wet** disc's magnets must be properly potted — fill the
  pockets with epoxy **and lay a thin continuous epoxy/glass cover coat over the
  whole magnet face**. A dab of glue is not marine sealing; NdFeB rusts through
  pinholes. Inspect seasonally.

See the bulkhead and dry-stack layout in [SELF_CONTAINED.md](SELF_CONTAINED.md) and
[BOX_AND_DUCT.md](BOX_AND_DUCT.md).

## What's modeled

`creekturbine/magnetics.py` (tested in `tests/test_magnetics.py`):

- `magnetic_pressure` / `gap_field` / `shear_stress` — the underlying magnetics
- `AxialMagCoupling` — a two-disc coupling → `max_torque()` and `holds(torque)`
- `magnets_needed(...)` — the magnet count to carry a torque with a safety margin
