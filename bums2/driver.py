#This is the main driver script of bums2
import sys
from pathlib import Path
import numpy as np
from typing import Tuple, List

from bums2.io.input import InputParser
from bums2.io.matrix import ResponseMatrix
from bums2.io.user_spectrum import UserSpectrumLoader
from bums2.io.output import CLIFormatter

from bums2.core.standardize import Standardize
from bums2.core.summary import Summary, SummaryCalculator

from bums2.algorithms.maxiet import maxiet
from bums2.algorithms.bon import bon
from bums2.algorithms.spunit import spunit
from bums2.algorithms.maxed import maxed
from bums2.algorithms.sand2 import sand2
from bums2.algorithms.guess import SpectrumGuesser

from bums2.utils.dose import DoseConverter


class Bums2Driver:
    def __init__(self):
        project_root = Path(__file__).parent.parent
        matrix_dir = project_root / "MATRIX"
        #Parse the input -> Bums2Config
        self.cfg = InputParser().parse()

        #Load in response matrix
        resp = ResponseMatrix.from_file(
            matrix_name= self.cfg.matrix_name,
            detector_mask= self.cfg.detector_mask,
            max_energy= self.cfg.max_energy,
            matrix_dir= matrix_dir
        )

        self.cfg.e_end = list(resp.e_end)
        
        self.cfg.iter_log = []

        #Number of detectors and number of groups
        self.cfg.num_det = resp.mat.shape[1]
        self.cfg.num_groups = resp.num_bins

        #Extract lethargy-weighted aleth matrix
        self.ce, self.aleth, self.wdleth = self.to_lethargy(resp.mat)

        self.cfg.aleth = self.aleth
        #Measured counts and error
        raw_bce    = np.array(self.cfg.measured_counts, dtype=float)
        raw_errbce = np.array(self.cfg.measured_errors, dtype=float)

        #Need to apply the detector mask to the counts and errors
        mask = np.array(self.cfg.detector_mask, dtype=bool)
        self.bce = raw_bce[mask]
        self.errbce = raw_errbce[mask]

        self.cfg.bce = self.bce
        self.cfg.errbce = self.errbce

        #Detector matrix
        self.mat = resp.mat

        #Pre-normalize parameters
        self._prepare_counts()

        self.cfg.whtbce = self.whtbce

    def _prepare_counts(self):
        #dead time correction, weighted calculations
        dead = self.cfg.dead
        self.bce = self.bce / (1.0 - dead * self.bce)

        sum_err = self.errbce.sum()
        n = len(self.errbce)
        self.whtbce = np.array([
        (sum_err / (n * e)) if e != 0.0 else 0.0
        for e in self.errbce
    ], dtype=float)

    def to_lethargy(self, mat) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        e_end = np.array(self.cfg.e_end, dtype=float)

        ce = np.zeros(self.cfg.num_groups, dtype=float)
        wdleth = np.zeros(self.cfg.num_groups, dtype=float)
        aleth = np.zeros((self.cfg.num_det, self.cfg.num_groups), dtype=float)

        for i in range(self.cfg.num_groups):
            ce[i] = (e_end[i] * e_end[i+1])**0.5
            wdleth[i] = np.log(e_end[i+1]) - np.log(e_end[i])

        for j in range(self.cfg.num_det):
            for i in range(self.cfg.num_groups):
                aleth[j, i] = mat[i+1, j] * wdleth[i]
        return ce, aleth, wdleth

    def run(self):

        out_path = Path(self.cfg.output_file)
        #Pick the initial spectrum
        if self.cfg.start_spec.upper().startswith("MAXIET"):
            with open(out_path, "w") as out:
                spli, tempm = maxiet(self.cfg).maxiet_spectrum(
                    ce = self.ce,
                    bce = self.bce,
                    aleth = self.aleth,
                    errbce = self.errbce,
                    whtbce = self.whtbce,
                    out=out
                )
            self.cfg.tempm = tempm
        elif self.cfg.start_spec.upper().startswith("USER INPUT"):
            loader = UserSpectrumLoader(self.cfg, self.ce)
            spli = loader.load()
        else:
            sg = SpectrumGuesser(self.cfg, Standardize())
            with open(out_path, "w") as out:
                best_file, spli = sg.guess(out)
            self.cfg.best_file = best_file
            spli = np.array(spli, dtype=float)


        #Transform and normalize
        alethnew, spl_unit = Standardize.trans_mat(self.aleth, spli)
        spl = Standardize.normalize(self.bce, self.errbce, alethnew, self.cfg.num_det, self.cfg.num_groups, spl_unit)
        sf = Standardize.scale_factor(self.bce, self.errbce, self.aleth, self.cfg.num_det, self.cfg.num_groups, spli) * self.cfg.cal_factor
        self.cfg.rnorm = sf
        bcc = Standardize.cal_response(alethnew, spl)

        #Compute diagonistics
        error = Standardize.fit_error(self.bce, bcc, self.whtbce)
        chi = Standardize.chi_squared(self.cfg.num_det, self.bce, bcc, self.errbce)

        #Store the scaled spectrum
        splstart = np.zeros_like(spli)
        for i in range(self.cfg.num_groups):
            splstart[i] = spli[i] * sf

        #Initialize the iterations and error
        iter_count = 0
        starterror = np.sqrt(error / self.cfg.num_det) * 100

        #Choose and run unfolding
        alg = self.cfg.alg.upper()
        
        if "MAXED" in alg:
            spl, splstart = maxed(self.cfg).maxed_unfold(
                self.mat, self.bce, self.errbce, spl, self.cfg.num_groups, self.cfg.num_det)
            
        elif "SANDII" in alg:
            spl, splstart = sand2(self.cfg).sand2_unfold(
                self.mat, self.bce, self.errbce, spl, self.cfg.num_groups, self.cfg.num_det)
            
        else:
            # both BON and SPUNIT go here
            if "BON" in alg:
                runner = bon(self.cfg)
                unfold = lambda it: runner.bon_unfolding(
                    alethnew, self.bce, spl, self.cfg.num_groups, self.cfg.num_det, iter_start=it
                    )
            else:  # SPUNIT
                runner = spunit(self.cfg)
                unfold = lambda it: runner.spunit_unfold(
                    alethnew, self.bce, bcc, spl, self.cfg.num_groups, self.cfg.num_det, iter_start=it
                    )

            # print the “Iteration = 0” line
            self.cfg.iter_log.append(
                f"Iteration = {iter_count:<4d}  Error = {starterror:>7.3f}  Chi-Squared = {chi:>11.3E}"
                )

            # only loop if the user asked for >0 iterations
            if self.cfg.iter > 0:
                old_chi = float("inf")
                # mimic `do { … } while(...)` in Perl:
                while True:
                    spl, bcc, iter_count = unfold(iter_count)

                    # re‐compute fit and χ²
                    error = Standardize.fit_error(self.bce, bcc, self.whtbce)
                    chi   = Standardize.chi_squared(self.cfg.num_det, self.bce, bcc, self.errbce)
                    up_error = np.sqrt(error / self.cfg.num_det) * 100

                    self.cfg.iter_log.append(
                        f"Iteration = {iter_count:<4d}  Error = {up_error:>7.3f}  Chi-Squared = {chi:>11.3E}"
                        )

                    # break exactly when the Perl until(...) is false
                    if not (
                        chi/old_chi < self.cfg.tstrat
                        and iter_count + self.cfg.itertesterror <= self.cfg.iter
                        and error > self.cfg.tstper
                    ):
                        break

                    old_chi = chi

            # stash final result back on the config so output.py can pick it up
            self.bcc = bcc
            self.cfg.iter_count = iter_count
            self.cfg.ce = self.ce

            #Apply sum data logic
            calc = SummaryCalculator(
                ce = self.ce,
                wdleth = self.wdleth,
                spli = spli,
                spl = spl,
                alethnew = alethnew,
                bce = np.array(self.bce),
                bcc = np.array(bcc),
                errbce = np.array(self.errbce),
                cal = self.cfg.cal_factor,
                df = DoseConverter(),
                cfg = self.cfg

            )

            summary: Summary = calc.compute(
                alg = self.cfg.alg,
                start_spec = self.cfg.start_spec,
                iter_count = iter,
                tempij = self.cfg.tempij
            )

            self.cfg.summary = summary

            cfg = self.cfg
            cfg.spc = summary.spc.tolist()
            cfg.spl = spl.tolist()
            cfg.rem = summary.rem.tolist()
            cfg.prem = summary.prem.tolist()
            cfg.splstart = splstart.tolist()
            cfg.pcterr = summary.pcterr.tolist()

            

            for det, bcc_val, pct in zip(cfg.detectors, bcc, summary.pcterr):
                det.bcc = bcc_val
                det.pcterr = pct
        
            #Call the ouput file
            CLIFormatter().render(cfg, out_path)
        

if __name__ == "__main__":
    try:
        Bums2Driver().run()
    except Exception:
        import traceback
        traceback.print_exc()       # <-- prints file, line, stack, and exception
        sys.exit(1)


    

