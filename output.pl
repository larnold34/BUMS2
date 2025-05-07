#!/usr/bin/perl
sub output{
my $i;
$HOSTNAME=`hostname`;
chomp($HOSTNAME);

	print hr;
	print qq!<font  face="courier"><pre>!,br,p;
#         123451234567123456123456,12345123456789112345678123456789123456789012        
	print "Response    Unfold   Maxwell      Calib.  Smooth   Per Cent    No. of",br;
	print "Matrix	     Code   Temp,Shape    Factor  Factor    Error      Iterations",br;
   print "________    ______  ____,_____    ______  ______   ________    __________",br;
	printf "%-5s%13s%6.2f,%-4.2f%  10.4f%8.4f %9.4f%12d\n\n",$rmtx,$unfold,$tempm,$shape,$cal,$smo,$perror,$iter;

#         12345678912345123456789012123123456789012121234567890
	print "Detectors     Measured       Calculated    Percent",br;
	print "              Counts         Counts        Difference",br;
	print "_________     ___________    ____________  __________",br;

	for ($i=0;$i<$num_det;$i++) {
		printf "%9s     %-12.3f   %-12.3f  %-10.3f",$ball[$i],$bce[$i],$bcc[$i],$pcterr[$i];
		print br;
	}

	print "\n";
   
	if (param('start_spec') =~ /MAXIET/){
		print "Starting Spectrum      = MAXIET Algorthm",br;
	}
	else {
		open(INFILE,"spectra/$best_file");
		$header=<INFILE>;
        close(INFILE);
		chomp ($header);
		print "Starting Spectrum      = $header",br;
	}
	
	printf "Total Fluence          = %11.3e Neutrons/cm2",$sumspc;
	print br;
	printf "Ave. Energy (Less Th.) = %11.3e MeV",$aveen;
	print br;
	printf "Dose Equivalent        = %11.3e REM",$sumrem;
	print br;
	print "\n";

#         12341123456789011123456789011123456789011123456789011123456789011123456789011
	print "BIN  ENERGY      FLUENCE     FLUENCE     DOSE EQV.   DOSE EQV.",br;
	print "No.  Max (MeV)   NEUT/CM2    N/CM2/LETH  (REM)       (% of Total)",br;

	for ($i=0;$i<$num_groups;$i++) {
		printf "%-4d %-11.3e %-11.3e %-11.3e %-11.3e %-11.3e",$i,$eend[$i+1],$spc[$i],$spl[$i],$rem[$i],$prem[$i];
	print br;
	}

print br;print br; print br;
&plot;
print img {src=>"/tmp/notezy/$gif_file",align=>'CENTER'},br; 
# print img {src=>"http://$HOSTNAME/tmp/notezy/$gif_file",align=>'LEFT'},br; 

$rm_file="/var/www/html/tmp/notezy/rm.$$";
open(OUT,">$rm_file");
		print OUT "rm /var/www/html/tmp/notezy/$gif_file\n";
      print OUT "rm /var/www/html/tmp/notezy/$rm_file\n";
close(OUT);

print `at -f /var/www/html/tmp/notezy/$rm_file now + 5 minutes`;


print start_form(-action=>'detector_response.cgi');

print "\n";
print qq/<INPUT TYPE="hidden" NAME="data" VALUE="\n/;
for ($i=0;$i<$num_groups;$i++) {
	printf "%11.3E	%11.3E\n",$ce[$i],$spc[$i];
}
print qq\">\;
print p;
print submit(-name=>'Dose and Detector Response');
}
1;
