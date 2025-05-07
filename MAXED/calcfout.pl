#!/usr/bin/perl

sub CALCFOUT {
	local *LAMBDA=shift;

	my @FOUT;
	my $I,$J;
	my $SUM2,@B;


	for($I=1;$I<$M+1;$I++){
		for($J=1;$J<$NB+1;$J++){
			$B[$I][$J] = $MM[$NB*($I-1)+$J];
		}
	}

	for($J=1;$J<$NB+1;$J++){
		$SUM2 = 0.0;
		for($I=1;$I<$M+1;$I++){
			$SUM2 = $SUM2 + $LAMBDA->[$I]*$B[$I][$J];
		}    
		$FOUT[$J] = $FI[$J]*exp(-$SUM2);
	}
	return (\@FOUT);
}
1;

