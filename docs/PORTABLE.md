# Portable creek power station — power anywhere there's moving water

> "Could this be portable (maybe slightly heavy) to use near any creek — backyard
> or camping — with a waterproof cable to shore, a battery, and a way to switch
> sources?"

**Yes, and it's a genuinely good product concept.** You've described a portable,
battery-buffered hydro generator — like a solar power station, but it works
**24/7: at night, in rain, in shade.** That continuous, weather-proof output is
the whole reason to carry one. Model it for your creek and kit with:

```bash
python -m scripts.portable --rotor-area 0.15 --battery-wh 500 --bus 48 \
                           --cable-length 25 --cable-area 4 --burst-load 60
```

## Architecture (this is the important part)

```
  IN THE WATER                 CABLE (low-voltage DC!)      ON DRY LAND
 ┌──────────────────┐                                    ┌───────────────────────┐
 │ rotor → sealed   │   ═══ marine cable, IP68 potted ══ │ charge controller     │
 │ generator (PMA)  │   ═══ connectors, 12–48 V DC   ═══ │  (MPPT, multi-input)  │
 │ +3-phase rectifier│                                   │        │              │
 └──────────────────┘                                    │   LiFePO4 battery     │
   Savonius = drop-in-any-creek                           │        │              │
   (self-starts, ignores flow direction)                 │  USB / USB-C / 12 V   │
                                                          │  (+ inverter → 120 V) │
                                                          └───────────────────────┘
```

**Three rules that shape everything:**

1. **The in-water cable is LOW-VOLTAGE DC (12–48 V), never mains AC.** The
   generator rectifies to DC right at the unit; only safe low-voltage DC travels
   the "extension cord." Any 120/230 V AC inverter lives **on dry land, after the
   battery** — never in or near the water. This is a safety hard rule.
2. **Loads run off the battery; the turbine tops it up.** That's what makes the
   output *sustained and smooth*: full power the instant you arrive (pre-charged),
   steady even when the creek is weak or gusty, and the ability to briefly **burst**
   a load bigger than the turbine makes.
3. **Keep the battery + electronics on shore.** Only the sealed generator and the
   cable get wet — the safest, most serviceable split.

## Your "switch between sources," done right

Rather than a manual A/B switch, use a **multi-input charge controller**: the same
battery accepts the **turbine**, and optionally **solar** and a **wall/USB-C**
charger. Loads always draw from the battery, so you never notice the handoff —
the creek charges it by day and night, solar helps when sunny, and a wall outlet
tops it off before you leave home. (If you specifically want to run a device
*directly* off the turbine and bypass the battery when flow is strong, a simple
DPDT source selector can do that — but the battery-buffered path is smoother and
protects the electronics.)

## Honest power expectations (from the model)

A compact portable rotor (~0.1–0.2 m²) is small on purpose. Realistic output:

| Creek speed | ~Continuous harvest (0.15 m² Savonius) | Feels like |
|---|---|---|
| 0.4 m/s (lazy) | ~0.5 W | slow phone top-ups |
| 0.8 m/s (healthy) | ~4 W (~95 Wh/day) | phones + lights + sensors, 24/7 |
| 1.2 m/s (brisk) | ~14 W (~330 Wh/day) | + a power bank, camp fridge trickle |

The battery lets you **burst** bigger loads (e.g., a 60 W device off a 500 Wh
pack for ~8 h) — but on a weak creek the turbine may take **days** to refill that,
so treat bursts as occasional. The bread-and-butter is the *sustained* few watts
that never stop. Want real power (tens–hundreds of watts)? Combine this with the
**built-in-head "box" design** in [BOX_AND_DUCT.md](BOX_AND_DUCT.md).

## The cable — the sneaky-hard part

Volt-drop over a long low-voltage run is brutal (`loss = I²R`). The model sizes
it, and the takeaway is: **for a long run to shore, use a higher bus voltage.**
Because current scales as 1/voltage for the same power, going 12 V → 48 V cuts the
required copper by ~16× (or the loss at the same gauge). So a 48 V generator with
a step-down on land beats a 12 V one for anything beyond a few meters — the cable
matters most once you're harvesting tens of watts (a brisk creek or the head-box
design). Use **marine tinned cable** and **IP68 potted/gel connectors**; seal
every junction as if it'll be underwater, because it will be.

## Deploy-anywhere checklist

- [ ] **Sealed generator** (potted PMA) or a **magnetic coupling** so nothing can
      leak — see [BOX_AND_DUCT.md](BOX_AND_DUCT.md#crossing-the-wetdry-wall--use-a-magnetic-coupling)
- [ ] **Savonius rotor** sized to submerge in your shallowest expected creek
      (drop-in, direction-agnostic, self-starting — ideal for "any creek")
- [ ] **Fast anchor**: stake + guy line, sandbags, or wedge between rocks; a
      trash screen upstream
- [ ] **Low-voltage DC** cable, marine-grade, IP68 connectors; inverter on land only
- [ ] **Battery + multi-input controller** on shore, **fused** at the battery
- [ ] Leave home with the pack **pre-charged** (wall/solar) so you have power on arrival
- [ ] Check local rules before deploying on water that isn't yours
      ([SITING.md](SITING.md#4-permits--neighbors-do-this-before-you-build)) and
      read [SAFETY.md](SAFETY.md)

## What's modeled

`creekturbine/portable.py` (tested in `tests/test_portable.py`):

- `runtime_hours` / `sustained_load_w` / `burst_runtime_hours` / `recharge_hours`
  — the battery-buffer math (sustained vs. burst vs. refill)
- `cable_voltage_drop` / `min_cable_area_mm2` — size the "waterproof extension
  cord" and see why higher voltage wins on a long run
- `battery_mass_kg` / `pack_weight_kg` — the carry-weight budget
- `PortableUnit` — ties creek speed + rotor + battery + cable into one report
