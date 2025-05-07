#!/usr/bin/perl
# Determine a scaling factor using a minimum chi-square method.

sub scale_factor{
	my $detector=shift;
	my $error=shift;
	my $response=shift;
	my $num_det=shift;
	my $num_energy=shift;
	my $flux=shift;

	my $i;
	my $sum1 = 0.0;
	my $sum2 = 0.0;
	my $scf;
	my @eig;

	for($i=0;$i<$num_det;$i++){
		$eig[$i]=0;
		for($k=0;$k<$num_energy;$k++){
			$eig[$i]=$eig[$i] + $response->[$i][$k]*$flux->[$k];
		}
		$sum1 = $sum1 + ($detector->[$i]*$eig[$i])/(($error->[$i])**2);
		$sum2 = $sum2 + (($eig[$i])**2)/(($error->[$i])**2);
	}

	$scf = $sum1/$sum2;
	return $scf;
}
1;
	
		

