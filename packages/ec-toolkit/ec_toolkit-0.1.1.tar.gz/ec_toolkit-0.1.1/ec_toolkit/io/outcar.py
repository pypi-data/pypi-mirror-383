from pathlib import Path
import numpy as np
from typing import Callable, Sequence
from ec_toolkit.io.vasp_helpers import read_reverse_order, read_positions_block
import math
from astropy import constants as const
from astropy import units as u
import warnings


class OutcarParser:
    """
    Parses VASP OUTCAR files for:
      - EDFT: the final electronic energy (eV),
      - ZPE: the summed zero-point correction (eV),
      - TΔS: the harmonic-approximate entropic term (eV) at 300 K (optional).
    """

    @staticmethod
    def read_edft(path: Path) -> float:
        """
        Scan the file in reverse order, find the last line containing 'sigma'
        (which VASP writes alongside the final electronic energy), and return it.
        """
        for line in read_reverse_order(path, max_lines=2000):
            if "sigma" in line.lower():
                return float(line.split()[-1])
        raise RuntimeError(f"No electronic energy ('sigma') line found in {path!r}")

    # default temperature (K) for TΔS; override if needed
    T: float = 298.15

    @staticmethod
    def read_zpe_tds(path: Path, calc_tds: bool = True) -> tuple[float, float]:
        """
        Computes zero‑point energy (ZPE) and vibrational entropy correction (TΔS)
        from a phonon-calculation OUTCAR, returning both in eV per molecule.

        Parameters
        ----------
        path : Path
            Path to the ZPE-calculation OUTCAR file.
        calc_tds : bool
            If False, returns (ZPE, 0.0). If True, computes TΔS at temperature `OutcarParser.T`.

        Returns
        -------
        (ZPE_eV, TDS_eV) : tuple[float,float]
            Zero‑point energy and entropy correction in eV per molecule.
        """
        # 1) Read raw frequencies in cm^-1
        freqs_cm = []
        with open(path, "r") as f:
            for line in f:
                # match lines like "  f  =    100.0 cm-1   0.0123 meV"
                if "cm-1" in line and "f/i" not in line:
                    parts = line.split()
                    try:
                        # your original code used index -2 for meV; here we want cm-1 at index 7
                        nu_cm = float(parts[7])
                        freqs_cm.append(nu_cm)
                    except (IndexError, ValueError):
                        continue

        if not freqs_cm:
            # no frequencies → zero ZPE; if TDS requested, still zero
            return 0.0, 0.0

        # Convert to astropy quantities (Hz):
        #   ν [cm^-1] → (ν * u.cm**-1) * c  → yields Hz
        freqs = u.Quantity(freqs_cm, u.cm**-1).to(u.m**-1) * const.c

        # --- ZPE: ½ h ν per mode ---
        zpe_per_mode = 0.5 * const.h * freqs  # J per molecule
        zpe_eV = zpe_per_mode.sum().to(u.eV).value

        # If TΔS disabled, return now
        if not calc_tds:
            return zpe_eV, 0.0

        # --- TΔS at temperature T ---
        T_q = OutcarParser.T * u.K

        # Floor frequencies below 50 cm^-1 for entropy
        freqs_floor = (
            u.Quantity([max(nu, 50.0) for nu in freqs_cm], u.cm**-1).to(u.m**-1)
            * const.c
        )

        # dimensionless x = h ν / (k_B T)
        x_arr = (const.h * freqs_floor) / (const.k_B * T_q)

        # compute entropy per mode: s_i = k_B [ x/(e^x -1) - ln(1 - e^-x) ]
        s_list = []
        for x in x_arr:
            xv = x.value
            try:
                term1 = xv / (math.exp(xv) - 1.0)
            except OverflowError:
                term1 = 0.0
            term2 = math.log(1.0 - math.exp(-xv))
            s_i = const.k_B * (term1 - term2)  # J / (K·molecule)
            s_list.append(s_i)

        s_total = u.Quantity(s_list).sum()  # J / (K·molecule)
        tds_J = (s_total * T_q).to(u.J)  # J / molecule
        tds_eV = tds_J.to(u.eV).value  # eV / molecule

        return zpe_eV, tds_eV

    @staticmethod
    def read_converged(path: Path) -> bool:
        """
        Checks if the structure is converged.

        Return True if the OUTCAR ended with
        'reached required accuracy - stopping structural energy minimisation'
        indicating the ionic relaxation converged.
        """
        # We only need to check the last few hundred lines, not the whole file
        lines = list(read_reverse_order(path, max_lines=2000))
        return any("reached required accuracy" in line.lower() for line in lines[:200])

    @classmethod
    def auto_read(
        cls,
        workdir: Path,
        subdirs: Sequence[str],
        *,
        calc_tds: bool = False,
        zpe_locator: Callable[[Path, str], Path] | None = None,
        check_structure: bool = False,
    ) -> tuple[list[float], list[float], list[float], list[bool] | None]:
        """
        Goes through each dir and combines the other classmethods.

        For each folder in `subdirs` under `workdir`, read:
          - EDFT       ← workdir/d/OUTCAR
          - ZPE & TΔS  ← path returned by zpe_locator(workdir, d)
        Optionally:
          - read_converged from the EDFT OUTCAR
          - if check_structure=True, verify last-step positions in EDFT
            match first-step positions in ZPE exactly.

        Returns (edft_list, zpe_list, tds_list) or, if check_structure,
        (edft_list, zpe_list, tds_list, conv_list).
        """
        # default: look in workdir/d/zpe/OUTCAR
        if zpe_locator is None:

            def zpe_locator(wd: Path, d: str) -> Path:
                return wd / d / "zpe" / "OUTCAR"

        edfts: list[float] = []
        zpes: list[float] = []
        tdss: list[float] = []
        convs: list[bool] = []

        for d in subdirs:
            base = workdir / d
            efile = base / "OUTCAR"
            edft = cls.read_edft(efile)
            edfts.append(edft)

            # ZPE + TΔS
            zfile = zpe_locator(workdir, d)
            if zfile.exists():
                zpe, tds = cls.read_zpe_tds(zfile, calc_tds)
            else:
                # **warn** that we couldn't find a ZPE OUTCAR here
                warnings.warn(
                    f"No ZPE/TdS OUTCAR found at {zfile!r}; setting ZPE and TdS to 0",
                    UserWarning,
                    stacklevel=2,
                )
                zpe, tds = 0.0, 0.0
            zpes.append(zpe)
            tdss.append(tds)

            # convergence of the energy run itself
            is_conv = cls.read_converged(efile)
            if check_structure and zfile.exists():
                last_pos = read_positions_block(efile, first=False)
                first_pos = read_positions_block(zfile, first=True)
                is_conv &= np.array_equal(last_pos, first_pos)
            convs.append(is_conv)

        if check_structure:
            return edfts, zpes, tdss, convs
        return edfts, zpes, tdss
