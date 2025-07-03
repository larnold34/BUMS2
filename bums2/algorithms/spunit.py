#The following will apply the spunit unfolding method
from typing import Tuple
import numpy as np

from bums2.core.config import Bums2Config

class spunit:
    #Paramters:
    #itertesterror : float, the number of iterations before checking the error
    #smoothing : float, smoothing factor
    def __init__(self, cfg: Bums2Config):
        self.itertesterror = cfg.itertesterror
        self.smoothing = cfg.smoothing
        self.ss = None

    def spunit_unfold(
            self,
            alethnew: np.ndarray,
            bce: np.ndarray,
            bcc: np.ndarray,
            spl: np.ndarray,
            num_groups: float,
            num_det: float,
            iter_start: int = 0
    ) -> Tuple[np.ndarray, np.ndarray, int]:
        #               BEGINNING OF SPUNIT UNFOLDING ALGORITHM   
        #Parameters:
        #alethnew : ndarray, shape(num_detectors, num_groups), The response matrix in terms of lethargy
        #bce: ndarray, shape(num_detectors,), The measured counts
        #bcc: ndarray, shape(num_detectors,), The expected counts
        #spl: ndarray, shape(num_groups,), The starting spectrum
        
        #Returns:
        #spl: ndarray, shape(num_groups,), The unfolded spectrum
        #bcc: ndarray, shape(num_detectors,), The calculated counts after unfolding
        #iter_count: int, total number of iterations performed

        iter_count = iter_start

        #Initial normalization ss[j] for the first run
        if iter_count == 0:
            ss = np.zeros(num_groups, dtype=float)
            for j in range(num_groups):
                #sum over detectors i: alethnew[i,j] / bce[i]
                denom = 0.0
                for i in range(num_det):
                    if bce[i] != 0:
                        denom += alethnew[i, j] / bce[i]
                ss[j] = denom
            self.ss = ss
        else:
            ss = self.ss
        
        #Main iteration loop
        for k in range(self.itertesterror):
            iter_count += 1

            #First: compute provisional spectrum spll
            spll = np.zeros(num_groups, dtype=float)
            for j in range(num_groups):
                if spl[j] <= 0.0 or ss[j] == 0.0:
                    continue
                for i in range(num_det):
                    if alethnew[i, j] != 0 and spl[j] != 0:
                        spll[j] += (spl[j]*alethnew[i, j] ) / (ss[j] * bcc[i])
                    #Too avoid any underflow
                    if spll[j] < 1.0e-37:
                        spll[j] = 0.0
            
            #Second: apply smoothing and update spl
            new_spl = np.empty_like(spll)
            

            #Remaining bins
            for j in range(2, num_groups):
                left  = spll[j-1] * self.smoothing
                mid   = spll[j]
                right = (spll[j+1] * self.smoothing) if (j+1) < num_groups else 0.0
                new_spl[j] = (left + mid + right) / (1.0 + 2.0*self.smoothing)

            #Bins 0 and 1 are just copied
            new_spl[0] = spll[0]
            if num_groups > 1:
                new_spl[1] = spll[1]
            

            spl[:] = new_spl

            # Recalculate bcc from unfolded spl
            for m in range(num_det):
                total = 0.0
                for j in range(num_groups):
                    total += alethnew[m, j] * spl[j]
                bcc[m] = total

            # DEBUG: print final spectrum and response
            # print(f"[DEBUG Py] final spl (len={len(spl)}) = {spl!r}")
            # print(f"[DEBUG Py] final bcc (len={len(bcc)}) = {bcc!r}")
        return spl, bcc, iter_count
        