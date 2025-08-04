#This will be a python conversion of fcn.pl in the MAXED directory
import numpy as np
import math

from bums2.FORTRAN_METHODS.MAXED.utils.NumberUtils import NumberUtils

#The following class will find the objective function for MAXED's maximum entropy deoconvolution
class ObjectiveFunction:
     
    # Evaluates the MAXED ‘FCN’ objective:
    #    H(λ) = - Σ_j FI[j] * exp(-Σ_i λ[i]*MM[i,j])
    #          - sqrt(OMEGA * Σ_i (S[i]*λ[i])^2)
    #          - Σ_i λ[i]*D[i]
    #          + FLUX
    def __init__(
            self,
            mm: np.ndarray,
            fi: np.ndarray,
            s: np.ndarray,
            d: np.ndarray,
            omega: float,
            flux: float,
            m, 
            nb
                 ):
        #Parameters:
        # mm : np.ndarray, shape (M, NB)
        #     Response matrix, where mm[i,j] == B[i][j].
        # fi : np.ndarray, shape (NB,)
        #     Default spectrum values per bin.
        # s : np.ndarray, shape (M,)
        #     Measurement errors.
        # d : np.ndarray, shape (M,)
        #     Measured data.
        # omega : float
        #     Omega parameter.
        # flux : float
        #     Default-spectrum sum (FLUX).
        self.mm = mm
        self.fi = fi.astype(np.longdouble)
        self.s = s.astype(np.float64)
        self.d = d.astype(np.float64)
        self.omega = np.float64(omega)
        self.flux = np.float64(flux)
        self.m = np.int64(m)
        self.nb = np.int64(nb)
    
    def __call__(self, lambdas: np.ndarray) -> float:
        #Compute exponent vector for each bin j
        lambdas = np.asarray(lambdas, dtype=np.float64)
        #exponent[j] = -sum_i(lambdas[i] * mm[i, j])
        # exponent = -np.tensordot(lambdas, self.mm, axes=(0,0))
        #Verify that the exponent is safe
        # exp_vals = np.array([NumberUtils.exprep(x) for x in exponent])
        # sum1 = np.dot(self.fi, exp_vals)

        # sum1 = 0.0
        # for j in range(self.nb):
        #     sum2 = 0.0
        #     for i in range(self.m):
        #         idx = self.nb * i + j
        #         sum2 += lambdas[i] * self.mm[idx]
        #     sum1 += self.fi[j] * NumberUtils.exprep(-sum2)
        sum1_terms = []
        for j in range(self.nb):
            sum2_terms = [
                np.float64(lambdas[i]) * np.float64(self.mm[self.nb * i + j])
                for i in range(self.m)
                ]
            sum2 = math.fsum(sum2_terms)
            exp_val = NumberUtils.exprep(-sum2)
            sum1_terms.append(np.float64(self.fi[j]) * exp_val)
        sum1 = np.sum(np.array(sum1_terms, dtype=np.longdouble), dtype=np.longdouble)

        #sum3 = sum_i(s[i] * lambdas)**2
        sum3 = math.fsum((self.s * lambdas) ** 2)
        sum4 = np.sum(np.array([np.longdouble(lambdas[i]) * np.longdouble(self.d[i]) for i in range(self.m)], dtype=np.longdouble), dtype=np.longdouble)

        H_ld = -sum1 - np.sqrt(self.omega * sum3) - sum4 + self.flux
        H = float(H_ld) 

        return H
        
        
  