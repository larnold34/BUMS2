#This file will be applying the logic used for SAND2
import numpy as np

class Sand2Solver:
    #Implement the SAND-II neutron spectrum unfolding algorithm
    def __init__(self, B, D, S, FI, max_iter=50, chi_fac=1, dev=1e-3):
        #Parameters:
        #B is the response matrix
        #D is the measured data
        #S is the measurement error
        #FI is the initial default spectrum
        #max_iter is the maximum number of iterations
        #chi_fac is the convergence criteria type(0 = fractional deviation, 1 = chi-square)
        #dev is the deviation threshold

        self.B = np.array(B, dtype=np.float64)
        self.D = np.array(D, dtype=np.float64)
        self.S = np.array(S, dtype=np.float64)
        self.FI = np.array(FI, dtype=np.float64)

        self.M = len(D)
        self.NB = self.B.shape[1]
        self.max_iter = max_iter
        self.chi_fac = chi_fac
        self.dev = dev

        self.FS = self.FI.copy()
        self.FSNEW = None
        self.chi2 = None
        self.iterations = 0

    def run(self):
        #Excutes the SAND-II unfolding algorithm, returns the final unfolded spectrum
        for iteration in range(1, self.max_iter+1):
            self.iterations = iteration

            #Calculate expected counts
            E = self.B @ self.FS
            R = self.D / E

            #Weight matrix
            W = self.B * (self.FS / E[:, np.newaxis])

            #Update the spectrum
            numer = np.sum(W * np.log(R[:, np.newaxis]), axis=0)
            denom = np.sum(W, axis=0)
            denom_safe = np.where(denom == 0, 1e-12, denom)

            self.FSNEW = self.FS * np.exp(numer / denom_safe)

            if self._converged():
                break
            self.FS = self.FSNEW.copy()

        self.chi2 = self._compute_chi_squared(self.FSNEW)
        return self.FSNEW
    
    def _compute_chi_squared(self, FS):
        E = self.B @ FS
        return np.sum(((self.D - E) / self.S)**2)
    
    def _converged(self):
        if self.chi_fac == 1:
            chi2 = self._compute_chi_squared(self.FSNEW)
            return chi2 <= self.M
        else:
            rel_diff = np.abs(self.FSNEW - self.FS) / np.maximum(self.FS, 1e-10)
            max_dev = np.max(rel_diff)
            return max_dev < self.dev
        
    def get_chi_squared(self):
        return self.chi2
    
    def get_iterations(self):
        return self.iterations
    
    def get_spectrum(self):
        return self.FSNEW
    
    def get_relative_deviation(self):
        return np.abs(self.FSNEW - self.FS) / np.maximum(self.FS, 1e-10)