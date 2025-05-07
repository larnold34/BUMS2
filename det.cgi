#!/usr/bin/perl
BEGIN {unshift(@INC,'/usr/lib/perl5/5.00503');}
unshift(@INC,".");
use CGI qw(:standard *table *TR *th *td :html3 :netscape);
require "dir_read.pl";

print header;
print start_html(-title=>'Notezy Home Page',
	         -BGCOLOR=>'blue', -LINK=>'Red', -VLINK=>'Red', -ALINK=>'blue');

