#This file will be the equivalent of mkebins4pd.pl from the original MAXED directory
import numpy as np
import math

class LogEnergyBinsPD:
    def __init__(self, enbf):
        self.enbf_input = np.array(enbf)
        self.n = len(enbf)
        self.enbf = np.zeros_like(enbf, dtype=float)

        self.EMEV_START = 1.3113526e-14
        self.TPOQ = 10 ** 0.25

    def _nint(self, x):
        #Fortran-style nearest integer rounding
        return int(x + 0.5)
    
    def generate_bins(self):
        emev = self.EMEV_START

        emax = self.enbf_input[-1]
        emin = self.enbf_input[0]

        #Find EMAX 
        for h in range(80):
            emev *= self.TPOQ
            if self.enbf_input[-1] >= emev:
                emax = emev 

        #Reset emev to find EMIN
        emev = self.EMEV_START
        for j in range(80):
            emev /= self.TPOQ
            if self.enbf_input[0] <= emev:
                emin = emev

        #Determine the number of bins
        n_bins = self._nint(4.0 * math.log10(emax / emin)) + 1

        #Build logarithmic bins
        self.enbf = np.zeros(n_bins)
        self.enbf[0] = emin
        for i in range(1, n_bins):
            self.enbf[i] = self.enbf[i-1] * self.TPOQ

        return self.enbf
