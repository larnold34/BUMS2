#!/usr/bin/perl
BEGIN {unshift(@INC,'/usr/lib/perl5/5.00503');}
unshift(@INC,".");
use File::Basename;
use File::Path qw(make_path);
# use CGI qw(:standard :html3 :netscape *table *TR *th *td);
# print header;
# print start_html(-title=>'NOTEZY OUTPUT PAGE',
# 				     -BGCOLOR=>'yellow');
require "htmlinput.pl";
require "initialize.pl";
require "response_matrix.pl";
require "print_mat.pl";
require "maxiet_cli.pl";
require "trans_mat.pl";
require "cal_response.pl";
require "spunit.pl";
require "bon.pl";
require "sum_data.pl";
require "output_cli.pl";
require "normalize.pl";
require "fit_error.pl";
require "dir_read.pl";
require "guess_cli.pl";
require "rebin.pl";
require "ede.pl";
require "plot.pl";
require "dfact.pl";
require "user_input_spectra.pl";
require "maxed_cli.pl";
require "scale_factor.pl";
require "chi_squared.pl";
require "sand2_cli.pl";
require "Math/Interpolate.pm";


use URI::Escape qw(uri_unescape);

# The following will allow for a file path to be an arguement with the initial command
my ($file_path, $out_path) = @ARGV;
unless ($file_path && $out_path) {
    die "Usage: $0 <path/to/input_file> <path/to/output_file>\n";
}

# Open your input data as before:
open my $fh, '<', $file_path
    or die "Cannot open '$file_path': $!\n";

my %data;
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/\r$//;          # remove trailing CR if present
    next if $line eq '';       # skip blank lines
    next if $line =~ /^\s*;/;  # skip comment lines, this is really only for testing

    # Split on the FIRST '='
    # end up in $value intact.
    my ($key, $value) = split(/=/, $line, 2);
    $value = '' unless defined $value;

    # Don’t uri_unescape here—keep "%2B", "%20", etc. as-is.
    $data{$key} = $value;
}
close $fh;

for my $k (keys %data) {
    # Decodes URI inputs
    $data{$k} = uri_unescape($data{$k});
}

# Making sure data is actually assigned
{
    no strict 'refs';
    for my $k (keys %data) {
        ${ $k } = $data{$k};
    }
    use strict 'refs';
}


use CGI qw(param);

# Set parameters to be both cgi applicale and cli applicable
# Allows for some of the older scripts to still be used since the inputs are still considered cgi
# New cli scripts will use the decoded data to generate the file outputs
our $use_det_bare        = $data{bare}             // '';
our $count_bare          = $data{bare_counts}       // 0;
our $count_error_bare    = $data{bare_counts_error} // 0;
our $use_det_barecd      = $data{barecd}           // '';
our $count_barecd        = $data{barecd_counts}    // 0;
our $count_error_barecd  = $data{barecd_counts_error}// 0;

our $use_det_2inch       = $data{'2inch'}          // '';
our $count_2inch         = $data{'2_inch_counts'}     // 0;
our $count_error_2inch   = $data{'2_inch_counts_error'}// 0;
our $use_det_2inchcd     = $data{'2inchcd'}        // '';
our $count_2inchcd       = $data{'2_inch_cd_counts'}     // 0;
our $count_error_2inchcd = $data{'2_inch_cd_counts_error'}// 0;

our $use_det_3inch       = $data{'3inch'}          // '';
our $count_3inch         = $data{'3_inch_counts'}     // 0;
our $count_error_3inch   = $data{'3_inch_counts_error'} // 0;
our $use_det_3inchcd     = $data{'3inchcd'}        // '';
our $count_3inchcd       = $data{'3_inch_cd_counts'}     // 0;
our $count_error_3inchcd = $data{'3_inch_cd_counts_error'}// 0;

our $use_det_5inch       = $data{'5inch'}          // '';
our $count_5inch         = $data{'5_inch_counts'}     // 0;
our $count_error_5inch   = $data{'5_inch_counts_error'} // 0;
our $use_det_5inchcd     = $data{'5inchcd'}        // '';
our $count_5inchcd       = $data{'5_inch_cd_counts'}     // 0;
our $count_error_5inchcd = $data{'5_inch_cd_counts_error'}// 0;

