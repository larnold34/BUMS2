#!/usr/bin/perl
BEGIN { unshift(@INC,'/usr/lib/perl5/5.00503'); }
unshift(@INC,".");
use CGI qw(:standard *table *TR *th *td :html3 :netscape);
use CGI::Cookie;
require "dir_read.pl";

# Determine if the user has submitted the form
my $submitted = param('Submit') || param('ReturnToMain');

# Prepare cookies if data has been submitted
my @cookies;
if ($submitted) {
    if (defined param('input_spectrum')) {
        push @cookies, CGI::Cookie->new(-name => 'input_spectrum', -value => param('input_spectrum'));
    }
    if (defined param('spectra_form')) {
        push @cookies, CGI::Cookie->new(-name => 'spectra_form', -value => param('spectra_form'));
    }
    print header(-type => 'text/html', -cookie => \@cookies);
} else {
    print header;
}

print start_html(-title=>'Custom Spectrum Input Page',
	         -BGCOLOR=>'yellow', -LINK=>'Red', -VLINK=>'Red', -ALINK=>'blue');
print qq\<meta http-equiv="Pragma" content="no-cache">\;

print center(h1("BUMS Custom Spectra Input Page!"));

# Load cookies if values not already present
my %cookies = CGI::Cookie->fetch();
foreach my $key (keys %cookies) {
    param(-name => $key, -value => $cookies{$key}->value) unless defined param($key);
}

#print start_form(-action=>'redirect.cgi');
print start_form(-method=>'POST');


print "Input your custom spectra with energy bins in the first 
column and the value in the second bin. The energy bands for the
neutron spectrum are determined by the preceding energy group 
(lower bound) and the indicated energy (upper bound). Therefore,
the first energy bin indicates the lowest energy boundary and its
associated value is not used.  The columns must be tab or space 
seperated.", br;

print br;

print "Select the form of the neutron spectrum.", br;
print radio_group(
    -name=>'spectra_form',
    -values=>[
        '1: (n fluence rate per bin)/(width of bin in E(MeV))',
        '2: (n fluence rate per bin)/(width of bin in ln(E/MeV))',
        '3: (n fluence rate per bin)'
    ],
    -default=>scalar param('spectra_form') || '',
    -linebreak=>'true'
);

print br;

print textarea(
    -name=>'input_spectrum',
    -rows=>31,
    -columns=>80,
    -default=>scalar param('input_spectrum')
);

print table(
    TR([
        td([submit(-name=>'Submit', -value=>'Save and Return to Main Page')])
    ])
);

# Re-post all other form fields as hidden inputs
foreach my $p (param()) {
    next if $p =~ /^input_spectrum$|^Submit$|^spectra_form$/;
    print hidden(-name=>$p, -default=>scalar param($p));
}

print end_form;
if ($submitted) {
    print hr, h2("DEBUG: Received Parameters"), start_table({border => 1});
    foreach my $name (param()) {
        my $val = param($name);
        $val =~ s/\n/<br>/g;  # display multiline spectrum properly
        print Tr(td([$name, $val]));
    }
    print end_table, hr;
}

print hr;
