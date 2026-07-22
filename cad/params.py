"""
Shared parameters for all CreekTurbine printed/cut parts (MILLIMETERS).

Edit values here and re-run `python -m cad.export_all` to regenerate every
STEP/STL. Everything is parametric so the parts adapt to YOUR hardware --
especially SHAFT_DIA (the rotor shaft you buy) and GEN_SHAFT_DIA (your
generator's shaft) and GEN_BODY_DIA (your PMA's body).

Design intent (see docs/HARDWARE.md and cad/README.md):
  * The rotor is a VERTICAL-AXIS Savonius. Its two scoops are cut from cheap
    PVC pipe or sheet -- NOT printed. What you print/cut is the structure that
    holds them: two END PLATES, a SHAFT COUPLER, and the GENERATOR MOUNT.
  * The generator sits on top, ABOVE the waterline. Only the shaft and its
    bearings are wet. That is the whole reason to pick a vertical axis.
  * Anything load-bearing that lives underwater long-term (the shaft, the
    fasteners, the bearings) should be STAINLESS -- never printed plastic.
"""

# --- Rotor sizing (defaults mirror the config's recommended rotor) ---------
# These are the printed-structure dims; the hydrodynamic size comes from
# creekturbine/config.py via `python -m scripts.size_turbine`.
ROTOR_DIA = 340.0          # mm, rotor tip-to-tip diameter (from the sizing report)
ROTOR_HEIGHT = 540.0       # mm, scoop height (submerged)
SCOOP_COUNT = 2            # 2 = classic Savonius; 3 = smoother torque, a bit less Cp
SCOOP_OVERLAP = 0.15       # fraction of bucket diameter the two scoops overlap

# Helical Savonius blade (see docs/RESEARCH_ROTORS.md). A twist improves self-
# starting at any flow angle, smooths torque ripple, and sheds debris. Print
# SCOOP_COUNT of these, phase them evenly, and clamp between the end plates.
BLADE_THK = 4.0            # mm, printed scoop wall thickness
BLADE_TWIST_DEG = 180.0    # total helical twist over ROTOR_HEIGHT (0 = straight)

# --- Shafts / bearings -- MEASURE these on the parts you buy ----------------
SHAFT_DIA = 16.0           # mm, rotor shaft (stainless, e.g. 16 mm)
GEN_SHAFT_DIA = 8.0        # mm, your generator/PMA input shaft
GEN_BODY_DIA = 90.0        # mm, your PMA body diameter (for the mount bore)
GEN_BOLT_CIRCLE = 75.0     # mm, PMA face mounting-bolt circle diameter
GEN_BOLT_COUNT = 4         # PMA face bolts

# --- Print / fit tolerances ------------------------------------------------
CLEARANCE = 0.30           # mm, added to bores for a slip fit (tune to printer)
WALL = 3.2                 # mm, default wall thickness (~8 perimeters at 0.4 nozzle)
SCREW_M5 = 5.5             # mm, M5 clearance hole (scoop + frame bolts)
SCREW_M5_TAP = 4.3         # mm, M5 self-tap / thread-forming hole
SETSCREW_M5 = 4.3          # mm, tap drill for an M5 grub/set screw

# --- End plates (top & bottom discs that clamp the scoops) -----------------
PLATE_DIA = ROTOR_DIA + 30.0   # mm, a little larger than the rotor (Savonius end
                               #     plates that overhang the scoops raise Cp)
PLATE_THK = 6.0                # mm
PLATE_LIGHTENING = True        # cut lightening holes to save plastic/weight
HUB_DIA = 40.0                 # mm, thickened boss around the shaft bore
HUB_THK = 12.0                 # mm, total hub height (plate + boss)
SCOOP_BOLTS_PER_SIDE = 4       # M5 bolts fixing each scoop edge to the plate

# --- Shaft coupler (rotor shaft <-> generator shaft) -----------------------
COUPLER_DIA = 34.0         # mm, outer diameter
COUPLER_LEN = 50.0         # mm, total length
COUPLER_SETSCREWS = 2      # per side

# --- Magnetic coupling discs (wet shaft <-> dry generator, no seal) ---------
# Print TWO: one on the rotor shaft (magnets face UP to the bulkhead), one on the
# generator shaft (magnets face DOWN). Press cylindrical magnets into the pockets
# in ALTERNATING polarity around the ring. Keep the bulkhead + gap small.
# Sizes mirror creekturbine.magnetics.AxialMagCoupling defaults; re-size with
# `python -m scripts.mag_coupling` for your rotor's torque.
MAG_COUNT = 12             # magnets per disc (alternating N/S)
MAG_DIA = 15.0            # mm, cylindrical magnet diameter
MAG_THK = 6.0            # mm, magnet thickness (= pocket depth)
MAG_MEAN_RADIUS = 55.0   # mm, ring radius the magnets sit on
MAG_POCKET_CLEAR = 0.2   # mm, added to pocket diameter for a press/glue fit
MAGDISC_DIA = 2 * MAG_MEAN_RADIUS + MAG_DIA + 12.0   # mm, disc outer diameter
MAGDISC_THK = MAG_THK + 3.0                          # mm, magnet depth + back wall

# --- Bulkhead / sealing plate (the non-magnetic wall the coupling drives through)
# NON-MAGNETIC material only (polycarbonate, fiberglass, aluminium/316) — never
# plain steel, which shorts the magnetic flux. Thin at the CENTER (that thickness
# is part of the coupling gap — keep it small); thick, bolted, O-ring-sealed rim.
BULKHEAD_DIA = MAGDISC_DIA + 30.0        # mm, outer diameter (flange beyond the discs)
BULKHEAD_CENTER_THK = 2.0                # mm, thin membrane the magnets couple through
BULKHEAD_FLANGE_THK = 8.0                # mm, thick sealing rim
BULKHEAD_MEMBRANE_DIA = MAGDISC_DIA + 8.0  # mm, thin zone covering the magnet ring
BULKHEAD_BOLTS = 8                       # clamp bolts around the rim
BULKHEAD_BOLT_CIRCLE = BULKHEAD_DIA - 14.0  # mm
BULKHEAD_ORING_MEAN = MAGDISC_DIA + 18.0    # mm, O-ring groove mean diameter
BULKHEAD_ORING_W = 3.0                   # mm, groove width (for a ~2.5 mm O-ring)
BULKHEAD_ORING_DEPTH = 2.0               # mm, groove depth

# --- Trash rack / intake screen (sheds debris — the top field-failure) ------
RACK_DIA = 160.0           # mm, screen outer diameter (size to your intake)
RACK_THK = 6.0            # mm
RACK_BAR = 4.0            # mm, bar width
RACK_GAP = 10.0          # mm, slot gap (debris larger than this is shed)
RACK_RIM = 8.0           # mm, solid outer rim width

# --- Generator mount (bracket carrying the PMA above the water) ------------
MOUNT_PLATE = 140.0        # mm, square top plate the PMA bolts onto
MOUNT_THK = 8.0            # mm
MOUNT_LEG_HEIGHT = 120.0   # mm, how far the PMA stands above the top end plate
MOUNT_LEG_COUNT = 3        # legs down to the frame
