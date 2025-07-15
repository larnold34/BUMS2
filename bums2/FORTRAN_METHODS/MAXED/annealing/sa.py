#This will be the python version of sa.py

#      SUBROUTINE SA(N,X,MAX,RT,EPS,NS,NT,NEPS,MAXEVL,LB,UB,C,IPRINT,
        #     1              ISEED1,ISEED2,T,VM,XOPT,FOPT,NACC,NFCNEV,NOBDS,IER,
        #     2              FSTAR,XP,NACP)

        #  Converted to perl for BUMS Bonner Sphere Unfolding Web interface
        #  By Jeremy Sweezy (jesweezy@yahoo.com) at Georgia Tech 5/1/00
        #
        # Converted to python for the python converted BUMS 
        #
        #  Version: 3.2
        #  Date: 1/22/94.
        #  Differences compared to Version 2.0:
        #     1. If a trial is out of bounds, a point is randomly selected
        #        from LB(i) to UB(i). Unlike in version 2.0, this trial is
        #        evaluated and is counted in acceptances and rejections.
        #        All corresponding documentation was changed as well.
        #  Differences compared to Version 3.0:
        #     1. If VM(i) > (UB(i) - LB(i)), VM is set to UB(i) - LB(i).
        #        The idea is that if T is high relative to LB & UB, most
        #        points will be accepted, causing VM to rise. But, in this
        #        situation, VM has little meaning; particularly if VM is
        #        larger than the acceptable region. Setting VM to this size
        #        still allows all parts of the allowable region to be selected.
        #  Differences compared to Version 3.1:
        #     1. Test made to see if the initial temperature is positive.
        #     2. WRITE statements prettied up.
        #     3. References to paper updated.
        #
        #  Synopsis:
        #  This routine implements the continuous simulated annealing global
        #  optimization algorithm described in Corana et al.'s article
        #  "Minimizing Multimodal Functions of Continuous Variables with the
        #  "Simulated Annealing" Algorithm" in the September 1987 (vol. 13,
        #  no. 3, pp. 262-280) issue of the ACM Transactions on Mathematical
        #  Software.
        #
        #  A very quick (perhaps too quick) overview of SA:
        #     SA tries to find the global optimum of an N dimensional function.
        #  It moves both up and downhill and as the optimization process
        #  proceeds, it focuses on the most promising area.
        #     To start, it randomly chooses a trial point within the step length
        #  VM (a vector of length N) of the user selected starting point. The
        #  function is evaluated at this trial point and its value is compared
        #  to its value at the initial point.
        #     In a maximization problem, all uphill moves are accepted and the
        #  algorithm continues from that trial point. Downhill moves may be
        #  accepted; the decision is made by the Metropolis criteria. It uses T
        #  (temperature) and the size of the downhill move in a probabilistic
        #  manner. The smaller T and the size of the downhill move are, the more
        #  likely that move will be accepted. If the trial is accepted, the
        #  algorithm moves on from that point. If it is rejected, another point
        #  is chosen instead for a trial evaluation.
        #     Each element of VM periodically adjusted so that half of all
        #  function evaluations in that direction are accepted.
        #     A fall in T is imposed upon the system with the RT variable by
        #  T(i+1) = RT*T(i) where i is the ith iteration. Thus, as T declines,
        #  downhill moves are less likely to be accepted and the percentage of
        #  rejections rise. Given the scheme for the selection for VM, VM falls.
        #  Thus, as T declines, VM falls and SA focuses upon the most promising
        #  area for optimization.
        #
        #  The importance of the parameter T:
        #     The parameter T is crucial in using SA successfully. It influences
        #  VM, the step length over which the algorithm searches for optima. For
        #  a small intial T, the step length may be too small; thus not enough
        #  of the function might be evaluated to find the global optima. The user
        #  should carefully examine VM in the intermediate output (set IPRINT =
        #  1) to make sure that VM is appropriate. The relationship between the
        #  initial temperature and the resulting step length is function
        #  dependent.
        #     To determine the starting temperature that is consistent with
        #  optimizing a function, it is worthwhile to run a trial run first. Set
        #  RT = 1.5 and T = 1.0. With RT > 1.0, the temperature increases and VM
        #  rises as well. Then select the T that produces a large enough VM.
        #
        #  For modifications to the algorithm and many details on its use,
        #  (particularly for econometric applications) see Goffe, Ferrier
        #  and Rogers, "Global Optimization of Statistical Functions with
        #  Simulated Annealing," Journal of Econometrics, vol. 60, no. 1/2, 
        #  Jan./Feb. 1994, pp. 65-100.
        #  For more information, contact 
        #              Bill Goffe
        #              Department of Economics and International Business
        #              University of Southern Mississippi 
        #              Hattiesburg, MS  39506-5072 
        #              (601) 266-4484 (office)
        #              (601) 266-4920 (fax)
        #              bgoffe@whale.st.usm.edu (Internet)
        #
        #  As far as possible, the parameters here have the same name as in
        #  the description of the algorithm on pp. 266-8 of Corana et al.
        #
        #  In this description, SP is single precision, DP is double precision,
        #  INT is integer, L is logical and (N) denotes an array of length n.
        #  Thus, DP(N) denotes a double precision array of length n.
        #
        #  Input Parameters:
        #    Note: The suggested values generally come from Corana et al. To
        #          drastically reduce runtime, see Goffe et al., pp. 90-1 for
        #          suggestions on choosing the appropriate RT and NT.
        #    N - Number of variables in the function to be optimized. (INT)
        #    X - The starting values for the variables of the function to be
        #        optimized. (DP(N))
        #    MAX - Denotes whether the function should be maximized or
        #          minimized. A true value denotes maximization while a false
        #          value denotes minimization. Intermediate output (see IPRINT)
        #          takes this into account. (L)
        #    RT - The temperature reduction factor. The value suggested by
        #         Corana et al. is .85. See Goffe et al. for more advice. (DP)
        #    EPS - Error tolerance for termination. If the final function
        #          values from the last neps temperatures differ from the
        #          corresponding value at the current temperature by less than
        #          EPS and the final function value at the current temperature
        #          differs from the current optimal function value by less than
        #          EPS, execution terminates and IER = 0 is returned. (EP)
        #    NS - Number of cycles. After NS*N function evaluations, each
        #         element of VM is adjusted so that approximately half of
        #         all function evaluations are accepted. The suggested value
        #         is 20. (INT)
        #    NT - Number of iterations before temperature reduction. After
        #         NT*NS*N function evaluations, temperature (T) is changed
        #         by the factor RT. Value suggested by Corana et al. is
        #         MAX(100, 5*N). See Goffe et al. for further advice. (INT)
        #    NEPS - Number of final function values used to decide upon termi-
        #           nation. See EPS. Suggested value is 4. (INT)
        #    MAXEVL - The maximum number of function evaluations. If it is
        #             exceeded, IER = 1. (INT)
        #    LB - The lower bound for the allowable solution variables. (DP(N))
        #    UB - The upper bound for the allowable solution variables. (DP(N))
        #         If the algorithm chooses X(I) .LT. LB(I) or X(I) .GT. UB(I),
        #         I = 1, N, a point is from inside is randomly selected. This
        #         This focuses the algorithm on the region inside UB and LB.
        #         Unless the user wishes to concentrate the search to a par-
        #         ticular region, UB and LB should be set to very large positive
        #         and negative values, respectively. Note that the starting
        #         vector X should be inside this region. Also note that LB and
        #         UB are fixed in position, while VM is centered on the last
        #         accepted trial set of variables that optimizes the function.
        #    C - Vector that controls the step length adjustment. The suggested
        #        value for all elements is 2.0. (DP(N))
        #    IPRINT - controls printing inside SA. (INT)
        #             Values: 0 - Nothing printed.
        #                     1 - Function value for the starting value and
        #                         summary results before each temperature
        #                         reduction. This includes the optimal
        #                         function value found so far, the total
        #                         number of moves (broken up into uphill,
        #                         downhill, accepted and rejected), the
        #                         number of out of bounds trials, the
        #                         number of new optima found at this
        #                         temperature, the current optimal X and
        #                         the step length VM. Note that there are
        #                         N*NS*NT function evalutations before each
        #                         temperature reduction. Finally, notice is
        #                         is also given upon achieveing the termination
        #                         criteria.
        #                     2 - Each new step length (VM), the current optimal
        #                         X (XOPT) and the current trial X (X). This
        #                         gives the user some idea about how far X
        #                         strays from XOPT as well as how VM is adapting
        #                         to the function.
        #                     3 - Each function evaluation, its acceptance or
        #                         rejection and new optima. For many problems,
        #                         this option will likely require a small tree
        #                         if hard copy is used. This option is best
        #                         used to learn about the algorithm. A small
        #                         value for MAXEVL is thus recommended when
        #                         using IPRINT = 3.
        #             Suggested value: 1
        #             Note: For a given value of IPRINT, the lower valued
        #                   options (other than 0) are utilized.
        #    ISEED1 - The first seed for the random number generator RANMAR.
        #             0 .LE. ISEED1 .LE. 31328. (INT)
        #    ISEED2 - The second seed for the random number generator RANMAR.
        #             0 .LE. ISEED2 .LE. 30081. Different values for ISEED1
        #             and ISEED2 will lead to an entirely different sequence
        #             of trial points and decisions on downhill moves (when
        #             maximizing). See Goffe et al. on how this can be used
        #             to test the results of SA. (INT)
        #
        #  Input/Output Parameters:
        #    T - On input, the initial temperature. See Goffe et al. for advice.
        #        On output, the final temperature. (DP)
        #    VM - The step length vector. On input it should encompass the
        #         region of interest given the starting value X. For point
        #         X(I), the next trial point is selected is from X(I) - VM(I)
        #         to  X(I) + VM(I). Since VM is adjusted so that about half
        #         of all points are accepted, the input value is not very
        #         important (i.e. is the value is off, SA adjusts VM to the
        #         correct value). (DP(N))
        #
        #  Output Parameters:
        #    XOPT - The variables that optimize the function. (DP(N))
        #    FOPT - The optimal value of the function. (DP)
        #    NACC - The number of accepted function evaluations. (INT)
        #    NFCNEV - The total number of function evaluations. In a minor
        #             point, note that the first evaluation is not used in the
        #             core of the algorithm; it simply initializes the
        #             algorithm. (INT).
        #    NOBDS - The total number of trial function evaluations that
        #            would have been out of bounds of LB and UB. Note that
        #            a trial point is randomly selected between LB and UB.
        #            (INT)
        #    IER - The error return number. (INT)
        #          Values: 0 - Normal return; termination criteria achieved.
        #                  1 - Number of function evaluations (NFCNEV) is
        #                      greater than the maximum number (MAXEVL).
        #                  2 - The starting value (X) is not inside the
        #                      bounds (LB and UB).
        #                  3 - The initial temperature is not positive.
        #                  99 - Should not be seen; only used internally.
        #
        #  Work arrays that must be dimensioned in the calling routine:
        #       RWK1 (DP(NEPS))  (FSTAR in SA)
        #       RWK2 (DP(N))     (XP    "  " )
        #       IWK  (INT(N))    (NACP  "  " )
        #
        #  Required Functions (included):
        #    EXPREP - Replaces the function EXP to avoid under- and overflows.
        #             It may have to be modified for non IBM-type main-
        #             frames. (DP)
        #    RMARIN - Initializes the random number generator RANMAR.
        #    RANMAR - The actual random number generator. Note that
        #             RMARIN must run first (SA does this). It produces uniform
        #             random numbers on [0,1]. These routines are from
        #             Usenet's comp.lang.fortran. For a reference, see
        #             "Toward a Universal Random Number Generator"
        #             by George Marsaglia and Arif Zaman, Florida State
        #             University Report: FSU-SCRI-87-50 (1987).
        #             It was later modified by F. James and published in
        #             "A Review of Pseudo-random Number Generators." For
        #             further information, contact stuart@ads.com. These
        #             routines are designed to be portable on any machine
        #             with a 24-bit or more mantissa. I have found it produces
        #             identical results on a IBM 3081 and a Cray Y-MP.
        #
        #  Required Subroutines (included):
        #    PRTVEC - Prints vectors.
        #    PRT1 ... PRT10 - Prints intermediate output.
        #    FCN - Function to be optimized. The form is
        #            SUBROUTINE FCN(N,X,F)
        #            INTEGER N
        #            DOUBLE PRECISION  X(N), F
        #            ...
        #            function code with F = F(X)
        #            ...
        #            RETURN
        #            END
        #          Note: This is the same form used in the multivariable
        #          minimization algorithms in the IMSL edition 10 library.
        #
        #  Machine Specific Features:
        #    1. EXPREP may have to be modified if used on non-IBM type main-
        #       frames. Watch for under- and overflows in EXPREP.
        #    2. Some FORMAT statements use G25.18; this may be excessive for
        #       some machines.
        #    3. RMARIN and RANMAR are designed to be protable; they should not
        #       cause any problems.

        #  Type all external variables.
