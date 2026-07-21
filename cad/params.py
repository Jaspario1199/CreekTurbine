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

# --- Generator mount (bracket carrying the PMA above the water) ------------
MOUNT_PLATE = 140.0        # mm, square top plate the PMA bolts onto
MOUNT_THK = 8.0            # mm
MOUNT_LEG_HEIGHT = 120.0   # mm, how far the PMA stands above the top end plate
MOUNT_LEG_COUNT = 3        # legs down to the frame
