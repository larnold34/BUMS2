#!/usr/bin/perl
use strict;
use warnings;
use CGI qw(:standard *table *TR *th *td :html3 :netscape);
require "dir_read.pl";

print header;
print start_html(
    -title   => 'Custom Spectrum Input Page',
    -BGCOLOR => 'yellow',
    -LINK    => 'Red',
    -VLINK   => 'Red',
    -ALINK   => 'blue'
);
print qq\<meta http-equiv="Pragma" content="no-cache">\;

print center(h1("BUMS Custom Spectra Input Page!"));

print start_form(-action => 'redirect.cgi');

print p("Input your custom spectra with energy bins in the first column and the value in the second bin. The energy bands for the neutron spectrum are determined by the preceding energy group (lower bound) and the indicated energy (upper bound). Therefore, the first energy bin indicates the lowest energy boundary and its associated value is not used. The columns must be tab or space separated.");

print p("Select the form of the neutron spectrum:");

print radio_group(
    -name      => 'spectra_form',
    -values    => [
        '1: (n fluence rate per bin)/(width of bin in E(MeV))',
        '2: (n fluence rate per bin)/(width of bin in ln(E/MeV))',
        '3: (n fluence rate per bin)'
    ],
    -linebreak => 'true'
);

print br();

print textarea(
    -name    => 'input_spectrum',
    -rows    => 31,
    -columns => 80
);

print table(
    TR([
        td([submit(-name => 'Submit'), reset])
    ])
);

# Create hidden fields for all parameters (except some)
my $q = new CGI();
foreach my $key ($q->param) {
    next if $key =~ /.fieldnames|input_spectrum|.parameters/;
    print hidden(-name => $key, -default => scalar $q->param($key)), "\n";
}

print end_form;
print hr;

print end_html;