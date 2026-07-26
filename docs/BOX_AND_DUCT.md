# The enclosed underwater box (ducted / low-head turbine)

> "Can I have an enclosed, mostly air-filled box underwater — dry inside — that
> lets water flow in through one part, past a turbine, and out?"

**Yes.** You've described a *ducted turbine with a dry nacelle*, which is how a
lot of real hydro gear is built. This page makes the idea quantitative. Model it
for your creek with:

```bash
python -m scripts.box_turbine --static-head 0.3 --throat 0.05 --air-volume 0.08
```

## The two things a box buys you

1. **A dry generator.** Routing water through only a defined channel lets the
   generator and electronics live in the air-filled part. Keeping the generator
   dry is the single hardest problem in the whole project, so this is a real win.
2. **Flow control / augmentation.** A shaped inlet nozzle + flared outlet
   (diffuser) can pull more flow through the turbine than a bare rotor of the
   same size — the "shrouded / diffuser-augmented" turbine, worth roughly
   1.3–2.5× for a good one. That's the `--diffuser` knob.

## The catch, and the thing that makes it actually worth it

A creek's **speed is worth almost no head**: `v²/2g` is only ~3.3 cm at 0.8 m/s.
So a box wrapped around a purely *kinetic* rotor gains little on its own — the
model shows ~4 W for a 0.05 m² throat at 0.8 m/s.

The unlock is **building in a real elevation drop** (head, `H`). Put the inlet a
little higher/upstream and the outlet lower, and you become a **low-head
turbine**, where power is `P = ρ·g·Q·H·η`. The numbers jump:

| Box (0.05 m² throat, 0.8 m/s creek) | Throat speed | Flow | ~Electrical |
|---|---|---|---|
| Purely kinetic (0 m drop) | 0.68 m/s | 34 L/s | ~4 W |
| **With a 0.30 m built-in drop** | 2.17 m/s | 109 L/s | **~140 W** |

A modest drop is worth **~30×** the kinetic-only box for the same opening. Head,
not velocity, is where a creek gives real power.

**But be honest about what "building in a drop" means.** You get head by
*diverting* water from an upstream point to a lower outlet (classic micro-hydro),
or by pooling it behind a small weir. That is a bigger intervention than a
drop-in kinetic rotor and carries real consequences:

- You need enough natural **slope** to find 0.2–0.5 m of drop over a sensible
  distance (many creeks have it; measure with a level and a stick).
- Diverting/pooling flow has **stronger permit and fish-passage implications**
  than a hydrokinetic rotor — see [SITING.md](SITING.md#4-permits--neighbors-do-this-before-you-build).
  Keep it small, keep it removable, keep a path for water and wildlife.
- More power means a **bigger battery, a real dump load, and heavier wiring** —
  re-read [SAFETY.md](SAFETY.md).

## Crossing the wet/dry wall — use a magnetic coupling

The turbine is wet; the generator is dry; something must connect them through the
box wall. Two ways:

- **Shaft seal** (lip/mechanical seal): cheap, but a wear item and the #1 leak
  point on any submerged machine.
- **Magnetic coupling** (recommended): the wet rotor carries magnets that drive a
  matching magnet set on the dry generator shaft *through* a solid, unbroken wall.
  **No penetration, nothing to seal, nothing to leak.** For a DIY box this is the
  elegant answer; size it for the torque from `scripts.size_turbine`.

## If you fully submerge it: buoyancy is the enemy

An air-filled box wants to **float, hard**. Even a small ~0.08 m³ air pocket lifts
with ~785 N (~80 kg). To sink and hold a submerged box you need serious ballast
(the model: ~180 kg of concrete for that case, with a safety factor), plus:

- A **vent/snorkel to the surface** — a sealed air pocket slowly dissolves into
  the water and the box floods over weeks.
- Anchoring to **bed and bank** against currents trying to lift/roll it.

**Simpler recommendation:** unless you need it hidden or the creek is deep, don't
fully submerge an air box. Keep the **dry generator housing at/above the water
surface** and duct the water through/under it. You get every benefit (dry
generator, ducted flow, optional head) without the buoyancy and air-loss
headaches.

## This changes the turbine you'd want

The Savonius wins in *open* water. Once flow is confined in a duct, its perks
(self-start, direction-agnostic) stop mattering and you'd switch to a higher-
efficiency type that suits a channel:

- a **ducted axial propeller** (the duct fixes its weaknesses), or
- a **crossflow / Banki turbine** — water enters, crosses the blades twice, and
  exits: simple to build, debris-tolerant, and a natural fit for a "water enters
  here, leaves there" box. If you go the small-head route, this is the pick.

## What's modeled here

`creekturbine/ducted.py` (tested in `tests/test_ducted.py`):

- `velocity_head(v)` — why a creek's speed is worth so little head
- `low_head_power(Q, H, η)` — the micro-hydro bedrock equation
- `throat_velocity(H, Cd)` — head → flow through the throat (Torricelli + losses)
- `DuctedBox` — a box with throat area, static head, diffuser gain → flow & power
- `buoyancy_force_n()` / `ballast_mass_kg()` — how much ballast a submerged air box needs
