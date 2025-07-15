#This file will be the equivalent to simann.pl from the oringinal MAXED directory

# SIGMANN
#   ***************************************************************************
#
#   NOTE 1: The rest of this file contains a modification of the program
#   SIMANN.  The program was modified by Marcel Reginatto.  The
#   modifications include:
#   (1) A new function subroutine FCN was put in place of the original one.
#   (2) The values of some of the input parameters (such as MAX, T, RT)
#       have been changed
#
#   NOTE 2: All comments that follow are the ones that appeared in the
#   original (unmodified) version of SIMANN.  Be aware that some of these
#   comments are specific to the original function, and do not necessarily
#   apply to the function optimized in this modified version.
#
#   
#
# ABSTRACT:
#   Simulated annealing is a global optimization method that distinguishes
#   between different local optima. Starting from an initial point, the
#   algorithm takes a step and the function is evaluated. When minimizing a
#   function, any downhill step is accepted and the process repeats from this
#   new point. An uphill step may be accepted. Thus, it can escape from local
#   optima. This uphill decision is made by the Metropolis criteria. As the
#   optimization process proceeds, the length of the steps decline and the
#   algorithm closes in on the global optimum. Since the algorithm makes very
#   few assumptions regarding the function to be optimized, it is quite
#   robust with respect to non-quadratic surfaces. The degree of robustness
#   can be adjusted by the user. In fact, simulated annealing can be used as
#   a local optimizer for difficult functions.
#
#   This implementation of simulated annealing was used in "Global Optimization
#   of Statistical Functions with Simulated Annealing," Goffe, Ferrier and
#   Rogers, Journal of Econometrics, vol. 60, no. 1/2, Jan./Feb. 1994, pp.
#   65-100. Briefly, we found it competitive, if not superior, to multiple
#   restarts of conventional optimization routines for difficult optimization
#   problems.
#
#   For more information on this routine, contact its author:
#   Bill Goffe, bgoffe@whale.st.usm.edu
#
#C      PROGRAM SIMANN
#  This file is an example of the Corana et al. simulated annealing
#  algorithm for multimodal and robust optimization as implemented
#  and modified by Goffe, Ferrier and Rogers. Counting the above line
#  ABSTRACT as 1, the routine itself (SA), with its supplementary
#  routines, is on lines 232-990. A multimodal example from Judge et al.
#  (FCN) is on lines 150-231. The rest of this file (lines 1-149) is a
#  driver routine with values appropriate for the Judge example. Thus, this
#  example is ready to run.
#
#  To understand the algorithm, the documentation for SA on lines 236-
#  484 should be read along with the parts of the paper that describe
#  simulated annealing. Then the following lines will then aid the user
#  in becomming proficient with this implementation of simulated
#  annealing.
#
#  Learning to use SA:
#      Use the sample function from Judge with the following suggestions
#  to get a feel for how SA works. When you've done this, you should be
#  ready to use it on most any function with a fair amount of expertise.
#    1. Run the program as is to make sure it runs okay. Take a look at
#       the intermediate output and see how it optimizes as temperature
#       (T) falls. Notice how the optimal point is reached and how
#       falling T reduces VM.
#    2. Look through the documentation to SA so the following makes a
#       bit of sense. In line with the paper, it shouldn't be that hard
#       to figure out. The core of the algorithm is described on pp. 68-70
#       and on pp. 94-95. Also see Corana et al. pp. 264-9.
#    3. To see how it selects points and makes decisions about uphill
#       and downhill moves, set IPRINT = 3 (very detailed intermediate
#       output) and MAXEVL = 100 (only 100 function evaluations to limit
#       output).
#    4. To see the importance of different temperatures, try starting
#       with a very low one (say T = 10E-5). You'll see (i) it never
#       escapes from the local optima (in annealing terminology, it
#       quenches) & (ii) the step length (VM) will be quite small. This
#       is a key part of the algorithm: as temperature (T) falls, step
#       length does too. In a minor point here, note how VM is quickly
#       reset from its initial value. Thus, the input VM is not very
#       important. This is all the more reason to examine VM once the
#       algorithm is underway.
#    5. To see the effect of different parameters and their effect on
#       the speed of the algorithm, try RT = .95 & RT = .1. Notice the
#       vastly different speed for optimization. Also try NT = 20. Note
#       that this sample function is quite easy to optimize, so it will
#       tolerate big changes in these parameters. RT and NT are the
#       parameters one should adjust to modify the runtime of the
#       algorithm and its robustness.
#    6. Try constraining the algorithm with either LB or UB.

