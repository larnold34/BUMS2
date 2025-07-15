#This will be a python conversion of fcn.pl in the MAXED directory
import numpy as np

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
        self.mm = mm.reshape((m, nb))
        self.fi = fi
        self.s = s
        self.d = d
        self.omega = omega
        self.flux = flux
    
    def __call__(self, lambdas: np.ndarray) -> float:
        #Compute exponent vector for each bin j
        #exponent[j] = -sum_i(lambdas[i] * mm[i, j])
        exponent = -np.tensordot(lambdas, self.mm, axes=(0,0))

        #Verify that the exponent is safe
        exp_vals = np.array([NumberUtils.exprep(x) for x in exponent])
        sum1 = np.dot(self.fi, exp_vals)

        #sum3 = sum_i(s[i] * lambdas)**2
        sum3 = np.sum((self.s * lambdas) ** 2)
        sum4 = np.dot(lambdas, self.d)

        H = -sum1 - np.sqrt(self.omega * sum3) - sum4 + self.flux
        return H
        
        
  