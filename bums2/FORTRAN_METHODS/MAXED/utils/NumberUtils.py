#This file will consist of a class that applies the same logic from exprep, ranmar and rmarin from the MAXED directory
import math

class NumberUtils:
    #  This subroutine and the next function generate random numbers. See
    #  the comments for SA for more information. The only changes from the
    #  orginal code is that (1) the test to make sure that RMARIN runs first
    #  was taken out since SA assures that this is done (this test didn't
    #  compile under IBM's VS Fortran) and (2) typing ivec as integer was
    #  taken out since ivec isn't used. With these exceptions, all following
    #  lines are original.

    # This is the initialization routine for the random number generator
    #     RANMAR()
    # NOTE: The seed variables can have values between:    0 <= IJ <= 31328
    #                                                      0 <= KL <= 30081
    def __init__(self, seed1: int=1, seed2: int=2):
        #Validate seeds
        if not (0 <= seed1 <= 31328 and 0 <= seed2 <= 30081):
            raise ValueError("Seed1 must be 0..31328 and Seed2 must be 0..30081")
        
        #Initialize
        self.U = [0.0] * 98
        self.C = 362436.0 / 16777216.0
        self.CD = 7654321.0 / 16777216.0
        self.CM = 16777213.0 / 16777216.0
        self.I97 = 97
        self.J97 = 33

        IJ = seed1
        KL = seed2

        i = (IJ // 177) % 177 + 2
        j = (IJ // 177) + 2
        k = (KL // 169) % 178 + 1
        l = (KL // 169)

        for ii in range(1, 98):
            s = 0.0
            t = 0.5
            for jj in range(1, 25):
                m = ((i * j) % 179 * k) % 179
                m = (m * k) % 179
                i, j, k = j, k, m
                l = (53 * l  + 1) % 169
                if ((l*m) % 64) >= 32:
                    s += t
                t *= 0.5
            self.U[ii] = s

    def RANMAR(self) -> float:
        uni = self.U[self.I97] - self.U[self.J97]

        if uni < 0.0:
            uni += 1.0
        self.U[self.I97] = uni
        self.I97 = self.I97 - 1

        if self.I97 == 0:
            self.I97 = 97
        self.J97 = self.J97 - 1

        if self.J97 == 0:
            self.J97 = 97
        self.C = self.C - self.CD

        if self.C < 0.0:
            self.C += self.CM
        uni = uni - self.C

        if uni < 0.0:
            uni += 1.0
        return uni

    @staticmethod
    def exprep(rdum: float) -> float:
        #Avoids unfer/overflow on modern IEEE floats
        if rdum > 700.0:
            return float('inf')
        elif rdum < -745.0:
            return 0.0
        else:
            return math.exp(rdum)
