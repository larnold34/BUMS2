#!/usr/bin/perl

BEGIN {unshift(@INC,'/usr/lib/perl5/5.00503');}
unshift(@INC,".");
use CGI qw(:standard *table *TR *th *td :html3 :netscape);
require "dir_read.pl";

opendir(DIR,"save");
@parentfiles=readdir(DIR);
closedir(DIR);
foreach $filename (@parentfiles) {
	if ($filename =~ /\Q$ENV{'REMOTE_ADDR'}\E/){
		open (IN,"save/$ENV{'REMOTE_ADDR'}") || die;
		restore_parameters(IN);
		close IN;
	}
}

print header;
print start_html(-title=>'Notezy Home Page',
	         -BGCOLOR=>'white', -LINK=>'red', -VLINK=>'Red', -ALINK=>'blue');
print qq\<meta http-equiv="Pragma" content="no-cache">\;

print center(h1("BUMS Input Page!")),
print center(h4("There are several qirks about the current version.  Do not use spheres that are not part of the response matrix.  It can't catch this and will give you a blank output.  Also do not use 0.  Enter a small number 0.000001 in place of 0. ")),

#start_form(-action=>'notezy.pl'),
start_form(-action=>'redirect.cgi'),
  
table(
     TR([
       th(["Description",textfield(-name=>'title',-maxlength=>90,-size=>50)])
     ])
);


print start_table(),
 start_TR(),
 start_th();
