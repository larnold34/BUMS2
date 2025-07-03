#This file is primarily composed of various math related files from the original perl structure
#Contained would be the equivalent to scale_factor, fit_error, chi_squared, trans_mat, cal_response, and normalize .pl
from math import sqrt
import numpy as np
from typing import Sequence, List, Tuple

class Standardize:

    @staticmethod
    def scale_factor(bce: np.ndarray, errbce: np.ndarray, response: np.ndarray, num_det: float, num_grps: float, flux: np.ndarray) -> float:
        #Compute a factor f such that sum(measured_i * response_i) / sum(response_i^2)

        #The following are some fail safe checks
        for i in range(num_det):
            if errbce[i] == 0:
                raise ValueError(f"Divide be zero due to {errbce[i]} being zero")

        flux_sum = sum(flux)
        if flux_sum == 0:
            raise ValueError("Flux values all zero")
        
        eig = np.zeros_like(flux)
        sum1 = sum2 = 0.0
        for i in range(num_det):
            for k in range(num_grps):
                eig[i] += response[i, k] * flux[k]
            sum1 += (bce[i] * eig[i]) / (errbce[i]**2)
            sum2 += (eig[i]**2) / (errbce[i]**2)
        return sum1/sum2
    
    @staticmethod
    def chi_squared(num_det: int, bce: np.ndarray, bcc: np.ndarray, errbce: np.ndarray) -> float:
        chisq = 0.0
        #Compute chi^2 = sum[(measured_i - model_i)^2 / error_i^2]
        for i in range(num_det):
            chisq += ((bce[i] - bcc[i])**2) / ((errbce[i])**2)
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
    def normalize(bce: np.ndarray, errbce: np.ndarray, response: np.ndarray, num_det: float, num_grps: float, flux: np.ndarray) -> List[float]:
        rnorm = Standardize.scale_factor(bce, errbce, response, num_det, num_grps, flux)

        for i in range(num_grps):
            flux[i] *= rnorm
        
        return flux

