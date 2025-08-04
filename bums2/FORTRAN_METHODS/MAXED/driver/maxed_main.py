#This file will be the equivalent of the original main.pl from the MAXED directory

#     PROGRAM MAXED
#
#     MAXED, A COMPUTER CODE FOR THE DECONVOLUTION OF MULTISPHERE
#     NEUTRON SPECTROMETER DATA USING THE MAXIMUM ENTROPY METHOD"
#
#     For more information on MAXED, see the report "MAXED, A COMPUTER
#     CODE FOR THE DECONVOLUTION OF MULTISPHERE NEUTRON SPECTROMETER
#     DATA USING THE MAXIMUM ENTROPY METHOD", Technical Report EML-595,
#     U.S. Department of Energy, New York,NY (1998).  This report can be
#     downloaded from the EML website at http://www.eml.doe.gov, or it
#     can be obtained directly from one of the authors by e-mailing a
#     request to Marcel Reginatto (mreg@eml.doe.gov) or Paul Goldhagen
#     (goldhagn@eml.doe.gov).
#
#     Revised on 5/19/98
#     lf90 maxed -fix -vax -dbl -o3 -bind
#
#     DISCLAIMER
#     "This report was prepared as an account of work sponsored by an
#     agency of the United States Government.  Neither the United States
#     Government nor any agency thereof, nor any of their employees,
#     makes any warranty, express or implied, or assumes any legal
#     liability or responsibility for the accuracy, completeness, or
#     usefulness of any information, apparatus, product, or process
#     disclosed, or represents that its use would not infringe privately
#     owned rights.  Reference herein to any specific commercial
#     product, process, or service by trade name, trademark,
#     manufacturer, or otherwise, does not necessarily constitute or
#     imply its endorsement, recommendation, or favoring by the United
#     States Government or any agency thereof.  The views and opinions
#     of authors expressed herein do not necessarily state or reflect
#     those of the United States Government or any agency thereof."
#
import numpy as np
import math
from bums2.FORTRAN_METHODS.MAXED.driver.maxed_input_parser import MaxedInputParser
from bums2.FORTRAN_METHODS.MAXED.driver.maxed import MaxedDriver
from bums2.FORTRAN_METHODS.MAXED.bins.mkebins import MergedEnergyBins
from bums2.FORTRAN_METHODS.MAXED.bins.mkebins4pd import LogEnergyBinsPD
from bums2.FORTRAN_METHODS.MAXED.bins.fillfil import SpectrumBinFiller
from bums2.FORTRAN_METHODS.MAXED.bins.responsel import ResponseMapper
from bums2.FORTRAN_METHODS.MAXED.spec_scaling.scaling import SpectrumScaler
from bums2.FORTRAN_METHODS.MAXED.bins.rebinffl import rebin_ffl


