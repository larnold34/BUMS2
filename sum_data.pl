#!/usr/bin/perl
sub sum_data{
	
# DO INVERSE TRANSFORM OF SPECTRUM AND MATRIX
my $i;
my $j;

unless (param('alg') =~/MAXED/ || param('alg')=~/SAND/){
	for ($i=0;$i<$num_groups;$i++) {
		$spl[$i]=$spl[$i]*$spli[$i];
	}
}	
#	for ($i=0;$i<$num_det;$i++) {
#		for ($j=1;$j<$num_groups;$j++) {
#			$alethnew[$i][$j]=$alethnew[$i][$j]/$spli[$j];
#		}
#	}
	
	unless ((param('start_spec') !~ /MAXIET/) && (param('iter')==0)){ 
		$hgtem=0.5*$hgtem/$spmx;
		$sumerr=0;
		for ($i=0;$i<$num_det;$i++) {
			$pcterr[$i]=100*($bcc[$i]-$bce[$i])/$bce[$i];
			$sumerr=$sumerr+$pcterr[$i]*$pcterr[$i];
		}
		$perror=($sumerr/$num_det)**0.5;
	}
   $sumspc=0;
	$sumrad=0;
	$sumrem=0;
	$sumexs=0;
	$sumtld=0;
	$sumhan=0;
	$sumntr=0;
	$suma70=0;
	
	for ($i=0;$i<$num_groups;$i++) {
		if ($i>$num_groups-1) {$spl[$i]=0;}
#      $crad[$i]= &ede($ce[$i]); 
		{my $hour_sec=1/3600;
        $crem[$i]= dfact(1,40,$ce[$i],1,1,$hour_sec);} 
		$spl[$i]=$spl[$i]*$cal;
		$splplt[$i][$kx]=$spl[$i];
		$spc[$i]=$spl[$i]*$wdleth[$i];
		$sumspc=$sumspc+$spc[$i];
		$rem[$i]=$crem[$i]*$spc[$i];
		$sumrem=$sumrem+$rem[$i];
		$rad[$i]=$crad[$i]*$spc[$i];
		$sumrad=$sumrad+$rad[$i];
		$sumexs=$sumexs+$ce[$i]*$spc[$i];
		$sumtld=$sumtld+$ctld[$i]*$spc[$i];
		$sumhan=$sumhan+$chan[$i]*$spc[$i];
		$sumntr=$sumntr+$cnutrk[$i]*$rem[$i];
		$sumnta=$sumnta+$cnta[$i]*$rem[$i];
		$suma70=$suma70+$ca70[$i]*$spc[$i];
		if ($rem[$i]<1.0E-37) {$rem[$i]=0;}
		if ($rad[$i]<1.0E-37) {$rad[$i]=0;}
	}


#	$qf=$sumrem/$sumrad;
	if ($sumspc-$spc[1]){
		$aveen=($sumexs-$ce[1]*$spc[1])/($sumspc-$spc[1]);
	}
	if ($sumrem) {
		$sumtld=($sumtld/$sumrem)/4.155E+06;
		$sumhan=($sumhan/$sumrem)/2.085E+06;
		$sumntr=($sumntr/$sumrem)/0.56905;
		$sumnta=($sumnta/$sumrem)/7.9607;
		$suma70=($suma70/$sumrem)/4.4079E+06;	

		for ($i=0;$i<$num_groups;$i++) {
			$prem[$i]=100*($rem[$i]/$sumrem);
		}
	}
}
1;



