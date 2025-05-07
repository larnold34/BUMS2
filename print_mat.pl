#!/usr/bin/perl
sub print_mat {
	for ($i=0;$i<($num_groups);$i++){
		print "$i,  $eend[$i], $mat[$i][3]\n",br;
	}
}
1;