class MaxedPipeline:
    def __init__(self, input_file, response_file, t=1.0, iqds=1, iqbs=3, rt=0.85):
        self.input_file = input_file
        self.response_file = response_file
        self.IQDS = iqds
        self.IQBS = iqbs
        self.T = t
        self.RT = rt
        self.FSCF = 1.0

    def run(self):
    #     Read in the input data from the files DH and EBH
    #     (1) M is the number of measurements.
    #     (2) N0 is the number of energy bin edges used for the default
    #         spectrum. 
    #     (3) The RFN are the detector numbers.
    #     (4) The D(I) are the measured data.
    #     (5) The S(I) are the errors assigned to each measurement.  
    #     (6) The ENBZKL(K) are the energy bin edges of the default
    #     spectrum, and the ZKL(K) the values of the default spectrum.
    #     ZKL(K) is the value of the default spectrum of the bin that is
    #     bounded by bin edges ENBZKL(K1) and ENBZKL(K+1).  There are N0    
    #     energy bins, and N0-1 values of ZKL(K).  The program reads in an
    #     extra value of ZKL(K), the last one (which is ZKL(N0)).  This
    #     value is not used by the program, and ZKL(N0) is usually set to
    #     zero in the input file.
    #     (7) MMM is the number of detectors in the response function file. 
    #     (8) N1 is the number of energy bin edges used in the calculation
    #     of the response function.
    #     (9) UNITS are the units of the response function.
    #     (10) The ENBR(L) are energy bin edges of the response function.
    #     (11) The RES(K,L) are the values of the response function.
        parser = MaxedInputParser(self.input_file, self.response_file)
        parser.parse()
        inp = parser.get_input_data()
        rsp = parser.get_response_data()

        M = inp["M"]
        N0 = inp["N0"]
        RFN = np.asarray(inp["RFN"], dtype=np.int64)
        D = np.asarray(inp["D"], dtype=np.float64)
        S = np.asarray(inp["S"], dtype=np.float64)
        ENBZKL = np.asarray(inp["ENBZKL"], dtype=np.float64)
        ZKL = np.asarray(inp["ZKL"], dtype=np.float64)
        ENBR = np.asarray(rsp["ENBR"], dtype=np.float64)
        RES = np.asarray(rsp["RES"], dtype=np.float64)

        

        #Normalize ZKL based on IQDS
        if self.IQDS == 1:
            ZKL[:-1] *= ENBZKL[1:] - ENBZKL[:-1]
        elif self.IQDS == 2:
            ZKL[:-1] *= np.log(ENBZKL[1:] / ENBZKL[:-1])

        

        #Bin structure logic
        if self.IQBS == 3:
            maxmin = max(ENBZKL[0], ENBR[0])
            minmax = min(ENBZKL[-1], ENBR[-1])
            ENBF = [x for x in ENBR if maxmin <= x <= minmax]
            FI = SpectrumBinFiller(ENBZKL, ZKL, ENBF).fill()
        elif self.IQBS == 2:
            ENBF = ENBZKL.copy()
            FI = ZKL.copy()
        elif self.IQBS == 1:
            ENBF = LogEnergyBinsPD(ENBZKL).generate_bins()
            FI = SpectrumBinFiller(ENBZKL, ZKL, ENBF).fill()
        elif self.IQBS == 0:
            ENBF, _ = MergedEnergyBins(ENBZKL, ENBR, N0 + len(ENBR)).merge_and_filter()
            FI = SpectrumBinFiller(ENBZKL, ZKL, ENBF).fill()

        ENBF = np.asarray(ENBF, dtype=np.float64)
        N = len(ENBF)
        NB = N -1

        #Fill FI
        #FI = SpectrumBinFiller(ENBZKL, ZKL, ENBF).fill()

        #Build the response matrix B
        B = ResponseMapper(RES, RFN, ENBF, ENBR, M, NB, len(ENBR)-1).map_response()

        #Scale FI
        FI = np.asarray(FI, dtype=np.longdouble)
        scf = np.longdouble(SpectrumScaler([], FI, ENBF).scale_fi(D, S, B, FI))
        # print(f" SCALE FACTOR/DEFAULT SPEC. FOR BEST FIT = {scf:.6E}")
        FI *= scf

        FI = FI.astype(np.float64)
        EDSP = B @ FI
        chi_default = np.sum(((D - EDSP)**2) / (S ** 2))
        print(f" CHI SQUARE/DEFAULT SPECTRUM  = {chi_default:.6f}")


        FLUX = np.sum(FI, dtype=np.longdouble)
        MM = B.T.flatten(order="F").tolist()

        #Run simulated annealing
        # print(f"Running SIMANN optimization with T={self.T}, RT={self.RT}")
        lambdas = MaxedDriver(N, M, NB, MM, FI, S, D, FLUX, t=self.T, rt=self.RT).run()

        #Compute FOUT
        FOUT = SpectrumScaler(MM, FI, ENBF).calc_fout(lambdas, M, NB, B)

        #Chi-square after optimization
        E = B @ FOUT
        chi_maxent = np.sum(((D - E) ** 2) / (S ** 2))
        print(f" CHI SQUARE/MAXIMUM ENTROPY  = {chi_maxent}\n")

        print(f" TOTAL NEUTRON FLUENCE RATE/DEFAULT SPECTRUM  = {FLUX:.6f}\n")
        print(f" TOTAL NEUTRON FLUENCE RATE/SOLUTION SPECTRUM = {FOUT.sum():.6f}")

        fil, fl = SpectrumScaler(MM, FI, ENBF).lethargy_normalize(FOUT)

        
        # Rebin solution spectrum (in lethargy units) to default-spectrum bins
        fbds, fbdsl, c1 = rebin_ffl(
            fl_leth=fl,
            enbf=ENBF,
            target_edges=ENBZKL,
            d=D,
            s=S,
            B=B,
            fortran_fidelity=True  # preserve legacy behavior
            )

        print(" CHI SQUARE AFTER REBINNING TO THE BIN STRUCTURE OF THE")
        print(f" DEFAULT SPECTRUM            = {c1:.10f}")

        # Rebin solution spectrum to response-function bins
        fbrf, fbrfl, c3 = rebin_ffl(
            fl_leth=fl,
            enbf=ENBF,
            target_edges=ENBR,
            d=D,
            s=S,
            B=B,
            fortran_fidelity=True
            )

        print(" CHI SQUARE AFTER REBINNING TO THE BIN STRUCTURE OF THE")
        print(f" RESPONSE FUNCTION           = {c3:.10f}")

        self.result = {
        "FI": FI,
        "FOUT": FOUT,
        "FIL": fil,
        "FL": fl,
        "FBDS": fbds,
        "FBDSL": fbdsl,
        "FBRF": fbrf,
        "FBRFL": fbrfl,
        "LAMBDA": lambdas,
        "CHI_DEFAULT": chi_default,
        "CHI_MAXENT": chi_maxent,
        "CHI_REBIN_DEFAULT": c1,
        "CHI_REBIN_RESPONSE": c3,
        "FLUX_DEFAULT": FI.sum(),
        "FLUX_SOLUTION": FOUT.sum(),
        }

        return self.result


