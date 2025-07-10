# #This file will be the combination of calcout, scalefi, and lethar from the MAXED directory
# import numpy as np

# class SpectrumScaler:
#     #Spectrum scaling utilities:
#     #calcfout: compute solution spectrum from lambdas
#     #scalefi: compute optimal scale factor, which might be the same as standardize.scale_factor
#     #lethar: convert spectra to per lethergy

#     @staticmethod
#     def calcout(lambda_vec: np.ndarray, mm: np.ndarray, fi: np.ndarray) -> np.ndarray:
#         #Compute output spectrum FOUT from lambda coefficients
#         #Parameters:
#         #lambda_vec: array_like, shape(M,), lambda parameters
#         #mm: array_like, shape(M, NB), Response matrix flattened for each detector i and bin j
#         #fi: array_like, shape(NB,), default spectrum values per bin

#         #Output:
#         #fout: ndarray, shape(NB,), unfolded solution spectrum per bin
