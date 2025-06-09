#!/usr/bin/perl
BEGIN {unshift(@INC,'/usr/lib/perl5/5.00503');}
unshift(@INC,".");
use CGI qw(:standard *table *TR *th *td :html3 :netscape);
require "dir_read.pl";
require "dfact.pl";

print header;
print start_html(-title=>'Notezy Home Page',
	         -BGCOLOR=>'yellow', -LINK=>'Red', -VLINK=>'Red', -ALINK=>'blue');

require "dir_read.pl";
use Math::IntervalSearch qw(interval_search);
use subs qw(linear_interpolate, 
		    log_linear_interpolate, 
            linear_log_interpolate, 
            log_log_interpolate);
use subs qw(dfact);
print center(h1("BUMS Detector Output Page!"));
print br;
print center(h2("Dose Response Functions"));

my $i;
my $j;
my $x;
my $y;
my $input;

$input=param('data');
@input=split(/\n/,$input);
foreach (@input) {
   	($ce[$j],$value[$j])=split(' ',$_); 
	if ($ce[$j]) { 
  		chomp($value[$j]);
   		$j++;
	} 
}
my $num_groups=$j++;

&dir_read("dose");
print start_table();
print start_TR();
print start_th(),"Response Name",
	  start_th()," ",
	  start_th(),"Response",
	  start_th(),"Units";
print end_TR;	
for ($i=0;$i<$#file+1;$i++) {
		open(FILE,"dose/$file[$i]");
		$head=<FILE>;
		chomp $head;
		$units=<FILE>;
		chomp $units;
		my $i=0;
		while (<FILE>){
			($x[$i],$y[$i])=split(' ',$_);
			$i++;
		}
		close(FILE);
		my $sum=0;
		for ($j=0;$j<$num_groups;$j++) {
			$sum=$sum+$value[$j]*log_linear_interpolate($ce[$j],\@x,\@y);
		}
		print start_TR();
		print start_td(),"$head";
		print start_td(); print "=";
		print start_td(); printf "%11.3E",$sum;
		print start_td(),"$units";
		print end_TR;
}
# Print functions from DFACT

#ICRP-21
{
	my $sum=0;
	for ($j=0;$j<$num_groups;$j++) {
		my $factor=1/3600;
		$sum=$sum+$value[$j]*dfact(1,10,$ce[$j],1,2,$factor)*1e12;
	}	
	print start_TR();
	print start_td(),"ICRP-21 Dose Equivalent H";
	print start_td(); print "=";
	print start_td(); printf "%11.3E",$sum;
	print start_td(),"pSv";
	print end_TR;
}
#NCRP-38
{
	my $sum=0;
	for ($j=0;$j<$num_groups;$j++) {
		my $factor=1/3600;
		$sum=$sum+$value[$j]*dfact(1,20,$ce[$j],5,2,$factor)*1e12;
	}	
	print start_TR();
	print start_td(),"NCRP-38 Dose Equivalent H";
	print start_td(); print "=";
	print start_td(); printf "%11.3E",$sum;
	print start_td(),"pSv";
	print end_TR;
}
#ANSI/ANS-6.1.1-1991 AP
{
	my $sum=0;
	for ($j=0;$j<$num_groups;$j++) {
		my $factor=1/3600;
		$sum=$sum+$value[$j]*dfact(1,31,$ce[$j],5,2,$factor)*1e12;
	}	
	print start_TR();
	print start_td(),"ANSI/ANS-6.1.1-1991 Equivalent Dose AP (H<sub>t</sub>)";
	print start_td(); print "=";
	print start_td(); printf "%11.3E",$sum;
	print start_td(),"pSv";
	print end_TR;
}
#ANSI/ANS-6.1.1-1991 PA
{
	my $sum=0;
	for ($j=0;$j<$num_groups;$j++) {
		my $factor=1/3600;
		$sum=$sum+$value[$j]*dfact(1,32,$ce[$j],5,2,$factor)*1e12;
	}	
	print start_TR();
	print start_td(),"ANSI/ANS-6.1.1-1991 Equivalent Dose PA (H<sub>t</sub>)";
	print start_td(); print "=";
	print start_td(); printf "%11.3E",$sum;
	print start_td(),"pSv";
	print end_TR;
}
#ANSI/ANS-6.1.1-1991 LAT
{
	my $sum=0;
	for ($j=0;$j<$num_groups;$j++) {
		my $factor=1/3600;
		$sum=$sum+$value[$j]*dfact(1,33,$ce[$j],5,2,$factor)*1e12;
	}	
	print start_TR();
	print start_td(),"ANSI/ANS-6.1.1-1991 Equivalent Dose LAT (H<sub>t</sub>)";
	print start_td(); print "=";
	print start_td(); printf "%11.3E",$sum;
	print start_td(),"pSv";
	print end_TR;
}
#ANSI/ANS-6.1.1-1991 ROT 
{
	my $sum=0;
	for ($j=0;$j<$num_groups;$j++) {
		my $factor=1/3600;
		$sum=$sum+$value[$j]*dfact(1,34,$ce[$j],5,2,$factor)*1e12;
	}	
	print start_TR();
	print start_td(),"ANSI/ANS-6.1.1-1991 Equivalent Dose ROT (H<sub>t</sub>)";
	print start_td(); print "=";
	print start_td(); printf "%11.3E",$sum;
	print start_td(),"pSv";
	print end_TR;
}
print end_table();
print hr;
print center(h2("Detector Responses"));

