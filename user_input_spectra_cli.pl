#!/usr/bin/perl
use strict;
use warnings;
use CGI qw(param);

# All the variables
our(@spli, @eend);


sub user_input_cli{
    my (@e_end, @value);

    # On CLI, will prompt to enter a file path to the spectrum of interest

        print STDERR "\n*** Enter path to your custom spectrum file ***\n";
        print STDERR "Spectrum file path: ";
        chomp(my $spec_path = <STDIN> // '');
        die "No path provided, aborting\n" unless $spec_path;

        open my $fh, '<', $spec_path
          or die "Cannot open spectrum file '$spec_path': $!\n";

        while (my $line = <$fh>) {
            chomp $line;
            next if $line =~ /^\s*$/;   # skip blank lines
            next if $line =~ /^\s*#/;   # skip comments
            my ($e, $v) = split ' ', $line, 2;
            next unless defined $e;
            push @e_end, $e;
            push @value, defined $v ? $v : 0;
        }
        close $fh;
    
	shift @value;
	my $num_bins = scalar @e_end;

    # Rebin as in the initial user_input
    @spli = (99) x scalar @e_end;
    rebin(
        scalar(@eend),     # # of target groups
        $num_bins,    # # of input bins
        1,                 # “order” argument
        \@e_end,           # input bin edges
        \@value,           # input values
        \@eend,            # global target edges
        \@spli             # OUTPUT array
    );
    shift @spli;
}

1;