#!/usr/bin/perl
#     calculate error on fit  
sub fit_error{
	my $i;

	$error=0;  
	for ($i=0;$i<$num_det;$i++){
		if ($bce[$i]>0){
	   		$err=($bcc[$i]-$bce[$i])/$bce[$i];   
		}
		else {
			$err=100;
		}
		$error=$error+$whtbce[$i]*$err*$err;
	}

}
1;

