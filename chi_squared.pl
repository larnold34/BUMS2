#!/usr/bin/perl

sub chi_squared{
	my $num_det=shift;
	my $bce=shift;
	my $bcc=shift;
	my $errbce=shift;
	my $chi2;
	my $i;

	for ($i=0;$i<$num_det;$i++){
		$chi2=$chi2+((bce->[$i]-$bcc->[$i])**2)/(($errbce->[$i])**2);
	}
	return $chi2;
}
1;
