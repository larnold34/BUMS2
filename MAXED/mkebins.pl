#!/usr/bin/perl

sub MKEBINS{
	local *ENBZKL=shift;
	local *ENBR=shift;
	local *ZKL=shift;
	local *NMAX=shift;
	local *N0=shift;
	local *N1=shift;
	local *ENB0=shift;
	local *N=shift;

#
	my $K,$MAXMIN,$MINMAX,$SORT;
#      
#     Set ENB0(K)=0.0, fill the array SORT(K) with ENBZKL(K), ENBR(K)
#
print "\n\n";
	print "MKEBINS 1\n";
	for($K=1;$K<$N0+1;$K++){
		$ENB0[$K] = 0.0;
		$SORT[$K] = $ENBZKL[$K];
	}
	print "MKEBINS 2\n";
	for($K=1;$K<$N1+1;$K++){
		$ENB0[$K+$N0] = 0.0;
		$SORT[$K+$N0] = $ENBR[$K];
	}
#
#     Use the subroutine HPSORT (taken from "NUMERICAL RECIPES IN 
#     FORTRAN", page 329) to sort the array SORT in ascending order.
#
	print "Entering HPSORT\n";
      &HPSORT(\$NMAX,\$SORT);
#
#     Find the lowest and highest bin edges common to both sets of
#     energy bins
#
      $MAXMIN = $ENBZKL[1];
    if ($MAXMIN< $ENBR[1]) {
		$MAXMIN = $ENBR[1];
	}
#


	$MINMAX = $ENBZKL[$N0];
    if ($MINMAX>$ENBR[$N1]) {
		$MINMAX = $ENBR[$N1];
	}
#
#     Fill the array ENB0(K) with those elements of SORT(K) that are:
#     (1) not smaller than than MAXMIN, (2) not larger than MINAMX, and
#     (3) do not repeat. 
#
      $ENB0[1] = $MAXMIN;  
#      
    $N = 1;
	print "MKEBINS 3\n";
	for($I=1;$I<$NMAX+1;$I++){
      	if ($SORT[$I]>$MAXMIN) {
			if ($SORT[$I]<=$MINMAX) {
	  			if ($SORT[$I]>$ENB0[$N]) {
	   			 	$N = $N + 1;
	    			$ENB0[$N] = $SORT[$I];
	  			}
			}
		}
	}
#
	return;
}
1;
