#The sand2 unfolding process is very similar in its set up as the maxed unfolding
#This main driver may look very similar to the maxed one, but with some changes to be more align with sand2
import numpy as np
from bums2.FORTRAN_METHODS.MAXED.driver.maxed_input_parser import MaxedInputParser
from bums2.FORTRAN_METHODS.MAXED.bins.mkebins import MergedEnergyBins
from bums2.FORTRAN_METHODS.MAXED.bins.mkebins4pd import LogEnergyBinsPD
from bums2.FORTRAN_METHODS.MAXED.bins.fillfil import SpectrumBinFiller
from bums2.FORTRAN_METHODS.MAXED.bins.responsel import ResponseMapper
from bums2.FORTRAN_METHODS.MAXED.spec_scaling.scaling import SpectrumScaler
from bums2.FORTRAN_METHODS.SAND2.sand2_algo import Sand2Solver

class Sand2Pipeline:
    def __init__(self, input_file, response_file, max_iter=10, iqds=1, iqbs=3, chi_fac=1, dev=1e-3):
        self.input_file = input_file
        self.response_file = response_file
        self.IQDS = iqds
        self.IQBS = iqbs
        self.max_iter = max_iter
        self.chi_fac = chi_fac
        self.dev = dev
        
    def run(self):
        parser = MaxedInputParser(self.input_file, self.response_file)
        parser.parse()
        inp = parser.get_input_data()
        rsp = parser.get_response_data()

        M = inp["M"]
        N0 = inp["N0"]
        RFN = np.array(inp["RFN"])
        D = np.array(inp["D"])
        S = np.array(inp["S"])
        ENBZKL = np.array(inp["ENBZKL"])
        ZKL = np.array(inp["ZKL"])
        ENBR = np.array(rsp["ENBR"])
        RES = np.array(rsp["RES"])

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
        elif self.IQBS == 2:
            ENBF = ENBZKL.copy()
        elif self.IQBS == 1:
            ENBF = LogEnergyBinsPD(ENBZKL).generate_bins()
        elif self.IQBS == 0:
            ENBF, _ = MergedEnergyBins(ENBZKL, ENBR, N0 + len(ENBR)).merge_and_filter()

        ENBF = np.array(ENBF)
        N = len(ENBF)
        NB = N -1

        #Fill FI
        FI = SpectrumBinFiller(ENBZKL, ZKL, ENBF).fill()

        #Build the response matrix B
        B = ResponseMapper(RES, RFN, ENBF, ENBR, M, NB, len(ENBR)-1).map_response()

        #Scale FI
        scf = SpectrumScaler([], FI, ENBF).scale_fi(D, S, B, FI)
        FI *= scf

        EDSP = B @ FI
        chi_default = np.sum(((D - EDSP)**2) / (S ** 2))
        print()
        print(f" CHI SQUARE/DEFAULT SPECTRUM  = {chi_default:.10f}\n")
        print(" STARTING SAND-II DECONVOLUTION\n")

        #Run sand2
        solver = Sand2Solver(B, D, S, FI, self.max_iter, self.chi_fac, self.dev)
        FSNEW = solver.run()
        chi_sand2 = solver.get_chi_squared()
        print(f" CHI SQUARE/SAND-II  = {chi_sand2:.10f}\n")

        #Rebin and normalize in terms of lethargy
        fil, fl  = SpectrumScaler([], FI, ENBF).lethargy_normalize(FI, FSNEW)

        #Chi-squared values after rebinning
        c1 = np.sum(((D - (B @ fil))**2) / (S ** 2))
        print(" CHI SQUARE AFTER REBINNING TO THE BIN STRUCTURE OF THE")
        print(f" DEFAULT SPECTRUM            = {c1:.10f}\n")

        c3 = np.sum(((D - (B @ fl))**2) / (S ** 2))
        print(" CHI SQUARE AFTER REBINNING TO THE BIN STRUCTURE OF THE")
        print(f" RESPONSE FUNCTION           = {c3:.10f}\n")

        return {
            "FI": FI,
            "FSNEW": FSNEW,
            "FIL": fil,
            "FL": fl,
            "CHI_DEFAULT": chi_default,
            "CHI_SAND2": chi_sand2,
            "CHI_REBIN_DEFAULT": c1,
            "CHI_REBIN_RESPONSE": c3,
            "FLUX_DEFAULT": FI.sum(),
            "FLUX_SOLUTION": FSNEW.sum()
        }