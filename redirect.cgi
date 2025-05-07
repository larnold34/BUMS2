#!/usr/bin/perl
BEGIN {unshift(@INC,'/usr/lib/perl5/5.00503');}
unshift(@INC,".");
use CGI qw(:standard *table *TR *th *td :html3 :netscape);
$test=param('start_spec');
$input_start=param('input_spectrum');
read(STDIN,$buffer,$ENV{'CONTENT_LENGTH'});

open (OUT,">save/$ENV{'REMOTE_ADDR'}") || die;
my $q = new CGI;
foreach $pair ( split(/&/,$buffer)){
	$pair =~ tr/+//;
	($name,$value) = split(/=/,$pair);
    $q->param(-name=>$name,-value=>$value);
}
$q->save(OUT);  
close OUT;            

print "Set-Cookie: user=$ENV{'REMOTE_ADDR'} path=/notezy\n";

if ( ($test=~ /User Input/) && (!$input_start) ) {
	print redirect('custom_spectra.cgi');
}
else {
	print redirect('notezy.pl');
}

