#!/usr/bin/perl

sub FILLFIL{
	local *ENBZKL=shift;
	local *ZKL=shift;
	local *N=shift;
	local *N0=shift;
	local *NB=shift;
	local *ENBF=shift;
	local *FI=shift;
	
	my $K,$L,$N0M1,$R1,$R2;
	my @FIL,@ZKLL;

	$N0M1 = $N0 - 1;

#print " FILLFIL stop 1\n";
	for ($K=1;$K<$N+1;$K++){
		$FIL[$K] = 0.0;
	}

#print " FILLFIL stop 2\n";
	for ($K=1;$K<$N0M1+1;$K++){
		$ZKLL[$K] = $ZKL[$K]/(log($ENBZKL[$K+1]) - log($ENBZKL[$K]));
	}  

#print " FILLFIL stop 3\n";
	for ($K=1;$K<$N0M1+1;$K++){
#print " FILLFIL stop 4\n";
		for ($L=1;$L<$NB+1;$L++){
	  		$R2 = log($ENBF[$L+1]) - log($ENBF[$L]); 
	  		if ( ($ENBF[$L]) <= ($ENBZKL[$K]) ) {
	    		if ( ($ENBF[$L+1]) > ($ENBZKL[$K]) ) { 
	      			if ( ($ENBF[$L+1])  >= ($ENBZKL[$K+1]) ) {
						$R1 = log($ENBZKL[$K+1]) - log($ENBZKL[$K]);
						$FIL[$L] = $FIL[$L] + $ZKLL[$K]*($R1/$R2);
					}
	      			elsif ( ($ENBF[$L+1]) < ($ENBZKL[$K+1]) ) {
						$R1 = log($ENBF[$L+1]) - log($ENBZKL[$K]) ;
						$FIL[$L] = $FIL[$L] + $ZKLL[$K]*($R1/$R2);
	      			}
	   			}
	  		}
			elsif ( ($ENBF[$L]) > ($ENBZKL[$K]) ){
	    		if ( ($ENBF[$L]) < ($ENBZKL[$K+1]) ){ 
	      			if ( ($ENBF[$L+1]) <= ($ENBZKL[$K+1])) {
						$R1 = log($ENBF[$L+1]) - log($ENBF[$L]);
						$FIL[$L] = $FIL[$L] + $ZKLL[$K]*($R1/$R2);
					}
	      			elsif ( ($ENBF[$L+1]) > ($ENBZKL[$K+1])){
						$R1 = log($ENBZKL[$K+1]) - log($ENBF[$L]);
						$FIL[$L] = $FIL[$L] + $ZKLL[$K]*($R1/$R2);
					}
				}
			}
		}
	}
#print " FILLFIL stop 5\n";

	for ($K=1;$K<$NB+1;$K++){
		$FI[$K] = $FIL[$K]*(log($ENBF[$K+1]) - log($ENBF[$K]));
	}  

	return;
}
1;
