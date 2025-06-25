#The following will parse any inputted spectrum given by a user using the cgi interface
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Union
from urllib.parse import unquote
import cgi

from utils.rebin import rebin
from core.config import Bums2Config

class UserSpectrumLoader:
    #The class will look into whether a user input spectrum was selected, then it will provide both
    #a CLI input or an input from the website.
    #If neither are detected, then it will defer to guess.py or maxiet.py depending on the selction

    def __init__(self, cfg: Bums2Config, matrix_endpoints: List[float]):
        self.cfg = cfg
        self.matrix_endpoints = matrix_endpoints
        self._raw_endpoints = List[float] = []
        self._raw_values = List[float] = []

    def _load_initial(self) -> List[float]:
        mode = self.cfg.start_spec.lower()
        if mode.startwith("user"):
            self.read_user_spectrum()
            spli = self._rebin_to_matrix()
            return spli[1:]
        elif mode.startwith("auto"):
            from algotithms.guess import guess_initial_spectrum
            return guess_initial_spectrum(self.cfg, self.matrix_endpoints)
        elif "maxiet" in mode:
            from alorithms.maxiet import maxiet_initial_spectrum
            return maxiet_initial_spectrum(self.cfg, self.matrix_endpoints)
        else:
            raise RuntimeError(f"Unknown start_spec: {self.cfg.start_spec!r}")
        
    
    #Populate _raw_values and _raw_endpoints
    def _read_user_spectrum(self) -> None:
        if self.cfg.user_spectrum_file:
            self._raw_endpoints, self._raw_values = self._load_from_file(self.cfg.user_spectrum_file)
        else:
            self._raw_endpoints, self._raw_values = self._load_from_cgi("spectrum_file")

    #Pull from a user spectrum file when using CLI
    def _load_from_file(self, path: Union[str, Path]) -> Tuple[List[float], List[float]]:
        text = Path(path).read_text(encoding="utf-8").splitlines()
        return self._parse_lines(text)
    
    #Pull from cgi input
    def _load_from_cgi_upload(self, field_name: str) -> Tuple[List[float], List[float]]:
        form = cgi.FieldStorage()
        item = form[field_name]
        if not getattr(item, "file", None):
            raise ValueError(f"No uploaded file under field {field_name!r}")
        raw = item.file.read().decode("utf-8").splitlines()
        return self._parse_lines(raw)
    
    #The following will actually parse the energy cutoffs and counts based on the spectrum
    @staticmethod
    def _parse_lines(lines: List[str]) -> Tuple[List[float], List[float]]:
        e_end, vals = [], []
        for raw in lines:
            s = raw.strip()
            if not s or s.startwith("#"):
                continue
            parts = s.split()
            try:
                e_end.append(float(parts[0]))
                vals.append(float(parts[1]) if len(parts) > 1 else 0.0)
            except ValueError:
                continue
        return e_end, vals
    
    #Call the rebin.py script to rebin the user input spectrum
    def _rebin_to_matrix(self) -> List[float]:
        return rebin(len(self.matrix_endpoints), len(self._raw_endpoints), 1, self._raw_endpoints, self._raw_values, self.matrix_endpoints)
    
    