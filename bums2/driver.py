#This is the main driver script of bums2
import sys
from pathlib import Path

from bums2.io.input import InputParser
from bums2.io.matrix import ResponseMatrix
from bums2.io.user_spectrum import UserSpectrumLoader
from bums2.io.output import OutputFormatter

from bums2.core.standardize import Standardize

from bums2.algorithms.maxiet import maxiet
from bums2.algorithms.bon import Bon
from bums2.algorithms.spunit import spunit
from bums2.algorithms.maxed import maxed
from bums2.algorithms.sand2 import sand2
from bums2.algorithms.guess import SpectrumGuesser


class Bums2Driver:
    def __init__(self):
        #Parse the input -> Bums2Config
        self.cfg = InputParser().parse()

        #Load in response matrix
        resp = ResponseMatrix.from_file(
            matrix_name= self.cfg.matrix_name,
            detector_mask= self.cfg.detector_mask,
            max_energy= self.cfg.max_energy,
        )

        #Extract lethargy-weighted aleth matrix
        self.ce, self.aleth, self.wdleth = resp.to_lethargy()

        #Measured counts and error
        self.bce = self.cfg. measured_counts
        self.errbce = self.cfg.measured_errors

        #Pre-normalize parameters
        self._prepare_counts()

    def _prepare_counts(self):
        #dead time correction, weighted calculations
        dead = self.cfg.dead
        corrected = []

        for c in self.bce:
            corrected.append(c / (1.0 - dead * c))

        self.bce = corrected
        sum_err = sum(self.errbce)
        n = len(sum_err)
        self.whtbce = [sum_err / (n * e) for e in self.errbce]

    def run(self):
        #Pick the initial spectrum
        if self.cfg.start_spec.upper().startswith("MAXIET"):
            spli, splmax, _ = maxiet(self.cfg).maxiet_spectrum(
                ce = self.ce,
                bce = self.bce,
                aleth = self.aleth,
                errbce = self.errbce,
                whtbce = self.whtbce,
            )
        elif self.cfg.start_spec.upper().startswith("USER INPUT"):
            spli = UserSpectrumLoader(self.cfg)._read_user_spectrum()
        else:
            spli = SpectrumGuesser(self.cfg).guess(
                ce = self.ce,
                bce = self.bce,
                errbce = self.errbce,
                whtbce = self.whtbce,
                aleth = self.aleth,
            )

        #Transform and normalize
        alethnew, spl_unit = Standardize.trans_mat(self.aleth, spli)
        sf = Standardize.scale_factor(self.bce, alethnew.dot(spl_unit))
        spli = [x * sf * self.cfg.cal_factor for x in spli]

        #Choose and run unfolding
        alg = self.cfg.alg.upper()
        
        if "BON" in alg:
            spl, bcc, _ = Bon(self.cfg).bon_unfolding(self.aleth, self.bce, spli)
        elif "SPUNIT" in alg:
            spl, bcc, _ = spunit(self.cfg).spunit_unfold(self.aleth, self.bce, spli)
        elif "MAXED" in alg:
            spl, splstart = maxed(self.cfg).maxed_unfold(self.aleth, self.bce, self.errbce, spli)
        elif "SANDII" in alg:
            spl, splstart = sand2(self.cfg).sand2_unfold(self.aleth, self.bce, self.errbce, spli)
        else:
            raise RuntimeError(f"Unknown unfolding algorithm: {self.cfg.alg}")
        
        #Compute diagonistics
        chi = Standardize.chi_squared(self.bce, bcc, self.errbce)
        err = Standardize.fit_error(self.bce, bcc, self.whtbce)

        #Write everything out
        

if __name__ == "__main__":
    try:
        Bums2Driver().run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


    

