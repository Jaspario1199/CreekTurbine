# The funnel — making a mellow, shallow creek charge a laptop

> "Couldn't a funnel let 6 inches do the trick, because it's almost funneled into
> more?"

**Yes — and this is the single best move for a mellow, shallow creek.** Wall the
creek into a **converging chute** so the flow squeezes through a narrow throat at
the rotor. It speeds up, and because power ∝ v³ the payoff is huge. Model it:

```bash
python -m scripts.funnel --up-vel 0.4 --up-width 1.5 --up-depth 0.3 \
                         --throat-width 0.4 --throat-depth 0.15
```

## Why it works — you tap the creek's *flow*, not just its speed

Continuity: `A₁·v₁ = A₂·v₂`. Squeeze the same water through a smaller opening and
it accelerates. The deeper insight is what you're actually harvesting:

> **P_available = ½·ρ·A_throat·v_throat³ = ½·ρ·Q·v_throat²**

Because `A·v = Q` (the creek's flow rate), the funnel routes the **whole creek's
discharge Q** through the rotor at an elevated speed. A lazy creek that's useless
to a small bare rotor still carries a lot of *water per second*; the funnel turns
that flow into power. A bare rotor sips; a funnel drinks.

## The honest ceiling: critical velocity

An **open-channel** constriction can't accelerate flow past the **critical
velocity** at the throat depth:

> **v_critical = √(g · y)**

Narrow it further and the flow **chokes** — it just ponds up upstream instead of
going faster. The happy accident: at **6 inches (0.15 m)** that ceiling is
**√(9.81 × 0.15) ≈ 1.2 m/s**, which is right where a 6-inch rotor starts charging
a laptop. So the funnel's natural cap in shallow water lands exactly where you need
it.

## Your numbers (a mellow creek, funneled into 6 inches)

A **0.40 m/s** creek, **1.5 m wide × 0.30 m deep** (Q ≈ 180 L/s), funneled to a
**0.40 × 0.15 m** throat:

| | Bare rotor | **Funnelled rotor** |
|---|---|---|
| Velocity at rotor | 0.40 m/s | **1.21 m/s** (choked at critical, 3.0×) |
| Power | 0.2 W | **5.6 W** (~28× — the v³ law) |
| Per day | ~4 Wh | **~101 Wh/day → ~1.4 laptop charges** |

So a funnel turns a mellow, 6-inch creek from "charges nothing" into "tops up a
laptop and your phones every day." That is the whole game.

## The catches (be honest before you dig)

- **It's a small weir, not a drop-in.** To stop water bypassing, the funnel walls
  must reach **both banks** — you're building a low wing-wall structure spanning
  the creek, not dropping in a box.
- **It ponds the upstream level.** The choked flow backs water up (that's where the
  speed-up energy comes from). Fine on a steep reach with room; a problem if it
  floods something upstream.
- **Bigger permit / fish-passage footprint.** Walling and ponding a creek edges
  toward "diverting" it — check water rights and fish rules first
  ([SITING.md](SITING.md#4-permits--neighbors-do-this-before-you-build)). Leave a
  fish/overflow bypass.
- **Debris clogs a throat faster** — an upstream **trash rack** is mandatory
  ([the `trash_rack` part](../cad/README.md)).
- **To go faster than critical**, you need a **closed, pressurized duct with real
  head** (a pipe from an upstream pool) — the [box-with-head design](BOX_AND_DUCT.md),
  not an open funnel.

## Design tips

- Make the throat roughly the **rotor size** so the rotor intercepts the sped-up
  flow instead of letting it bypass.
- A **gentle contraction** (long, smooth wing walls, ~a 3:1 length:offset taper)
  loses less energy than an abrupt one.
- **Deepen the throat if you can** — critical velocity rises with √(depth), so
  ponding to a slightly deeper throat raises the ceiling and the power.
- Feed the resulting multiplier back into the sizing: set
  `VELOCITY_AUGMENTATION = throat_velocity / creek_velocity` in `config.py` and
  re-run `size_turbine`.

## What's modeled

`creekturbine/funnel.py` (tested in `tests/test_funnel.py`):

- `critical_velocity` / `froude_number` — the open-channel ceiling
- `FunnelIntake` — approach + throat → throat velocity (with choke), power, and the
  gain vs a bare rotor
- `throat_width_for_velocity` — size the throat for a target speed (capped at critical)
