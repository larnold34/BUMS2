#!/usr/bin/perl
sub ede{

# Parameters are ($_[0]=Energy (MeV))
local ($energy) = @_;
local $x;

if ($energy<=0.01){
	$c0=3.420895;
	$c1=7.725710e-11;
	$c2=9.834081e-02;
	$c3=4.903466e-03;
	$c4=8.149667e-05;
}

if ($energy>0.01){
	$c0=4.952167e+00;
	$c1=6.644235e-01;
	$c2=-1.017445e-01;
	$c3=-1.496004e-03;
	$c4=3.636748e-03;
}

$x=log($energy);

$he=1e-12*exp($c0+$c1*$x+$c2*$x**2+$c3*$x**3+$c4*$x**4);
}
;
1
