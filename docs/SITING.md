# Siting — measure first, then make the water faster

Because power scales with **velocity cubed**, the two highest-leverage things you
can do cost nothing: **measure honestly**, then **put the rotor where (or make
the water) fastest**.

## 1. Measure your creek (20 minutes, ~$0)

Run `python -m scripts.measure_creek` for the interactive version. The field
procedure:

1. **Pick a reach.** A straight, roughly uniform stretch a few meters long — not
   a still pool, not a waterfall. The best turbine spot is usually the fastest,
   narrowest, shallowest **riffle** you can find.
2. **Width.** Measure the water-surface width (m).
3. **Depth.** Measure depth at several points across the width and **average**
   them (m). Use the average, not the deepest hole.
4. **Velocity — the float method.** Mark two lines a known distance apart (say
   5 m). Drop a floating stick/orange just upstream so it's up to speed, then
   time it between the lines. Average 3–5 runs. Multiply the surface speed by
   **0.85** to get the depth-averaged mean (the surface moves faster than the
   bulk).

Put the three numbers (`CREEK_VELOCITY`, `CREEK_WIDTH`, `CREEK_DEPTH`) into
`creekturbine/config.py`, then run `python -m scripts.size_turbine`.

**Measure in more than one season.** Your rotor and generator should be matched
to **low flow** (so it charges most of the year), while the *frame and anchoring*
must survive **high flow** (spring melt, storms).

## 2. Make the water faster (the v³ lever)

A bare rotor sees the open-channel speed. You can do much better by **speeding
the water up right at the rotor** — and since power ∝ v³, a modest 1.2× speed-up
is a ~1.7× power gain; 1.5× is ~3.4×.

- **Find a natural narrows.** Nature already built chutes — use them.
- **Build a chute (a "penstock" for kinetic flow).** Funnel the flow through a
  narrower cross-section at the rotor with rock, board, or sandbag wing-walls.
  Conservation of flow (`A₁v₁ = A₂v₂`) means halving the area doubles the speed.
  Set `VELOCITY_AUGMENTATION` in the config to the ratio you actually achieve.
- **Shroud / diffuser.** A duct around the rotor (a "diffuser-augmented" turbine)
  raises throughput; a good one is worth ~1.3–2× but is real engineering.

Don't over-block the natural channel. Backing water up scours the bed, floods
upstream, strands fish, and is exactly what triggers permit trouble. Keep a bare
rotor under ~25–30% of the wetted cross-section (the sizing report checks this),
and always leave a path for water and wildlife around the structure.

## 3. Anchoring, debris, and survival

- **Anchor to both the bed and the bank** so a flood can't walk the turbine
  downstream. Design the frame to be **liftable/removable** before big storms.
- **Trash rack.** Put an angled screen upstream to shed leaves and sticks — a
  clogged rotor makes no power and a jammed one can break. A Savonius shrugs off
  debris far better than a propeller, which is a big reason it's the default.
- **Silt & ice.** Keep bearings above the silt line; plan to pull the unit in a
  hard freeze.

## 4. Permits & neighbors (do this before you build)

Water in a creek is legally not yours to obstruct in most places.

- **Water rights** vary hugely by country/state (riparian vs. prior-appropriation
  in the US). Diverting or obstructing flow can require a permit even for a tiny
  turbine.
- **Environmental rules** protect fish passage, banks, and wetlands. A
  removable, low-blockage, no-dam hydrokinetic unit is the least-intrusive
  option, but **still check** with your local water authority / fish & wildlife
  office first.
- **Talk to downstream neighbors.** Changing flow or clarity, even slightly, is a
  fast way to make enemies. Keep it small, keep it removable, keep it legal.

See **[SAFETY.md](SAFETY.md)** for the electrical and mechanical hazards.
