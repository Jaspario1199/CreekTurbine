# Design critique — the red-team audit and what was done about it

A deliberate attempt to break the design across manufacturability, flooding,
power, and field-survival, with every finding tracked to a resolution. Statuses:
**FIXED-IN-CODE** (model/CAD now handles it), **DOCUMENTED** (procedure/spec
change), **ACCEPTED** (known limit, stated honestly), **OPEN** (needs field data).

## 🔴 Critical — would have stopped the build working

| # | Finding | Resolution |
|---|---------|------------|
| 1 | **Recommended generator Ke was unbuyable.** The report asked for 0.3–1.0 V/rpm PMAs; the market tops out ~0.10–0.15 V/rpm. Direct-drive at 40 rpm on a 12 V bus was a fantasy — the classic dead-on-arrival DIY mistake. | **FIXED-IN-CODE** — `generator.practical_options()` reality-checks the Ke; `size_turbine` now prints **Fix A: boost-type MPPT** (charges 12 V from a few volts of PMA output, cut-in no longer needs to beat battery voltage) or **Fix B: ~4:1 belt step-up** onto a realistic 0.12 V/rpm PMA. BOM updated. |
| 2 | **Magnetic coupling axial pull unmodeled.** The discs don't just make torque — they attract with ~**380 N (~39 kg), constantly**. On plain radial bearings that grinds the drivetrain flat. | **FIXED-IN-CODE** — `AxialMagCoupling.axial_force_n()`; `mag_coupling` prints the pull and the required **thrust/angular-contact bearing** rating. [MAG_COUPLING.md](MAG_COUPLING.md) updated. |
| 3 | **Helical blade was unprintable** (540 mm tall vs ~240 mm printer Z). | **FIXED-IN-CODE** — blade now exports as **one stackable segment** (`BLADE_SEGMENTS` auto-computed from `PRINTER_MAX_Z`; segments of a helix are identical, so one STL → print `SCOOP_COUNT × BLADE_SEGMENTS` copies), registered on 3 mm pins through end-face holes, epoxied. |
| 4 | **Blade-to-plate attachment didn't exist** — a twisted blade edge can't take a vertical bolt; the bolt rings were decorative for a helical blade. | **FIXED-IN-CODE** — end plates now cut **profile-matched seating grooves** from the *same* cross-section definition the blade extrudes (`cad/lib.py`, single source of truth). Blade ends drop in, epoxy + through-rods clamp. Plates stay identical parts (grooves are SCOOP_COUNT-fold symmetric; clock the top plate to the twist at assembly). |

## 🟠 Serious — wrong numbers or predictable field failures

| # | Finding | Resolution |
|---|---------|------------|
| 5 | **Flood loading never checked** — stability used *operating* velocity; a 2.5 m/s storm pushes ~**670 N (~10×** operating). | **FIXED-IN-CODE** — `flood_drag_n()` / `flood_anchor_force_n()`; `self_contained` prints the flood case and the honest advice: **retrieval line, pull before storms**. |
| 6 | **Charge-controller idle draw ignored** — a typical MPPT idles ~0.25 W, 24/7, dry creek included; that's 15 %+ of a small harvest. | **FIXED-IN-CODE** — `energy.net_daily_energy_wh()` (can go **negative**, and warns); `CONTROLLER_IDLE_W` in config; report shows net. BOM: spec **low-quiescent (<10 mA)** controllers. |
| 7 | **Funnel `confinement = 0.82` is an invented number** — no literature covers a free-standing intake's realized speed-up. | **DOCUMENTED + OPEN** — flagged as an engineering assumption in code + [FUNNEL.md](FUNNEL.md); field-calibrate by floating a stick through the throat. Absolute watts carry this uncertainty. |
| 8 | **Universal funnel gathered the full water column** even in 3 ft water, though the intake mouth is ~0.35 m tall. | **FIXED-IN-CODE** — `universal()` caps gathered depth at `intake_height`. (Choke already capped the output, so published numbers stand.) |
| 9 | **BMS disconnect defeats the dump load** — battery full/cold → BMS opens → PMA open-circuits and overspeeds *despite* a "correctly wired" dump. | **DOCUMENTED** — wire the dump/clamp **on the generator side, before the BMS**, so it can never be disconnected ([SAFETY.md](SAFETY.md)). |
| 10 | **LiFePO4 won't charge below 0 °C** — silent winter failure. | **DOCUMENTED** — BOM requires a BMS **with low-temp charge cutoff**; winter pull-out already in SAFETY. |

