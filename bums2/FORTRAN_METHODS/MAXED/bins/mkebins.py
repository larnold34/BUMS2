#This file will be the equivalent of mkebins.pl from the original MAXED directory
import numpy as np

class MergedEnergyBins:
    def __init__(self, enbzkl, enbr, nmax):
        self.enbzkl = np.sort(np.array(enbzkl, dtype=np.float64))
        self.enbr = np.sort(np.asarray(enbr, dtype=np.float64))
        self.nmax = nmax
        self.enb0 = None
        self.n = 0

    def merge_and_filter(self):
        
        #Merge into SORT array, accounting for sorting similar to HPSORT in the fortran
        sort = np.sort(np.concatenate((self.enbzkl, self.enbr)))

        #Determine shared range
        maxmin = max(self.enbzkl[0], self.enbr[0])
        minmax = min(self.enbzkl[-1], self.enbr[-1])

        #Filter unique values within [maxmin, minmax]
        self.enb0 = [maxmin]
        tol = 1e-12
        for val in sort:
            if val > maxmin and val <= minmax and (val - self.enb0[-1]) > tol:
                self.enb0.append(val)

        self.n = len(self.enb0)
        return self.enb0, self.n