our $use_det_8inch       = $data{'8inch'}          // '';
our $count_8inch         = $data{'8_inch_counts'}     // 0;
our $count_error_8inch   = $data{'8_inch_counts_error'} // 0;

our $use_det_10inch      = $data{'10inch'}         // '';
our $count_10inch        = $data{'10_inch_counts'}    // 0;
our $count_error_10inch  = $data{'10_inch_counts_error'}// 0;

our $use_det_12inch      = $data{'12inch'}         // '';
our $count_12inch        = $data{'12_inch_counts'}     // 0;
our $count_error_12inch  = $data{'12_inch_counts_error'} // 0;

our $use_det_15inch      = $data{'15inch'}         // '';
our $count_15inch        = $data{'15_inch_counts'}     // 0;
our $count_error_15inch  = $data{'15_inch_counts_error'} // 0;

our $use_det_18inch      = $data{'18inch'}         // '';
our $count_18inch        = $data{'18_inch_counts'}     // 0;
our $count_error_18inch  = $data{'18_inch_counts_error'} // 0;

our $max_iter           = $data{iter}          // 0;
our $itrtst         = $data{itertesterror} // 0;
our $tstper         = $data{endtesterror}  // 0;
our $tempm          = $data{tempij}        // 0.0;
our $smo            = $data{smoothing}     // 0.0;
our $shape          = $data{shape}         // 0.0;
our $perurb         = $data{perturbation}  // 0.0;
our $cal            = $data{cal_factor}    // 0.0;
our $max_energy     = $data{max_energy}    // 0.0;
our $start_spec     = $data{start_spec}    // '';
our $matrix_file    = $data{matrix}        // '';
our $alg            = $data{alg}           // '';


our @use_detectors = (
  $use_det_bare,    $use_det_barecd,  $use_det_2inch,
  $use_det_2inchcd, $use_det_3inch,   $use_det_3inchcd,
  $use_det_5inch,   $use_det_5inchcd, $use_det_8inch,
  $use_det_10inch,  $use_det_12inch,  $use_det_15inch,
  $use_det_18inch
);

our @detector_counts = (
  $count_bare,   $count_barecd,  $count_2inch,
  $count_2inchcd,$count_3inch,   $count_3inchcd,
  $count_5inch,  $count_5inchcd, $count_8inch,
  $count_10inch, $count_12inch,  $count_15inch,
  $count_18inch
);

our @detector_errors = (
  $count_error_bare,   $count_error_barecd,  $count_error_2inch,
  $count_error_2inchcd,$count_error_3inch,   $count_error_3inchcd,
  $count_error_5inch,  $count_error_5inchcd, $count_error_8inch,
  $count_error_10inch, $count_error_12inch,  $count_error_15inch,
  $count_error_18inch
);

our @detector_names = (
  "bare",   "barecd",  "2inch",   "2inchcd",
  "3inch",  "3inchcd", "5inch",   "5inchcd",
  "8inch",  "10inch",  "12inch",  "15inch",
  "18inch"
);

# Seed CGI::param so older modules still see them via param('foo'):
param($_ => $data{$_}) for keys %data;

# Now immediately redirect ALL prints to our output file:
open STDOUT, '>', $out_path
    or die "Cannot open output file '$out_path': $!\n";


# Since cgi files are still in effect, htmlinput needs to be used
# This will cause errors when trying to do a full CLI integration
eval { &htmlinput };
warn $@ if $@; 
&initialize;

# Select which detectors are “true” and build $ball[], $bce[], $errbce[]:
our $j = -1;
for (my $i = 0; $i <= $#use_detectors; $i++) {
    if ($use_detectors[$i] =~ /true/) {
        $j++;
        $ball[$j]   = $detector_names[$i];
        $bce[$j]    = $detector_counts[$i];
        $errbce[$j] = $detector_errors[$i];
    }
}
our $num_det = $j + 1;


