# CAD — the printed & cut structure

The Savonius rotor's **scoops** are cut from cheap PVC pipe or sheet (not
printed). What's parametric here is the **structure that holds them and carries
the shaft up to the dry generator**:

| Part | What it is | Print notes |
|------|-----------|-------------|
| `end_plate` | Top & bottom discs that clamp the scoops and carry the shaft hub. Print **2**. | PETG, 4+ walls, 40%+ infill. Overhangs the scoops on purpose (raises Cp). |
| `savonius_blade` | Helical (twisted) Savonius scoop — the research-backed rotor blade. Print **`SCOOP_COUNT`** (default 2). | PETG/ASA, 4+ walls; print upright. Twist = `BLADE_TWIST_DEG`; set 0 for a straight rotor. See [RESEARCH_ROTORS.md](../docs/RESEARCH_ROTORS.md). |
| `shaft_coupler` | Joins the rotor shaft to the generator shaft; radial set screws. | Print solid-ish (PETG/ABS/nylon), or buy a metal coupler and use this as the fit reference. |
| `generator_mount` | Top plate the PMA bolts to, standing above the waterline on legs. | PETG, 5+ walls. |

Load-bearing, permanently-wet parts — the **shaft, fasteners, bearings** — are
**metal (stainless)**, never printed.

![end plate](previews/end_plate.png) ![helical blade](previews/savonius_blade.png) ![shaft coupler](previews/shaft_coupler.png) ![generator mount](previews/generator_mount.png)

## Regenerating

```bash
pip install -r requirements-cad.txt        # heavy: pulls OpenCascade
# 1. edit cad/params.py — especially SHAFT_DIA, GEN_SHAFT_DIA, GEN_BODY_DIA,
#    GEN_BOLT_CIRCLE to match the parts you actually buy, and ROTOR_DIA /
#    ROTOR_HEIGHT to match `python -m scripts.size_turbine`
python -m cad.export_all                   # writes cad/step/*.step + cad/stl/*.stl
```

The committed STEP/STL match the defaults in `cad/params.py` (which mirror the
recommended rotor from the default `config.py`). **Always sanity-check the mesh
in your slicer before printing** — the bolt patterns are a sensible starting
point, not a guarantee they line up with your specific scoop pipe.

## Printing for water

- **PETG** is the sweet spot: cheap, tough, low water absorption, UV-OK for a
  season. **ASA/ABS** if you want better UV life. Avoid bare **PLA** underwater
  — it creeps and slowly hydrolyzes.
- Print **watertight**: 4–6 perimeters, 30–50% infill, and consider a wipe of
  epoxy on the end plates for a multi-season part.
- Anything structural underwater should really be **metal**; treat printed parts
  as brackets and jigs, not the primary wet load path.
