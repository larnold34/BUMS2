#The following will apply the maxed unfolding method
import subprocess
from pathlib import Path
from typing import Tuple, List
import numpy as np
import contextlib

from bums2.core.config import Bums2Config
from bums2.FORTRAN_METHODS.MAXED.driver.maxed_main import MaxedPipeline

class maxed:
    def __init__(self, cfg: Bums2Config, workdir: Path = Path("maxed_data")):
        self.cfg = cfg
        self.e_end = self.cfg.e_end
        self.workdir = workdir
        self.workdir.mkdir(exist_ok=True)

    def maxed_unfold(
            self,
            mat: np.ndarray,
            bce: np.ndarray,
            errbce: np.ndarray,
            spli: np.ndarray,
            num_groups: float,
            num_det: float,
            out: Path = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        #Perform MAXED unfolding
        #Parameters:
        #mat : ndarray, shape(num_detectors, num_groups), The response matrix
        #bce: ndarray, shape(num_detectors,), The measured counts
        #errbce: ndarray, shape(num_detectors,), The error of the measured counts
        #spli: ndarray, shape(num_groups,), The initial spectrum
        
        #Returns:
        #spl: ndarray, shape(num_groups,), The unfolded spectrum
        #splstart: ndarray, shape(num_groups,), The initial spectrum feed into maxed
        total_groups = num_groups+1

        #Frist: write input_data file
        inp = self.workdir / "input_data"
        with inp.open("w") as fh:
            fh.write(f"{num_det},{total_groups}\n")

            #For detector lines index out bce and errbce
            for i in range(num_det):
                fh.write(f"{i+1},{bce[i]},{errbce[i]}\n")

            #Parse the energy and initial spectrum values
            for j in range(num_groups):
                fh.write(f"{self.cfg.e_end[j]},{spli[j]}\n")
            fh.write(f"{self.cfg.e_end[num_groups]},0\n")

            #Some harcoded lines from the original perl file
            fh.write("2,3\n")
            fh.write("1,0.85\n")

        #Second: write a response file
        resp = self.workdir / "response"
        with resp.open("w") as fh:
            fh.write(f"{num_det}\n")
            fh.write(f"{total_groups}\n")
            fh.write(f"cm**2\n")

            #First energy endpoint
            fh.write(f"{self.cfg.e_end[0]}\n")

            #Form the response matrix where each line is eend[j],value
            for i in range(total_groups - 1):  # i = 0 to num_groups - 1
                fh.write(f"{self.cfg.e_end[i + 1]}")  # Upper bin edge, equivalent to Perl's eend[i]
                for j in range(num_det):
                    fh.write(f",{mat[i][j]}")
                fh.write("\n")
        
        #Third: Call the maxed pipeline and find spl and splstart
        pipeline = MaxedPipeline(
            input_file= inp,
            response_file= resp,
            iqds=2,
            iqbs=3,
        )
        
        with open(out, "a") as f, contextlib.redirect_stdout(f):
            result = pipeline.run()

        spl = result["FL"]
        splstart = result["FIL"]
      
        return spl, splstart