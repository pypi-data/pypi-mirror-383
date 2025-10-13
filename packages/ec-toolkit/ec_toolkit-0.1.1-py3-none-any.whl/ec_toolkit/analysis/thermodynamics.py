import numpy as np
from typing import Sequence, Tuple


def compute_delta_g(
    dE: Sequence[float],
    dZPE: Sequence[float],
    dTS: Sequence[float],
    el_steps: Sequence[bool],
    eq_pot: float,
    sym_fac: int = 1,
) -> np.ndarray:
    """
    Compute the zero‑bias ΔG for each elementary step, then append
    the final “top‑up” so that sum(ΔG) == eq_pot * (# of e– steps).

    Parameters
    ----------
    dE      : step electronic energies [eV]
    dZPE    : zero‑point corrections [eV]
    dTS     : entropic corrections [eV]
    el_steps: booleans, True if that step is electrochemical (1 e–)
    eq_pot  : equilibrium potential [V]
    sym_fac : symmetry factor (defaults to 1)

    Returns
    -------
    ΔG : (N+1,) array of free‐energy changes [eV],
         where N = len(dE), last entry is the “eq top‑up” term.
    """
    dE = np.asarray(dE)
    dZPE = np.asarray(dZPE)
    dTS = np.asarray(dTS)
    el = np.asarray(el_steps, dtype=int)

    # Stepwise zero‑bias ΔG
    dg = (dE + dZPE - dTS) / sym_fac

    # number of electrons total
    n_e = el.sum()
    # energy delivered by eq_pot per electron
    G_eq = eq_pot * n_e

    # top‑up so that sum(dg)+dg_top = G_eq
    dg_top = G_eq - dg.sum()

    return np.concatenate([dg, [dg_top]])


def compute_eta_td(
    dg: Sequence[float],
    el_steps: Sequence[bool],
    eq_pot: float,
) -> Tuple[float, int]:
    """
    Thermodynamic overpotential η_TD = max(ΔG_i) + 0 (assuming reference electrode at 0 V),
    but shifted by eq_pot.  Returns (η_TD, step_index), where step_index is 1‐based.

    Parameters
    ----------
    dg      : zero‑bias ΔG array, length N
    el_steps: booleans, True if the step involves 1e–
    eq_pot  : equilibrium potential [V]

    Returns
    -------
    η_TD         : overpotential [V]
    step_index   : the step (1…N) where the largest ΔG occurs
    """
    dg = np.asarray(dg)
    el = np.asarray(el_steps, dtype=int)

    # Branch that each electrochemical step contributes -(eq_pot) to ΔG
    # so effective ΔG_i(U=0) = dg_i + el_i * eq_pot
    dg_shifted = dg + el * eq_pot

    # η_TD is the maximum uphill barrier
    idx = np.argmax(dg_shifted)  # 0-based
    eta = dg_shifted[idx]

    # step index in chemical ordering is idx+1
    return float(eta), int(idx + 1)


def compute_g_max(
    dg: Sequence[float], el_steps: Sequence[bool], op: float
) -> Tuple[float, Tuple[int, int]]:
    """
    Compute G_max over subsequences that begin on an electrochemical step,
    when held at an overpotential `op` above equilibrium.

    Parameters
    ----------
    dg      : zero‑bias ΔG array, length N
    el_steps: booleans, True if that step involves 1e–
    op      : overpotential above equilibrium (V)

    Returns
    -------
    G_max      : maximum uphill barrier [eV]
    (i, j)     : tuple of step‐indices (1‐based) between which G_max occurs
    """
    import numpy as np

    dg = np.asarray(dg, dtype=float)
    el = np.asarray(el_steps, dtype=bool)

    # bias only the electrochemical steps by op
    dg_biased = dg + el.astype(float) * op

    max_barrier = -np.inf
    best_i = best_j = None

    N = len(dg_biased)
    # Only consider subsequences starting at electrochemical steps
    for i in range(N):
        if not el[i]:
            continue
        run_sum = 0.0
        # accumulate from i through j inclusive
        for j in range(i, N):
            run_sum += dg_biased[j]
            if run_sum > max_barrier:
                max_barrier = run_sum
                best_i, best_j = i, j

    # Convert to 1-based indices
    return float(max_barrier), (best_i + 1, best_j + 1)
