#!/usr/bin/perl

sub FCN {
	my $MDUMMY=shift;
	my $LAMBDA=shift;
	my $M=shift;
	my $NB=shift;
	my $MM=shift;
	my $FI=shift;
	my $S=shift;
	my $D=shift;
	my $OMEGA=shift;
	my $FLUX=shift;
	
#	print "Starting FCN\n";
	my ($I,$J,$SUM1,$SUM2,$SUM3,$SUM4,@B);    

#	print "N=$N M=$M  NB=$NB OMEGA=$OMEGA FLUX=$FLUX\n";
	for ($I=1;$I<$M+1;$I++){	
		for ($J=1;$J<$NB+1;$J++){	
#	print "Initiallizing I=$I J=$J\n";
	  		$B[$I][$J]=0;
		}
	}

#	print "FCN 1a M=$M NB=$NB\n";
	for ($I=1;$I<$M+1;$I++){	
#	print "FCN 1b M=$M\n";
		for ($J=1;$J<$NB+1;$J++){	
#	print "FCN 1c I=$I J=$J\n";
	  		$B[$I][$J]= $MM->[$NB*($I-1)+$J];
		}
	}

	$SUM1 = 0.0;
#	print "FCN 2\n";
	for ($J=1;$J<$NB+1;$J++){ 	
		$SUM2 = 0.0;
		for ($I=1;$I<$M+1;$I++){ 	
			$SUM2 = $SUM2 + $LAMBDA->[$I]*$B[$I][$J];
		}    
		$SUM1 = $SUM1 + $FI->[$J]*exp(-$SUM2);
	}

	$SUM3 = 0.0;
	$SUM4 = 0.0;
#	print "FCN 3\n";
	for ($I=1;$I<$M+1;$I++){ 	
		$SUM3 = $SUM3 + ($S->[$I]*$LAMBDA->[$I])**2;
		$SUM4 = $SUM4 + $LAMBDA->[$I]*$D->[$I];
#	    print "SUM3=$SUM3  SUM4=$SUM4 S=$S->[$I] LAMBDA=$LAMBDA->[$I] D=$D->[$I]\n";
	}
#	print "FCN 4\n";

#	print "SUM1=$SUM1 SUM2=$SUM2 SUM3=$SUM3 SUM4=$SUM4 OMEGA=$OMEGA FLUX=$FLUX\n";

	$H = -$SUM1-sqrt($OMEGA*$SUM3)-$SUM4+$FLUX;
#	print "\nIn FCN F=$H\n";

	return $H;
}
1;
