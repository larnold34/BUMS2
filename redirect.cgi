#!/usr/bin/perl

use CGI qw(:standard);
use CGI::Cookie;

# Fixed list of expected form fields (add others if needed)
my @expected_fields = qw(
    title bare barecd 2inch 2inchcd 3inch 3inchcd 5inch 5inchcd
    8inch 10inch 12inch 15inch 18inch
    bare_counts bare_counts_error
    barecd_counts barecd_counts_error
    2_inch_counts 2_inch_counts_error
    2_inch_cd_counts 2_inch_cd_counts_error
    3_inch_counts 3_inch_counts_error
    3_inch_cd_counts 3_inch_cd_counts_error
    5_inch_counts 5_inch_counts_error
    5_inch_cd_counts 5_inch_cd_counts_error
    8_inch_counts 8_inch_counts_error
    10_inch_counts 10_inch_counts_error
    12_inch_counts 12_inch_counts_error
    15_inch_counts 15_inch_counts_error
    18_inch_counts 18_inch_counts_error
    iter itertesterror endtesterror tempij smoothing shape
    perturbation cal_factor max_energy
    start_spec alg matrix
    input_spectrum spectra_form Submit
);

# Build full param hash
my %params;
foreach my $field (@expected_fields) {
    $params{$field} = defined param($field) ? param($field) : '';
}

# Create and print cookies
foreach my $key (keys %params) {
    my $cookie = CGI::Cookie->new(-name => $key, -value => $params{$key});
    print "Set-Cookie: $cookie\n";
}

# Save to file
my $ip = $ENV{'REMOTE_ADDR'};
open(my $fh, ">save/$ip") or die "Cannot open save file: $!";
foreach my $key (keys %params) {
    my $val = $params{$key};
    $val =~ s/([^A-Za-z0-9])/sprintf("%%%02X", ord($1))/seg;
    print $fh "$key=$val\n";
}
close $fh;

# Redirect
if (param('Submit')) {
    print redirect('notezy.pl');
} else {
    print redirect('notezy.cgi');
}
