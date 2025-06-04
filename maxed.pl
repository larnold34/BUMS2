#!/usr/bin/perl
sub maxed{
#               BEGINNING OF MAXED UNFOLDING ALGORITHM      
	my $j;
	my $i;
	my $k;
	my $m;
	my $junk;

# Write output file "input_data"

	open(DATA,">maxed_data/input_data");

	my $total_groups=$num_groups+1;
	print DATA "$num_det,$total_groups\n";

	for($i=0;$i<$num_det;$i++){
		my $ii=$i+1;
		print DATA "$ii,$bce[$i],$errbce[$i]\n";
	}
	for($i=0;$i<$num_groups;$i++){
		print DATA "$eend[$i],$spli[$i]\n";
	}
	print DATA "$eend[$num_groups],0\n";
	print DATA "2,3\n";
	print DATA "1,0.85\n";
	close DATA;

# Write output file "response_function"

	open(DATA,">maxed_data/response");
	print DATA "$num_det\n";
	print DATA "$total_groups\n";
	print DATA "cm**2\n";
	print DATA "$eend[0]\n";
	for($i=1;$i<$num_groups+1;$i++){
		print DATA "$eend[$i]";
		for($j=0;$j<$num_det;$j++){
			print DATA ",$mat[$i][$j]";
		}
		print DATA "\n";
	}
	close DATA;

	system "killall -9 sand2";
	system "killall -9 maxed";
	$rm_file="./tmp/notezy/rm.$$";
	open(OUT,">$rm_file");
	print OUT "killall -9 maxed\n";
    print OUT "rm $rm_file\n";
	close(OUT);
	print `at -f $rm_file now + 15 minutes`;

	print "<pre>";
	chdir "maxed_data";	
	system "rm OUT.OUT";		
	system "rm OUT.TBL";
	print "DEBUG: launching MAXED\n";		
	print  `/usr/local/bin/maxed`;
	print "</pre>";	
	sleep 5;

	open(IN,"OUT.OUT");
	$junk=<IN>;
	$junk=<IN>;
	for($i=0;$i<$num_groups;$i++){
		$junk=<IN>;
		my @data=split(' ',$junk);
		$spl[$i]=$data[4];
		$splstart[$i]=$data[3];
	}
	close IN;
	system "rm OUT.OUT";		
	system "rm OUT.TBL";		
	chdir "..";
}
1;
