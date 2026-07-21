# Self-contained all-in-one unit — a box with a handle you set in the creek

> "By portable I just mean the box has a handle on top. I want a fully
> self-contained, almost plug-and-play unit."

That's the cleanest form of the whole project, and the **vertical-axis Savonius is
what makes it possible.** Because the shaft is vertical, the whole machine is a
vertical stack in one housing: rotor at the bottom (wet), everything else stacked
above the waterline (dry). No cable, no separate shore box — carry it, set it in
the stream, and the outlets on top are live.

![Self-contained unit](images/self_contained.png)

Model it for your creek with:

```bash
python -m scripts.self_contained --box-dia 0.30 --box-height 0.65 --submerged 0.30 --figs
```

## How it's laid out

```
   ┌─ handle ─┐
   │ outlets  │   DRY  — USB / USB-C / 12 V, a little charge display
   │ battery  │  (the "freeboard": the part standing above the water)
   │ generator│   DRY, sealed — magnetically coupled to the rotor below
   ~~~~~~~~~~~~~  waterline
   │  rotor   │   WET — Savonius in the flow (self-starts, any direction)
   └─ base ───┘   weighted / staked so the current can't move it
```

The rotor spins a set of magnets; a matching set on the generator shaft picks that
up **through the sealed bulkhead** (a magnetic coupling — no shaft hole, nothing to
leak). The generator, battery, charge controller, and outlets all live in the dry
upper box.

## Plug-and-play means the electronics manage themselves

- **Self-starting rotor** (Savonius) — no aiming, no manual spin-up, works whatever
  direction the creek runs.
- **Automatic charge controller** — the moment there's flow it charges the internal
  battery; no tuning.
- **Battery always ready** — outlets are live even before the creek does much,
  because you draw from the battery, not the rotor directly.
- **Sealed, protected outputs** — USB/12 V on the dry top, ideally behind a splash
  cover.

Leave home with it charged, set it in the creek, plug in. That's the experience.

## The two things that actually decide if it works

**1. Geometry — does the rotor fit, and does the top stay dry?**
A carriable box is small, so the rotor is small, so the power is small. For a 30 cm
box, ~30 cm deep in a healthy 0.8 m/s creek, the model gives a ~0.065 m² rotor →
**~2 W** (≈45 Wh/day, buffered). The box needs the creek to be at least as deep as
the submerged section, while the top stays above water (the "freeboard") so the
outlets are dry. Want more power? A bigger box, a deeper/faster spot, or the
built-in-head **[box design](BOX_AND_DUCT.md)** — same honest v³ physics.

**2. Stability — will the current push it over or downstream?**
This is the real catch of a free-standing box. The flow exerts a drag force
`½·ρ·Cd·A·v²` on the submerged body — ~32 N for that example, and it grows with v².
A tall box must out-weigh that in both **sliding** (bed friction vs. drag) and
**tipping** (restoring moment vs. overturning moment). The model sizes the base
ballast; for the example it's a modest **+5 kg** in the base, but a brisk creek
needs much more. The fix is a **wide, weighted base plus one stake or tether** —
that turns it into "set-and-forget."

## Two variants

- **Top-stays-dry (recommended, shown above):** outlets live while it runs. Needs
  the creek deep enough to submerge the rotor but not the outlets.
- **Fully submerged, sealed:** the whole box goes under, charges its internal
  battery, and you lift it out to use the outlets. More rugged and hide-able, but
  not "plug-and-play while running," and it's very buoyant if it holds air (see the
  ballast math in [BOX_AND_DUCT.md](BOX_AND_DUCT.md)).

## What's modeled

`creekturbine/selfcontained.py` (tested in `tests/test_selfcontained.py`):

- `SelfContainedUnit` — box geometry → rotor that fits, power, freeboard, min water
  depth
- `drag_force_n` — the current's push on the submerged body (`½·ρ·Cd·A·v²`)
- `hold_mass_for_sliding_kg` / `hold_mass_for_tipping_kg` /
  `required_base_ballast_kg` — how heavy/anchored the base must be
