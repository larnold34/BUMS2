#!/usr/bin/perl
use strict;
use warnings;

# Make sures "dir_read.pl" and "dfact.pl" are in @INC
use FindBin qw($Bin);
use lib $Bin;         

# Make sures all HTML based headings are corrected
use HTML::Entities qw(decode_entities);

# Import the modules from .cgi counterpart
use Math::IntervalSearch qw(interval_search);

require "dir_read.pl";   
require "dfact.pl";  

# Makes a fillable array for dir_read()
our @file;

# read our “ce value” pairs from STDIN
my (@ce, @value);
{
    my $j = 0;
    while (<STDIN>) {
        chomp;
        next if /^\s*$/;
        my ($c, $v) = split;
        next unless defined $c and defined $v;
        $ce[$j]    = $c;
        $value[$j] = $v;
        $j++;
    }
    @ce
      or die "Usage: detector_response_cli.pl <datafile>\n"
         . "       datafile must contain lines of “ce value” pairs\n";
}

my $num_groups = scalar(@ce);

# Print the header
print "\n";
print "=" x 50, "\n";
print "       BUMS Detector Responses\n";
print "=" x 50, "\n\n";

# ---- Dose Response Functions ----
print "Dose Response Functions:\n";
printf "%-30s %15s %8s\n", "Name", "Response", "Units";
print "-" x 50, "\n";

dir_read("dose");
for my $fn (@file) {
    open my $F, '<', "dose/$fn"
      or warn "Cannot open dose/$fn: $!\n" and next;
	chomp(my $head = <$F>);
	$head = decode_entities($head);
	$head =~ s/<[^>]+>//g;
	chomp(my $units = <$F>);

    my (@x, @y);
    while (<$F>) {
        chomp;
        my ($xx, $yy) = split;
        push @x, $xx;
        push @y, $yy;
    }
    close $F;

    my $sum = 0;
    for my $j (0 .. $num_groups-1) {
        $sum += $value[$j] * log_linear_interpolate($ce[$j], \@x, \@y);
    }

    printf "%-30s %15.5e %8s\n", $head, $sum, $units;
}
print "\n";

#----Standard Equivalent Dose Calculations ----
print "Standard Equivalent Dose Calculations:\n";
printf "%-45s %15s\n", "Name", "Value (pSv)";
print "-" x 60, "\n";

#ICRP-21
{
	my $sum = 0;
	for my $j (0 .. $num_groups-1){
		my $factor = 1/3600;
		$sum += $value[$j] * dfact(1,10,$ce[$j], 1,2,$factor) * 1e12;
	}
	printf "%-45s %15.5e pSv\n", "ICRP-21 Dose Equivalent H", $sum;
}
# NCRP-38
{
  my $sum = 0;
  for my $j (0 .. $num_groups-1) {
    my $factor = 1/3600;
    $sum += $value[$j] * dfact(1,20,$ce[$j],5,2,$factor) * 1e12;
  }
  printf "%-45s %15.5e pSv\n", "NCRP-38 Dose Equivalent H", $sum;
}

# ANSI/ANS-6.1.1-1991 AP
{
  my $sum = 0;
  for my $j (0 .. $num_groups-1) {
    my $factor = 1/3600;
    $sum += $value[$j] * dfact(1,31,$ce[$j],5,2,$factor) * 1e12;
  }
  printf "%-45s %15.5e pSv\n",
    "ANSI/ANS-6.1.1-1991 Equivalent Dose AP (Ht)", $sum;
}

# ANSI/ANS-6.1.1-1991 PA
{
  my $sum = 0;
  for my $j (0 .. $num_groups-1) {
    my $factor = 1/3600;
    $sum += $value[$j] * dfact(1,32,$ce[$j],5,2,$factor) * 1e12;
  }
  printf "%-45s %15.5e pSv\n",
    "ANSI/ANS-6.1.1-1991 Equivalent Dose PA (Ht)", $sum;
}

# ANSI/ANS-6.1.1-1991 LAT
{
  my $sum = 0;
  for my $j (0 .. $num_groups-1) {
    my $factor = 1/3600;
    $sum += $value[$j] * dfact(1,33,$ce[$j],5,2,$factor) * 1e12;
  }
  printf "%-45s %15.5e pSv\n",
    "ANSI/ANS-6.1.1-1991 Equivalent Dose LAT (Ht)", $sum;
}

# ANSI/ANS-6.1.1-1991 ROT
{
  my $sum = 0;
  for my $j (0 .. $num_groups-1) {
    my $factor = 1/3600;
    $sum += $value[$j] * dfact(1,34,$ce[$j],5,2,$factor) * 1e12;
  }
  printf "%-45s %15.5e pSv\n",
    "ANSI/ANS-6.1.1-1991 Equivalent Dose ROT (Ht)", $sum;
}

print "\n";

# ---- Detector Responses ----
print "Detector Responses:\n";
printf "%-30s %15s %8s\n", "Name", "Response", "Units";
print "-" x 50, "\n";

dir_read("response");
for my $fn (@file) {
    open my $F, '<', "response/$fn"
      or warn "Cannot open response/$fn: $!\n" and next;
    chomp(my $head  = <$F>);
    $head = decode_entities($head);
    $head =~ s/<[^>]+>//g;
    chomp(my $units = <$F>);

    my (@x, @y);
    while (<$F>) {
        chomp;
        my ($xx, $yy) = split;
        push @x, $xx;
        push @y, $yy;
    }
    close $F;

    my $sum = 0;
    for my $j (0 .. $num_groups-1) {
        $sum += $value[$j] * log_linear_interpolate($ce[$j], \@x, \@y);
    }

    printf "%-30s %15.5e %8s\n", $head, $sum, $units;
}
print "\n";
print "=" x 50, "\n\n";

# ---- interpolation routines ----

sub linear_interpolate {
    my ($x, $X, $Y) = @_;
    my $n = @$X;
    return unless $n == @$Y;
    my $j = interval_search($x, $X);
    $j = 0      if $j < 0;
    $j = $n - 2 if $j >= $n - 1;
    my $k = $j + 1;
    my $dy = ($Y->[$k] - $Y->[$j]) / ($X->[$k] - $X->[$j]);
    return $dy * ($x - $X->[$j]) + $Y->[$j];
}

sub log_linear_interpolate {
    my ($x, $X, $Y) = @_;
    my $n = @$X;
    return 0 unless $n == @$Y;

    # find bracketing indices
    my $j = interval_search($x, $X);
    $j =   0       if $j <  0;
    $j = $n - 2    if $j >= $n - 1;
    my $k = $j + 1;

    # otherwise do the log‐linear
    my $dy   = (log($Y->[$k]) - log($Y->[$j])) / ($X->[$k] - $X->[$j]);
    my $logy = $dy * ($x - $X->[$j]) + log($Y->[$j]);
    return exp($logy);
}

