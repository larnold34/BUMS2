#!/usr/bin/perl
sub initialize{

# Initial variables

$slopej=0;
$splmin = -0.2;
$slpmax=0.5;
$perslp=0.01;
$thermj=1.0;
$thmmin=.1;
$thmmax=100;
$dead=0.0;
$shp=0.01;
$tstrat=.999;
$jx=1;
$kx=1;
$lx=1;
$jjj=0;
$spmx=1;
$perthm=1.0+20*$perslp;
$pere=1.0+10*$perslp;

$tstper=($num_det*$tstper**2)/10000;
$tempi=$tempij;
$slopei=$slopej;
$thermi=$thermj;

}
1;
