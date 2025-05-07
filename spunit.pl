#!/usr/bin/perl
sub spunit{
#               BEGINNING OF SPUNIT UNFOLDING ALGORITHM      
my $j;
my $i;
my $k;
my $m;

	unless ($iter>0){
   	for ($j=0;$j<$num_groups;$j++){
      	$ss[$j]=0;  
   		for ($i=0;$i<$num_det;$i++){
      		$ss[$j]=$ss[$j]+$alethnew[$i][$j]/$bce[$i];
			}
		}
	}

	for ($k=1;$k<param('itertesterror')+1;$k++){
      	$iter=$iter+1;
		for ($j=0;$j<$num_groups;$j++){
			$spll[$j]=0;  
			for ($i=0;$i<$num_det;$i++){
				if ($alethnew[$i][$j] && $spl[$j]){
       				$spll[$j]=$spll[$j]+($spl[$j]*$alethnew[$i][$j]/($ss[$j]*$bcc[$i]));
				}
#                       **** to avoid underflow problems :
      			if ($spll[$j]<1.0e-37) {$spll[$j]=0;}
			}
		}
	

		for ($j=2;$j<$num_groups;$j++){
       		$spl[$j]=($spll[$j-1]*$smo+$spll[$j]+$spll[$j+1]*$smo)/(1+2*$smo); 
		}
		$spl[0]=$spll[0];     
		$spl[1]=$spll[1];     

		for ($m=0;$m<$num_det;$m++){
			$bcc[$m]=0;   
			for ($j=0;$j<$num_groups;$j++){
				$bcc[$m]=$bcc[$m]+$alethnew[$m][$j]*$spl[$j];
			}
		}    
	} 
#          end of spunit unfolding algorithm  
}
1;
