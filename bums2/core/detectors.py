#This file will apply all the calculations done from the original detector_response.pl file.
from pathlib import Path
from typing import List, Tuple, Dict
import warnings
import re
from html import unescape

from bums2.utils.interpolate import Interpolator
from bums2.utils.dose import DoseConverter

class ResponseCurve:
    def __init__(self, path: Path):
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) < 3:
            raise ValueError(f"{path} does not look like a valid dose file")
        raw = lines[0].strip()
        decoded = unescape(raw)
        clean = re.sub(r'<[^>]+>', '', decoded)
        self.name = clean
        self.units = lines[1].strip()
        data = []
        for L in lines[2:]:
            L = L.strip()
            if not L:
                continue
            parts = L.split()
            if len(parts) != 2:
                continue
            e, v = parts
            data.append((float(e), float(v)))
        if not data:
            raise ValueError(f"{path} contained no data points")
        self.energies, self.values = zip(*data)

    def apply(self, ce: List[float], spectrum: List[float]) -> float:
        tot = 0.0
        for j, (e, val) in enumerate(zip(ce, spectrum)):
            y = Interpolator.log_linear(e, list(self.energies), list(self.values))
            contrib = val * y
            tot += contrib
        return tot


class DetectorResponses:
    # the file‐stem order you want to print in
    DOSE_ORDER = [
        "ICRP74_effective_dose_RLAT",
        "ICRP74_effective_dose_AP",
        "dose_from_gamma_n",
        "ICRU25_dose_equivalent_index",
        "tissue_kerma",
        "ICRP74_personal_dose_equivalent",
        "ICRP74_ambient_dose_equivalent",
        "charged_particle_dose",
        "ICRP74_effective_dose_PA",
        "ICRP74_effective_dose_LLAT",
        "ICRP74_effective_dose_ROT",       
        "ICRP74_effective_dose_ISO",

    ]

    RESPONSE_ORDER = [
        "nta",
        "hankins_tld",
        "nrl_tld",
        "anpdr70",
        "neutrak_144",
        "LB6411",
    ]

    def __init__(
        self,
        ce: List[float],
        values: List[float],
        dose_dir: Path = Path("dose"),
        response_dir: Path = Path("response"),
    ):
        # Ensure we have Path objects:
        dose_dir = Path(dose_dir)
        response_dir = Path(response_dir)

        # Try lowercase first, then uppercase folder name if missing:
        if not dose_dir.exists():
            alt = Path(str(dose_dir).upper())
            if alt.exists():
                dose_dir = alt

        if not response_dir.exists():
            alt = Path(str(response_dir).upper())
            if alt.exists():
                response_dir = alt

        self.ce = ce
        self.values = values
        self.dose_dir = dose_dir
        self.response_dir = response_dir
        self._dc = DoseConverter()

    def dose_functions(self) -> List[Tuple[str, float, str]]:
        results: Dict[str, Tuple[str, float, str]] = {}

        # --- build a dict keyed by the *stem* (filename without extension) ---
        for p in self.dose_dir.iterdir():
            if not p.is_file():
                continue
            stem = p.stem
            curve = ResponseCurve(p)
            s = curve.apply(self.ce, self.values)
            # *KEY* by stem, *not* by curve.name
            results[stem] = (curve.name, s, curve.units)

        # --- now pull them out in the exact order you want ---
        out: List[Tuple[str, float, str]] = []
        for stem in self.DOSE_ORDER:
            if stem not in results:
                warnings.warn(f"Missing dose curve: {stem}")
                continue
            out.append(results[stem])

        return out



    def standard_equivalent(self) -> List[Tuple[str, float, str]]:
        specs = [
            (10, 1, "ICRP-21 Dose Equivalent H"),
            (20, 5, "NCRP-38 Dose Equivalent H"),
            (31, 5, "ANSI/ANS-6.1.1-1991 Equivalent Dose AP (Ht)"),
            (32, 5, "ANSI/ANS-6.1.1-1991 Equivalent Dose PA (Ht)"),
            (33, 5, "ANSI/ANS-6.1.1-1991 Equivalent Dose LAT (Ht)"),
            (34, 5, "ANSI/ANS-6.1.1-1991 Equivalent Dose ROT (Ht)"),
        ]
        out = []
        for ic, it, label in specs:
            total = 0.0
            for e, v in zip(self.ce, self.values):
                df = self._dc.dfact(1, ic, e, it, 2, 1.0 / 3600) * 1e12
                total += v * df
            out.append((label, total, "pSv"))
        return out

    def detector_response(self) -> List[Tuple[str, float, str]]:
        results = {}
        for p in sorted(self.response_dir.iterdir()):
            if not p.is_file():
                continue
            stem = p.stem
            curve = ResponseCurve(p)
            s = curve.apply(self.ce, self.values)
            results[stem] = (curve.name, s, curve.units)

        out = []
        for stem in self.RESPONSE_ORDER:
            if stem not in results:
                warnings.warn(f"Missing response curve: {stem}")
                continue
            out.append(results[stem])
        return out
