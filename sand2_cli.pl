#!/usr/bin/perl
use strict;
use warnings;
use File::Path qw(make_path);

# Declare globals that sand2_cli expects
our $num_groups;   # from matrix_in
our $num_det;      # number of detectors
our @bce;          # measured counts
our @errbce;       # count errors
our @mat;          # response matrix
our @eend;         # matrix endpoints
our @spli;         # initial spectrum (rebinned)
our @splstart;
our @spl;     
our $itrmax;       # max iterations for SANDII
our $rnorm;        # scale factor result

sub sand2_cli {
    my ($i, $j, $junk);


    # Ensure the “sand2” directory exists before writing files
    unless (-d "sand2") {
        make_path("sand2") or die "Cannot create directory 'sand2': $!\n";
    }

    # Write “sand2/input_data”
    open my $in_fh, '>', "sand2/input_data"
      or die "Cannot open sand2/input_data: $!\n";

    my $total_groups = $num_groups + 1;
    print $in_fh "$num_det,$total_groups\n";

    for ($i = 0; $i < $num_det; $i++) {
        my $ii = $i + 1;
        print $in_fh "$ii,$bce[$i],$errbce[$i]\n";
    }
    for ($i = 0; $i < $num_groups; $i++) {
        print $in_fh "$eend[$i],$spli[$i]\n";
    }
    print $in_fh "$eend[$num_groups],0\n";
    print $in_fh "2,3\n";
    print $in_fh "$itrmax,1,1\n";
    close $in_fh;

    # Write “sand2/response”
    open my $resp_fh, '>', "sand2/response"
      or die "Cannot open sand2/response: $!\n";

    print $resp_fh "$num_det\n";
    print $resp_fh "$total_groups\n";
    print $resp_fh "cm**2\n";
    print $resp_fh "$eend[0]\n";
    for ($i = 1; $i < $num_groups + 1; $i++) {
        print $resp_fh "$eend[$i]";
        for ($j = 0; $j < $num_det; $j++) {
            print $resp_fh ",$mat[$i][$j]";
        }
        print $resp_fh "\n";
    }
    close $resp_fh;

    # Ensure “./tmp/notezy” exists before writing the cleanup script
    my $tmpdir = "./tmp/notezy";
    unless (-d $tmpdir) {
        make_path($tmpdir)
          or die "Cannot create directory '$tmpdir': $!\n";
    }

    # Plain‐text header instead of HTML <pre>
    print "-" x 80, "\n";
    print "DEBUG: launching SAND2\n";
    print "\n";

    chdir "sand2"
      or die "Cannot chdir to sand2: $!\n";

    # Remove old output files if they exist
    system "rm -f OUT.SII OUT.TS2";

    # Run the “sand2” executable; its console output goes to STDOUT
    print `/usr/local/bin/sand2`;
    print "\n";

    # Allow sand2 time to write its files
    sleep 5;

    # Read “OUT.SII” for the new spectrum
    open my $in_sii, '<', "OUT.SII"
      or die "Cannot open sand2/OUT.SII: $!\n";

    # Skip the first two header lines
    $junk = <$in_sii>;
    $junk = <$in_sii>;

    for ($i = 0; $i < $num_groups; $i++) {
        $junk = <$in_sii>;
        my @fields = split ' ', $junk;
        $splstart[$i] = $fields[3];
        $spl[$i] = $fields[4];
    }
    close $in_sii;

    # Clean up output files
    system "rm -f OUT.SII OUT.TS2";
    chdir ".."
      or die "Cannot chdir back to parent: $!\n";
}

1;
