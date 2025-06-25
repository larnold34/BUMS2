#This file will apply all the calculations done from the original detector_response.pl file.
from pathlib import Path
from typing import List, Tuple
import re

from bums2.utils.interpolate import Interpolator
from bums2.utils.dose import DoseConverter

#The first class will load in the dose file and parse it
class ResponseCurve:
    def __init__(self, path: Path):
        lines  = path.read_text(encoding="utf-8").splitlines()
        if len(lines) < 3:
            raise ValueError(f"{path} does not look like a valid dose file")
        self.name = lines[0].strip()
        self.units = lines[1]. strip()
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
        for e, val in zip(ce, spectrum):
            y = Interpolator.log_linear(e, list(self.energies), list(self.values))
            tot += val*y
        return tot
    
#The second class will apply all the calculations associated with the files within dose and response directories
class DetectorResponses:
    def __init__(self, ce: List[float], values: List[float], dose_dir: Path = Path("dose"), response_dir: Path = Path("response"),):
        self.ce = ce
        self.values = values
        self.dose_dir = dose_dir
        self.response_dir = response_dir
        self._dc = DoseConverter()

    def dose_functions(self) -> List[Tuple[str, float, str]]:
        out = []
        for p in sorted(self.dose_dir.iterdir()):
            if not p.is_file(): continue
            curve = ResponseCurve(p)
            s = curve.apply(self.ce, self.values)
            out.append((curve.name, s, curve.units))
        return out
    
    def standard_equivalent(self) -> List[Tuple[str, float, str]]:
        #This function will do the calculations associated with the following:
        #ICRP-21
        #NCRP-38
        #ANSI/ANS-6.1.1-1991 AP
        #ANSI/ANS-6.1.1-1991 PA
        #ANSI/ANS-6.1.1-1991 LAT
        #ANSI/ANS-6.1.1-1991 ROT
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
                df = self._dc.dfact(1, ic, e, it, 2, 1.0/3600) * 1e12
                total += v * df
            out.append((label, total, "pSv"))
        return out
    
    def detector_response(self) -> List[Tuple[str, float, str]]:
        out = []
        for p in sorted(self.response_dir.iterdir()):
            if not p.is_file(): continue
            curve = ResponseCurve(p)
            s = curve.apply(self.ce, self.values)
            out.append((curve.name, s, curve.units))
        return out

        
