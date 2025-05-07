#!/usr/bin/perl
sub cal_response{
#                 calculate sphere responses and sum from initial spectrum 
my $m;
my $j;
for ($m=0;$m<$num_det;$m++){
  	$bcc[$m]=0;   
	for ($j=0;$j<$num_groups;$j++){
		$bcc[$m]=$bcc[$m]+$alethnew[$m][$j]*$spl[$j];
	}
}    
}
1;
