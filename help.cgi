#!/usr/bin/perl
BEGIN {unshift(@INC,'/usr/lib/perl5/5.00503');}
unshift(@INC,".");
use CGI qw(:standard *table *TR *th *td :html3 :netscape);

print header;
print start_html(-title=>'HELP',
	         -BGCOLOR=>'white', -LINK=>'Red', -VLINK=>'Red', -ALINK=>'blue');

$page=param('page');

if ($page=~ /\./){
  print "Error - What are you trying to do, get the password file?";
}
else {
open(IN,"help/$page");
 while(<IN>) {
	print "$_";
 }
}
close(IN);
