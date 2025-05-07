#!/usr/bin/perl

sub SCALEFI{
	local *D=shift;
	local *S=shift;
	local *B=shift;
	local *M=shift;
	local *NB=shift;
	local *FI=shift;

	my $I,$K,$SUM1,$SUM2,@EIG;
#
#     Convolve the default spectrum with the response functions
#
	for ($I=1;$I<$M+1;$I++){
		$EIG[$I] = 0;
		for ($K=1;$K<$NB+1;$K++){
#			print "i=$I k=$K FI(K)=$FI[$K] B(i,k)=$B[$I][$K]\n";
	  		$EIG[$I] = $EIG[$I] + $B[$I][$K]*$FI[$K];
		}
	} 
#
#     Scale the default spectrum so that the chi-square is a minimum
#
      $SUM1 = 0.0;
      $SUM2 = 0.0;
	for ($I=1;$I<$M+1;$I++){
#		print "D=$D[$I]  EIG=$EIG[$I]  S=$S[$I]\n";
		$SUM1 = $SUM1 + ($D[$I]*$EIG[$I])/(($S[$I])**2);
		$SUM2 = $SUM2 + (($EIG[$I])**2)/(($S[$I])**2);
	}
#
	$SCF = $SUM1/$SUM2;
#
	return $SCF;
}
1;
