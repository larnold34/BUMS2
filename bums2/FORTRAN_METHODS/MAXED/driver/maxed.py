#This file will be the equivalent of the maxed.pl file from the original MAXED directory, not to be confused with the unfolding script
from bums2.FORTRAN_METHODS.MAXED.annealing.simann import SimulatedAnnealingRunner

class MaxedDriver:
    def __init__(self, m, nb, mm, fi, s, d, flux, t=1.0, rt=0.9):
        self.M = m
        self.NB = nb
        self.MM = mm
        self.FI = fi
        self.S = s
        self.D = d
        self.FLUX = flux
        self.T = t
        self.RT = rt

        self.OMEGA = float(m)

    def run(self):
        # print(f"Calling Minimization Subroutine: SIMANN T={self.T}\n")

        runner = SimulatedAnnealingRunner(
            N=self.M,
            M=self.M,
            NB=self.NB,
            MM=self.MM,
            FI=self.FI,
            S=self.S,
            D=self.D,
            OMEGA=self.OMEGA,
            FLUX=self.FLUX,
            T=self.T,
            RT=self.RT
        )

        lambda_vec = runner.run()

        print("\nCurrent values of Lambdas:")
        for i, val in enumerate(lambda_vec, start=1):
            print(f"  Detector={i}  Lambda={val:.6f}")

        return lambda_vec
        