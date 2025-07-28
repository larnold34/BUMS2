# #This file will be the combination of calcout, scalefi, and lethar from the MAXED directory
import numpy as np

class SpectrumScaler:
    def __init__(self, mm, fi, enbf):
        self.mm = np.asarray(mm, dtype=np.float64) #Response matrix
        self.fi = np.asarray(fi, dtype=np.float64) #Default spectrum
        self.enbf = np.asarray(enbf, dtype=np.float64) #Bin edges

    def calc_fout(self, lambdas, m, nb, b):
        lambdas = np.asarray(lambdas, dtype=np.float64)
        fout = np.zeros(nb, dtype=np.float64)
        # for j in range(nb):
        #     sum2 = 0.0
        #     for i in range(m):
        #         sum2 += lambdas[i] * b[i, j]
        exponent = -np.dot(lambdas, b)
        fout = self.fi * np.exp(exponent)

        return fout
    
    def scale_fi(self, d, s, b, fi):
        m, nb, = b.shape
        eig = np.dot(b, fi)
        sum1 = np.sum((d * eig) / (s ** 2))
        sum2 = np.sum((eig ** 2) / (s ** 2))

        scf = sum1 / sum2
        return scf
    
    def lethargy_normalize(self, fout):
        nb = len(self.fi)
        fil = np.zeros(nb, dtype=np.float64)
        fl = np.zeros(nb, dtype=np.float64)

        for k in range(nb):
            z = np.log(self.enbf[k + 1]) - np.log(self.enbf[k])
            fil[k] = self.fi[k] / z
            fl[k] = fout[k] / z

        return fil, fl
       
        