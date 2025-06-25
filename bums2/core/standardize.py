#This file is primarily composed of various math related files from the original perl structure
#Contained would be the equivalent to scale_factor, fit_error, chi_squared, trans_mat, cal_response, and normalize .pl
from math import sqrt
import numpy as np
from typing import Sequence, List, Tuple

class Standardize:

    @staticmethod
    def scale_factor(measured: Sequence[float], response_applied: Sequence[float]) -> float:
        
        #Compute a factor f such that sum(measured_i * response_i) / sum(response_i^2)

        num = sum(m * r for m, r in zip(measured, response_applied))
        den = sum(r * r for r in response_applied)
        if den == 0:
            raise ValueError("Cannot compute scale factor: zero denominator")
        return num / den
    
    @staticmethod
    def chi_squared(measured: Sequence[float], model: Sequence[float], errors: Sequence[float]) -> float:

        #Compute chi^2 = sum[(measured_i - model_i)^2 / error_i^2]

        chisq = 0.0
        for m, c, e, in zip(measured, model, errors):
            if e <= 0:
                raise ValueError("All errors must be greater than 0")
            chisq += ((m-c)**2)/ (e**2)
        return chisq
    
    @staticmethod
    def fit_error(measured: Sequence[float], model: Sequence[float], weights: Sequence[float]) -> float:
        total = 0.0
        for m, c, w in zip(measured, model, weights):
            if m > 0:
                err = (c - m) / m
            else:
                err = 100.0
            total += w * err * err
        return total
    
    @staticmethod
    def trans_mat(aleth: np.ndarray, spli: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        num_det, num_groups = aleth.shape
        alethnew = np.zeros_like(aleth)
        for i in range(num_groups):
            for k in range(num_det):
                alethnew[k, i] = aleth[k, i] * spli[i]
        
        spl = np.ones(num_groups, dtype=spli.dtype)
        return alethnew, spl
    
    @staticmethod
    def cal_response(alethnew: np.ndarray, spl: np.ndarray) -> np.ndarray:
        num_det, num_groups = alethnew.shape
        bcc = np.zeros(num_det, dtype=alethnew.dtype)

        for m in range(num_det):
            for j in range(num_groups):
                bcc[m] += alethnew[m, j] * spl[j]
        return bcc


    @staticmethod
    def normalize( initial_spectrum: List[float], response_matrix: List[List[float]], measured_counts: List[float]) -> List[float]:
        modeled = [
            sum(row[j] * initial_spectrum[j] for j in range(len(initial_spectrum)))
            for row in response_matrix
        ]
        sf = Standardize.scale_factor(measured_counts, modeled)
        return [val * sf for val in initial_spectrum]


