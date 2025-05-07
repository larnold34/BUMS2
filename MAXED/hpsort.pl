#!/usr/bin/perl

sub HPSORT{
	local *n=shift;
	local *ra=shift;

	my $i,$ir,$j,$l,$rra;

	if ($n<2) {return;}
    $l=$n/2+1;
    $ir=$n;

	$test=1;

	do {

		if($l>1){
		  	$l=$l-1;
			$rra=$ra[$l];
		}
		else {
			$rra=$ra[$ir];
			$ra[$ir]=$ra[1];
			$ir=$ir-1;
			if($ir==1){
			    $ra[1]=$rra;
	    		return;
			}
		}
		$i=$l;
		$j=$l+$l;

		do {
			if($j<$ir){
		    	if(($ra[$j])<($ra[$j+1])){
					$j=$j+1;
				}
			}
	  		if($rra<($ra[$j])){
	    		$ra[$i]=$ra[$j];
	    		$i=$j;
	    		$j=$j+$j;
	  		}
			else {
	    		$j=$ir+1;
	  		}
		} while ($j<=$ir);

		$ra[$i]=$rra;

	} while ($test);

	return;
#  (C) Copr. 1986-92 Numerical Recipes Software %-,.
}
1;

