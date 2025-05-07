#!/usr/bin/perl

sub SA{
	local *N=shift;
	local *X=shift;
	local *MAX=shift;
	local *RT=shift;
	local *EPS=shift;
	local *NS=shift;
	local *NT=shift;
	local *NEPS=shift;
	local *MAXEVL=shift;
	local *LB=shift;
	local *UB=shift;
	local *C=shift;
	local *IPRINT=shift;
	local *ISEED1=shift;
	local *ISEED2=shift;
	local *T=shift;
	local *VM=shift;
	local *XOPT=shift;
	local *FOPT=shift;
	local *NACC=shift;
	local *NFCNEV=shift;
	local *NOBDS=shift;
	local *IER=shift;
	local *FSTAR=shift;
	local *XP=shift;
	local *NACP=shift;
	local *M=shift;
	local *NB=shift;
	local *MM=shift;
	local *FI=shift;
	local *S=shift;
	local *D=shift;
	local *OMEGA=shift;
	local *FLUX=shift;

	use subs qw(RANMAR EXPREP);
	print "\nBeginning of SA N=$N M=$M OMEGA=$OMEGA RT=$RT\n";


		#      SUBROUTINE SA(N,X,MAX,RT,EPS,NS,NT,NEPS,MAXEVL,LB,UB,C,IPRINT,
		#     1              ISEED1,ISEED2,T,VM,XOPT,FOPT,NACC,NFCNEV,NOBDS,IER,
		#     2              FSTAR,XP,NACP)

		#  Converted to perl for BUMS Bonner Sphere Unfolding Web interface
		#  By Jeremy Sweezy (jesweezy@yahoo.com) at Georgia Tech 5/1/00
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

		#  Initialize the random number generator RANMAR.
	my (@U_RASET1,$C_RASET1,$CD_RASET1,$CM_RASET1,$I97_RASET1,$J97_RASET1);
	my ($I,$J,$H);
	
#	for ($I=1;$I<$N+1;$I++){
#		print "I=$I C=$C[$I]\n";
#	}

	$test1=EXPREP(175);
	$test2=EXPREP(-185);
	$test3=EXPREP(100);
	print "exprep(175)=$test1 exprep(-185)=$test2 exprep(100)=$test3\n";

	for ($I=1;$I<98;$I++){
		$U_RASET1[$I]=0;
	}

#	print "SA 1 N=$N\n";
	&RMARIN(\$ISEED1,\$ISEED2,\@U_RASET1,\$C_RASET1,\$CD_RASET1,\$CM_RASET1,\$I97_RASET1,\$J97_RASET1);
#	print "SA 2 N=$N I97=$I97_RASET1\n";


		#  Set initial values.
	$NACC = 0;
	$NOBDS = 0;
	$NFCNEV = 0;
	$IER = 99;

#	print "SA 3 N=$N\n";
	for($I=1;$I<$N+1;$I++){
		$XOPT[$I] = $X[$I];
		$NACP[$I] = 0;
	}

#	print "SA 4 N=$N\n";
	for($I=1;$I<$NEPS+1;$I++){
		$FSTAR[$I] = 1.0E+20;
	}

#  If the initial temperature is not positive, notify the user and 
#  return to the calling routine.  
	if ($T <= 0.0){
	 	print "  THE INITIAL TEMPERATURE IS NOT POSITIVE. ",br,
     		     "  RESET THE VARIABLE T. ",br;
	 	$IER = 3;
#		print "Returning from SA 1 N=$N\n";
		return;
	}	

#  If the initial value is out of bounds, notify the user and return
#  to the calling routine.
	for($I=1;$I<$N+1;$I++){
	 	if (( ($X[$I]) > ($UB[$I])) || (($X[$I]) < ($LB[$I]))) {
	    	&PRT1;
	    	$IER = 2;
#		print "Returning from SA 2 N=$N\n";
			return;
		}
	}

#  Evaluate the function with input X and return value as F.
	my ($F);
#	print "SA 5 N=$N M=$M OMEGA=$OMEGA\n";

	$F = &FCN($N,\@X,$M,$NB,\@MM,\@FI,\@S,\@D,$OMEGA,$FLUX);
#	print "Out of FCN 1 F=$F\n";

#  If the function is to be minimized, switch the sign of the function.
#  Note that all intermediate and final output switches the sign back
#  to eliminate any possible confusion for the user.
	unless($MAX) {$F = -$F;}
	$NFCNEV = $NFCNEV + 1;
	$FOPT = $F;
	$FSTAR[1] = $F;
#	print "\nF=$F\n";
	if ($IPRINT >= 1) {&PRT2(\$MAX,\$N,\$X,\$F);}

#  Start the main loop. Note that it terminates if (i) the algorithm
#  succesfully optimizes the function or (ii) there are too many
#  function evaluations (more than MAXEVL).
	$STOP=1;
	do {
		$NUP = 0;
		$NREJ = 0;
		$NNEW = 0;
		$NDOWN = 0;
		$LNOBDS = 0;
#	print "SA 6 N=$N\n";
		my $X;
		for ($Z=1;$Z<$NT+1;$Z++){
#	print "SA 7 N=$N\n";
			for ($J=1;$J<$NS+1;$J++){
#	print "SA 8 N=$N\n";
				for ($H=1;$H<$N+1;$H++){

#	print "SA 9 N=$N\n";
#  Generate XP, the trial value of X. Note use of VM to choose XP.
					for ($I=1;$I<$N+1;$I++){
#	print "SA 10 Loop # $I N=$N\n";
						if ($I == $H) {
#								print "I97=$I97_RASET1\n";
							$XP[$I]=$X[$I]+(RANMAR(\@U_RASET1,\$C_RASET1,\$CD_RASET1,\$CM_RASET1,\$I97_RASET1,\$J97_RASET1)*2-1)*$VM[$I];
#						print "Z=$Z J=$J H=$H I=$I X=$X[$I] XP=$XP[$I] VM=$VM[$I]\n";
						}
						else {
							$XP[$I] = $X[$I];
						}

#	print "SA 11 N=$N\n";
#  If XP is out of bounds, select a point in bounds for the trial.
						if(($XP[$I]<$LB[$I]) || ($XP[$I]>$UB[$I])){
					print "XP=$XP[$I]  Z=$Z J=$J H=$H I=$I\n";
							$XP[$I] = $LB[$I] + ($UB[$I] - $LB[$I])*RANMAR(\@U_RASET1,\$C_RASET1,\$CD_RASET1,\$CM_RASET1,\$I97_RASET1,\$J97_RASET1);
							$LNOBDS = $LNOBDS + 1;
							$NOBDS = $NOBDS + 1;
							if($IPRINT>=3) {&PRT3(\$MAX,\$N,\@XP,\@X,\$FP,\$F);}
#					print "XP=$XP[$I]  Z=$Z J=$J H=$H I=$I\n";
						}
					} 

#	print "SA 12 N=$N\n";
#  Evaluate the function with the trial point XP and return as FP.
#					print "Lambda(1)=$XP[1]\n";
					$FP=&FCN($N,\@XP,$M,$NB,\@MM,\@FI,\@S,\@D,$OMEGA,$FLUX);

#	print "Out of FCN 2 Z=$Z J=$J H=$H I=$I FP=$FP\n";
					unless($MAX) {$FP = -$FP;}
#	print "SA 12 b N=$N\n";
					$NFCNEV = $NFCNEV + 1;
					if($IPRINT>=3) {
						&PRT4(\$MAX,\$N,\@XP,\@X,\$FP,\$F);
#	print "SA 12 c N=$N\n";
					}

#	print "SA 13 c N=$N\n";
#  If too many function evaluations occur, terminate the algorithm.
					if($NFCNEV>=$MAXEVL) {
						&PRT5;
						unless($MAX) {$FOPT = -$FOPT;}
						$IER = 1;
						return;
					}

#	print "SA 14 N=$N\n";
#  Accept the new point if the function value increases.
#					print "FP=$FP   F=$F Z=$Z J=$J H=$H\n";
					if($FP>=$F) {
						if($IPRINT>=3) {
							print "  POINT ACCEPTED",br;
						}
						for($I=1;$I<$N+1;$I++){
							$X[$I] = $XP[$I];
						}
						$F = $FP;
						$NACC = $NACC + 1;
						$NACP[$H] = $NACP[$H] + 1;
						$NUP = $NUP + 1;

#	print "SA 15a\n";
#  If greater than any other point, record as new optimum.
						if ($FP>$FOPT) {
#	print "SA 15b\n";
							if($IPRINT>=3) {
#	print "SA 15c\n";
								print "NEW OPTIMUM",br;
							}
#	print "SA 15d\n";
							for($I=1;$I<$N+1;$I++){
								$XOPT[$I] = $XP[$I];
							}
#	print "SA 15e\n";
							$FOPT = $FP;
							$NNEW = $NNEW + 1;
						}
					}
#  If the point is lower, use the Metropolis criteria to decide on
#  acceptance or rejection.
					else {
#	print "SA 16 T=$T FP=$FP F=$F\n";

						$P = EXPREP(($FP-$F)/$T);
						$PP =  &RANMAR(\@U_RASET1,\$C_RASET1,\$CD_RASET1,\$CM_RASET1,\$I97_RASET1,\$J97_RASET1);
#					print "P=$P PP=$PP Z=$Z J=$J H=$H\n";
						if ($PP<$P){
#							print "In PP<P\n";
							if($IPRINT>=3) {&PRT6(\$MAX);}
							for($I=1;$I<$N+1;$I++){
								$X[$I] = $XP[$I];
							}
							$F = $FP;
							$NACC = $NACC + 1;
							$NACP[$H] = $NACP[$H] + 1;
							$NDOWN = $NDOWN + 1;
						}
						else {
							$NREJ = $NREJ + 1;
							if($IPRINT>=3) {&PRT7(\$MAX);}
						}
					}
				}
			}
#	print "SA 17\n";
#  Adjust VM so that approximately half of all evaluations are accepted.
			for($I=1;$I<$N+1;$I++){
#	print "SA 18\n";
				$RATIO = $NACP[$I]/$NS;
				if ($RATIO>0.6){
					$VM[$I] = $VM[$I]*(1. + $C[$I]*($RATIO - .6)/.4);
				}
				elsif ($RATIO<0.4){
					$VM[$I] = $VM[$I]/(1. + $C[$I]*((.4 - $RATIO)/.4));
				}
				if ($VM[$I]>($UB[$I]-$LB[$I])) {
					$VM[$I] = $UB[$I] - $LB[$I];
				}
			}

			if($IPRINT>=2) {
				&PRT8(\$N,\@VM,\@XOPT,\@X);
			}
#	print "SA 19\n";

			for($I=1;$I<$N+1;$I++){
				$NACP[$I] = 0;
			}
		}

		if($IPRINT>=1){
			&PRT9(\$MAX,\$N,\$T,\@XOPT,\@VM,\$FOPT,\$NUP,\$NDOWN,\$NREJ,\$LNOBDS,\$NNEW);
		}

#  Check termination criteria.
		$QUIT = "";
		$FSTAR[1] = $F;
		if (($FOPT - $FSTAR[$1])<= $EPS) {$QUIT = 1;}
#	print "SA 20\n";
		for($I=1;$I<$NEPS+1;$I++){
			if (abs($F - $FSTAR[$I])>$EPS) {$QUIT = "";}
		}

#  Terminate SA if appropriate.
#	print "SA 21\n";
		if ($QUIT){
			for($I=1;$I<$N+1;$I++){
				$X[$I] = $XOPT[$I];
			}
			$IER = 0;
			unless ($MAX) {$FOPT = -$FOPT;}
			if($IPRINT>=1) {&PRT10};
			return;
		}

#  If termination criteria is not met, prepare for another loop.
		$T = $RT*$T;
#	print "SA 22 T=$T RT=$RT\n";
		for($I=$NEPS;$I>1;$I--){
			$FSTAR[$I] = $FSTAR[$I-1];
		}
		$F = $FOPT;
#	print "SA 23\n";
		for($I=1;$I<$N+1;$I++){
			$X[$I] = $XOPT[$I];
		}
#	print "End of SA Loop\n";
#  Loop again.
	} while $STOP;
}
1;

