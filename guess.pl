#!/usr/bin/perl
sub guess{

# This program scans the guesses listed in the spectra directory
#Outline
#_______
# Read spectrum file
# Rebin spectrum to matrix energy bins 
#
my $i;
my $j;

if (param('start_spec') =~ /Automatic/){
	print start_table();
	print start_TR({align=>left});
	print start_th({align=>left}),"Starting Spectra",
	  start_th({align=>left})," ",
	  start_th({align=>left}),"Chi - Squared";
	print end_TR;	
	print start_TR({align=>left});
	print start_td({align=>left}),"----------------",
	  start_td({align=>left})," ",
	  start_td({align=>left}),"-------------";
	print end_TR;	

	$best_error=9E+99;
	&dir_read("spectra");
	for ($i=0;$i<$#file+1;$i++){
		open(SPEC,"spectra/$file[$i]"); 
		$j=0;
		$junk=<SPEC>;
		print start_TR();
		print start_td();
		print "$junk";
	  	print start_td(); print "=";
	
		@value='';
		@e_end='';
		while(<SPEC>){
   			($e_end[$j],$value[$j])=split(/[,\s]/,$_); 
   			chomp($value[$j]);
      		$j++; 
		}
		close(SPEC);	

		for ($j=0;$j<($#eend+1);$j++){
			$spli[$j]=99;
		}
		&rebin($#eend+1,$#e_end+1,1,\@e_end,\@value,\@eend,\@spli);
		shift @spli;

		&trans_mat;
		
		&normalize;
		&cal_response;
		&fit_error;
		$chi=&chi_squared($num_det,\@bce,\@bcc,\@errbce);
	  	print start_td({align=>left});
		printf "%11.3G",$chi;	
		print end_TR;	
		if ($chi<$best_error) {
			$best_error=$chi;
			$best_file=$file[$i];
		}

	}
	print end_table();
	print hr;

}	
else {
	$best_file=param('start_spec')
}
	open(SPEC,"spectra/$best_file"); 
    $j=0;
	$junk=<SPEC>;
	@value='';
	@e_end='';
	while(<SPEC>){
	   	($e_end[$j],$value[$j])=split(/[,\s]/,$_); 
   		chomp($value[$j]);
      	$j++; 
	}
	shift @value;
	close(SPEC);	

	for ($j=0;$j<($#eend+1);$j++){
		$spli[$j]=99;
	}
		
	&rebin($#eend+1,$#e_end+1,1,\@e_end,\@value,\@eend,\@spli);
	shift @spli;

}
1;
