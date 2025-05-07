#!/usr/bin/perl

sub RESPONSEL{
	local *RES=shift;
	local *RFN=shift;
	local *B=shift;
	local *ENBF=shift;
	local *ENBR=shift;
	local *M=shift;
	local *MMM=shift;
	local *N=shift;
	local *NB=shift;
	local *N1=shift;
	local *NB1=shift;
 
	my $I,$K;

#print "In RESPONSEL\n";
#print "RESPONSEL 1\n";
 	for($I=1;$I<$M+1;$I++){
#print "RESPONSEL 2  NB=$NB\n";

 		for($K=1;$K<$NB+1;$K++){
#print "i=$I k=$K RES = $RES[$I][$K]\n";
			$B[$I][$K] = 0.0;
		}
	}

#print "RESPONSEL 3\n";
	for($K=1;$K<$NB1+1;$K++){ 
#print "RESPONSEL 4\n";
		for($L=1;$L<$NB+1;$L++){ 
#print "RESPONSEL 5\n";
			$R2 = log($ENBF[$L+1]) - log($ENBF[$L]);   
			if ( ($ENBF[$L]) <= ($ENBR[$K]) ) {
				if ( ($ENBF[$L+1]) > ($ENBR[$K]) ){ 
					if ( ($ENBF[$L+1]) >= ($ENBR[$K+1]) ) {
						$R1 = log($ENBR[$K+1]) - log($ENBR[$K]);  
						for($I=1;$I<$M+1;$I++){ 
#print "RESPONSEL 6\n";
							$J = $RFN[$I];
							$B[$I][$L] = $B[$I][$L] + $RES[$J][$K]*($R1/$R2); 
						}
					}
					elsif ( ($ENBF[$L+1]) < ($ENBR[$K+1]) ) {
						$R1 = log($ENBF[$L+1]) - log($ENBR[$K]);
						for($I=1;$I<$M+1;$I++){ 
#print "RESPONSEL 7\n";
		  				$J = $RFN[$I];
							$B[$I][$L] = $B[$I][$L] + $RES[$J][$K]*($R1/$R2);
						}
					}
				}
			}
			elsif ( ($ENBF[$L]) > ($ENBR[$K]) ) {
				if ( ($ENBF[$L]) < ($ENBR[$K+1]) ){ 
					if ( ($ENBF[$L+1]) <= ($ENBR[$K+1]) ){
						$R1 = log($ENBF[$L+1]) - log($ENBF[$L]);
						for($I=1;$I<$M+1;$I++){ 
#print "RESPONSEL 8\n";
							$J = $RFN[$I];
							$B[$I][$L] = $B[$I][$L] + $RES[$J][$K]*($R1/$R2);
						}
					}
					elsif ( ($ENBF[$L+1]) > ($ENBR[$K+1]) ){
						$R1 = log($ENBR[$K+1]) - log($ENBF[$L]);
						for($I=1;$I<$M+1;$I++){ 
							$J = $RFN[$I];
#print "RESPONSEL 9\n";
							$B[$I][$L] = $B[$I][$L] + $RES[$J][$K]*($R1/$R2);
						}
					}
				}
			}
		}
	}
#print "Finishing RESPONSEL\n";

	return;
}
1;
