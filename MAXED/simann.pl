#!/usr/bin/perl

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

sub simann {
	local *N=shift;
	local *T=shift;
	local *RT=shift;
	local *M=shift;
	local *NB=shift;
	local *MM=shift;
	local *FI=shift;
	local *S=shift;
	local *D=shift;
	local *OMEGA=shift;
	local *FLUX=shift;

	print "SIMANN OMEGA=$OMEGA T=$T RT=$RT\n";
	my @LAMBDA;
	$NEPS=4;

#  Set input parameters.
	my $MAX = 1;
	my $EPS = 1.0E-6;
	my $ISEED1 = 1;
	my $ISEED2 = 2;
	my $NS = 20;
	my $NT = 5;
	my $MAXEVL = 100000; 
	my $IPRINT = 1;

	my ($I, @LB, @UB, @C);

	for($I=1;$I<$N+1;$I++){
		$LB[$I] = -1.0E25;
		$UB[$I] =  1.0E25;
		$C[$I] = 2.0;
	}

	my (@X);
#  Initialize the X(I) to zero.
	for($I=1;$I<$N+1;$I++){
		$X[$I] = 0.0;
	}

#  Set input values of the input/output parameters.
	my (@VM);
	for($I=1;$I<$N+1;$I++){
		$VM[$I] = 1.0;
	}

	       
	print "SIMULATED ANNEALING EXAMPLE";
	print "\n";
	printf " NUMBER OF PARAMETERS: %3d   MAXIMAZATION: %d",$N,$NMAX;
	print "\n";
#	print br;
	printf " INITIAL TEMP: %8.2g   RT: %8.2g   EPS: %8.2g",$T,$RT,$EPS;
	print "\n";
#	print br;
	printf " NS: %3d   NT: %2d   NEPS: %2d",$NS,$NT,$NEPS;
	print "\n";
#	print br;
	printf " MAXEVL: %10d   IPRINT: %1d   ISEED1: %4d",$MAXEVL,$IPRINT,$ISEED1;
	print "\n";
#	print br;
	printf " ISEED2: %4d",$ISEED2;
	print "\n";
#	print br;


	&PRTVEC(\@X,$N,'STARTING VALUES');
	&PRTVEC(\@VM,$N,'INITIAL STEP LENGTH');
	&PRTVEC(\@LB,$N,'LOWER BOUND');
	&PRTVEC(\@UB,$N,'UPPER BOUND');
	&PRTVEC(\@C,$N,'C VECTOR');

	print "  ****   END OF DRIVER ROUTINE OUTPUT   ****",br,
		"  ****   BEFORE CALL TO SA.             ****",br;      
	
	print " Before SA N=$N\n";

	&SA(\$N,\@X,\$MAX,\$RT,\$EPS,\$NS,\$NT,\$NEPS,\$MAXEVL,\@LB,\@UB,\@C,\$IPRINT,\$ISEED1,
	\$ISEED2,\$T,\@VM,\@XOPT,\$FOPT,\$NACC,\$NFCNEV,\$NOBDS,\$IER,\@FSTAR,\@XP,\@NACP,
	\$M,\$NB,\@MM,\@FI,\@S,\@D,\$OMEGA,\$FLUX);
	print "  ****   RESULTS AFTER SA   ****   ",br;
      
	&PRTVEC(\@XOPT,$N,'SOLUTION');
	&PRTVEC(\@VM,$N,'FINAL STEP LENGTH');


	printf " OPTIMAL FUNCTION VALUE: %20.13g",$FOPT;
	print br;
	printf " NUMBER OF FUNCTION EVALUATIONS:     %10d",$NFCNEV;
	print br;
	printf " NUMBER OF ACCEPTED EVALUATIONS:     %10d",$NACC;
	print br;
	printf " NUMBER OF OUT OF BOUND EVALUATIONS: %10d",$NOBDS;
	print br;
	printf " FINAL TEMP: %20.13g  IER: %3d",$T,$IER;

	my (@LAMBDA);

	for($I=1;$I<$N+1;$I++){
		$LAMBDA[$I] = $XOPT[$I];
	}
	return (\@LAMBDA);
}
1;
