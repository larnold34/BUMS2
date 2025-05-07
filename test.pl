#!/usr/bin/perl
BEGIN {unshift(@INC,'/usr/lib/perl5/5.00503');}
unshift(@INC,".");

require "dfact.pl";
# require "interpolate.pl";
$id=1;
$ic=10;
$en=3001;
$it=1;
$iu=2;
$acr=1.0;

$value=dfact($id,31,2.4E-8,5,$iu,$acr);
print "value=$value\n";
$value=dfact($id,31,2.5E-8,5,$iu,$acr);
print "value=$value\n";
$value=dfact($id,31,14,5,$iu,$acr);
print "value=$value\n";
$value=dfact($id,31,15,5,$iu,$acr);
print "value=$value\n";
