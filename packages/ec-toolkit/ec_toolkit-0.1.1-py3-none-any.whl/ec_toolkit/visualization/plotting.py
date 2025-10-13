import numpy as np
import matplotlib.pyplot as plt
from typing import Sequence, Optional, Tuple
from ec_toolkit.analysis.thermodynamics import compute_eta_td, compute_g_max


def plot_free_energy(
    dg: Sequence[float],
    el_steps: Sequence[bool],
    labels: Sequence[str],
    eq_pot: float = 0.0,
    op: Optional[float] = None,
    sym_fac: int = 1,
    ref_el: str = "RHE",
    annotate_eta: bool = False,
    annotate_gmax: Optional[float] = None,
    annotate_gmax_coord: Optional[Tuple[int, int]] = None,
    ax: Optional[plt.Axes] = None,
    **step_kwargs,
) -> plt.Axes:
    """
    Plot a free‐energy diagram (stepwise) for a reaction mechanism.

    Parameters
    ----------
    dg         : sequence of zero‑bias ΔG for each step (length N+1 if including top-up).
    el_steps   : bool mask, True for electrochemical steps (length N).
    labels     : labels for each state (length N+1).
    eq_pot     : equilibrium potential [V] (used in the U label).
    op         : if given, add an overpotential (eq_pot+op) bias to electrochemical steps.
    sym_fac    : symmetry factor (defaults to 1).
    ref_el     : reference electrode string (e.g. "RHE").
    annotate_eta : if True, compute & draw η_TD (requires op=None).
    annotate_gmax: if not None, a float overpotential at which to compute & annotate G_max.
    annotate_gmax_coord: optionally supply (i,j) for G_max annotation.
    ax         : optional matplotlib Axes to draw into.
    **step_kwargs: passed to plt.step for line styling.
    """

    ax = ax or plt.gca()
    # transform ΔG into cumulative profile
    dg_arr = np.asarray(dg, float)
    # apply overpotential if requested
    if op is not None:
        el = np.asarray(el_steps, int)
        dg_arr = dg_arr + np.concatenate(([0], el * op))

    cum = np.concatenate(([0.0], np.cumsum(dg_arr[:-1])))
    # final plateau
    cum = np.concatenate((cum, [cum[-1] + dg_arr[-1]]))

    # clean spines
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    # plot
    xs = np.arange(len(cum))
    ax.step(xs, cum, where="post", **step_kwargs)
    ax.set_xlim(xs[0], xs[-1])
    ax.set_ylabel("Free energy (eV)")
    ax.set_xlabel("Reaction coordinate")
    U = eq_pot + (op if op is not None else 0.0)
    ax.text(
        0.95,
        -0.05,
        rf"$U_{{{ref_el}}} = {U:.2f}\,$V",
        transform=ax.transAxes,
        va="top",
        ha="right",
    )

    # annotate η_TD
    if annotate_eta:
        # feed zero-overpotential dg (without top-up element)
        eta, step_i = compute_eta_td(dg_arr[:-1], el_steps, eq_pot)
        # draw double arrow
        y0 = cum[step_i - 1]
        y1 = cum[step_i]
        ax.annotate(
            "",
            xy=(step_i, y1),
            xytext=(step_i, y0),
            arrowprops=dict(arrowstyle="<->", lw=1.2),
        )
        ax.text(
            step_i + 0.1,
            (y0 + y1) / 2,
            rf"$\eta_{{TD}} = {eta:.2f}\,\mathrm{{V}}$",
            va="center",
            rotation=270,
        )

    # annotate G_max
    if annotate_gmax is not None:
        Gmax, (i, j) = compute_g_max(dg_arr[:-1], el_steps, annotate_gmax)
        # draw
        y0 = cum[i - 1]
        y1 = cum[j]
        ax.annotate(
            "",
            xy=(j, y1),
            xytext=(i - 1, y0),
            arrowprops=dict(arrowstyle="<->", linestyle="--", lw=1),
        )
        ax.text(
            j + 0.1,
            (y0 + y1) / 2,
            rf"$G_{{\mathrm{{max}}}}({annotate_gmax:.2f}) = {Gmax:.2f}\,$eV",
            va="center",
        )

    ax.margins(x=0.02)
    return ax
