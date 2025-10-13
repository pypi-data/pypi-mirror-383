#EC Toolkit

Electrochemical thermodynamics toolkit for VASP workflows:  
– Parse `OUTCAR` & `POSCAR`  
– Build reaction mechanisms from DFT energies, ZPE, and entropy  
– Compute ΔG profiles, overpotentials, & $G_{max}$
– Plot free‐energy diagrams

---

## Features

- **I/O parsers**
  - `OutcarParser.read_edft`, `read_zpe_tds`, `read_converged`, `auto_read`
  - `PoscarParser` backed by ASE, full support for selective dynamics
- **Data models**
  - `Compound`, `ElementaryStep`, `ReactionIntermediate`, `Mechanism`
- **Thermo analysis**
  - `compute_delta_g`, `compute_eta_td`, `compute_g_max`
- **Visualization**
  - `plot_free_energy` with optional η and $G_{max}$ annotations
- **Extensible**: CLI entry‐points, custom ZPE locators, caching, and more

---

## Installation

```bash
pip install ec-toolkit
```

---

## Quickstart

```python
from pathlib import Path
import matplotlib.pyplot as plt

from ec_toolkit.io.outcar import OutcarParser
from ec_toolkit.models.classes import Compound, ElementaryStep, ReactionIntermediate, Mechanism
from ec_toolkit.analysis.thermodynamics import compute_delta_g
from ec_toolkit.visualization.plotting import plot_free_energy

# 1) Read energies from VASP runs
workdir = Path("my_vasp_runs")
steps   = ["s1", "s2", "s3"]
edfts, zpes, tdss = OutcarParser.auto_read(
    workdir, steps, calc_tds=True
)

# 2) Wrap as Compounds
compounds = {
    name: Compound(name, {"dft": e, "zpe": z, "tds": t}, converged=True)
    for name, e, z, t in zip(steps, edfts, zpes, tdss)
}

# 3) Define stoichiometry & build ReactionIntermediate
stoich1 = { compounds["s1"]:-1, compounds["s2"]: +1 }
stoich2 = { compounds["s2"]:-1, compounds["s3"]: +1 }

ri1 = ReactionIntermediate(ElementaryStep(stoich1), label="s1→s2", is_electrochemical=True)
ri2 = ReactionIntermediate(ElementaryStep(stoich2), label="s2→s3", is_electrochemical=False)

# 4) Assemble Mechanism & compute ΔG profile
mech = Mechanism([ri1, ri2], eq_pot=1.23)
dg0  = compute_delta_g(mech.dE_array, mech.dZPE_array, mech.dTS_array, mech.el_steps, mech.eq_pot)

# 5) Plot
fig, ax = plt.subplots()
plot_free_energy(dg0, mech.el_steps, mech.labels, eq_pot=mech.eq_pot, annotate_eta=True)
plt.tight_layout()
plt.show()
```

### Custom ZPE locator

By default ZPE/TdS is looked for under s1/zpe/OUTCAR, but you can customize. If your ZPE runs live elsewhere (e.g. in step1_zpe), pass your own locator:

```python
def my_zpe_locator(wd: Path, step: str) -> Path:
    return wd / f"{step}_zpe" / "OUTCAR"

edfts, zpes, tdss = OutcarParser.auto_read(
    workdir, steps, calc_tds=True,
    zpe_locator=my_zpe_locator
)
```

---

## License

This project is released under the MIT License. See [License](./LICENSE) for details.

---

## Contributors

- Noel Marks
- Maksim Sokolov
