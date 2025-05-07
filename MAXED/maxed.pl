#!/usr/bin/perl

# maxed(Number of detectors, number of energies -1, matrix, energy bins, guess Temp, RT)

sub maxed{
	local *M=shift;
	local *T=shift;
	local *RT=shift;
	local *M=shift;
	local *NB=shift;
	local *MM=shift;
	local *FI=shift;
	local *S=shift;
	local *D=shift;
	local *OMEGA=shift;
	local *FLUX=shift;

#    common ($S,$D,$FI,$MM,$FLUX,$OMEGA,$N,$N0,$MP1);
	my ($i);

	$OMEGA=$M;
	print "Calling Mininimization Subroutine SIMANN T=$T\n";
	print "\n";
#	print br;
	(*LAMBDA)=&simann(\$M,\$T,\$RT,\$M,\$NB,\@MM,\@FI,\@S,\@D,\$OMEGA,\$FLUX);

#	print "$LAMBDA[1]\n";
	
	print "Current values of Lambdas:";
	print "\n";
#	print br;
	for($i=1;$i<$M+1;$i++){
		print "Detector=$i  Lambda=$LAMBDA[$i]";
		print "\n";
#		print br;
	}
	print br;

	return (\@LAMBDA);
}
1;
	
