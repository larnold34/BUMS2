#!/usr/bin/perl
#  normalize calculated sphere responses and initial      
#  spectrum to experimental data      
sub normalize{
   my $i;
	$rnorm=&scale_factor(\@bce,\@errbce,\@alethnew,$num_det,$num_groups,\@spli);
   
	for ($i=0;$i<$num_groups;$i++){
       		$spl[$i]=$spli[$i]*$rnorm;
	}  
}
1;