print table({align=>center},
 TR(
   [
	th([qq!<a href="help.cgi?page=detector">Detector</a>&#160 &#160!,
	    a({href=>"help.cgi?page=detectors_used"},"Detectors<br>Used<br>To Unfold"),
	    a({href=>"help.cgi?page=ball_count"},"Ball<br>Count"),
	    a({href=>"help.cgi?page=ball_error"},"Percent<br>Error")]),
	td(["Bare",
	   checkbox(-name=>'bare',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'bare_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'bare_counts_error',-size=>4,-maxlength=>10)]),
	td(["Bare Cd",
	   checkbox(-name=>'barecd',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'barecd_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'barecd_counts_error',-size=>4,-maxlength=>10)]),
	td(["2 Inch",
	   checkbox(-name=>'2inch',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'2_inch_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'2_inch_counts_error',-size=>4,-maxlength=>10)]),
	td(["2 Inch Cd",
	   checkbox(-name=>'2inchcd',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'2_inch_cd_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'2_inch_cd_counts_error',-size=>4,-maxlength=>10)]),
	td(["3 Inch",
	   checkbox(-name=>'3inch',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'3_inch_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'3_inch_counts_error',-size=>4,-maxlength=>10)]),
	td(["3 Inch Cd",
	   checkbox(-name=>'3inchcd',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'3_inch_cd_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'3_inch_cd_counts_error',-size=>4,-maxlength=>10)]),
	td(["5 Inch",
	   checkbox(-name=>'5inch',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'5_inch_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'5_inch_counts_error',-size=>4,-maxlength=>10)]),
	td(["5 Inch Cd",
	   checkbox(-name=>'5inchcd',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'5_inch_cd_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'5_inch_cd_counts_error',-size=>4,-maxlength=>10)]),
	td(["8 Inch",
	   checkbox(-name=>'8inch',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'8_inch_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'8_inch_counts_error',-size=>4,-maxlength=>10)]),
	td(["10 Inch",
	   checkbox(-name=>'10inch',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'10_inch_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'10_inch_counts_error',-size=>4,-maxlength=>10)]),
	td(["12 Inch",
	   checkbox(-name=>'12inch',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'12_inch_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'12_inch_counts_error',-size=>4,-maxlength=>10)]),
	td(["15 Inch",
	   checkbox(-name=>'15inch',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'15_inch_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'15_inch_counts_error',-size=>4,-maxlength=>10)]),
	td(["18 Inch",
	   checkbox(-name=>'18inch',-checked=>'',-value=>'true',-label=>''),
	   textfield(-name=>'18_inch_counts',-size=>8,-maxlength=>90),
	   textfield(-name=>'18_inch_counts_error',-size=>4,-maxlength=>10)]),
   ]));
print end_th;
print start_th({NOWRAP});
  print "&#160 &#160 &#160 &#160 &#160 &#160";
print end_th();
print start_th();

print table(
      TR({align=>"left"},
	[
	td([a({href=>"help.cgi?page=max_iter"},"Max. Number of Iterations"),
	 textfield(-name=>'iter',-size=>5,-default=>'1000',-maxlength=>90)]),
	td([a({href=>"help.cgi?page=iter_error"},"Iterations before test error"),
	 textfield(-name=>'itertesterror',-size=>5,-default=>'10',-maxlength=>90)]),
	td([a({href=>"help.cgi?page=final_error"},"Final error %"),
	 textfield(-name=>'endtesterror',-size=>2,-default=>'10',-maxlength=>90)]),
	td([a({href=>"help.cgi?page=max_temp"},"Maxwellian Temp"),
	 textfield(-name=>'tempij',-size=>6,-default=>'1.42',-maxlength=>90)]),
	td([a({href=>"help.cgi?page=smooth"},"Smoothing Factor"),
	 textfield(-name=>'smoothing',-size=>4,-default=>'0.1',-maxlength=>90)]),
	td([a({href=>"help.cgi?page=shape"},"Shape"),
	 textfield(-name=>'shape',-size=>4,-default=>'0.0',-maxlength=>90)]),
	td([a({href=>"help.cgi?page=perturbation"},"Perturbation"),
	 textfield(-name=>'perturbation',-size=>4,-default=>'0.1',-maxlength=>90)]),
	td([a({href=>"help.cgi?page=cal_factor"},"Calibration Factor"),
	 textfield(-name=>'cal_factor',-size=>7,-default=>'1.0',-maxlength=>90)]),
	td([a({href=>"help.cgi?page=max_energy"},"Maximum Energy"),
	 textfield(-name=>'max_energy',-size=>6,-default=>'10.0',-maxlength=>90)]),
	]));
print end_th;
print end_TR,end_table;

print start_table(), 
  start_TR(),
   start_td({-valign=>bottom}),
    a({href=>"help.cgi?page=starting_spectrum"},"Select a starting spectrum"),
   start_td({valign=>center}),
    q/<SELECT NAME="start_spec" LABEL="">/;
	if (param('start_spec')=~/Automatic Search/) {
		print q/<OPTION SELECTED VALUE="Automatic Search">Automatic Search/;
	}
	else {
    	print q/<OPTION VALUE="Automatic Search">Automatic Search/;
	}	
	if (param('start_spec')=~/User Input/) {
    	print q/<OPTION SELECTED VALUE="User Input">User Input/;
	}
	else {
    	print q/<OPTION VALUE="User Input">User Input/;
	}
	if (param('start_spec')=~/MAXIET/) {
		print q/<OPTION SELECTED VALUE="MAXIET">MAXIET/;
	}
	else {
		print q/<OPTION  VALUE="MAXIET">MAXIET/;
	}
    &dir_read("spectra");
    for ($i=0;$i<$#file+1;$i++) {
		open(FILE,"spectra/$file[$i]");
		$head=<FILE>;
		close(FILE);
		if (param('start_spec') eq $file[$i]) {
			print "<OPTION SELECTED VALUE=$file[$i]>$head";
		}
		else {
			print "<OPTION VALUE=$file[$i]>$head";
		}	
    }
   print "</SELECT>";
 print end_TR;

 print start_TR(),
   start_td(),a({href=>"help.cgi?page=unfolding_method"},"Select an unfolding method"),
   start_td(),popup_menu(-name=>'alg',-values=>['SPUNIT','BON','MAXED','SANDII'],-default=>'SPUNIT',-label=>''),
 end_TR,

 start_TR(),
   start_td(),a({href=>"help.cgi?page=unfolding_matrix"},"Select an unfolding matrix"),
   start_td(),
    q/<SELECT NAME="matrix" LABEL="">/;
    &dir_read("matrix");
    for ($i=0;$i<$#file+1;$i++) {
		open(FILE,"matrix/$file[$i]");
		$head=<FILE>;
		close(FILE);
		if (param('matrix') eq $file[$i]) {
			print "<OPTION SELECTED VALUE=$file[$i]>$file[$i] - $head";
		}
		else {
			print "<OPTION VALUE=$file[$i]>$file[$i] - $head";
		}
    }
    print "</SELECT>";
 print end_TR,

 TR([
    td([submit(-name=>'Submit'),reset])
   ]),
end_table;

print "\n";
if (param('start_spec')=~/User Input/) {
	print a({href=>"custom_spectra.cgi"},"User Input Spectrum Form");
}                                                
print "\n";


print hidden(-name=>'input_spectrum',-value=>param('input_spectrum'));
print end_form,
hr;

