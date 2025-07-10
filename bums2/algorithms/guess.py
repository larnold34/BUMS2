#This file will be the other initial spectrum algorithm, and will also include the logic of dir_read.pl
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np
import re
import sys

from bums2.core.config import Bums2Config
from bums2.core.standardize import Standardize
from bums2.utils.rebin import Rebin


# This program scans the guesses listed in the spectra directory
#Outline
#_______
# Read spectrum file
# Rebin spectrum to matrix energy bins 
#
class SpectrumGuesser:
    def __init__(self, cfg: Bums2Config, standardize: Standardize, spectra_dir: Path = Path("spectra")):
        self.cfg = cfg
        self.standardize = standardize
        self.spectra_dir = spectra_dir

    def _list_spectra(self) -> List[Path]:
        #This function will be like dir_read
        return [p for p in sorted(self.spectra_dir.iterdir())
                if p.is_file() and not p.name.startswith(".")]
    
    def _load_spectrum(self, path: Path) -> Tuple[str, np.ndarray, np.ndarray]:
        #Read in header and two-column data
        with path.open() as fh:
            header = fh.readline().strip()
            ends, vals = [], []
            for line in fh:
                parts = re.split(r"[,\s]+", line.strip())
                if len(parts) >= 2:
                    ends.append(float(parts[0]))
                    vals.append(float(parts[1]))
        return header, np.array(ends), np.array(vals)
    
    def guess(self, out) -> Tuple[str, np.ndarray]:
        #If Automatic is selected apply the original logic
        chosen: None
        best_chi = np.inf
        spli = np.zeros(self.cfg.num_groups, dtype=float)

        if self.cfg.start_spec.upper().startswith("AUTOMATIC"):
            print("Starting Spectra      Chi - Squared", file=out)
            print("---------------       -----------", file=out)

            for spec_path in self._list_spectra():
                #Load in name and two column data
                header, e_end_in, val_in = self._load_spectrum(spec_path)
                print(f"{header:20s}", end=" ", file=out)

                val_in = val_in[1:]
                #Rebin the spectrum
                val1 = Rebin(
                    old_edges=e_end_in,
                    old_values=val_in,
                    new_edges=self.cfg.e_end
                ).transform()

                candidate_spli = val1[1:].copy()
                
                #Apply standarization pipelne
                alethnew, prog_spl = self.standardize.trans_mat(
                    aleth= self.cfg.aleth,
                    spli = np.array(candidate_spli, dtype=float)
                )

                norm_spl = self.standardize.normalize(
                    bce=self.cfg.bce,
                    errbce=self.cfg.errbce,
                    response=alethnew,
                    num_det=self.cfg.num_det,
                    num_grps=self.cfg.num_groups,
                    flux=prog_spl
                )

                bcc = self.standardize.cal_response(
                    alethnew=np.array(alethnew),
                    spl=norm_spl
                )


                chi = self.standardize.chi_squared(
                    num_det=self.cfg.num_det,
                    bce=self.cfg.bce,
                    bcc=bcc.tolist(),
                    errbce=self.cfg.errbce
                )

                print(f"{chi:11.3E}", file=out)
                if chi < best_chi:
                    best_chi = chi
                    chosen = spec_path
                    spli = candidate_spli
        
        else:
            #Specified initial spectrum
            chosen = self.spectra_dir / self.cfg.start_spec

            #Rebin the chosen spectrum only
            _, e_end2, val2 = self._load_spectrum(chosen)
            val2 = val2[1:]
            full = Rebin(
               old_edges= e_end2,
               old_values= val2,
               new_edges= self.cfg.e_end
            ).transform()

            spli = full[1:].copy()
        return chosen, spli