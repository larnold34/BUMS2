# #This file will be the combination of calcout, scalefi, and lethar from the MAXED directory
import numpy as np

class SpectrumScaler:
    def __init__(self, mm, fi, enbf):
        self.mm = np.array(mm) #Response matrix
        self.fi = np.array(fi) #Default spectrum
        self.enbf = np.array(enbf) #Bin edges

    def calc_fout(self, lambdas, m, nb, b):
        lambdas = np.array(lambdas)
        
        #Reubild the matrix b from mm
        for i in range(m):
            for j in range(nb):
                b[i, j] = self.mm[i * nb + j]
        
        fout = np.zeros(nb)
        for j in range(nb):
            sum2 = 0.0
            for i in range(m):
                sum2 += lambdas[i] * b[i, j]
            fout[j] = self.fi[j] * np.exp(-sum2)

        return fout
    
    def scale_fi(self, d, s, b, fi):
        m, nb, = b.shape
        eig = np.dot(b, fi)

        sum1 = np.sum((d * eig) / (s ** 2))
        sum2 = np.sum((eig ** 2) / (s ** 2))

        scf = sum1 / sum2
        return scf
    
    def lethargy_normalize(self, fi, fout):
        nb = len(fi)
        fil = np.zeros(nb)
        fl = np.zeros(nb)

        for k in range(nb):
            z = np.log(self.enbf[k + 1]) - np.log(self.enbf[k])
            fil[k] = fi[k] / z
            fl[k] = fout[k] / z

        return fil, fl
       
        