from typing import Tuple, List
import numpy as np
from bums2.FORTRAN_METHODS.MAXED.annealing.prt import SAReporter
from bums2.FORTRAN_METHODS.MAXED.annealing.prtvec import VectorPrinter
from bums2.FORTRAN_METHODS.MAXED.annealing.fcn import ObjectiveFunction
from bums2.FORTRAN_METHODS.MAXED.utils.NumberUtils import NumberUtils

class SimulatedAnnealing:
    def __init__(self, N, M, NB, MM, FI, S, D, OMEGA, FLUX, T, RT,
             EPS, NS, NT, NEPS, MAXEVL,
             ISEED1, ISEED2, IPRINT, MAX,
             X, VM, LB, UB, C):
    
        # Problem dimensions and data
        self.N = N
        self.M = M
        self.NB = NB
        self.MM = np.array(MM)
        self.FI = np.array(FI)
        self.S = np.array(S)
        self.D = np.array(D)
        self.OMEGA = OMEGA
        self.FLUX = FLUX

        # SA configuration
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

        # Optimization state vectors
        self.X = X
        self.VM = VM
        self.LB = LB
        self.UB = UB
        self.C = C
        
    def optimize(self):
        #Run the SA optimization and return the best solution vector
        #Print initial state
        VectorPrinter.print_vector("STARTING VALUES", self.X)
        VectorPrinter.print_vector("INITIAL STEP LENGTH", self.VM)
        VectorPrinter.print_vector("LOWER BOUND", self.LB)
        VectorPrinter.print_vector("UPPER BOUND", self.UB)
        VectorPrinter.print_vector("C VECTOR", self.C)

        #Start the core sa algorithm
        self._initialize()
        self._first_evaluation()
        self._anneal_loop()
        return self.XOPT
    
    def _initialize(self):
        #Initialize RNG, counter, history, etc...
        print(f"\nBeginning of SA N={self.N} M={self.M}, OMEGA={self.OMEGA}, RT={self.RT}\n")

        #Init RNG and exprep
        self.rng = NumberUtils(seed1=1, seed2=2)
        self.exprep = NumberUtils.exprep

        #SA counters and histories
        self.NACC = 0 #Accepted evaluations
        self.NOBDS = 0 #Out-of-bounds proposals
        self.NFCNEV = 0 #Total function evaluations
        self.IER = 99 #Error code

        self.XOPT = self.X.copy()
        self.NACP = [0] * self.N  #Accepted count per dimension
        self.FSTAR = [float('inf')] * self.NEPS

    def _first_evaluation(self):
        #If the initial temperature is not positive, notify the user and 
        #return to the calling routine.
        if self.T <= 0.0:
            print("  THE INITIAL TEMPERATURE IS NOT POSITIVE.\n  RESET THE VARIABLE T.\n")
            self.IER = 3
            return
        
        #If the initial value is out of bounds, notify the user and return
        #to the calling routine.
        for i, xi in enumerate(self.X):
            if xi < self.LB[i] or xi > self.UB[i]:
                SAReporter.prt1(i, xi, self.LB[i], self.UB[i])
                self.IER = 2
                return

        #Evaluate the function with input X and return value as F.
        self.F = self._evaluate(self.X)
        self.FOPT = self.F
        self.FSTAR[0] = self.F

        if self.IPRINT >= 1:
            SAReporter.prt2(self.MAX, self.X, self.F)

    def _anneal_loop(self):
        #Start the main loop. Note that it terminates if (i) the algorithm
        #succesfully optimizes the function or (ii) there are too many
        #function evaluations (more than MAXEVL).
        while True:
            NUP = NDOWN = NREJ = NNEW = LNOBDS = 0

            for z in range(self.NT):
                for j in range(self.NS):
                    for h in range(self.N):
                        NUP, NNEW, NREJ, NDOWN = self._inner_step(h, z, j, LNOBDS, NUP, NNEW, NREJ, NDOWN)

                self._adapt_steps()

                if self.IPRINT >= 2:
                    SAReporter.prt8(self.VM, self.XOPT, self.X)

            if self.IPRINT >= 1:
                SAReporter.prt9(
                    self.MAX,
                    self.N,
                    self.T,
                    self.XOPT,
                    self.VM,
                    self.FOPT,
                    self.NACC - NDOWN - NREJ,
                    NDOWN,
                    NREJ,
                    self.NOBDS - self.NOBDS,
                    NNEW
                )

            #Convergence test
            if self._converged():
                self.IER = 0
                if not self.MAX:
                    self.FOPT = -self.FOPT
                if self.IPRINT >= 1:
                    SAReporter.prt10()
                break

            #Cool down and prepare for the next loop
            self.T *= self.RT
            self.FSTAR = [self.F] + self.FSTAR[:-1]
            self.F = self.FOPT
            self.X[:] = self.XOPT
    
    def _inner_step(self, h: int, z: int, j:int, LNOBDS: int, NUP: int, NNEW: int, NREJ: int, NDOWN: int):
        #Perform a single trial on variable h

        #Propose new XP
        XP, oob = self._propose(h, z, j, LNOBDS)
        self.XP = XP

        #Evaluate
        f_new = self._evaluate(XP)

        #Accept the new point if the function value increases.
        if f_new >= self.F:
            #Accepted
            if self.IPRINT >= 3:
                print("POINT ACCEPTED")
            self.X, self.F = XP, f_new
            self.NACC += 1
            self.NACP[h] += 1
            NUP += 1

            #New global optimum?
            if f_new > self.FOPT:
                if self.IPRINT >= 3:
                    print("NEW OPTIMUM")
                self.FOPT = f_new
                self.XOPT = XP.copy()
                NNEW += 1

        #If the point is lower, use the Metropolis criteria to decide on acceptance or rejection.
        else:
             p = self.exprep((f_new - self.F) / self.T)
             pp = self.rng.RANMAR()
             if pp < p:
                  if self.IPRINT >= 3:
                       SAReporter.prt6(self.MAX)
                  self.X, self.F = XP, f_new
                  self.NACC += 1
                  self.NACP[h] += 1
                  NDOWN += 1
                  
             else:
                 if self.IPRINT >= 3:
                     NREJ += 1
                     SAReporter.prt7(self.MAX)
        return NUP, NNEW, NREJ, NDOWN
                     
                     
    
    def _propose(self, h: int, z: int, j: int, LNOBDS: int) -> Tuple[List[float], bool]:
        XP = self.X.copy()
        for i in range(self.N):
            if i == h:
                #Build the trial XP for the variable h
                delta = (self.rng.RANMAR() * 2 - 1) * self.VM[h]
                XP[i] += delta
                oob = False
            else:
                XP[i] = self.X[i]

            #Out of bounds?
            if XP[i] < self.LB[i] or XP[i] > self.UB[i]:
                print(f"XP={XP[i]}  Z={z} J={j} H={h} I={i}\n")
                XP[i] = self.LB[i] + (self.UB[i] - self.LB[i]) * self.rng.RANMAR()
                LNOBDS += 1
                self.NOBDS += 1
                oob = True
                if self.IPRINT >= 3:
                    SAReporter.prt3(self.MAX, XP, self.X, self.F)
        return XP, oob
    
    def _evaluate(self, X: List[float]) -> float:
        #Compute f(x), handling maximizing or minimizing
        f = ObjectiveFunction(
            mm= self.MM,
            fi= self.FI,
            s= self.S,
            d= self.D,
            omega= self.OMEGA,
            flux= self.FLUX,
            m= self.M,
            nb= self.NB
        )
        result = f(X)

        if not self.MAX:
            result = -result
        
        self.NFCNEV += 1
        if self.IPRINT >= 3:
            SAReporter.prt4(self.MAX, self.XP, X, self.F, f)

        if self.NFCNEV >= self.MAXEVL:
            SAReporter.prt5()
            self.IER = 1
            raise RuntimeError("Exceeded maximum function evaluations")
        return result
         
    def _adapt_steps(self):
        #Adjust each VM[i] so ~50% acceptance per dimension
        for i in range(self.N):
            ratio = self.NACP[i] / self.NS

            if ratio > 0.6:
                self.VM[i] *= 1 + self.C[i] * (ratio - 0.6) / 0.4
            elif ratio < 0.4:
                self.VM[i] /= 1 + self.C[i] * (0.4 - ratio) / 0.4
            #Enforce VM <= (UB-LB)
            self.VM[i] = min(self.VM[i], self.UB[i] - self.LB[i])
            self.NACP[i] = 0

    def _converged(self) -> bool:
        #Check if the last NEPS values of F differ by < EPS
        #Shift history
        self.FSTAR.pop(0)
        self.FSTAR.append(self.F)
        #If all within EPS of each other, done
        return max(self.FSTAR) - min(self.FSTAR) <= self.EPS








        










        