#This is the python version of prt.pl
#prt.pl operates as an SA intermediate output reported

#  This subroutine prints intermediate output, as does PRT2 through
#  PRT10. Note that if SA is minimizing the function, the sign of the
#  function value and the directions (up/down) are reversed in all
#  output to correspond with the actual function optimization. This
#  correction is because SA was written to maximize functions and
#  it minimizes by maximizing the negative a function.

from .prtvec import VectorPrinter

class SAReporter:
    #Prints the simulated annealing intermediate messages, all the methods should correspond if they share a name
    @staticmethod
    def prt1(i, xi, LB, UB):
        print(f"  THE STARTING VALUE {xi} IS OUTSIDE THE BOUNDS")
        print("  (LB AND UB). EXECUTION TERMINATED WITHOUT ANY")
        print("  OPTIMIZATION. RESPECIFY X, UB OR LB SO THAT")
        print(f"  {LB} < {xi} < {UB}, I = {i}, N.")

    @staticmethod
    def prt2(maximize, x, f):
        print()
        VectorPrinter.print_vector("INITIAL X", x)
        print(f"  INITIAL F: {f if maximize else -f:.18g}")

    @staticmethod
    def prt3(maximize, xp, x, f):
        print()
        VectorPrinter.print_vector("CURRENT X", x)
        print(f"  CURRENT F: {f if maximize else -f:.18g}")
        VectorPrinter.print_vector("TRIAL X", xp)
        print("  POINT REJECTED SINCE OUT OF BOUNDS")

    @staticmethod
    def prt4(maximize, xp, x, fp, f):
        VectorPrinter.print_vector("CURRENT X", x)
        print(f"  CURRENT F: {f if maximize else -f:.18g}")
        VectorPrinter.print_vector("TRIAL X", xp)
        print(f"  RESULTING F: {fp if maximize else -fp:.18g}")

    @staticmethod
    def prt5():
        print("  TOO MANY FUNCTION EVALUATIONS; CONSIDER")
        print("  INCREASING MAXEVL OR EPS, OR DECREASING")
        print("  NT OR RT. THESE RESULTS ARE LIKELY TO BE")
        print("  POOR.")

    @staticmethod
    def prt6(maximize):
        if maximize:
            print("  THOUGH LOWER, POINT ACCEPTED")
        else:
            print("  THOUGH HIGHER, POINT ACCEPTED")

    @staticmethod
    def prt7(maximize):
        if maximize:
            print("  LOWER POINT REJECTED")
        else:
            print("  HIGHER POINT REJECTED")

    @staticmethod
    def prt8(vm, xopt, x):
        print("\nINTERMEDIATE RESULTS AFTER STEP LENGTH ADJUSTMENT\n")
        VectorPrinter.print_vector("NEW STEP LENGTH (VM)", vm)
        VectorPrinter.print_vector("CURRENT OPTIMAL X", xopt)
        VectorPrinter.print_vector("CURRENT X", x)
        print()

    @staticmethod
    def prt9(
        maximize, n, t, xopt, vm, fopt,
        nup, ndown, nrej, out_of_bounds, nnew
    ):
        totmov = nup + ndown + nrej
        print("\n\nINTERMEDIATE RESULTS BEFORE NEXT TEMPERATURE REDUCTION")
        print(f"  CURRENT TEMPERATURE: {t}")
        if maximize:
            print(f"  MAX FUNCTION VALUE SO FAR: {fopt:.18g}")
            print(f"  TOTAL MOVES: {totmov}")
            print(f"  UPHILL: {nup}")
            print(f"     ACCEPTED DOWNHILL: {ndown}")
            print(f"     REJECTED DOWNHILL: {nrej}")
            print(f"  OUT OF BOUNDS TRIALS: {out_of_bounds}")
            print(f"  NEW MAXIMA THIS TEMPERATURE: {nnew}")
        else:
            print(f"  MIN FUNCTION VALUE SO FAR: {-fopt:.18g}")
            print(f"  TOTAL MOVES: {totmov}")
            print(f"     DOWNHILL: {nup}")
            print(f"     ACCEPTED UPHILL: {ndown}")
            print(f"     REJECTED UPHILL: {nrej}")
            print(f"  TRIALS OUT OF BOUNDS: {out_of_bounds}")
            print(f"  NEW MINIMA THIS TEMPERATURE: {nnew}")
        VectorPrinter.print_vector("CURRENT OPTIMAL X", xopt)
        VectorPrinter.print_vector("STEP LENGTH (VM)", vm)

    @staticmethod
    def prt10():
        print("  SA ACHIEVED TERMINATION CRITERIA. IER = 0.")