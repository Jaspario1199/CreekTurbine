"""
size_turbine — the end-to-end brain.

Reads your creek numbers from creekturbine/config.py and prints an honest sizing
report: how much power your creek can actually make, how big a rotor that needs,
what generator to match, what a day's energy runs, and how big a battery to buy.

    python -m scripts.size_turbine            # text report
    python -m scripts.size_turbine --figs     # also render figures into ./output

Nothing here is hardware-specific — it's all arithmetic on your measured creek,
so you can run it today, before buying a single part.
"""

from __future__ import annotations

import argparse
import math

from creekturbine.config import DEFAULT_CONFIG as cfg
from creekturbine import hydrokinetics as hk
from creekturbine import rotor as rotor_mod
from creekturbine import generator as gen_mod
from creekturbine import energy as en


def _fmt_len(x: float) -> str:
    return "∞ (creek too slow for this target)" if not math.isfinite(x) else f"{x:.2f} m"


def main() -> None:
    ap = argparse.ArgumentParser(description="Size a creek turbine from config.py")
    ap.add_argument("--figs", action="store_true", help="also render figures to ./output")
    ap.add_argument("--outdir", default="output")
    args = ap.parse_args()

    ve = cfg.effective_velocity
    rho = cfg.water_density

    print("=" * 70)
    print(" CreekTurbine — sizing report")
    print("=" * 70)
    print(f" Creek: {cfg.velocity:.2f} m/s measured"
          + (f" x {cfg.velocity_augmentation:.2f} augmentation = {ve:.2f} m/s at rotor"
             if cfg.velocity_augmentation != 1.0 else "")
          + f", channel {cfg.width:.2f}×{cfg.depth:.2f} m ({cfg.channel_area:.2f} m²)")
    print(f" Water carries {hk.power_flux(ve, rho):.0f} W per m² of frontal area"
          f" at {ve:.2f} m/s.")
    prof = (f", {cfg.savonius_profile} profile" if cfg.turbine_type == "savonius"
            and cfg.savonius_profile != "custom" else "")
    print(f" Turbine: {cfg.turbine_type.upper()}{prof}  (Cp={cfg.cp:.2f}, "
          f"generator η={cfg.generator_efficiency:.2f}, drivetrain η="
          f"{cfg.drivetrain_efficiency:.2f})")
    print(f" End-to-end efficiency (water→battery): {cfg.system_efficiency*100:.0f}%")
    print("-" * 70)

    # --- Rotor sized to the target -----------------------------------------
    rot = rotor_mod.make_rotor_from_config(cfg)
    print(f" TARGET: {cfg.target_power_w:.1f} W continuous at the battery")
    if cfg.turbine_type == "savonius":
        print(f"   → Savonius rotor: Ø {_fmt_len(rot.diameter)}"
              + (f" × {rot.height:.2f} m tall" if math.isfinite(rot.diameter) else "")
              + (f"  (frontal area {rot.frontal_area:.2f} m²)"
                 if math.isfinite(rot.frontal_area) else ""))
    else:
        print(f"   → Axial rotor: Ø {_fmt_len(rot.diameter)}"
              + (f"  (swept area {rot.frontal_area:.2f} m²)"
                 if math.isfinite(rot.frontal_area) else ""))

    if math.isfinite(rot.frontal_area):
        blockage = hk.blockage_ratio(rot.frontal_area, cfg.channel_area)
        verdict = ("comfortable" if blockage < 0.25 else
                   "tight — may back water up / need a permit" if blockage < 0.5 else
                   "TOO BIG for this creek at this speed")
        print(f"   Blocks {blockage*100:.0f}% of the wetted channel — {verdict}.")

        perf = rot.performance(ve, rho=rho)
        p_elec = rot.electrical_power(ve, cfg.generator_efficiency,
                                      cfg.drivetrain_efficiency, rho)
        print(f"   At {ve:.2f} m/s: shaft ≈ {perf.rpm:.0f} rpm, "
              f"torque ≈ {perf.torque_nm:.1f} N·m, "
              f"mechanical ≈ {perf.mechanical_w:.1f} W → battery ≈ {p_elec:.1f} W")
    print("-" * 70)

    # --- Generator matching -------------------------------------------------
    if math.isfinite(rot.frontal_area):
        low_v = cfg.velocity * 0.6  # design cut-in for low-season flow
        ke = gen_mod.recommend_ke(rot, low_v, cfg.system_voltage)
        rpm_design = hk.rpm_at_velocity(rot.optimal_tsr, ve, rot.radius)
        print(" GENERATOR MATCH (the part people get wrong):")
        if math.isfinite(ke):
            print(f"   Rotor turns ~{rpm_design:.0f} rpm at {ve:.2f} m/s — that's SLOW.")
            print(f"   Ideal direct-drive PMA: Ke ≈ {ke:.3f} V/rpm "
                  f"(≈ {1/ke:.0f} rpm/V) to cut in at low-season ~{low_v:.2f} m/s.")
            opts = gen_mod.practical_options(ke)
            if opts["buyable"]:
                print("   ✓ That Ke is purchasable — direct-drive works.")
            else:
                print(f"   ✗ REALITY CHECK: no off-the-shelf PMA reaches "
                      f"{ke:.2f} V/rpm (market tops out ~{gen_mod.MAX_PRACTICAL_KE}).")
                print(f"     Fix A (recommended): a BOOST-type MPPT controller — "
                      f"charges the {cfg.system_voltage:.0f} V battery from a few "
                      f"volts of PMA output, so slow rpm still charges.")
                print(f"     Fix B: a ≈ {opts['step_up']:.0f}:1 belt/gear step-up "
                      f"onto a realistic ~0.12 V/rpm PMA.")
        print("-" * 70)

        # --- Energy + battery ----------------------------------------------
        p_elec = rot.electrical_power(ve, cfg.generator_efficiency,
                                      cfg.drivetrain_efficiency, rho)
        daily = en.net_daily_energy_wh(p_elec, cfg.controller_idle_w,
                                       cfg.flow_availability)
        annual = en.annual_energy_kwh(p_elec, cfg.flow_availability)
        ah = en.battery_capacity_ah(max(daily, 0.0), cfg.system_voltage,
                                    cfg.days_autonomy, cfg.depth_of_discharge)
        print(f" ENERGY: ({p_elec:.1f} W × {cfg.flow_availability:.0%} uptime − "
              f"{cfg.controller_idle_w:.2f} W controller idle) × 24 h "
              f"≈ {daily:.0f} Wh/day net  (~{annual:.0f} kWh/yr gross)")
        if daily <= 0:
            print("   ⚠ NET NEGATIVE: the controller's idle draw exceeds the "
                  "harvest — the battery drains. Bigger rotor or lower-quiescent "
                  "controller required.")
        print(f" BATTERY: {ah:.0f} Ah at {cfg.system_voltage:.0f} V "
              f"({cfg.battery_chemistry}) for {cfg.days_autonomy:.0f} days autonomy "
              f"at {cfg.depth_of_discharge:.0%} DoD")
        print(" WHAT IT RUNS (fits within a day's harvest?):")
        for load, ok, frac in en.what_it_runs(daily):
            mark = "✓" if ok else "✗"
            print(f"   {mark} {load.name:<28} {load.wh_per_day:>4.0f} Wh/day "
                  f"({frac*100:>3.0f}% of budget)  {load.note}")
    else:
        print(" This creek is too slow for that target with a sanely sized rotor.")
        print(" Options, in order of impact (v³!):")
        print("   1. Find a faster spot (a natural narrows/riffle).")
        print("   2. Build a chute/shroud to speed the water up at the rotor.")
        print("   3. Lower TARGET_POWER_W — even 2-5 W is a useful trickle.")
    print("=" * 70)

    if args.figs:
        from creekturbine import simulator
        paths = simulator.render_all(cfg, args.outdir)
        print("Figures written:")
        for p in paths:
            print("  ", p)


if __name__ == "__main__":
    main()
