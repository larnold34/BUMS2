#!/usr/bin/perl
BEGIN {unshift(@INC,'/usr/lib/perl5/5.00503');}
unshift(@INC,".");
use CGI qw(:standard :html3 :netscape *table *TR *th *td);
print header;
print start_html(-title=>'NOTEZY OUTPUT PAGE',
				     -BGCOLOR=>'yellow');
require "htmlinput.pl";
require "initialize.pl";
require "response_matrix.pl";
require "print_mat.pl";
require "maxiet.pl";
require "trans_mat.pl";
require "cal_response.pl";
require "spunit.pl";
require "bon.pl";
require "sum_data.pl";
require "output.pl";
require "normalize.pl";
require "fit_error.pl";
require "dir_read.pl";
require "guess.pl";
require "rebin.pl";
require "ede.pl";
require "plot.pl";
require "dfact.pl";
require "user_input_spectra.pl";
require "maxed.pl";
require "scale_factor.pl";
require "chi_squared.pl";
require "sand2.pl";
require "Math/Interpolate.pm";

# There seems to be an issue with macOS populating the parameters from the input file
use URI::Escape qw(uri_unescape);

# opendir(DIR,"save");
# @parentfiles=readdir(DIR);
# closedir(DIR);
# foreach $filename (@parentfiles) {
# 	if ($filename =~ /$ENV{'REMOTE_ADDR'}/){
# 		open (IN,"save/$ENV{'REMOTE_ADDR'}") || die;
# 		restore_parameters(IN);
# 		close IN;
# 	}
# }

my $ip = $ENV{'REMOTE_ADDR'};
my $filepath = "save/$ip";

if (-e $filepath) {
    open (IN, $filepath) or die "Cannot open $filepath: $!";

    while (<IN>) {
        chomp;
        next if $_ eq '' || $_ eq '=';  # skip empty lines
        my ($key, $value) = split(/=/, $_, 2);
        next unless defined $key;

        # Decode URL-encoded values
        $value = uri_unescape($value // '');  # handle undefined safely
        param(-name => $key, -value => $value);
    }

    close IN;
} else {
    print "Warning: Input file $filepath not found", br;
}

&htmlinput;
&initialize;

@use_detectors=  ($use_det_bare,$use_det_barecd,$use_det_2inch,
                  $use_det_2inchcd,$use_det_3inch,
                  $use_det_3inchcd,$use_det_5inch,$use_det_5inchcd,
                  $use_det_8inch,$use_det_10inch,$use_det_12inch,$use_det_15inch,
                  $use_det_18inch);
@detector_counts=($count_bare,$count_barecd,$count_2inch,$count_2inchcd,
                  $count_3inch,$count_3inchcd,$count_5inch,$count_5inchcd,
                  $count_8inch,$count_10inch,$count_12inch,$count_det_15inch,
                  $count_18inch);
@detector_errors=($count_error_bare,$count_error_barecd,$count_error_2inch,
                  $count_error_2inchcd,$count_error_3inch,$count_error_3inchcd,
                  $count_error_5inch,$count_error_5inchcd,$count_error_8inch,
                  $count_error_10inch,$count_error_12inch,$count_error_15inch,
                  $count_error_18inch);
@detector_names=("bare","barecd","2inch","2inchcd","3inch","3inchcd","5inch", 
                 "5inchcd","8inch","10inch","12inch","15inch","18inch");

$j=-1;
for ($i=0;$i<($#use_detectors+1);$i++){
	if ($use_detectors[$i] =~ /true/) {
		$j++;
		$ball[$j]=$detector_names[$i];
		$bce[$j]=$detector_counts[$i];
		$errbce[$j]=$detector_errors[$i];
		# print "j=$j ball[$j]=$ball[$j] bce[$j]=$bce[$j]\n",br;
	}
}
$num_det=$j+1;
(*mat,*eend,*num_groups)=&matrix_in(\$matrix_file,\@use_detectors,\$max_energy);
# &print_mat;
	   

for($i=0;$i<$num_groups;$i++){
       $ce[$i]=($eend[$i]*$eend[$i+1])**.5;
       $wdleth[$i] = log($eend[$i+1]) - log($eend[$i]);
}

# Sum errors , make dead time correction to ball counts
$sumwht=0;
for ($i=0;$i<$num_det;$i++){
	$sumwht=$sumwht+$errbce[$i];
	$bce[$i]=$bce[$i]/(1.0-$bce[$i]*$dead);
}
# calculate ball count error weights
for ($i=0;$i<$num_det;$i++){
	$whtbce[$i]=$sumwht/($num_det*$errbce[$i]);
}

# change Response Matrix to unfold per unit lethargy

for ($j=0;$j<$num_det;$j++){
	for ($i=0;$i<$num_groups;$i++){
		$aleth[$j][$i]=$mat[$i+1][$j]*$wdleth[$i];
	}
}
# Call Maxiet if required
if (param('start_spec') =~ /MAXIET/){
	&maxiet;
}
elsif (param('start_spec') =~ /User Input/){
	&user_input;
}
else {
	&guess;
}

#Transfor matrix to constant initial spectrum
&trans_mat;
#Calculate Sphere Responses and sum from initial spectrum

&normalize;

# $rnorm=&scale_factor(\@bce,\@errbce,\@aleth,$num_det,$num_groups,\@spli)*$cal;
$rnorm = &scale_factor(\@bce,\@errbce,\@aleth,$num_det,$num_groups,\@spli) * $cal;

print "rnorm = $rnorm",br;
&cal_response;
&fit_error;
$chi=&chi_squared($num_det,\@bce,\@bcc,\@errbce);
for ($i=0;$i<$num_groups;$i++){
	$splstart[$i]=$spli[$i]*$rnorm;
}

$iter=0;
$starterror=sqrt($error/$num_det)*100;

if (param('alg') =~/MAXED/){
	&maxed;
}
elsif (param('alg') =~/SAND/){
	&sand2;
}
else {
	print hr;
			$iter=0;
			print "<pre>";
			printf "Iteration = %-4d &#160 &#160 Error = %7.3f &#160 &#160  Chi-Squared = %11.3E",$iter,$starterror,$chi;
			print "\n",br;
	if (param('iter')>0) {
	 	$chi=9E+99;	
		do {
			$erroru=$error;
			$old_chi=$chi;
			if (param('alg') =~ /SPUNIT/) {
				&spunit;
			}
			elsif (param('alg') =~ /BON/) {
				&bon;
			}
			&fit_error;
			$chi=&chi_squared($num_det,\@bce,\@bcc,\@errbce);
   	# 	TEST FOR COMPLETION
			$stuf=sqrt($error/$num_det)*100;
			printf "Iteration = %-4d &#160 &#160 Error = %7.3f &#160 &#160  Chi-Squared = %11.3E",$iter,$stuf,$chi;
			print "\n",br;

		} while ($chi/$old_chi<$tstrat && $iter+$itrtst<=$itrmax && $error>$tstper);
	}
}
&sum_data;
print "</pre>";
print br;
&output;


