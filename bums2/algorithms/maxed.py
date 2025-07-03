#The following will apply the maxed unfolding method
import subprocess
from pathlib import Path
from typing import Tuple, List
import numpy as np

from bums2.core.config import Bums2Config

class maxed:
    def __init__(self, cfg: Bums2Config, maxed_executable: Path = Path("/usr/local/bin/maxed"), workdir: Path = Path("maxed_data"),):
        self.cfg = cfg
        self.e_end = self.cfg.e_end
        self.maxed_exe = maxed_executable
        self.workdir = workdir
        self.workdir.mkdir(exist_ok=True)

    def maxed_unfold(
            self,
            mat: np.ndarray,
            bce: np.ndarray,
            errbce: np.ndarray,
            spli: np.ndarray,
            num_groups: float,
            num_det: float
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
            for j in range(1, total_groups):
                row = mat[j-1,:]
                vals = ",".join(str(x) for x in row)
                fh.write(f"{self.cfg.e_end[j]},{vals}\n")
        
        #Third: Invoke the external MAXED binaries
        res = subprocess.run(
            [str(self.maxed_exe)],
            cwd=self.workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )

        #Fourth: parse OUT.OUT
        out = self.workdir / "OUT.OUT"
        with out.open() as fh:
            #Skip the header lines
            fh.readline()
            fh.readline()

            spl = np.zeros(num_groups, dtype=float)
            splstart = np.zeros(num_groups, dtype=float)
            for j in range(num_groups):
                line = fh.readline().strip()
                parts = line.split()
                
                #Staying consistent with the perl indexing
                spl[j] = float(parts[4])
                splstart[j] = float(parts[3])
        return spl, splstart