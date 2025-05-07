#!/usr/bin/perl

sub PRT1{
#  This subroutine prints intermediate output, as does PRT2 through
#  PRT10. Note that if SA is minimizing the function, the sign of the
#  function value and the directions (up/down) are reversed in all
#  output to correspond with the actual function optimization. This
#  correction is because SA was written to maximize functions and
#  it minimizes by maximizing the negative a function.

	print "  THE STARTING VALUE (X) IS OUTSIDE THE BOUNDS ",
		br,"  (LB AND UB). EXECUTION TERMINATED WITHOUT ANY",
		br,"  OPTIMIZATION. RESPECIFY X, UB OR LB SO THAT  ",
		br,"  LB(I) .LT. X(I) .LT. UB(I), I = 1, N. ",br;

	return;
}

sub PRT2{
	local *MAX=shift;
	local *N=shift;
	local *X=shift;
	local *F=shift;

	print "   ";
    &PRTVEC(\@X,$N,'INITIAL X');
	print "\n";
	if($MAX) {
		printf "  INITIAL F: %25.18g",$F;
	}
	else{
		printf "  INITIAL F: %25.18g",-$F;
	}

	return;
}

sub PRT3{
	local *MAX=shift;
	local *N=shift;
	local *XP=shift;
	local *X=shift;
	local *FP=shift;
	local *F=shift;

	print "   ";
    &PRTVEC(\@X,$N,'CURRENT X');
	if($MAX) {
		printf "  CURRENT F: %25.18g",$F;
	}
	else{
		printf "  CURRENT F: %25.18g",-$F;
	}
    &PRTVEC(\@XP,$N,'TRIAL X');
    print "  POINT REJECTED SINCE OUT OF BOUNDS";
	return;
}

      

sub PRT4{
	local *MAX=shift;
	local *N=shift;
	local *XP=shift;
	local *X=shift;
	local *FP=shift;
	local *F=shift;
	
    print "   ";
	&PRTVEC(\@X,$N,'CURRENT X');
	if($MAX) {
		printf "  CURRENT F: %25.18g",$F;
		&PRTVEC(\$XP,$N,'TRIAL X');
		printf "  RESULTING F: %25.18g",$FP;
	}
	else{
		printf "  CURRENT F: %25.18g",-$F;
		&PRTVEC(\$XP,\$N,'TRIAL X');
		printf "  RESULTING F: %25.18g",-$FP;
	}
	return;
}


      
sub PRT5{

	print  "  TOO MANY FUNCTION EVALUATIONS; CONSIDER ",
		br,"  INCREASING MAXEVL OR EPS, OR DECREASING ",
		br,"  NT OR RT. THESE RESULTS ARE LIKELY TO BE ",
		br,"  POOR.";
	return;
}


sub PRT6{
	local *MAX=shift;

	if ($MAX){
		print "  THOUGH LOWER, POINT ACCEPTED";
	}
	else {
		print "  THOUGH HIGHER, POINT ACCEPTED";
	}

	return;
}

sub PRT7{
	local *MAX=shift;

	if ($MAX){
		print "  LOWER POINT REJECTED";
	}
	else {
		print "  HIGHER POINT REJECTED";
	}
	return;
}


sub PRT8{
	local *N=shift;
	local *VM=shift;
	local *XOPT=shift;
	local *X=shift;

	print "\n";
	print "INTERMEDIATE RESULTS AFTER STEP LENGTH ADJUSTMENT";
	print "\n";
#	print br;
	&PRTVEC(\@VM,$N,'NEW STEP LENGTH (VM)');
    &PRTVEC(\@XOPT,$N,'CURRENT OPTIMAL X');
    &PRTVEC(\@X,$N,'CURRENT X');
    print br;
	return;
}

sub PRT9{
	local *MAX=shift;
	local *N=shift;
	local *T=shift;
	local *XOPT=shift;
	local *VM=shift;
	local *FOPT=shift;
	local *NUP=shift;
	local *NDOWN=shift;
	local *NREJ=shift;
	local *LNOBDS=shift;
	local *NNEW=shift;

	my $TOTMOV;

	$TOTMOV = $NUP + $NDOWN + $NREJ;

	print "\n\n";
	print  "  INTERMEDIATE RESULTS BEFORE NEXT TEMPERATURE REDUCTION";
	print "\n\n";
	print br;
	printf "  CURRENT TEMPERATURE:            %12.5g",$T;
	print "\n";
	print br;

	if ($MAX){
		printf "  MAX FUNCTION VALUE SO FAR:  %25.18g",$FOPT;
		print "\n";
#		print br;
		printf "  TOTAL MOVES:                %8d",$TOTMOV;
		print "\n";
#		print br;
	 	printf "  UPHILL:                     %8d",$NUP;
		print "\n";
#		print br;
		printf "     ACCEPTED DOWNHILL:       %8d", $NDOWN;
		print "\n";
#		print br;
		printf "     REJECTED DOWNHILL:       %8d", $NREJ;
		print "\n";
#		print br;
		printf "  OUT OF BOUNDS TRIALS:       %8d", $LNOBDS;
		print "\n";
#		print br;
		printf "  NEW MAXIMA THIS TEMPERATURE:%8d", $NNEW;
		print "\n";
#		print br;
	}
	else {
		printf "  MIN FUNCTION VALUE SO FAR:  %25.18g", -$FOPT;
#		print br;
		print "\n";
		printf "  TOTAL MOVES:                %8d", $TOTMOV;
		print "\n";
#		print br;
		printf "     DOWNHILL:                %8d", $NUP;
		print "\n";
#		print br;
		printf "     ACCEPTED UPHILL:         %8d", $NDOWN;
		print "\n";
#		print br;
		printf "     REJECTED UPHILL:         %8d", $NREJ;
		print "\n";
#		print br;
		printf "  TRIALS OUT OF BOUNDS:       %8d", $LNOBDS;
		print "\n";
#		print br;
		printf "  NEW MINIMA THIS TEMPERATURE:%8d", $NNEW;
		print "\n";
#		print br;
	}
	&PRTVEC(\@XOPT,$N,'CURRENT OPTIMAL X');
    &PRTVEC(\@VM,$N,'STEP LENGTH (VM)');
	print br;
	return;
}

sub PRT10{

	printf "  SA ACHIEVED TERMINATION CRITERIA. IER = 0. ",br;
	return;
}
1;

