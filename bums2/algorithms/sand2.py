#The following will apply the sand2 unfolding method
import subprocess
import time
from pathlib import Path
from typing import Tuple
import numpy as np
import contextlib

from bums2.core.config import Bums2Config
from bums2.FORTRAN_METHODS.SAND2.sand2_main import Sand2Pipeline

class sand2:
    def __init__(self, cfg: Bums2Config, workdir: Path = Path("sand2")):
        self.cfg = cfg
        self.workdir = workdir
        self.workdir.mkdir(exist_ok=True)
    
    def sand2_unfold(
            self,
            mat: np.ndarray,
            bce: np.ndarray,
            errbce: np.ndarray,
            spli: np.ndarray,
            num_groups: float,
            num_det: float,
            out: Path = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        #Perform SAND2 unfolding
        #Parameters:
        #mat : ndarray, shape(num_detectors, num_groups)
        #bce: ndarray, shape(num_detectors,), The measured counts
        #errbce: ndarray, shape(num_detectors,), The error of the measured counts
        #spli: ndarray, shape(num_groups,), The initial spectrum
        
        #Returns:
        #spl: ndarray, shape(num_groups,), The unfolded spectrum
        #splstart: ndarray, shape(num_groups,), The initial spectrum feed into maxed
        total_groups = num_groups + 1
        
        #First: write sand2/input_data
        inp = self.workdir / "input_data"
        with inp.open("w") as fh:
            fh.write(f"{num_det},{total_groups}\n")
            # per‐detector lines: index, count, error
            for i in range(num_det):
                fh.write(f"{i+1},{bce[i]},{errbce[i]}\n")
            # energy & initial spectrum
            for j in range(num_groups):
                fh.write(f"{self.cfg.e_end[j]},{spli[j]}\n")
            # final “zero” line
            fh.write(f"{self.cfg.e_end[num_groups]},0\n")
            # fixed control lines
            fh.write("2,3\n")
            # itrmax,1,1 (max iterations, chi_fac, dev)
            fh.write(f"{self.cfg.iter},1,1\n")

        #Second: write sand2/response
        resp = self.workdir / "response"
        with resp.open("w") as fh:
            fh.write(f"{num_det}\n")
            fh.write(f"{total_groups}\n")
            fh.write("cm**2\n")
            fh.write(f"{self.cfg.e_end[0]}\n")
            # each subsequent row is eend[j], mat[j,i] for i in detectors
            for i in range(total_groups - 1):  # i = 0 to num_groups - 1
                fh.write(f"{self.cfg.e_end[i + 1]}")  # Upper bin edge, equivalent to Perl's eend[i]
                for j in range(num_det):
                    fh.write(f",{mat[i][j]}")
                fh.write("\n")

        #Third: call the sand2 pipline to find spl and splstart
        pipeline = Sand2Pipeline(
            input_file= inp,
            response_file= resp,
            iqds= 2,
            iqbs= 3,
            max_iter= self.cfg.iter,
        )

        with open(out, "a") as f, contextlib.redirect_stdout(f):
            result = pipeline.run()

        spl = result["FSNEW"]
        splstart = result["FI"]

        return spl, splstart