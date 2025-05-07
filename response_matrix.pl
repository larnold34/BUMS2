# Read in Response matrix 
sub matrix_in{
	local (*matrix_file,*detector_used,*max_energy) =@_;
    my (@matrix,$x,$test,$energy,$num_det_matrix,$i,$num_det);
    my $total_num_det;

	open(MATRIX,"matrix/$matrix_file"); 
	
	$x=0;
	$test=0;
	$junk=<MATRIX>;
	while(<MATRIX>){ 
		if ($_ !~ /^#/) {
			@matrix=split(/[,\s]/,$_); 

			$junk=$#matrix;
			for ($i=0;$i<$junk;$i++){
				if ($matrix[0]!~ /\D+/) { 
					shift @matrix;
				}
				else {
				$i=$junk;
				}
			}

			$energy=$matrix[0];
    		if ($#matrix!=($#detector_used+1)){ 
				print "Response Matrix doesn't match data sent to subroutine matrix_in",br;
				print "# of detectors used = $#detector_used+1 matrix
detectors=$#matrix",br;
				die "Response Matrix doesn't match data sent to subroutine matrix_in";
			}
		
			$num_det_matrix=$#matrix;
			$num_det=0;

			$x++; 
   			$eend[$x-1]=$energy;   

# Fill in response matrix, ball vector, count vector, and error vector
			for ($i=0;$i<$num_det_matrix+1;$i++){
				if ($detector_used[$i] =~ /true/) {
					$num_det++;
       				$mat[$x-1][$num_det-1]=$matrix[$i+1];
				}
				$total_num_det=$num_det;
			}
 
			$num_det_used=$num_det;

			if ($energy<=$max_energy) {
      			$num_energy_bins=$x;
      		}
		}
	} 

    if ($energy<=$max_energy){
		$num_energy_bins--;
	}

# Determine minimum usable energy

	my ($i,$j,$sum);
   	for ($i=1;$i<$num_energy_bins;$i++) {
		$sum=0;
   		for ($j=0;$j<$total_num_det;$j++) {
			$sum=$sum+$mat[$i][$j];
		}
		if ($sum==0){
			$num_energy_bins=$i-1;
		}
	}
	
	return (\@mat,\@eend,\$num_energy_bins);
}
1;
