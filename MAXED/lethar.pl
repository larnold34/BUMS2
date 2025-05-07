#!/usr/bin/perl

sub LETHAR{
	local *FI=shift;
	local *FOUT=shift;
	local *ENBF=shift;
	local *N=shift;
	local *NB=shift;
	local *FIL=shift;
	local *FL=shift;
	
	my $K,$Z;

	for ($K=1;$K<$NB+1;$K++){
		$Z = log($ENBF[$K+1]) - log($ENBF[$K]); 
		$FIL[$K] = $FI[$K]/$Z;
		$FL[$K] = $FOUT[$K]/$Z;
	}    
	return;
}
1;

