#The following will parse any inputted spectrum given by a user using the cgi interface
import sys
import os
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Union
from urllib.parse import unquote
import cgi

from bums2.utils.rebin import Rebin
from bums2.core.config import Bums2Config

class UserSpectrumLoader:
    #The class will look into whether a user input spectrum was selected, then it will provide both
    #a CLI input or an input from the website.
    #If neither are detected, then it will defer to guess.py or maxiet.py depending on the selction

    def __init__(self, cfg: Bums2Config, matrix_endpoints: List[float]):
        self.cfg = cfg
        self.matrix_endpoints = matrix_endpoints
        self._raw_endpoints: List[float] = []
        self._raw_values: List[float] = []

    def load(self) -> List[float]:
        #Read in a two-column spectrum from CLI of CGI, rebin it, drop the first bin, and then return
        if "GATEWAY_INTERFACE" in os.environ:
            self._read_from_cgi()
        else:
            self._read_from_cli()
        
        #Perl applies a shift to the values before feeding it into the rebin
        self._raw_values = self._raw_values[1:]

        rebinned = Rebin(
            self._raw_endpoints,
            self._raw_values,
            self.cfg.e_end
        ).transform()

        #Same as Perl's version of shift
        rebinned  = rebinned[1:]

        return np.array(rebinned)
        
    
    #Pull spectrum file from CLI
    def _read_from_cli(self):
        path = input("Spectrum file path: ").strip()
        if not path:
            raise RuntimeError("No spectrum file path provided, aborting")
        lines = Path(path).read_text().splitlines()
        self._raw_endpoints, self._raw_values = self._parse_lines(lines)

    #Pull from CGI through file upload
    def _read_from_cgi(self):
        form = cgi.FieldStorage()
        item = form.getfirst("spectrum_file")
        if not getattr(item, "file", None):
            raise RuntimeError("No uploaded spectrum_file provided")
        raw = item.file.read().decode("utf-8").splitlines()
        self._raw_endpoints, self._raw_values = self._parse_lines(raw)
    
    #The following will actually parse the energy cutoffs and counts based on the spectrum
    @staticmethod
    def _parse_lines(lines: List[str]) -> Tuple[List[float], List[float]]:
        e_end, vals = [], []
        for raw in lines:
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split(None, 2)
            try:
                e_end.append(float(parts[0]))
                vals.append(float(parts[1]) if len(parts) > 1 else 0.0)
            except ValueError:
                continue
        return e_end, vals