# Some of the matrices give issues with the number of groups
# These lines are used to just verify the assigned number is actually used
my ($mat_ref, $eend_ref, $maybe_num_groups) =
    matrix_in(\$matrix_file, \@use_detectors, \$max_energy);

# Normalize “$maybe_num_groups” into a true integer $num_groups. 
if (ref($maybe_num_groups) eq 'SCALAR'){
    $num_groups = $$maybe_num_groups;
}
else {
    # otherwise assume it’s already a plain scalar (even undef),
    $num_groups = $maybe_num_groups // 0;
}

@mat        = @{ $mat_ref   // [] };
@eend       = @{ $eend_ref  // [] };
	   

for(my $i=0;$i<$num_groups;$i++){
       $ce[$i]=($eend[$i]*$eend[$i+1])**.5;
       $wdleth[$i] = log($eend[$i+1]) - log($eend[$i]);
}

# Sum errors , make dead time correction to ball counts
$sumwht=0;
for (my $i=0;$i<$num_det;$i++){
	$sumwht=$sumwht+$errbce[$i];
	$bce[$i]=$bce[$i]/(1.0-$bce[$i]*$dead);
}
# calculate ball count error weights
for (my $i=0;$i<$num_det;$i++){
	$whtbce[$i]=$sumwht/($num_det*$errbce[$i]);
}

# change Response Matrix to unfold per unit lethargy

for (my $j=0;$j<$num_det;$j++){
	for (my $i=0;$i<$num_groups;$i++){
		$aleth[$j][$i]=$mat[$i+1][$j]*$wdleth[$i];
	}
}
# Call Maxiet if required
if ($start_spec =~ /MAXIET/){
	&maxiet_cli;
}
elsif ($start_spec =~ /User Input/){
	&user_input;
}
else {
	&guess_cli;
}

#Transfor matrix to constant initial spectrum
&trans_mat;
#Calculate Sphere Responses and sum from initial spectrum

&normalize;

$rnorm=&scale_factor(\@bce,\@errbce,\@aleth,$num_det,$num_groups,\@spli)*$cal;

	
print "rnorm = $rnorm\n";

&cal_response;
&fit_error;
my $chi = &chi_squared($num_det, \@bce, \@bcc, \@errbce);

for (my $i = 0; $i < $num_groups; $i++) {
    $splstart[$i] = $spli[$i] * $rnorm;
}

{
  no warnings 'redefine';
  our $iter = 0;
}
my $starterror = sqrt($error / $num_det) * 100;

our $unfold = "";

if ($alg =~ /MAXED/) {
	$unfold = "MAXED";
    &maxed_cli;
}
elsif ($alg =~ /SAND/) {
	$unfold = "SANDII";
    &sand2_cli;
}
else {
	# This assigns the unfolding for the output file
	if ($alg =~ /BON/) {
        $unfold = "BON";
    }
    elsif ($alg =~ /SPUNIT/) {
        $unfold = "SPUNIT";
    }

    printf "Iteration = %-4d   Error = %7.3f   Chi-Squared = %11.3E\n",
           $iter, $starterror, $chi;

    if ($max_iter > 0) {
        $chi = 9e+99;
        do {
            $erroru  = $error;
            $old_chi = $chi;
			# This actually runs the unfolding
			if ($alg =~ /BON/) {
				&bon;
    		}	
    		elsif ($alg =~ /SPUNIT/) {
				&spunit;
    		}
            &fit_error;
            $chi = &chi_squared($num_det, \@bce, \@bcc, \@errbce);

            my $stuf = sqrt($error / $num_det) * 100;
            printf "Iteration = %-4d   Error = %7.3f   Chi-Squared = %11.3E\n",
                   $iter, $stuf, $chi;
        }
        while ($chi / $old_chi < $tstrat
            && $iter + $itrtst <= $itrmax
            && $error > $tstper);
    }
}
# Just a verification that the right unfolding method was used
print STDERR "\$unfold = '$unfold'\n";

&sum_data;
&output_cli;

exit 0;
