#The following will apply the sand2 unfolding method
import subprocess
import time
from pathlib import Path
from typing import Tuple
import numpy as np

from bums2.core.config import Bums2Config

class sand2:
    def __init__(self, cfg: Bums2Config, sand2_exectable: Path = Path("/usr/local/bin/sand2"), workdir: Path = Path("sand2")):
        self.cfg = cfg
        self.sand2_exe = sand2_exectable
        self.workdir = workdir
        self.workdir.mkdir(exist_ok=True)
    
    def sand2_unfold(
            self,
            mat: np.ndarray,
            bce: np.ndarray,
            errbce: np.ndarray,
            spli: np.ndarray,
            num_groups: float,
            num_det: float
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
            # itrmax,1,1  (SANDII wants max‐iterations and two flags)
            fh.write(f"{self.cfg.iter},1,1\n")

        #Second: write sand2/response
        resp = self.workdir / "response"
        with resp.open("w") as fh:
            fh.write(f"{num_det}\n")
            fh.write(f"{total_groups}\n")
            fh.write("cm**2\n")
            fh.write(f"{self.cfg.e_end[0]}\n")
            # each subsequent row is eend[j], mat[j,i] for i in detectors
            for j in range(1, total_groups):
                row = mat[:, j-1]
                vals = ",".join(str(v) for v in row)
                fh.write(f"{self.cfg.e_end[j]},{vals}\n")

        #Third: invoke the external SANDII binary
        subprocess.run(
            [str(self.sand2_exe)],
            cwd=self.workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )


        #Fourth: parse sand2/OUT.SII
        outfi = self.workdir / "OUT.SII"
        spl = np.zeros(num_groups, dtype=float)
        splstart = np.zeros(num_groups, dtype=float)
        with outfi.open() as fh:
            # skip two header lines
            next(fh)
            next(fh)
            for j in range(num_groups):
                parts = fh.readline().split()
                # 4th field is splstart, 5th is spl
                splstart[j] = float(parts[3])
                spl[j]      = float(parts[4])

        return spl, splstart