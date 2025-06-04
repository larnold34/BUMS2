#!/usr/bin/perl

sub MKEBINS4PD {
	local *ENBF=shift;
	local *N=shift;

	my $EMIN,$EMAX,$EMEV,$TPOQ;
	my $I,$K;

	use subs qw(nint);
	use Math::Fortran qw(log10); 

#     Note: 10 to the power 0.25 equals 1.778279410

	$TPOQ = 1.778279410;
	$EMEV = 1.3113526E-14;

#     Find lowest and highest energy bins
	for ($K=1;$K<81;$K++){
		$EMEV = $EMEV*$TPOQ;
		if ( ($ENBF[$N]) >= $EMEV ){
	  		$EMAX = $EMEV;
		}
	}

	for ($K=1;$K<81;$K++){
		$EMEV = $EMEV/$TPOQ;
		if ( ($ENBF[1]) <= $EMEV ) {
	  		$EMIN = $EMEV;
		}
	}

#     Fill out the array

	for ($I=1;$I<$N+1;$I++){
		$ENBF[$I] = 0.0;
	} 

	$N = nint(4.0*log10($EMAX/$EMIN)) + 1;

    $ENBF[1] = $EMIN;
	for ($I=2;$I<$N+1;$I++){
		$ENBF[$I] = $ENBF[$I-1]*$TPOQ;
	}
	return;
}

sub nint{
	my $x=shift;
	
	my $extra;
	my $nint;
	
	$extra=$x-int($x);
	
	if ($x < 0.5) {
		$nint=int($x);
	}
	else {
		$nint=int($x)+1;
	}

	return $nint;
}
1;
