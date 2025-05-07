#!/usr/bin/perl
sub maxiet{
print hr;
print "Running MAXIET fit algorithm.",br;
print "<pre>";
print "Temp  Shape HGTE    SLOPE  THERM    ERROR\n",br;
print "----  ----- ------  -----  ------   ------\n",br;
print br;
#111111111111111111111111111111111111111111111111111111111111111111111
 do{
	$slpmin=0;
	$slpmax=.51;
	$errore=123456789;
	$temp=$tempi;
	$errorm=$errore;

#222222222222222222222222222222222222222222222222222222222222222222222
	do{
		$slope=$slopei;
		$therm=$thermi;
		$spmx=0;

		for ($i=0;$i<$num_groups+1;$i++){
			$splmax[$i]=($ce[$i]**1.5)*(exp(-$ce[$i]/$temp));
			if ($splmax[$i]>$spmx)  {
				$spmx=$splmax[$i]; 
			}    
			else {
				$splmax[$i]=$spmx**$shape*$splmax[$i]**(1.0-$shape);     
				if ($splmax[$i]<$splmax[$i-1]*$shp) {
					$splmax[$i]=$splmax[$i-1]*$shp;  
				}     
			} 
		}
#  QA to this point to be OK


#     CALCULATE 1/E INITIAL SPECTRUM  
		$error=123456789;    
		$errore=123456789;   
		$hgte=$spmx*$pere;     
		$errort=$error;   
		$test="";
		$hgte=$hgte/$pere;   
#33333333333333333333333333333333333333333333333333333333333333333333
# THIRD INNER LOOP
		do{

#44444444444444444444444444444444444444444444444444444444444444444444
# FOURTH INNER LOOP
			do{ 
#55555555555555555555555555555555555555555555555555555555555555555555		
#		FIFTH INNER LOOP    			
				$test="";
				do{


					for ($i=0;$i<$num_groups+1;$i++){ 
						$spli[$i]=$hgte*$ce[$i]**$slope;
					}


# 										COMBINE MAXWELLIAN AND 1/E SPECTRA 
					for ($i=0;$i<$num_groups+1;$i++){ 

						if($spli[$i]<$splmax[$i]) {
							$h=$i;
							$i=$num_groups+1;
							$test=1;
						}
						else {
							$spli[$i]=($spli[$i]+$splmax[$i])*0.5;
						}
					}
					if ($test!=1) {$hgte=$hgte/$pere;}
				} until ($test); 
#55555555555555555555555555555555555555555555555555555555555555555555			
#			print "Leaving level 5",br;

				for ($j=$h;$j<$num_groups+1;$j++){
					$spli[$j]=$splmax[$j];
				}
#                               adjust thermal energy bin       
				$spli[0]=$spli[1]*$therm;

#                  calculate sphere responses and sum from spectrum   QA'ed 
				for ($m=0;$m<$num_det;$m++){     
					$bcc[$m]=0;   
					for ($j=0;$j<$num_groups+1;$j++){    
						$bcc[$m]=$bcc[$m]+$aleth[$m][$j]*$spli[$j];
					}
				}   
#-------------------------------------------------------------
# Old scaling method
#                               calculate sums of sphere data   
#				$sumbce=0;   
#				$sumbcc=0;   
#				for ($i=0;$i<$num_det;$i++){
#					$sumbce=$sumbce+$bce[$i]; 
#					$sumbcc=$sumbcc+$bcc[$i];
#					print "det=$i sumbce=$sumbce sumbcc=$sumbcc",br;
#				}
#                                normalize calculated sphere responses     
#                                to experimental data  
#				$rnorm=$sumbce/$sumbcc;  
#				print "rnorm=$rnorm",br;
# -------------------------------------------------
# New least squares fit scaling method
				{
					my $sum1;
					my $sum2;
					$sum1 = 0.0;
					$sum2 = 0.0;
					for ($i=0;$i<$num_det;$i++){
						$sum1=$sum1+($bce[$i]*$bcc[$i])/($errbce[$i]**2);
						$sum2=$sum2+(($bcc[$i])**2)/($errbce[$i]**2);
					}
					$rnorm=$sum1/$sum2;
				}
#---------------------------------------------------
				for ($i=0;$i<$num_det;$i++){
					$bcc[$i]=$bcc[$i]*$rnorm;
				}
#                               calculate error on fit
				$error=0;  

				for ($i=0;$i<$num_det;$i++){
					$err=($bcc[$i]-$bce[$i])/$bce[$i];   
					$error=$error+$whtbce[$i]*$err*$err;
				}
				$test3="";
				if ($error<$errort){
					$test3=1;
					$errort=$error;
					$hgte=$hgte/$pere;
				}
			} while ($test3);  
#444444444444444444444444444444444444444444444444444444444444444444444
#			print "Leaving level 4",br;

			$hgte=$hgte*$pere;     

#                     save best values of fit parameters
			if($errort<$errore){     
				$errore=$errort;
				$hgtee=$hgte;
				$therme=$therm;
				$slopee=$slope;
				$mx=0;
			}

#                     change slope
			if ($slope<$slpmax) {
				$slope=$slope+$perslp;
			}
  
			if ($mx==1) {
				$slope=$slopee;
			}

#                   change thermal bin    
			$therm=$therme*$perthm;  
			$test1="";
			if ($therm<$thmmax){
				if ($mx==0){
					$therm=$therme;
				}
				$mx=$mx+1;  
				if ($mx<=10){ 
					$hgte=$hgte*$pere*(1.0+10*$perslp); 
					if ($mx==1){
						$hgte=$hgtee*$pere*$perthm;
					}
#                  reset error, search for better fit parameters       
						$errort=123456789;
				}
				else {
					$test1=1;
				}
			}  
			else {
				$test1=1;
			}

		} until ($test1);
#33333333333333333333333333333333333333333333333333333333333333333333333
#		print "Leaving Level 3",br;

#               calculate error on fit
		$perror=100*($errore/$num_det)**.5; 
#               write best values of fit parameters to terminal     
		printf "%4.2f  %4.2f  %#6.4f  %4.2f  %7.3f  %7.3f",
		$temp,$shape,$hgtee,$slopee,$therme,$perror;
		print br;  
		$test2="";

#                            save best values of fit parameters
		if ($errore<$errorm){
			$tempm=$temp;
			$hgtem=$hgtee;
			$thermm=$therme;
			$slopem=$slopee;
			$errorm=$errore;
#                           change maxwellian temperature if required 
			if ($pertmp!=0) {    
				$temp=$temp-$pertmp;   
				if ($temp>$pertmp) {
					$test2=1;
				}
			}
		}
#                           return and search for better parameters if
#                           maxwellian temp is in range     
	}  while ($test2==1);  
#222222222222222222222222222222222222222222222222222222222222222222222222
#			  	if final parameters equal initial parameters cahnge 
#     		initial parameters and continue search    
#		print "Leaving Level 2",br;

	$a1=0;     
	if ($slopem==$slopei && $slopei>$slpmin){
		$a1=1;
	} 
	$a2=0;     
	if ($thermm==$thermi && $thermi>=$thmmin){
		$a2=1;
	}    
	$a3=0;     
	if ($tempm==$tempi && $tempm<($tempij+10*$pertmp)){
		$other=$tempij+10*$pertmp;
		$a3=1;
	}
	if($pertmp==0){$a3=0;}  
	if($a1==1){$slopei=$slopei-10*$perslp;}     
	if($a2==1){$thermi=$thermi/$perthm**3;}     
	if($a3==1){$tempi=$tempi+3*$pertmp;}
	$a4=$a1+$a2+$a3;
} while ($a4>0.5);
# 111111111111111111111111111111111111111111111111111111111111111111111111
#            if not, calculate initial spectrum with best parameters       
#		print "Leaving Level 1",br;

$spmx=0;   

for ($i=0;$i<$num_groups+1;$i++){
	$splmax[$i]=($ce[$i]**1.5)*(exp(-$ce[$i]/$tempm)); 
	if($splmax[$i]>$spmx){$spmx=$splmax[$i];}    
	if($spmx!=$splmax[$i]){
		$splmax[$i]=$spmx**$shape*$splmax[$i]**(1.0-$shape);     
		if($splmax[$i]<$splmax[$i-1]*$shp){
			$splmax[$i]=$splmax[$i-1]*$shp; 
		}
	} 
}

for ($i=0;$i<$num_groups+1;$i++){
	$spli[$i]=$hgtem*$ce[$i]**$slopem;
}
for ($i=0;$i<$num_groups+1;$i++){
	if($spli[$i]>=$splmax[$i]){     
		$spli[$i]=($spli[$i]+$splmax[$i])*0.5;
	}
	else {
		$isave=$i;
		$i=$num_groups+1;
	}
}	

for ($j=$isave;$j<$num_groups+1;$j++){
	$spli[$j]=$splmax[$j];
}
$spli[0]=$spli[1]*$thermm;
print "</pre>";



 
#                           completion of maxiet algorithm     
#                           maxiet QA'ed.
}  
1; 
