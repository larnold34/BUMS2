#!/usr/bin/perl
use strict;
use warnings;

# These globals must already have been declared in your CLI driver:
our $start_spec;    # from param('start_spec')
our @file;          # filled by dir_read("spectra")
our $best_error;
our $best_file;
our @eend;          # matrix endpoints from matrix_in
our @spli;          # rebinned output spectrum (what’s usually all zeros)
our $num_det;       # number of detectors
our @bce;           # measured counts
our @bcc;           # calculated counts
our @errbce;        # measure errors

sub guess_cli {
    my ($i, $j, $junk);

    # If “Automatic” was selected, compare all spectra/*.txt
    if ($start_spec =~ /Automatic/) {
        print "Starting Spectra      Chi - Squared\n";
        print "---------------       -----------\n";

        $best_error = 9E+99;
        &dir_read("spectra");   # assumes this populates @file

        for ($i = 0; $i <= $#file; $i++) {
            open my $spec_fh, '<', "spectra/$file[$i]"
              or next;           # skip if cannot open
            $j    = 0;
            $junk = <$spec_fh>;  # first line = name or header
            chomp $junk;
            print "$junk    ";    # print name, leave gap for chi

            # Read user‐spectrum into @e_end_in and @value_in
            my (@e_end_in, @value_in);
            while (<$spec_fh>) {
                ($e_end_in[$j], $value_in[$j]) = split /[,\s]/;
                chomp $value_in[$j];
                $j++;
            }
            close $spec_fh;

            # Initialize @spli to 99 for each matrix bin
            @spli = map { 99 } 0 .. $#eend;

            # —— DEBUG: print what we read
            # print STDERR "DEBUG: file[$i] => \@e_end_in = (", join(', ', @e_end_in), ")\n";
            # print STDERR "DEBUG: matrix \@eend = (",        join(', ', @eend),     ")\n";

            # Rebin user spectrum (@e_end_in,@value_in) into @spli over @eend
            # The arguments are (n_output_bins, n_input_points, scale_flag, 
            #                     \@input_endpoints, \@input_values, \@matrix_endpoints, \@output_spli)
            &rebin(
                scalar(@eend),       # number of matrix bins  
                scalar(@e_end_in),   # number of input points
                1,                   # (scale_flag—usually “1”)
                \@e_end_in,          # input‐spectrum endpoints
                \@value_in,          # input‐spectrum values
                \@eend,              # matrix endpoints
                \@spli               # OUTPUT: will be overwritten
            );

            shift @spli;

            # —— DEBUG: show @spli right after rebin (before passing it on)
            # print STDERR "DEBUG: after rebin, \@spli = (", join(', ', @spli), ")\n";

            # Run the matrix pipeline on that rebinned spectrum
            &trans_mat;
            &normalize;
            &cal_response;
            &fit_error;

            # Compute chi-squared
            my $chi = &chi_squared($num_det, \@bce, \@bcc, \@errbce);
            printf "%11.3G\n", $chi;

            # Track the best (smallest) chi
            if ($chi < $best_error) {
                $best_error = $chi;
                $best_file  = $file[$i];
            }
        }

        print "-" x 80, "\n";
    }
    else {
        # If user gave a specific filename (not “Automatic”), use it directly
        $best_file = $start_spec;
    }

    # Now re‐load the chosen “best” spectrum:
    open my $spec_fh2, '<', "spectra/$best_file"
      or die "Cannot open spectra/$best_file: $!\n";

    $j    = 0;
    $junk = <$spec_fh2>;  # skip first line (header)
    my (@e_end2, @value2);
    while (<$spec_fh2>) {
        ($e_end2[$j], $value2[$j]) = split /[,\s]/;
        chomp $value2[$j];
        $j++;
    }
    close $spec_fh2;
    shift @value2;  # drop the first “junk” element (if that’s what the original code did)

    # Initialize @spli to 99 for each matrix endpoint
    @spli = map { 99 } 0 .. $#eend;

    # Rebin the chosen spectrum
    &rebin(
        scalar(@eend),     # number of matrix bins
        scalar(@e_end2),   # number of input points
        1,
        \@e_end2,
        \@value2,
        \@eend,
        \@spli
    );
    shift @spli;  # same as above

    # —— DEBUG: to see why @spli might still be all zeros, uncomment:
    #print STDERR "DEBUG (final): chosen '$best_file' => \@spli = (", join(', ', @spli), ")\n";
}

1;
