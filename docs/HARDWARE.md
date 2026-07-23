# Hardware — bill of materials & the generator problem

Prices are rough 2026 USD for a small (~5–20 W) creek build and will vary. Run
`python -m scripts.size_turbine` first — it tells you the rotor size, the shaft
rpm, and the generator Ke to shop for.

## The one hard part: the generator

Everything else is plumbing; the generator is where builds live or die, for two
reasons the toolkit makes explicit:

1. **Low rpm.** A Savonius turns *tens* of rpm. Most cheap motors are wound to
   make their rated voltage at *thousands* of rpm, so used bare they never
   "cut in" (reach charging voltage) in a creek.
2. **Cut-in.** Below the rpm where the rectified voltage exceeds your battery,
   **zero** current flows. `generator.py` computes the cut-in *velocity*; aim it
   at your creek's **low-season** flow.

Three ways to solve it, cheapest first:

| Option | What | Trade-off |
|--------|------|-----------|
| **Low-Kv PMA** (recommended) | A purpose-made low-rpm permanent-magnet alternator / "PMA" / axial-flux generator (the kind sold for small wind turbines, e.g. rated ~12 V at a few hundred rpm). | Cleanest match; direct-drive a Savonius via the coupler. Costs more than a scrap motor. |
| **Step-up drive** | A common motor + a belt/gear step-up (the report prints the ratio, often ~5–15:1). | Uses cheap parts; adds friction, noise, a wear item, and a few % loss. |
| **Repurposed motor** | A brushed DC motor, a stepper (rectified), a car alternator (no — needs field current & high rpm), or a hoverboard/e-bike hub motor (good: many poles, low Kv). | Free-ish; you must measure its Ke and check cut-in. Hub motors are the best scrap option. |

**Rectifier:** a PMA is 3-phase AC — add a **3-phase bridge rectifier** (six
diodes / a module) to make DC. A brushed DC motor needs only a single diode to
block back-feed.

## Bill of materials

### Rotor & structure
| Item | Notes | ~USD |
|------|-------|-----:|
| PVC pipe or HDPE drum for scoops | e.g. a 200 mm PVC pipe cut lengthwise = two scoops; or half a plastic barrel | 10–30 |
| 3D-printed end plates ×2, coupler, gen mount | PETG; print from `cad/` (or cut plywood/HDPE plates) | filament you have |
| **Stainless shaft** (e.g. 16 mm) | permanently wet — must be stainless | 15–30 |
| **Marine/stainless bearings** ×2 (pillow-block) | top can be a plain bearing; keep above silt | 15–35 |
| Stainless bolts/nuts/washers (M5/M6/M8) | scoops, plates, frame | 15–25 |

### Frame & siting
| Item | Notes | ~USD |
|------|-------|-----:|
| Frame (galv/stainless unistrut, EMT, or treated lumber) | must survive a flood; make it liftable | 25–60 |
| Anchoring (rebar stakes, ground anchors, sandbags) | to bed AND bank | 15–40 |
| Trash rack / intake screen | angled mesh upstream of the rotor | 10–25 |

### Electrical
| Item | Notes | ~USD |
|------|-------|-----:|
| **Low-Kv PMA / hub motor generator** | the heart. REALITY CHECK: buyable PMAs top out ~0.10–0.15 V/rpm — if the report recommends more, use a **boost MPPT** (below) or a belt step-up; don't shop for a unicorn | 40–150 |
| 3-phase bridge rectifier (or Schottky diodes) | AC → DC | 8–20 |
| **BOOST-type MPPT charge controller w/ dump load** | steps a few volts of slow-PMA output UP to the battery — the modern fix for slow-rotor cut-in. Spec **low quiescent draw (<10 mA)**: a 25 mA idler eats 15 %+ of a small harvest, 24/7 | 30–100 |
| **Dump/diversion resistor or heating element** | soaks up power when the battery is full — wired **generator-side, before the BMS** (see SAFETY) | 10–25 |
| **LiFePO4 battery** (12 V, sized by the report, e.g. 20–50 Ah) | BMS **must include low-temperature charge cutoff** (LiFePO4 won't take charge below 0 °C) | 60–180 |
| **Thrust / angular-contact bearings** (pair) | the magnetic coupling's discs pull together with ~300–400 N constantly — plain radial bearings grind flat | 10–30 |
| **12 V → USB-C PD buck module (45–65 W)** | what actually charges the laptop from the battery | 12–30 |
| **Main fuse + holder** at the battery + terminal | the most important safety part | 5–15 |
| Marine tinned wire, gel/heatshrink connectors, sealed enclosure | corrosion is relentless near water | 25–60 |
| (optional) 12 V→USB / small pure-sine inverter | to actually use the power | 15–60 |

**Ballpark:** a minimal ~5–10 W trickle-charger lands around **$250–450**; add
$100–200 for a bigger battery, a nicer MPPT controller, and an inverter.

## Portable ("camping") variant

For a carry-anywhere unit (see [PORTABLE.md](PORTABLE.md)), swap the fixed frame
for a lighter kit and add:

| Item | Notes | ~USD |
|------|-------|-----:|
| Compact sealed generator + **magnetic coupling** | no shaft seal to leak; drop-in-any-creek. Magnets: ~24 × Ø15×6 mm N42 NdFeB (two discs) + a thin non-magnetic bulkhead. Size with `scripts.mag_coupling`; see [MAG_COUPLING.md](MAG_COUPLING.md) | 50–120 |
| **Marine tinned DC cable** + **IP68 potted connectors** | the "waterproof extension cord" — low-voltage DC only | 20–60 |
| Portable **LiFePO4 pack** (e.g. 300–500 Wh) | the buffer that gives smooth, instant, 24/7 power | 150–350 |
| **Multi-input charge controller** (turbine + solar + USB-C) | your "switch between sources" | 30–90 |
| Fast anchor kit (stake + guy line / sandbags) | deploy in minutes | 15–35 |
| **Scuff-resistant outer**: HDPE/UHMW shell (or ASA + bed-liner coat) + **UHMW skid plate** + **TPU corner bumpers** | takes gravel drag and rock knocks; skid/bumpers are cheap sacrificial wear parts | 20–70 |

Use a **higher bus voltage (24–48 V)** for anything but the shortest cable run —
it slashes the copper needed and the volt-drop (the model shows ~16× less copper
going 12 V → 48 V). Keep any 120/230 V AC inverter **on land, after the battery**.

## What NOT to do
- **No car alternator** for direct creek drive — it needs field excitation and
  thousands of rpm; it won't cut in.
- **No bare PLA** underwater — it creeps and hydrolyzes. PETG/ASA or metal.
- **Never** run the turbine with no electrical load and no dump — it free-spins
  and destroys itself (and spikes the electronics). See [SAFETY.md](SAFETY.md).
