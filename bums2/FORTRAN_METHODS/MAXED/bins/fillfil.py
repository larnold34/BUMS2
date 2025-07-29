#This file will be the equivalent of fillfil.pl from the original MAXED directory
import numpy as np

class SpectrumBinFiller:
    def __init__(self, enbzkl, zkl, enbf):
        self.enbzkl = np.asarray(enbzkl, dtype=np.float64)
        self.zkl = np.asarray(zkl, dtype=np.float64)
        self.enbf = np.asarray(enbf, dtype=np.float64)

        self.n0 = len(enbzkl)
        self.nb = len(enbf) - 1
        self.n = len(enbf) - 1

        self.fil = np.zeros(self.nb, dtype=np.float64)
        self.fi = np.zeros(self.nb, dtype=np.float64)

    def fill(self):
        n0m1 = self.n0 - 1

        #Precompute ZKLL, the log scaled bin height
        zkll = self.zkl[:n0m1] / (np.log(self.enbzkl[1:self.n0]) - np.log(self.enbzkl[:n0m1]))

        #Main loop from the original Perl
        for k in range(n0m1):
            for l in range(self.nb):
                r2 = np.log(self.enbf[l + 1]) - np.log(self.enbf[l])

                #Case 1: ENBF[l] ≤ ENBZKL[k] < ENBF[l+1]
                if self.enbf[l] <= self.enbzkl[k] < self.enbf[l + 1]:
                    if self.enbf[l + 1] >= self.enbzkl[k + 1]:
                        r1 = np.log(self.enbzkl[k + 1]) - np.log(self.enbzkl[k])
                        self.fil[l] += zkll[k] * (r1/r2)
                    elif self.enbf[l + 1] < self.enbzkl[k + 1]:
                        r1 = np.log(self.enbf[l + 1]) - np.log(self.enbzkl[k])
                        self.fil[l] += zkll[k] * (r1/r2)
                
                #Case 2: ENBF[l] > ENBZKL[k]
                elif self.enbf[l] > self.enbzkl[k]:
                    if self.enbf[l] < self.enbzkl[k + 1]:
                        if self.enbf[l + 1] <= self.enbzkl[k + 1]:
                            r1 = np.log(self.enbf[l + 1]) - np.log(self.enbf[l])
                            self.fil[l] += zkll[k] * (r1/r2)
                        elif self.enbf[l + 1] > self.enbzkl[k + 1]:
                            r1 = np.log(self.enbzkl[k + 1]) - np.log(self.enbf[l])
                            self.fil[l] += zkll[k] * (r1/r2)

        #Final adjustment to get FI
        for h in range(self.nb):
            width = np.log(self.enbf[h + 1]) - np.log(self.enbf[h])
            self.fi[h] = self.fil[h] * width

            
        return self.fi

        