from functools import cached_property
from dataclasses import dataclass
import numpy as np
import pathlib as Path
from ec_toolkit.io.outcar import OutcarParser


class Compound:
    """
    Models a chemical species with its reference energies and convergence metadata.
    """

    def __init__(
        self,
        formula: str,
        reference_energies: dict[str, float],
        converged: bool = True,
        convergence_info: dict[str, float] | None = None,  # optional metadata
    ):
        self.formula = formula
        self.reference_energies = reference_energies
        self.converged = converged
        # store any extra convergence metrics; if None, defaults to empty dict
        self.convergence_info = convergence_info or {}

    def energy(self, kind: str = "dft") -> float:
        return self.reference_energies.get(kind, 0.0)

    def is_stable(self) -> bool:
        force = self.convergence_info.get("max_force", 0.0)
        return self.converged and force < self.convergence_info.get(
            "force_threshold", float("inf")
        )

    def __repr__(self):
        refs = ", ".join(f"{k}={v:.3f}" for k, v in self.reference_energies.items())
        status = "OK" if self.converged else "FAILED"
        return f"{self.formula}({refs}, status={status})"

    @classmethod
    def from_outcar(cls, path: Path, temp: float = 298.15):
        e = OutcarParser.read_edft(path)
        z, t = OutcarParser.read_zpe_tds(path, calc_tds=True)
        conv = OutcarParser.read_converged(path)
        return cls(path.name, {"dft": e, "zpe": z, "tds": t}, converged=conv)


class ElementaryStep:
    """
    Captures the stoichiometry of a single reaction step.
    Maps each `Compound` to a signed coefficient (negative for reactants).
    """

    def __init__(self, stoich: dict[Compound, float]):
        self.stoich = stoich

    def __repr__(self):
        # List products (coeff > 0) first, then reactants (coeff < 0)
        prods = [(c, v) for c, v in self.stoich.items() if v > 0]
        reacs = [(c, v) for c, v in self.stoich.items() if v < 0]
        parts = []
        for comp, coeff in prods + reacs:
            parts.append(f"{coeff:+g} {comp.formula}")
        return " ".join(parts)


@dataclass
class ReactionIntermediate:
    elementary: ElementaryStep
    label: str
    is_electrochemical: bool

    @cached_property
    def dE(self) -> float:
        return sum(
            comp.energy("dft") * coeff for comp, coeff in self.elementary.stoich.items()
        )

    @cached_property
    def dZPE(self) -> float:
        return sum(
            comp.energy("zpe") * coeff for comp, coeff in self.elementary.stoich.items()
        )

    @cached_property
    def dTS(self) -> float:
        return sum(
            comp.energy("tds") * coeff for comp, coeff in self.elementary.stoich.items()
        )


class Mechanism:
    """
    A sequence of ``ReactionIntermediate`` instances representing a full catalytic
    pathway, plus metadata (equilibrium potential, symmetry factor, reference electrode).
    """

    def __init__(
        self,
        steps: list[ReactionIntermediate],
        eq_pot: float,
        sym_fac: int = 1,
        ref_el: str = "RHE",
    ):
        # 1. steps must be a non‐empty list of ReactionStep
        if not isinstance(steps, list) or len(steps) == 0:
            raise ValueError(
                "`steps` must be a non‐empty list of ReactionStep instances."
            )
        for idx, s in enumerate(steps):
            if not isinstance(s, ReactionIntermediate):
                raise TypeError(f"steps[{idx}] is not a ReactionStep (got {type(s)})")

        # 2) eq_pot must be numeric
        if not isinstance(eq_pot, (int, float)):
            raise TypeError("`eq_pot` must be a number (int or float).")

        # 3. sym_fac should be a positive integer
        if not isinstance(sym_fac, int) or sym_fac < 1:
            raise ValueError("`sym_fac` must be a positive integer")

        # 4. ref_el should be a non‐empty string
        if not isinstance(ref_el, str) or ref_el.strip() == "":
            raise ValueError("`ref_el` must be a non‐empty string")

        self.steps = steps
        self.eq_pot = eq_pot
        self.sym_fac = sym_fac
        self.ref_el = ref_el
        self.el_steps = [step.is_electrochemical for step in steps]
        self.labels = [step.label for step in steps]

    @property
    def dE_array(self) -> np.ndarray:
        return np.array([s.dE for s in self.steps])

    @property
    def dZPE_array(self) -> np.ndarray:
        return np.array([s.dZPE for s in self.steps])

    @property
    def dTS_array(self) -> np.ndarray:
        return np.array([s.dTS for s in self.steps])

    def set_labels(self, new_labels: list[str]):
        if len(new_labels) != len(self.steps):
            raise ValueError("Label count mismatch")
        self.labels = new_labels
