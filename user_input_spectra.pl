#!/usr/bin/perl
sub user_input{

my $i;
my $j;
my $input;

	$input=param('input_spectrum');
	@input=split(/\n/,$input);

    $j=0;
	@value='';
	@e_end='';
	foreach (@input) {
	   	($e_end[$j],$value[$j])=split(' ',$_); 
		if ($e_end[$j]) { 
  			chomp($value[$j]);
      		$j++;
		} 
	}
	shift @value;
	my $num_bins=$j;

	$spectra_form=param('spectra_form');
	print "spectra form = $spectra_form",br;

	if ($spectra_form=~/1/){
		for($k=0;$k<$num_bins-1;$k++){
			$value[$k]=$value[$k]*($e_end[$k+1]-$e_end[$k])/(log($e_end[$k+1])-log($e_end[$k]));
		}
	}
	elsif ($spectra_form=~/3/){
		for($k=0;$k<$num_bins-1;$k++){
			$value[$k]=$value[$k]/(log($e_end[$k+1])-log($e_end[$k]));
		}
	}

	for ($j=0;$j<($num_bins);$j++){
		$spli[$j]=99;
	}
		
	&rebin($#eend+1,$num_bins,1,\@e_end,\@value,\@eend,\@spli);
	for ($i=0;$i<$#eend;$i++){
	}
	shift @spli;

}
1;
