#!/usr/bin/perl

sub  EXPREP{
	my $RDUM=shift;

#  This function replaces exp to avoid under- and overflows and is
#  designed for IBM 370 type machines. It may be necessary to modify
#  it for other machines. Note that the maximum and minimum values of
#  EXPREP are such that they has no effect on the algorithm.

	my $EXPREP;

	if ($RDUM>174.0){
		$EXPREP = 3.69E+75;
	}
	elsif ($RDUM<-180.0){
		$EXPREP = 0.0;
	}
	else {
		$EXPREP = exp($RDUM)
	}
	return $EXPREP;
}
1;
