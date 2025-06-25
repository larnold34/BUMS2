#The following will be used to load up the selected response matrix selected in the either input
import logging
from pathlib import Path
from typing import List, Tuple
import numpy as np

from bums2.core.config import Bums2Config

logger = logging.getLogger(__name__)

# The following class will hold a Bonner-sphere response matrix, where:
# e_end: 1D array of energy bin endpoints
# mat: 2D array shape (n_bins, n_det) of response values
# num_bins: number of usable energy bins

class ResponseMatrix:
    def __init__(self, e_end: np.ndarray, mat: np.ndarray, num_bins: int):
        self.e_end = e_end
        self.mat = mat
        self.num_bins = num_bins

    @classmethod
    def from_config(cls, cfg: Bums2Config, matrix_dir: Path = Path("matrix")):
        rm = cls.from_file(
                matrix_name = cfg.matrix_name,
                detector_mask= cfg.detector_mask,
                max_energy= cfg.max_energy,
                matrix_dir= matrix_dir)
        cfg.e_end = list(rm.e_end)
        return rm
    
    #The following will load in a response matrix from matrix/matrix_name. And skip any commentted lines
    #Each response matrix should have the following structure
    #The first column is energy bins
    #Each column after that is a specific detector in full order, but only mark the columns being used
    #Collect rows until energy > max_energy
    @classmethod
    def from_file(cls, matrix_name: str, detector_mask: List[bool], max_energy: float, matrix_dir: Path = Path("matrix")) -> "ResponseMatrix":
        path = matrix_dir / matrix_name
        logger.debug(f"Attempting to open '{matrix_name}' @ {path}")
        energies = []
        rows = []
        with path.open() as fh:
            first = fh.readline()  #Skip the header
            for line in fh:
                line = line.strip()
                if not line or line .startswith("#"):
                    continue
                parts = line.replace(",", " ").split()

                #Find first non-numeric start, drop any leading labels
                while parts and not parts[0].replace(".", "", 1).replace("E", "", 1).replace("+", "", 1).replace("-", "", 1).isdigit():
                    parts.pop(0)
                if not parts:
                    continue
                e = float(parts[0])
                vals = [float(v) for v in parts[1:]]

                #Same sanity check as the original perl script
                if len(vals) != len(detector_mask):
                    raise ValueError(f"Matrix file '{matrix_name}' has {len(vals)} cols; expected {len(detector_mask)} detectors")
                
                if e <= max_energy:
                    energies.append(e)
                    rows.append([v for v, use in zip(vals, detector_mask) if use])
                else:
                    break
        if not energies:
            raise ValueError(f"No bins ≤ max_energy={max_energy} in {matrix_name}")
        
        #Staying consistent with the perl logic, remove the last bin
        num_bins = len(energies)-1
        logger.debug(f"loaded {len(energies)} bins; using first {num_bins}")

        e_end = np.array(energies)
        mat = np.array(rows)[:num_bins, :]

        #Further trim away any trailing zero sum bins
        sums = mat.sum(axis=1)
        zero_idxs = np.where(sums == 0)[0]
        if zero_idxs.size:
            cutoff = zero_idxs[0]
            logger.debug(f"zero-sum detected at bin {cutoff}, trimming")
            mat = mat[:cutoff, :]
            e_end = e_end[:cutoff]
            num_bins = cutoff
        return cls(e_end=e_end, mat=mat, num_bins=num_bins)
