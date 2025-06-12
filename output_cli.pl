#!/usr/bin/perl
use strict;
use warnings;

use Chart::Graph qw(gnuplot);
use File::Path qw(make_path);
use File::Basename;

# Declare all globals
our $rmtx;
our $unfold;
our $tempm;
our $shape;
our $cal;
our $smo;
our $perror;
our $iter;

our $num_det;
our @ball;
our @bce;
our @bcc;
our @pcterr;

our $start_spec;
our $best_file;

our $sumspc;
our $aveen;
our $sumrem;

our $num_groups;
our @eend;
our @spc;
our @spl;
our @rem;
our @prem;
our @ce;
our @splstart;

sub output_cli {
    my $i;

    # Print the horizontal divider:
    print "-" x 80, "\n";

    # Summary header:
    print "Response    Unfold   Maxwell      Calib.  Smooth   Per Cent    No. of\n";
    print "Matrix       Code   Temp,Shape    Factor  Factor    Error      Iterations\n";
    print "________    ______  ____,_____    ______  ______   ________    __________\n";

    # Main summary line:
    printf "%-5s%13s%6.2f,%-4.2f%10.4f%8.4f%9.4f%12d\n\n",
        $rmtx // "",      # Response Matrix code
        $unfold // "",    # Unfold Code
        $tempm // 0,      # Temperature
        $shape // 0,      # Shape
        $cal   // 0,      # Calib. Factor
        $smo   // 0,      # Smooth Factor
        $perror// 0,      # Percent Error
        $iter  // 0;      # Number of Iterations

    # Detector table header:
    print "Detectors     Measured       Calculated    Percent\n";
    print "              Counts         Counts        Difference\n";
    print "_________     ___________    ____________  __________\n";

    # Loop over each detector and print its line
    for ($i = 0; $i < ($num_det // 0); $i++) {
        printf "%-9s   %12.3f   %12.3f   %10.3f\n",
            ($ball[$i]    // ""),   # Detector name
            ($bce[$i]     // 0),    # Measured counts
            ($bcc[$i]     // 0),    # Calculated counts
            ($pcterr[$i]  // 0);    # Percent difference
    }
    print "\n";

    # Starting spectrum info:
    if (($start_spec // "") =~ /MAXIET/) {
        print "Starting Spectrum      = MAXIET Algorithm\n";
    }
    else {
        if (defined $best_file && -r "spectra/$best_file") {
            open my $INFILE, '<', "spectra/$best_file"
              or die "Cannot open spectra/$best_file: $!\n";
            my $header = <$INFILE>;
            chomp $header;
            close $INFILE;
            print "Starting Spectrum      = $header\n";
        }
        else {
            print "Starting Spectrum      = (none)\n";
        }
    }
    print "\n";

    # Totals and averages:
    printf "Total Fluence          = %11.3e Neutrons/cm2\n", ($sumspc // 0);
    printf "Ave. Energy (Less Th.) = %11.3e MeV\n",            ($aveen // 0);
    printf "Dose Equivalent        = %11.3e REM\n",           ($sumrem // 0);
    print "\n";

    # Group‐by‐group bin table header:
    print "BIN  ENERGY      FLUENCE     FLUENCE     DOSE EQV.   DOSE EQV.\n";
    print "No.  Max (MeV)   NEUT/CM2    N/CM2/LETH  (REM)       (% of Total)\n";

    # Print each group’s data:
    for ($i = 0; $i < ($num_groups // 0); $i++) {
        printf "%-4d %11.3e %11.3e %11.3e %11.3e %11.3e\n",
            $i,
            ($eend[$i+1]  // 0),  # ENERGY Max (MeV)
            ($spc[$i]     // 0),  # FLUENCE NEUT/CM2
            ($spl[$i]     // 0),  # FLUENCE N/CM2/LETH
            ($rem[$i]     // 0),  # DOSE EQV. (REM)
            ($prem[$i]    // 0);  # DOSE EQV. (% of Total)
    }
    print "\n\n";

    # Plot spectras
    _make_plot();

    my $out_dir = "/usr/lib/cgi-bin/OUTPUT";
    make_path($out_dir) unless -d $out_dir;

    my $dat     = "$out_dir/for_detector_response.dat";


    open my $DF, '>', $dat
        or die "Cannot write $dat: $!\n";

    for my $j (0 .. $num_groups - 1) {
        my $cev  = $ce[$j];
        my $flux = $spc[$j] // 0;
        printf $DF "%e %e\n", $cev, $flux;
    }
    close $DF;


    # Call the detector script, redirecting STDIN
    open my $DR, '-|', "perl /usr/lib/cgi-bin/detector_response_cli.pl < $dat"
        or die "Can't run detector_response_cli.pl: $!\n";
    open my $OUT, '>', "$out_dir/detector_response.txt" or die $!;
    print $OUT $_ while <$DR>;
    close $DR;
    close $OUT;

    unlink $dat;
    #warn "Wrote detector response to $out_dir/detector_response.txt\n";
}

sub _make_plot {
    # Determine “OUTPUT” directory inside /usr/lib/cgi-bin
    my $out_dir = "/usr/lib/cgi-bin/OUTPUT";
    unless (-d $out_dir) {
        make_path($out_dir) or die "Cannot create $out_dir: $!\n";
    }

    # Build two temporary data files under /usr/lib/cgi-bin/OUTPUT
    my $pid        = $$;
    my $data1_file = "$out_dir/data1.$pid";
    my $data2_file = "$out_dir/data2.$pid";
    my $gif_file   = "spectrum.$pid.gif";

    # data1: each line is “eend[i]  spl[i-1]”
    open my $D1, '>', $data1_file
      or die "Cannot open $data1_file: $!\n";
    {
        print $D1 ($eend[0] // 0), " ", ($spl[0] // 0), "\n";
        for my $i (1 .. ($num_groups // 0)) {
            print $D1 ($eend[$i] // 0), " ", ($spl[$i-1] // 0), "\n";
        }
    }
    close $D1;

    # data2: each line is “eend[i]  splstart[i-1]”
    open my $D2, '>', $data2_file
      or die "Cannot open $data2_file: $!\n";
    {
        print $D2 ($eend[0] // 0), " ", ($splstart[0] // 0), "\n";
        for my $i (1 .. ($num_groups // 0)) {
            print $D2 ($eend[$i] // 0), " ", ($splstart[$i-1] // 0), "\n";
        }
    }
    close $D2;

    # Chart::Graph’s gnuplot() to generate the GIF
    my $gif_path = "$out_dir/$gif_file";
    gnuplot(
        {   "title"          => "Bonner Sphere Unfolding",
            "x-axis label"  => "Neutron Energy (MeV)",
            "y-axis label"  => "Neutron Flux per Unit Lethargy (n/cm²/lethargy)",
            "logscale x"    => "1",
            "logscale y"    => "1",
            "output file"   => $gif_path,
        },
        [ { "title" => "Unfolded Spectrum",
            "style" => "fsteps",
            "type"  => "file"
          },
          $data1_file
        ],
        [ { "title" => "Starting Spectrum",
            "style" => "fsteps",
            "type"  => "file"
          },
          $data2_file
        ],
    ) or die "gnuplot() failed: $!\n";
	unlink $data1_file;
	unlink $data2_file;

    # Make the resulting GIF world-readable:
    chmod 0755, $gif_path;
}

1;
