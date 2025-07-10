#!/usr/bin/perl

BEGIN {unshift(@INC,'/usr/lib/perl5/5.00503');}
unshift(@INC,".");
use CGI qw(:standard *table *TR *th *td :html3 :netscape);
use CGI::Cookie;
require "dir_read.pl";

# Restore values from cookies
#my %cookies = CGI::Cookie->fetch;
#foreach my $key (keys %cookies) {
#    param(-name => $key, -value => $cookies{$key}->value) unless defined param($key);
#}
# Force overwrite values from cookies
my %cookies = CGI::Cookie->fetch;
foreach my $key (keys %cookies) {
    param(-name => $key, -value => $cookies{$key}->value);  # always overwrite
}


# Read saved file if it exists
opendir(DIR,"save");
@parentfiles=readdir(DIR);
closedir(DIR);
foreach my $filename (@parentfiles) {
    if ($filename =~ /\Q$ENV{'REMOTE_ADDR'}\E/) {
        open(IN,"save/$ENV{'REMOTE_ADDR'}") || die;
        while (<IN>) {
            chomp;
            next if $_ eq '' || $_ eq '=';
            my ($key, $value) = split(/=/, $_, 2);
            $value =~ s/\+/ /g;
            $value =~ s/%([0-9A-Fa-f]{2})/chr(hex($1))/eg;
            param(-name => $key, -value => $value) unless defined param($key);
        }
        close IN;
    }
}

print header;
print start_html(-title=>'Notezy Home Page',
                 -BGCOLOR=>'white', -LINK=>'red', -VLINK=>'Red', -ALINK=>'blue');
print qq\<meta http-equiv="Pragma" content="no-cache">\;

print center(h1("BUMS Input Page!"));
print center(h4("There are several qirks about the current version.  Do not use spheres that are not part of the response matrix.  It can't catch this and will give you a blank output.  Also do not use 0.  Enter a small number 0.000001 in place of 0. "));

print start_form(-action=>'redirect.cgi');

print table(TR([
    th(["Description", textfield(-name=>'title', -maxlength=>90, -size=>50)]),
]));

print start_table(), start_TR(), start_th();
print table({align=>center},
    TR([
        th([
            qq!<a href="help.cgi?page=detector">Detector</a>&#160 &#160!,
            a({href=>"help.cgi?page=detectors_used"},"Detectors<br>Used<br>To Unfold"),
            a({href=>"help.cgi?page=ball_count"},"Ball<br>Count"),
            a({href=>"help.cgi?page=ball_error"},"Percent<br>Error")
        ]),
        td(["Bare", checkbox(-name=>'bare', -value=>'true', -label=>''),
            textfield(-name=>'bare_counts', -size=>8),
            textfield(-name=>'bare_counts_error', -size=>4)]),
        td(["Bare Cd", checkbox(-name=>'barecd', -value=>'true', -label=>''),
            textfield(-name=>'barecd_counts', -size=>8),
            textfield(-name=>'barecd_counts_error', -size=>4)]),
        td(["2 Inch", checkbox(-name=>'2inch', -value=>'true', -label=>''),
            textfield(-name=>'2_inch_counts', -size=>8),
            textfield(-name=>'2_inch_counts_error', -size=>4)]),
        td(["2 Inch Cd", checkbox(-name=>'2inchcd', -value=>'true', -label=>''),
            textfield(-name=>'2_inch_cd_counts', -size=>8),
            textfield(-name=>'2_inch_cd_counts_error', -size=>4)]),
        td(["3 Inch", checkbox(-name=>'3inch', -value=>'true', -label=>''),
            textfield(-name=>'3_inch_counts', -size=>8),
            textfield(-name=>'3_inch_counts_error', -size=>4)]),
        td(["3 Inch Cd", checkbox(-name=>'3inchcd', -value=>'true', -label=>''),
            textfield(-name=>'3_inch_cd_counts', -size=>8),
            textfield(-name=>'3_inch_cd_counts_error', -size=>4)]),
        td(["5 Inch", checkbox(-name=>'5inch', -value=>'true', -label=>''),
            textfield(-name=>'5_inch_counts', -size=>8),
            textfield(-name=>'5_inch_counts_error', -size=>4)]),
        td(["5 Inch Cd", checkbox(-name=>'5inchcd', -value=>'true', -label=>''),
            textfield(-name=>'5_inch_cd_counts', -size=>8),
            textfield(-name=>'5_inch_cd_counts_error', -size=>4)]),
        td(["8 Inch", checkbox(-name=>'8inch', -value=>'true', -label=>''),
            textfield(-name=>'8_inch_counts', -size=>8),
            textfield(-name=>'8_inch_counts_error', -size=>4)]),
        td(["10 Inch", checkbox(-name=>'10inch', -value=>'true', -label=>''),
            textfield(-name=>'10_inch_counts', -size=>8),
            textfield(-name=>'10_inch_counts_error', -size=>4)]),
        td(["12 Inch", checkbox(-name=>'12inch', -value=>'true', -label=>''),
            textfield(-name=>'12_inch_counts', -size=>8),
            textfield(-name=>'12_inch_counts_error', -size=>4)]),
        td(["15 Inch", checkbox(-name=>'15inch', -value=>'true', -label=>''),
            textfield(-name=>'15_inch_counts', -size=>8),
            textfield(-name=>'15_inch_counts_error', -size=>4)]),
        td(["18 Inch", checkbox(-name=>'18inch', -value=>'true', -label=>''),
            textfield(-name=>'18_inch_counts', -size=>8),
            textfield(-name=>'18_inch_counts_error', -size=>4)]),
    ])
);
print end_th(), start_th({NOWRAP => ''}), "&#160 &#160 &#160 &#160 &#160 &#160", end_th(), start_th();

