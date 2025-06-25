#This file will be the other initial spectrum algorithm, and will also include the logic of dir_read.pl
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

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
                parts = line.strip().split()
                if len(parts) >= 2:
                    ends.append(float(parts[0]))
                    vals.append(float(parts[1]))
        return header, np.array(ends), np.array(vals)
    
    def guess(self) -> Tuple[str, np.ndarray]:
        #If Automatic is selected apply the original logic
        best_file: Optional[Path]
        best_chi = np.inf

        if "Automatic" in self.cfg.start_spec:
            for spec_path in self._list_spectra():
                header, e_end_in, val_in = self._load_spectrum(spec_path)

                #Rebin into matrix bins
                spli = Rebin(
                    old_edges= e_end_in.tolist(),
                    old_values= val_in.tolist(),
                    new_edges= self.cfg.e_end
                ).transform()

                #Drop the first bin
                spli = spli[1:]

                #Run the pipline
                alethnew, prog_spl = self.standardize.trans_mat(
                    aleth= self._response_matrix, #Will need to change after making driver
                    spli=spli
                )

                #Normalize
                norm_spl = self.standardize.normalize(
                    initial_spectrum= prog_spl.tolist(),
                    response_matrix= alethnew.tolist(),
                    measured_counts= self.cfg.measured_counts,
                )

                #Cal_response
                bcc = self.standardize.cal_response(alethnew= np.array(alethnew), spl= np.array(norm_spl))

                #Fit error, will need to edit when the driver is made. weights should be whtbce
                fit_err = self.standardize.fit_error(measured= self.cfg.measured_counts, model= bcc.tolist(), weights= self.cfg.measured_errors)

                #Chi squared
                chi = self.standardize.chi_squared(measured= self.cfg.measured_counts, model= bcc.tolist(), errors= self.cfg.measured_errors)

                if chi < best_chi:
                    best_chi = chi
                    best_file = spec_path
                
                print("-" * 80)
                chosen = best_file
        
        else:
            #Specified initial spectrum
            chosen = self.spectra_dir / self.cfg.start_spec

            #Rebin the chosen spectrum only
            _, e_end2, val2 = self._load_spectrum(chosen)
            spli2 = Rebin(
               old_edges= e_end2,
               old_values= val2,
               new_edges= self.cfg.e_end
            )[1:]
        return chosen.name, spli2