&dir_read("response");
print start_table();
print start_TR();
print start_th(),"Response Name",
	  start_th()," ",
	  start_th(),"Response",
	  start_th(),"Units";
print end_TR;	
for ($i=0;$i<$#file+1;$i++) {
		open(FILE,"response/$file[$i]");
		$head=<FILE>;
		chomp $head;
		$units=<FILE>;
		chomp $units;
		my $i=0;
		while (<FILE>){
			($x[$i],$y[$i])=split(' ',$_);
			$i++;
		}
		close(FILE);
		my $sum=0;
		for ($j=0;$j<$num_groups;$j++) {
			$sum=$sum+$value[$j]*log_linear_interpolate($ce[$j],\@x,\@y);
		}
		print start_TR();
		print start_td(),"$head";
		print start_td(); print "=";
		print start_td(); printf "%11.3E",$sum;
		print start_td(),"$units";
		print end_TR;
}
print end_table();


print "</HTML>";

sub linear_interpolate {
  my $x = shift;
  return unless defined($x);

  my $X = shift;
  return unless defined($X);
  return unless ref($X);

  my $Y = shift;
  return unless defined($Y);
  return unless ref($Y);

  my $num_x = @$X;
  my $num_y = @$Y;
  return unless $num_x == $num_y;

  # Find where the point to be interpolated lies in the input sequence.
  # If the point lies outside, then coerce the index value to be legal for
  # the routine to work.  Remember, this is only an interpreter, not an
  # extrapolator.
  my $j = interval_search($x, $X);
  if ( $j < 0 ) {
    $j = 0;
  }
  elsif ( $j >= $num_x - 1 ) {
    $j = $num_x - 2;
  }
  my $k = $j + 1;

  # Calculate the linear slope between the two points.
  my $dy = ($Y->[$k] - $Y->[$j]) / ($X->[$k] - $X->[$j]);

  # Use the straight line between the two points to interpolate.
  my $y  = $dy*($x - $X->[$j]) + $Y->[$j];

  return wantarray ? ($y, $dy) : $y;
}

sub linear_log_interpolate {
  my $x = shift;
  return unless defined($x);

  my $X = shift;
  return unless defined($X);
  return unless ref($X);

  my $Y = shift;
  return unless defined($Y);
  return unless ref($Y);

  my $num_x = @$X;
  my $num_y = @$Y;
  return unless $num_x == $num_y;

  # Find where the point to be interpolated lies in the input sequence.
  # If the point lies outside, then coerce the index value to be legal for
  # the routine to work.  Remember, this is only an interpreter, not an
  # extrapolator.
  my $j = interval_search($x, $X);
  if ( $j < 0 ) {
    $j = 0;
  }
  elsif ( $j >= $num_x - 1 ) {
    $j = $num_x - 2;
  }
  my $k = $j + 1;

  # Calculate the log-log slope between the two points.
  my $dy = (log($Y->[$k]) - log($Y->[$j])) / (($X->[$k]) - ($X->[$j]));

  # Use the straight line between the log of the two points to interpolate.
  my $y  = ($dy*(($x) - ($X->[$j]))) + log($Y->[$j]);
  my $y  = exp($y);

  return wantarray ? ($y, $dy) : $y;
}

sub log_log_interpolate {
  my $x = shift;
  return unless defined($x);

  my $X = shift;
  return unless defined($X);
  return unless ref($X);

  my $Y = shift;
  return unless defined($Y);
  return unless ref($Y);

  my $num_x = @$X;
  my $num_y = @$Y;
  return unless $num_x == $num_y;

  # Find where the point to be interpolated lies in the input sequence.
  # If the point lies outside, then coerce the index value to be legal for
  # the routine to work.  Remember, this is only an interpreter, not an
  # extrapolator.
  my $j = interval_search($x, $X);
  if ( $j < 0 ) {
    $j = 0;
  }
  elsif ( $j >= $num_x - 1 ) {
    $j = $num_x - 2;
  }
  my $k = $j + 1;

  # Calculate the log-log slope between the two points.
  my $dy = (log($Y->[$k]) - log($Y->[$j])) / (log($X->[$k]) - log($X->[$j]));

  # Use the straight line between the log of the two points to interpolate.
  my $y  = ($dy*(log($x) - log($X->[$j]))) + log($Y->[$j]);
  my $y  = exp($y);

  return wantarray ? ($y, $dy) : $y;
}


sub log_linear_interpolate {
  my $x = shift;
  return unless defined($x);

  my $X = shift;
  return unless defined($X);
  return unless ref($X);

  my $Y = shift;
  return unless defined($Y);
  return unless ref($Y);

  my $num_x = @$X;
  my $num_y = @$Y;
  return unless $num_x == $num_y;

  # Find where the point to be interpolated lies in the input sequence.
  # If the point lies outside, then coerce the index value to be legal for
  # the routine to work.  Remember, this is only an interpreter, not an
  # extrapolator.
  my $j = interval_search($x, $X);
  if ( $j < 0 ) {
    $j = 0;
  }
  elsif ( $j >= $num_x - 1 ) {
    $j = $num_x - 2;
  }
  my $k = $j + 1;

  # Calculate the log slope between the two points.
  my $dy = ($Y->[$k] - $Y->[$j]) / (log($X->[$k]) - log($X->[$j]));

  # Use the straight line between the two points to interpolate.
  my $y  = $dy*(log($x) - log($X->[$j])) + $Y->[$j];

  return wantarray ? ($y, $dy) : $y;
}

