#!/usr/bin/perl

sub PRTVEC{
#      SUBROUTINE PRTVEC(VECTOR,NCOLS,NAME)
#  This subroutine prints the double precision vector named VECTOR.
#  Elements 1 thru NCOLS will be printed. NAME is a character variable
#  that describes VECTOR. Note that if NAME is given in the call to
#  PRTVEC, it must be enclosed in quotes. If there are more than 10
#  elements in VECTOR, 10 elements will be printed on each line.

	my $VECTOR=shift;
	my $NCOLS=shift;
	my $NAME=shift;

	my ($LINES,$LL,$I,$J);

	print "\n                         $NAME";
	print "\n";
#	print br;

    if ($NCOLS> 10) {
	 	$LINES = int($NCOLS/10.0);
	

		for($I=1;$I<$LINES+1;$I++){

	    	$LL = 10*($I - 1);
			for($J=1+$LL;$I<(11+$LL);$I++){
	    		printf "%12.5g ",$VECTOR->[$J];
			}
			print "\n";
#			print br;
		}
		for($J=11+$LL;$I<$NCOLS+1;$I++){
	   		printf "%12.5g ",$VECTOR->[$J];
		}
			print "\n";
#			print br;
	}	
	else {
		for($J=1;$I<$NCOLS+1;$I++){
	   		printf "%12.5g ",$VECTOR->[$J];
		}
#			print br;
			print "\n";
	}		
}
1;
