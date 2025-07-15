#This file will be the equivalent of mkebins.pl from the original MAXED directory
import numpy as np

class MergedEnergyBins:
    def __init__(self, enbzkl, enbr, nmax):
        self.enbzkl = np.sort(np.array(enbzkl))
        self.enbr = np.sort(np.array(enbr))
        self.nmax = nmax

        self.sort = []
        self.enb0 = []
        self.n = 0

    def merge_and_filter(self):
        
        #Merge into SORT array
        self.sort = np.concatenate((self.enbzkl, self.enbr))

        #Sort using np.sort, should replace HPSORT
        self.sort = np.sort(self.sort)

        #Determine shared range
        maxmin = max(self.enbzkl[0], self.enbr[0])
        minmax = min(self.enbzkl[-1], self.enbr[-1])

        #Filter unique values within [maxmin, minmax]
        self.enb0 = [maxmin]
        self.n = 1
        for val in self.sort:
            if val > maxmin and val <= minmax and val > self.enb0[-1]:
                self.enb0.append(val)
                self.n += 1
        
        return self.enb0, self.n