print table(TR({align=>"left"}, [
    td([a({href=>"help.cgi?page=max_iter"},"Max. Number of Iterations"),
        textfield(-name=>'iter', -size=>5, -default=>'1000')]),
    td([a({href=>"help.cgi?page=iter_error"},"Iterations before test error"),
        textfield(-name=>'itertesterror', -size=>5, -default=>'10')]),
    td([a({href=>"help.cgi?page=final_error"},"Final error %"),
        textfield(-name=>'endtesterror', -size=>2, -default=>'10')]),
    td([a({href=>"help.cgi?page=max_temp"},"Maxwellian Temp"),
        textfield(-name=>'tempij', -size=>6, -default=>'1.42')]),
    td([a({href=>"help.cgi?page=smooth"},"Smoothing Factor"),
        textfield(-name=>'smoothing', -size=>4, -default=>'0.1')]),
    td([a({href=>"help.cgi?page=shape"},"Shape"),
        textfield(-name=>'shape', -size=>4, -default=>'0.0')]),
    td([a({href=>"help.cgi?page=perturbation"},"Perturbation"),
        textfield(-name=>'perturbation', -size=>4, -default=>'0.1')]),
    td([a({href=>"help.cgi?page=cal_factor"},"Calibration Factor"),
        textfield(-name=>'cal_factor', -size=>7, -default=>'1.0')]),
    td([a({href=>"help.cgi?page=max_energy"},"Maximum Energy"),
        textfield(-name=>'max_energy', -size=>6, -default=>'10.0')])
]));

print end_th(), end_TR(), end_table;

print start_table(), start_TR(),
    start_td({-valign => 'bottom'}),
    a({href=>"help.cgi?page=starting_spectrum"},"Select a starting spectrum"),
    start_td({-valign => 'center'}),
    q/<SELECT NAME="start_spec">/;

# Start Spec options
if (param('start_spec')=~/Automatic Search/) {
    print q/<OPTION SELECTED VALUE="Automatic Search">Automatic Search/;
} else {
    print q/<OPTION VALUE="Automatic Search">Automatic Search/;
}
if (param('start_spec')=~/User Input/) {
    print q/<OPTION SELECTED VALUE="User Input">User Input/;
} else {
    print q/<OPTION VALUE="User Input">User Input/;
}
if (param('start_spec')=~/MAXIET/) {
    print q/<OPTION SELECTED VALUE="MAXIET">MAXIET/;
} else {
    print q/<OPTION VALUE="MAXIET">MAXIET/;
}

&dir_read("spectra");
for (my $i = 0; $i <= $#file; $i++) {
    open(FILE, "spectra/$file[$i]");
    my $head = <FILE>;
    close(FILE);
    if (param('start_spec') eq $file[$i]) {
        print "<OPTION SELECTED VALUE=$file[$i]>$head";
    } else {
        print "<OPTION VALUE=$file[$i]>$head";
    }
}
print "</SELECT>", end_td(), end_TR();

print start_TR(),
    td([a({href=>"help.cgi?page=unfolding_method"},"Select an unfolding method")]),
    td([popup_menu(-name=>'alg', -values=>['SPUNIT','BON','MAXED','SANDII'], -default=>'SPUNIT')]),
end_TR();

print start_TR(),
    td([a({href=>"help.cgi?page=unfolding_matrix"},"Select an unfolding matrix")]),
    start_td(), q/<SELECT NAME="matrix">/;
&dir_read("matrix");
for (my $i = 0; $i <= $#file; $i++) {
    open(FILE,"matrix/$file[$i]");
    my $head = <FILE>;
    close(FILE);
    if (param('matrix') eq $file[$i]) {
        print "<OPTION SELECTED VALUE=$file[$i]>$file[$i] - $head";
    } else {
        print "<OPTION VALUE=$file[$i]>$file[$i] - $head";
    }
}
print "</SELECT>", end_td(), end_TR();

print TR([td([submit(-name=>'Submit'), reset])]),
end_table();

print "\n";

if (param('start_spec') =~ /User Input/) {
    print hr;
    print h3("User Input Spectrum Entry:");

    print "Select the form of the neutron spectrum:", br;
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

    
    print "Input your custom spectra with energy bins in the first 
    column and the value in the second bin. The energy bands for the
    neutron spectrum are determined by the preceding energy group 
    (lower bound) and the indicated energy (upper bound). Therefore,
    the first energy bin indicates the lowest energy boundary and its
    associated value is not used.  The columns must be tab or space 
    seperated.", br;

    print textarea(
        -name=>'input_spectrum',
        -rows=>31,
        -columns=>80,
        -default=>scalar param('input_spectrum') || ''
    );
    print hr;
}

print "\n";
print hidden(-name=>'input_spectrum', -value=>param('input_spectrum'));
print end_form, hr;
