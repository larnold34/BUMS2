#!/usr/bin/perl
BEGIN {unshift(@INC,'/usr/lib/perl5/5.00503');}
unshift(@INC,".");
use CGI qw(:standard *table *TR *th *td :html3 :netscape);
require "dir_read.pl";

print header;
print start_html(-title=>'Custom Spectrum Input Page',
	         -BGCOLOR=>'blue', -LINK=>'Red', -VLINK=>'Red', -ALINK=>'blue');
print qq\<meta http-equiv="Pragma" content="no-cache">\;

print center(h1("BUMS Custom Spectra Input Page!"));

#__END__
start_form(-action=>'redirect.cgi');
opendir(DIR,"save");
@parentfiles=readdir(DIR);
closedir(DIR);
foreach $filename (@parentfiles) {
	if ($filename =~ /$ENV{'REMOTE_ADDR'}/){
		open (IN,"save/$ENV{'REMOTE_ADDR'}") || die;
		restore_parameters(IN);
		close IN;
		open (IN,"save/$ENV{'REMOTE_ADDR'}") || die;
		*q = new CGI(IN);
		close IN;
	}
}
print "Input your custom spectra with energy bins in the first 
column and the value in the second bin. The energy bands for the
neutron spectrum are determined by the preceding energy group 
(lower bound) and the indicated energy (upper bound). Therefore,
the first energy bin indicates the lowest energy boundary and its
associated value is not used.  The columns must be tab or space 
seperated.",br;
print br;


print "Select the form of the neutron spectrum.",br;
print radio_group(-name=>'spectra_form',
                        -values=>['1: (n fluence rate per bin)/(width of bin in E(MeV))',
                                 '2: (n fluence rate per bin)/(width of bin in ln(E/MeV))',
                                  '3: (n fluence rate per bin)'
                                 ],
						-linebreak=>'true'
                       );

#print table(
#	TR([
#		th([radio_group(-name=>'spectra_form',
#
#                        -values=>['1: (n fluence rate per bin)/(width of bin in E(MeV))',
#                                 '2: (n fluence rate per bin)/(width of bin in ln(E/MeV))',
#                                  '3: (n fluence rate per bin)'
#                                 ]
#                       )
#          ]);
#	]);
	
#);
print "\n";
print br;

print textarea(-name=>'input_spectrum',
                          -rows=>31,
                          -columns=>80);
  
print table(
#	TR([
#		th(["",textarea(-name=>'spectrum',-maxlength=>90,-size=>100)])
#	]),
	
 	TR([
		td([submit(-name=>'Submit'),reset])
	])
);
print "\n";
while (($key,$value)=each(%q)){
	unless ($key =~ /.fieldnames/ || $key=~/input_spectrum/ || $key=~/.parameters/){
		print hidden(-name=>$key,-default=>$value->[0]),"\n";
	}
}

print end_form;
print hr;

__END__
