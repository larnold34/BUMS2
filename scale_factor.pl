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

	#The following is intended only for debugging reasons. At somepoint sum2 is ending up being zero, which results in a divide by zero error
	#Need to verify if response, the flux, or the  error is zero which might be the cause of the error

	#First, check the error
	for (my $i=0; $i < $num_det; $i++){
		die "ERROR: error[$i] is zero\n" if $error->[$i] == 0;
	}

	#Second, check the flux
	my $flux_sum = 0;
	$flux_sum += abs($_) for @{$flux};
	die "flux is all zero\n" if $flux_sum == 0;


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
	
		

