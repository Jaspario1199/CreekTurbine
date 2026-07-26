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

# Printability: a 540 mm blade fits NO consumer printer, so the blade exports as
# ONE stackable segment — print SCOOP_COUNT × BLADE_SEGMENTS copies (segments are
# identical; each is the previous rotated by the segment twist), register them on
# 3 mm pins (filament works) through the end-face pin holes, and epoxy.
PRINTER_MAX_Z = 240.0      # mm, your printer's usable Z height
import math as _math
BLADE_SEGMENTS = max(1, _math.ceil(ROTOR_HEIGHT / (PRINTER_MAX_Z - 10.0)))
BLADE_SEG_H = ROTOR_HEIGHT / BLADE_SEGMENTS       # mm, one segment's height
BLADE_SEG_TWIST = BLADE_TWIST_DEG / BLADE_SEGMENTS  # deg twist per segment
BLADE_PIN_DIA = 3.2        # mm, alignment pin hole (3 mm pin / filament)
BLADE_PIN_DEPTH = 6.0      # mm, pin hole depth in each face

# End plates seat the blade ends in profile-matched GROOVES (cut from the same
# profile definition in cad/lib.py) — a twisted blade edge can't take a bolt, so
# it drops into a recess and gets clamped/epoxied instead.
PLATE_GROOVE_DEPTH = 2.5   # mm, blade-seat groove depth in each end plate

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
# NON-MAGNETIC material only (cut from polycarbonate/FR4 sheet; the STEP is the
# drill template) — never plain steel, which shorts the flux. Thin at the CENTER
# (that thickness is part of the coupling gap); thick, bolted, O-ring rim.
# NOTE: flange widened +8 mm after the detailing pass caught the O-ring groove
# colliding with the bolt holes (CRITIQUE.md #19) — groove now sits 8 mm inboard.
BULKHEAD_DIA = MAGDISC_DIA + 38.0        # mm, outer diameter (flange beyond the discs)
BULKHEAD_CENTER_THK = 2.0                # mm, thin membrane the magnets couple through
BULKHEAD_FLANGE_THK = 8.0                # mm, thick sealing rim
BULKHEAD_MEMBRANE_DIA = MAGDISC_DIA + 8.0  # mm, thin zone covering the magnet ring
BULKHEAD_BOLTS = 8                       # clamp bolts around the rim
BULKHEAD_BOLT_CIRCLE = BULKHEAD_DIA - 14.0  # mm (= 161 with defaults)
BULKHEAD_ORING_MEAN = MAGDISC_DIA + 13.0    # mm, O-ring groove mean diameter
BULKHEAD_ORING_W = 3.0                   # mm, groove width (for a ~2.5 mm O-ring)
BULKHEAD_ORING_DEPTH = 2.0               # mm, groove depth

# ===========================================================================
# FULL-UNIT PARTS — one consistent dimensional chain, rotor outward:
#   blade -> end plate (ROTOR_DIA+30) -> housing bore (+6 clearance) -> shell
#   -> cage rings (columns OUTSIDE the plate swing) -> skid -> wings.
# Change ROTOR_DIA/ROTOR_HEIGHT and everything re-derives.
# ===========================================================================

# --- Dry housing (upper canister: generator, battery, electronics, outlets) ---
HOUSING_WALL = 4.0                     # mm, shell wall
HOUSING_ID = PLATE_DIA + 6.0           # mm, bore clears the spinning end plates
HOUSING_OD = HOUSING_ID + 2 * HOUSING_WALL
HOUSING_DRY_H = 350.0                  # mm, dry section height
HOUSING_FLOOR_THK = 6.0                # mm, sealed floor the bulkhead clamps under
HOUSING_FLOOR_OPEN = BULKHEAD_MEMBRANE_DIA + 1.0  # mm, coupling window in the floor
HOUSING_FLANGE_OD = HOUSING_OD + 20.0  # mm, top lid flange
HOUSING_LID_BOLTS = 6
HOUSING_LID_BC = HOUSING_OD + 10.0     # mm, lid bolt circle
PANEL_CUT_W = 60.0                     # mm, side cutout for the USB/12V outlet panel
PANEL_CUT_H = 40.0

# --- Lid with carry handle ---------------------------------------------------
LID_THK = 6.0
LID_LIP_DEPTH = 6.0                    # registers inside the shell bore
HANDLE_BAR_DIA = 24.0                  # mm, comfortable grip
HANDLE_SPAN = 140.0                    # mm, between posts
HANDLE_CLEAR = 60.0                    # mm, knuckle room under the bar

# --- Rotor cage (wet section: open frame the rotor spins in) -----------------
# Two printed rings + 4 BOUGHT columns (20 mm aluminium square tube, cut to
# CAGE_COL_LEN) — a 600 mm one-piece cage is unprintable, tube is stiffer anyway.
CAGE_COL = 20.0                        # mm, square column tube size
CAGE_COL_COUNT = 4
CAGE_COL_R = PLATE_DIA / 2 + 4.0 + CAGE_COL / 2   # mm, centres OUTSIDE plate swing
CAGE_RING_OD = 2 * (CAGE_COL_R + CAGE_COL / 2 + 6.0)  # mm, rim beyond the sockets
CAGE_RING_THK = 8.0
CAGE_SOCKET_DEPTH = 15.0               # mm, column pocket in each ring
CAGE_SOCKET_CLEAR = 0.4                # mm, tube slip fit
CAGE_COL_LEN = ROTOR_HEIGHT + 64.0     # mm, rotor + plates/hubs + bearing room
BEARING_OD = 22.0                      # mm, flanged bearing seat in the bottom boss

# --- Skid / ballast base -----------------------------------------------------
SKID_SIZE = CAGE_RING_OD + 30.0        # mm, square footprint
SKID_THK = 8.0
SKID_RUNNER_W = 24.0                   # mm, two sacrificial UHMW-replaceable runners
SKID_RUNNER_H = 15.0
TRAY_WALL_T = 3.0                      # mm, ballast tray wall on top
TRAY_WALL_H = 18.0
STAKE_HOLE = 10.0                      # mm, corner stake-down holes
CAGE_BOLT_R = CAGE_RING_OD / 2 - 12.0  # mm, cage-to-skid bolt radius (4x M5)

# --- Funnel wing wall (print/cut 2 — same part, one flipped) -----------------
WING_LEN = 500.0                       # mm, panel length
WING_H = 350.0                         # mm, panel height (= funnel intake height)
WING_THK = 6.0
WING_FLANGE_W = 30.0                   # mm, L-return that bolts to a cage column
WING_STAKE_SLOT = (12.0, 35.0)         # mm, stake slots near the outer end
WING_RIB = (12.0, 8.0)                 # mm, horizontal stiffener (w, t)

# --- Magnet cover (seals the WET coupling disc's magnet faces) ---------------
MAGCOVER_DIA = MAGDISC_DIA + 2.0
MAGCOVER_THK = 1.2                     # bonded over the potted magnets
MAGCOVER_HOLE = HUB_DIA + 4.0

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