import numpy as np
from bums2.FORTRAN_METHODS.MAXED.annealing.sa import SimulatedAnnealing
from bums2.FORTRAN_METHODS.MAXED.annealing.prtvec import VectorPrinter

class SimulatedAnnealingRunner:
    def __init__(self, N, M, NB, MM, FI, S, D, OMEGA, FLUX, T=1.0, RT=0.9, EPS=1e-6, NS=20, NT=5,
                 NEPS=4, MAXEVL=100_000, ISEED1=1, ISEED2=2, IPRINT=0, MAX=True):
        self.N = N
        self.M = M
        self.NB = NB
        self.MM = np.array(MM)
        self.FI = np.array(FI)
        self.S = np.array(S)
        self.D = np.array(D)
        self.OMEGA = OMEGA
        self.FLUX = FLUX

        # SA settings
        self.T = T
        self.RT = RT
        self.EPS = EPS
        self.NS = NS
        self.NT = NT
        self.NEPS = NEPS
        self.MAXEVL = MAXEVL
        self.ISEED1 = ISEED1
        self.ISEED2 = ISEED2
        self.IPRINT = IPRINT
        self.MAX = MAX

        # Optimization vectors
        self.X = [0.0] * N
        self.VM = [1.0] * N
        self.LB = [-1e25] * N
        self.UB = [1e25] * N
        self.C = [2.0] * N

    def run(self):
        print("\n==== Simulated Annealing Runner ====")
        print(f"OMEGA: {self.OMEGA}, T: {self.T}, RT: {self.RT}")
        print(f"MAXIMIZE: {self.MAX}, DIM: {self.N}, ISEED1/2: {self.ISEED1}, {self.ISEED2}")
        print(f"NT: {self.NT}, NS: {self.NS}, MAXEVL: {self.MAXEVL}, NEPS: {self.NEPS}")

        if self.IPRINT:
            VectorPrinter.print_vector("STARTING VALUES", self.X)
            VectorPrinter.print_vector("INITIAL STEP LENGTH", self.VM)
            VectorPrinter.print_vector("LOWER BOUND", self.LB)
            VectorPrinter.print_vector("UPPER BOUND", self.UB)
            VectorPrinter.print_vector("C VECTOR", self.C)

        sa = SimulatedAnnealing(
            N=self.N,
            M=self.M,
            NB=self.NB,
            MM=self.MM,
            FI=self.FI,
            S=self.S,
            D=self.D,
            OMEGA=self.OMEGA,
            FLUX=self.FLUX,
            T=self.T,
            RT=self.RT,
            EPS=self.EPS,
            NS=self.NS,
            NT=self.NT,
            NEPS=self.NEPS,
            MAXEVL=self.MAXEVL,
            ISEED1=self.ISEED1,
            ISEED2=self.ISEED2,
            IPRINT=self.IPRINT,
            MAX=self.MAX,
            X=self.X,
            VM=self.VM,
            LB=self.LB,
            UB=self.UB,
            C=self.C
        )

        try:
            XOPT = sa.optimize()
        except RuntimeError as e:
            print("\nWARNING: Optimization did not converge", e)
            XOPT = sa.XOPT

        print("  ****   RESULTS AFTER SA   ****   ")
        VectorPrinter.print_vector("SOLUTION", XOPT)
        VectorPrinter.print_vector("FINAL STEP LENGTH", sa.VM)
        print(f"OPTIMAL FUNCTION VALUE: {sa.FOPT:.10f}")
        print(f"FUNCTION EVALUATIONS:  {sa.NFCNEV}")
        print(f"ACCEPTED EVALUATIONS:  {sa.NACC}")
        print(f"OUT OF BOUNDS EVALS:   {sa.NOBDS}")
        print(f"FINAL TEMP: {sa.T:.10f}  IER: {sa.IER}")
        return XOPT

