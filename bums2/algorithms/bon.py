#The following will apply the bon unfolding method
from typing import Tuple
import numpy as np

from bums2.core.config import Bums2Config

class bon:
    def __init__(self, cfg: Bums2Config):
        self.itertesterror = cfg.itertesterror
        self.smoothing = cfg.smoothing
        self.num_grps = cfg.num_groups
        self.num_det = cfg.num_det
        self._bk = np.zeros((self.num_grps, self.num_grps), dtype=float)
        self._vect = np.zeros(self.num_grps, dtype=float)

    def bon_unfolding(
            self,
            alethnew: np.ndarray,
            bce: np.ndarray,
            spl_init: np.ndarray,
            num_groups: float,
            num_det: float,
            iter_start: int = 0
    ) -> Tuple[np.ndarray, np.ndarray, int]:
        #Perform BON unfolding
        #Parameters:
        #alethnew : ndarray, shape(num_detectors, num_groups), The response matrix in terms of lethargy
        #bce: ndarray, shape(num_detectors,), The measured counts
        #spl_init: ndarray, shape(num_groups,), The starting spectrum
        
        #Returns:
        #spl: ndarray, shape(num_groups,), The unfolded spectrum
        #bcc: ndarray, shape(num_detectors,), The calculated counts after unfolding
        #iter_count: int, total number of iterations performed

        #Initialize the outputs by copying the inputs
        spl = spl_init.copy()
        bcc = np.zeros(num_det, dtype=float)
        iter_count = iter_start

        #Precompute bk and vect only once if starting fresh
        if iter_count <= 0:
            #Build bk exactly like perl does
            for j in range(self.num_grps):
                for i in range(self.num_grps):
                    s = 0.0
                    for m in range(self.num_det):
                        s += alethnew[m, j] * alethnew[m, i]
                    self._bk[j, i] = s
            

            #Build vect exactly like perl does
            for i in range(self.num_grps):
                s = 0.0
                for j in range(self.num_det):
                    s += alethnew[j, i] * bce[j]
                self._vect[i] = s
             

        #Iteration loop
        for k in range(self.itertesterror):
            iter_count += 1

            #Provisional spectrum
            spll = np.zeros_like(spl)

            #For each energy bin j, ax = sum_m(spl[m]*bk[j,m])
            #Enforce a similar underflow condition as spunit
            #Update spll as spll[j] = spl[j] * vect[j] / ax
            ax = spl @ self._bk.T #vectorized: shape(num_groups,)
            ax = np.where(ax < 1e-37, 1e-37, ax)

            spll = spl * self._vect / ax
            spll = np.where(spll < 1e-37, 0.0, spll)

            #Smoothing update
            new_spl = spll.copy()
            if num_groups > 2:
                 denom = 1.0 + 2.0 * self.smoothing
                 for j in range(2, num_groups):
                    hi = spll[j+1] if j+1 < num_groups else 0.0
                    new_spl[j] = (spll[j-1]*self.smoothing + spll[j] + hi*self.smoothing) / denom
                      
            # first two bins are direct
            new_spl[0] = spll[0]
            new_spl[1] = spll[1]

            spl = new_spl

        # finally, recompute bcc from unfolded spl
        bcc = alethnew.dot(spl)  
        return spl, bcc, iter_count