## 🟡 Moderate — cost, wear, and honesty items

| # | Finding | Resolution |
|---|---------|------------|
| 11 | Bulkhead spec said "print in polycarbonate" — hobby PC printing is impractical, and the part is just a flat disc. | **DOCUMENTED** — **cut it from 3 mm PC/acrylic/FR4 sheet**; the STEP file is the drill/routing template. |
| 12 | End plate Ø370 mm also exceeds print beds. | **DOCUMENTED** — cut from HDPE sheet / plywood for large rotors using the STEP as template; printing is for small rotors. |
| 13 | Wet coupling-disc magnets "epoxied in" is not marine sealing — NdFeB rusts through pinholes. | **DOCUMENTED** — pot pockets full, then a **thin epoxy/glass cover coat over the whole magnet face**; inspect seasonally. |
| 14 | "Charge a laptop" needs actual hardware, not just Wh. | **DOCUMENTED** — BOM adds a **12 V → USB-C PD (45–65 W) buck module**; battery must sustain ~5 A bursts. |
| 15 | Sediment deposition behind the funnel throat buries the bottom bearing. | **DOCUMENTED** — keep the lower bearing ≥ skid height off the bed; seasonal check. Sediment is also why the base uses a skid, not feet. |
| 16 | Lab/CFD Cp values (0.19/0.24 profiles) will run 20–30 % lower in a real build. | **ACCEPTED** — defaults stay conservative (`custom` 0.18); profile presets note CFD optimism ([RESEARCH_ROTORS.md](RESEARCH_ROTORS.md) caveats). |
| 17 | Trash rack orientation/limits under-specified — a clogged rack *is* the blockage. | **DOCUMENTED** — mount angled, bars aligned with flow, sized via `siting.screen_*`; clean-by-design expectations in [FUNNEL.md](FUNNEL.md). |
| 18 | Funnel throat concentrates debris — clog rate scales with the speed-up. | **ACCEPTED + DOCUMENTED** — the trash rack is **mandatory** with a funnel; maintenance interval is site-dependent (OPEN: measure it). |

| 19 | **Bulkhead O-ring groove collided with its bolt holes** (groove Ø153.5–156.5 vs bolt holes spanning Ø150.25–155.75) — found while detailing the full-unit CAD; the part would not have sealed. | **FIXED-IN-CODE** — flange widened +8 mm, groove moved 8 mm inboard of the bolt circle; part re-exported. A good example of why the hyper-detail pass exists. |

## What deliberately remains open (needs a wet prototype, not more modeling)

Each open item now has a concrete procedure with pass/fail gates and a
feed-back-into-config step in **[TEST_PROTOCOL.md](TEST_PROTOCOL.md)**:

1. Field-calibrated funnel `confinement` → protocol **F2**.
2. Measured rotor Cp vs. the profile presets → protocol **F3**.
3. Real fouling/sediment maintenance interval → protocol **F4**.
4. Coupling slip torque verified on the bench → protocol **B2**
   (plus generator cut-in **B1**, drivetrain drag **B3**, watertightness **B4**,
   controller idle **B5**).

*Everything in the tables is implemented in the same commit series that added this
file; `python -m pytest` (115 checks) and `python -m cad.export_all` (7 parts)
verify the claims that are verifiable in software.*
