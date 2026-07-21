"""
Simulator / visualiser — renders the physics to PNGs so you can SEE the trade.

No display required (uses the Agg backend). Every function returns the path it
wrote. `render_all(cfg, outdir)` produces the whole picture book:

    power_vs_velocity.png   the v^3 law, with YOUR creek marked
    sizing_curve.png        rotor size needed vs velocity for your target
    energy_budget.png       what a day's harvest actually runs
    savonius_schematic.png  a labelled cross-section of the recommended rotor

These are the figures a README should show, in the spirit of RoomCleaner's
workspace/scene renders.
"""

from __future__ import annotations

import math
import os

import matplotlib
matplotlib.use("Agg")  # headless: render straight to files
import matplotlib.pyplot as plt
import numpy as np

from . import hydrokinetics as hk
from . import energy as en
from . import rotor as rotor_mod
from .config import CreekConfig, DEFAULT_CONFIG

_INK = "#1b3a4b"
_WATER = "#2a7fb8"
_AVAIL = "#9ecae1"
_GOOD = "#3aa66f"
_BAD = "#d0605e"


def _ensure(outdir: str) -> str:
    os.makedirs(outdir, exist_ok=True)
    return outdir


def power_vs_velocity(cfg: CreekConfig, outdir: str, vmax: float = 1.6) -> str:
    """Available vs extractable electrical power across velocity, for the
    config's recommended rotor, with the creek's velocity marked."""
    _ensure(outdir)
    rot = rotor_mod.make_rotor_from_config(cfg)
    area = rot.frontal_area if math.isfinite(rot.frontal_area) else cfg.channel_area * 0.25

    v = np.linspace(0.01, vmax, 200)
    avail = np.array([hk.available_power(area, vi, cfg.water_density) for vi in v])
    elec = np.array([hk.extractable_power(area, vi, cfg.cp, cfg.generator_efficiency,
                                          cfg.drivetrain_efficiency, cfg.water_density)
                     for vi in v])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(v, 0, avail, color=_AVAIL, alpha=0.6,
                    label=f"Kinetic power in the water (A={area:.2f} m²)")
    ax.plot(v, elec, color=_GOOD, lw=2.5,
            label=f"Delivered to battery (Cp·η = {cfg.system_efficiency*100:.0f}%)")

    ve = cfg.effective_velocity
    p_here = hk.extractable_power(area, ve, cfg.cp, cfg.generator_efficiency,
                                  cfg.drivetrain_efficiency, cfg.water_density)
    ax.axvline(ve, color=_INK, ls="--", lw=1.3)
    ax.plot([ve], [p_here], "o", color=_INK, ms=8, zorder=5)
    ax.annotate(f"  your creek\n  {ve:.2f} m/s → {p_here:.1f} W",
                (ve, p_here), color=_INK, va="bottom", fontsize=10, fontweight="bold")

    ax.set_xlabel("water speed at the rotor  (m/s)")
    ax.set_ylabel("power  (W)")
    ax.set_title("Creek power scales with velocity³ — speed is everything")
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", framealpha=0.9)
    path = os.path.join(outdir, "power_vs_velocity.png")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def sizing_curve(cfg: CreekConfig, outdir: str, vmax: float = 1.6) -> str:
    """Rotor frontal area required to hit the target power, vs velocity."""
    _ensure(outdir)
    v = np.linspace(0.15, vmax, 200)
    area = np.array([hk.swept_area_for_power(cfg.target_power_w, vi, cfg.cp,
                                             cfg.generator_efficiency,
                                             cfg.drivetrain_efficiency,
                                             cfg.water_density) for vi in v])
    area = np.clip(area, 0, 50)  # keep the axis readable when slow creeks blow up

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(v, area, color=_WATER, lw=2.5)
    ax.fill_between(v, 0, area, color=_WATER, alpha=0.12)

    # Mark the creek and a "sane size" band (rotor area vs channel area)
    ve = cfg.effective_velocity
    a_here = hk.swept_area_for_power(cfg.target_power_w, ve, cfg.cp,
                                     cfg.generator_efficiency,
                                     cfg.drivetrain_efficiency, cfg.water_density)
    ax.axvline(ve, color=_INK, ls="--", lw=1.3)
    if math.isfinite(a_here) and a_here < 50:
        ax.plot([ve], [a_here], "o", color=_INK, ms=8, zorder=5)
        ax.annotate(f"  {a_here:.2f} m² needed here", (ve, a_here), color=_INK,
                    va="bottom", fontsize=10, fontweight="bold")

    sane = cfg.channel_area * 0.30  # a rotor blocking ~30% of the channel
    ax.axhline(sane, color=_BAD, ls=":", lw=1.5)
    ax.annotate(f"~30% of your channel ({sane:.2f} m²): bigger than this "
                f"backs water up", (vmax * 0.02, sane), color=_BAD, va="bottom",
                fontsize=9)

    ax.set_xlabel("water speed at the rotor  (m/s)")
    ax.set_ylabel(f"rotor frontal area for {cfg.target_power_w:.0f} W  (m²)")
    ax.set_title("How big a rotor your target needs (smaller is better)")
    ax.set_ylim(0, min(50, np.nanmax(area[np.isfinite(area)]) * 1.1 + 0.1))
    ax.grid(alpha=0.25)
    path = os.path.join(outdir, "sizing_curve.png")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def energy_budget(cfg: CreekConfig, outdir: str) -> str:
    """Horizontal bars: each common load vs the day's harvested energy."""
    _ensure(outdir)
    rot = rotor_mod.make_rotor_from_config(cfg)
    p = rot.electrical_power(cfg.effective_velocity, cfg.generator_efficiency,
                             cfg.drivetrain_efficiency, cfg.water_density)
    daily = en.daily_energy_wh(p, cfg.flow_availability)

    rows = en.what_it_runs(daily)
    names = [ld.name for ld, _, _ in rows]
    vals = [ld.wh_per_day for ld, _, _ in rows]
    colors = [_GOOD if ok else _BAD for _, ok, _ in rows]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    y = np.arange(len(names))
    ax.barh(y, vals, color=colors, alpha=0.85)
    ax.axvline(daily, color=_INK, lw=2)
    ax.annotate(f"your daily harvest ≈ {daily:.0f} Wh/day",
                (daily, len(names) - 0.4), color=_INK, fontsize=10,
                fontweight="bold", ha="right" if daily > max(vals) * 0.6 else "left")
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("energy per day  (Wh)")
    ax.set_title("What one day of creek keeps alive (green = fits, red = too big)")
    ax.grid(axis="x", alpha=0.25)
    path = os.path.join(outdir, "energy_budget.png")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def savonius_schematic(cfg: CreekConfig, outdir: str) -> str:
    """A labelled top-down cross-section of a two-scoop Savonius rotor."""
    _ensure(outdir)
    rot = rotor_mod.make_rotor_from_config(cfg)
    D = rot.diameter if (cfg.turbine_type == "savonius" and math.isfinite(rot.diameter)) else 0.5
    R = D / 2.0
    bucket_r = R * 0.55
    overlap = 0.15 * bucket_r

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    # two semicircular scoops offset around the shaft, S-shape when viewed top-down
    th = np.linspace(0, math.pi, 60)
    c1 = (-overlap, 0.0)
    c2 = (overlap, 0.0)
    ax.plot(c1[0] + bucket_r * np.cos(th), c1[1] + bucket_r * np.sin(th),
            color=_WATER, lw=6, solid_capstyle="round")
    ax.plot(c2[0] + bucket_r * np.cos(th + math.pi), c2[1] + bucket_r * np.sin(th + math.pi),
            color=_WATER, lw=6, solid_capstyle="round")
    ax.plot([0], [0], "o", color=_INK, ms=10)  # central shaft
    ax.annotate("shaft ↑ to generator\n(above waterline)", (0, 0), (0.02, R * 0.9),
                fontsize=9, color=_INK, ha="left")

    # flow arrows
    for yy in np.linspace(-R * 1.1, R * 1.1, 5):
        ax.annotate("", xy=(-R * 0.9, yy), xytext=(-R * 1.6, yy),
                    arrowprops=dict(arrowstyle="->", color=_GOOD, lw=2))
    ax.annotate("creek flow", (-R * 1.6, R * 1.25), color=_GOOD, fontsize=10,
                fontweight="bold")

    ax.annotate("", xy=(R, -R * 1.35), xytext=(-R, -R * 1.35),
                arrowprops=dict(arrowstyle="<->", color=_INK))
    ax.annotate(f"rotor Ø = {D:.2f} m", (0, -R * 1.5), color=_INK, ha="center",
                fontsize=10, fontweight="bold")

    lim = R * 1.8
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Recommended Savonius rotor (top-down)\n"
                 "self-starting · flow-direction agnostic", fontsize=12)
    path = os.path.join(outdir, "savonius_schematic.png")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def render_all(cfg: CreekConfig = DEFAULT_CONFIG, outdir: str = "output") -> list[str]:
    """Render the whole picture book; returns the list of written paths."""
    paths = [
        power_vs_velocity(cfg, outdir),
        sizing_curve(cfg, outdir),
        energy_budget(cfg, outdir),
    ]
    if cfg.turbine_type == "savonius":
        paths.append(savonius_schematic(cfg, outdir))
    return paths
