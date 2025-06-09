#!/usr/bin/perl
use File::Path qw(make_path);
sub maxed_cli{
#               BEGINNING OF MAXED UNFOLDING ALGORITHM      
	my $j;
	my $i;
	my $k;
	my $m;
	my $junk;

# Write output file "input_data"

    open my $out1, ">", "maxed_data/input_data"
      or die "Cannot open maxed_data/input_data: $!\n";

    my $total_groups = $num_groups + 1;
    print $out1 "$num_det,$total_groups\n";

    for ($i = 0; $i < $num_det; $i++) {
        my $ii = $i + 1;
        print $out1 "$ii,$bce[$i],$errbce[$i]\n";
    }
    for ($i = 0; $i < $num_groups; $i++) {
        print $out1 "$eend[$i],$spli[$i]\n";
    }
    print $out1 "$eend[$num_groups],0\n";
    print $out1 "2,3\n";
    print $out1 "1,0.85\n";
    close $out1;

# Write output file "response_function"

	open my $out2, ">", "maxed_data/response"
      or die "Cannot open maxed_data/response: $!\n";

    print $out2 "$num_det\n";
    print $out2 "$total_groups\n";
    print $out2 "cm**2\n";
    print $out2 "$eend[0]\n";
    for ($i = 1; $i < $num_groups + 1; $i++) {
        print $out2 "$eend[$i]";
        for ($j = 0; $j < $num_det; $j++) {
            print $out2 ",$mat[$i][$j]";
        }
        print $out2 "\n";
    }
    close $out2;

    system "killall -9 sand2";
    system "killall -9 maxed";

	my $tmpdir = "./tmp/notezy";
    unless (-d $tmpdir) {
        make_path($tmpdir)
          or die "Cannot create directory '$tmpdir': $!\n";
    }

    my $rm_file = "./tmp/notezy/rm.$$";
    open my $rmfh, ">", $rm_file
      or die "Cannot open $rm_file: $!\n";
    print $rmfh "killall -9 maxed\n";
    print $rmfh "rm $rm_file\n";
    close $rmfh;

    print `at -f $rm_file now + 15 minutes`;

	print "-" x 80, "\n";
    # print "DEBUG: launching MAXED\n";

    chdir "maxed_data"
      or die "Cannot chdir to maxed_data: $!\n";

    # Remove any previous outputs
    system "rm -f OUT.OUT OUT.TBL";

    # Run the actual maxed binary (its own console output will include newlines)
    print `/usr/local/bin/maxed`;
    print "\n";

	# Allow maxed time to write its files
    sleep 5;

	open my $in, "<", "OUT.OUT"
      or die "Cannot open maxed_data/OUT.OUT: $!\n";

    # Skip first two header lines
    $junk = <$in>;
    $junk = <$in>;

    for ($i = 0; $i < $num_groups; $i++) {
        $junk = <$in>;
        my @data = split ' ', $junk;
        $spl[$i]      = $data[4];
        $splstart[$i] = $data[3];
    }
    close $in;

    system "rm -f OUT.OUT OUT.TBL";
    chdir ".."
      or die "Cannot chdir back to parent: $!\n";
}

1;
