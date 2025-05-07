#!/usr/bin/perl
# bon
sub bon{
my $i;
my $j;
my $m;
my $n;

if ($iter<=0) {
	for ($i=0;$i<$num_groups;$i++){   
		for ($j=0;$j<$num_groups;$j++){
			$bk[$j][$i] = 0;
			for ($m=0;$m<$num_det;$m++){
				$bk[$j][$i] = $bk[$j][$i] + $alethnew[$m][$j]*$alethnew[$m][$i];
			}
		}
	}

	for ($i=0;$i<$num_groups;$i++){
		$vect[$i]=0;
		for ($j=0;$j<$num_det;$j++){
			$vect[$i]=$vect[$i]+$alethnew[$j][$i]*$bce[$j];
		}
	}
}

for ($n=1;$n<param('itertesterror')+1;$n++){
	$iter=$iter+1;
	for ($j=0;$j<$num_groups;$j++){
		$ax=0;
		for ($m=0;$m<$num_groups;$m++){
			$ax=$spl[$m]*$bk[$j][$m]+$ax;
		}
		if ($ax<1e-37) {$ax=1.0e-37;}
		$spll[$j]=$spl[$j]*$vect[$j]/$ax;
		if ($spll[$j]<1.0E-37) {$spll[$j]=0;}
	}
 
   for ($j=2;$j<$num_groups;$j++){
      $spl[$j]=($spll[$j-1]*$smo+$spll[$j]+$spll[$j+1]*$smo)/(1+2*$smo)
   }
	
	$spl[0]=$spll[0];
	$spl[1]=$spll[1];
}

for ($m=0;$m<$num_det;$m++){
	$bcc[$m]=0;
	for ($j=0;$j<$num_groups;$j++){
		$bcc[$m]=$bcc[$m]+$alethnew[$m][$j]*$spl[$j];
	}
}

}
1;
