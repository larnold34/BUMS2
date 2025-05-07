#!/usr/bin/perl

sub RMARIN{
	local *IJ=shift;
	local *KL=shift;
	local *U=shift;
	local *C=shift;
	local *CD=shift;
	local *CM=shift;
	local *I97=shift;
	local *J97=shift;

#  This subroutine and the next function generate random numbers. See
#  the comments for SA for more information. The only changes from the
#  orginal code is that (1) the test to make sure that RMARIN runs first
#  was taken out since SA assures that this is done (this test didn't
#  compile under IBM's VS Fortran) and (2) typing ivec as integer was
#  taken out since ivec isn't used. With these exceptions, all following
#  lines are original.

# This is the initialization routine for the random number generator
#     RANMAR()
# NOTE: The seed variables can have values between:    0 <= IJ <= 31328
#                                                      0 <= KL <= 30081
my ($i,$j,$k,$l,$ii,$s,$t);
use subs qw(mod);

	if( $IJ<0 || $IJ> 31328 || $KL<0 || $KL>30081) {
		print " The first random number seed must have a value 
		        between 0 and 31328.",br;
		print " The second seed must have a value between 0 and 30081",br;
		die;
	}   
	$i = mod($IJ/177, 177) + 2;
	$j = mod($IJ, 177) + 2;
	$k = mod($KL/169, 178) + 1;
	$l = mod($KL, 169);
#	print "i=$i j=$j k=$k l=$l\n";
	for ($ii=1;$ii<98;$ii++){	
		$s = 0.0;
		$t = 0.5;
		for ($jj=1;$jj<25;$jj++){
			$m = mod(mod($i*$j, 179)*$k, 179);
			$i = $j;
			$j = $k;
			$k = $m;
			$l = mod(53*$l+1, 169);
			if (mod($l*$m, 64)>=32) {
				$s = $s + $t;
			}
			$t = 0.5 * $t;
		}
		$U[$ii] = $s;
	}
	$C = 362436.0 / 16777216.0;
	$CD = 7654321.0 / 16777216.0;
	$CM = 16777213.0 / 16777216.0;
	$I97 = 97;
	$J97 = 33;

#    print "IN RMARIN U(I97)=$U[$I97] U(J97)=$U[$J97] C=$C CD=$CD CM=$CM I97=$I97 J97=$J97\n";
	return
}

sub mod{
	my $n=shift;
	my $k=shift;
	
	my $value;
	$n=int($n);

	$value=$n - int($n/$k)*$k;
	return $value;
}
1;
