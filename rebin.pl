#!/usr/bin/perl
sub rebin{

# usage rebin(# new energy bins, # old energy bins, binning parameter, 
#             old energy bins, old values,new energy bins)
#
# new_values are returned.
#              
# Taken from MAXED fillfil subroutine
#______________________________________________________________
 
# Program is to rebin data into a given energy structure.
	my $num_new_bins=shift;
	my $num_old_bins=shift;
	my $bin_para=shift;
	my $old_bin=shift;
	my $old_value=shift;
	my $new_bin=shift;
	local *new_value=shift;

	my $minmax,$maxmin;


# ----------------------------------------------
# Choose range of new bin values
# Example:
# new bins            [ * * 3 4 5 6 7 8 9 ]
# old bins            [ 1 2 3 4 5 6 7 * * ]
# new bin value range [ * * 3 4 5 6 7 * * ]

	if ( ($old_bin->[0]) < ($new_bin->[0]) ) {
		$maxmin=$new_bin->[0];
	}
	else {
		$maxmin=$old_bin->[0];
	}

	if (($old_bin->[$num_old_bins-1]) > ($new_bin->[$num_new_bins-1]) ){
		$minmax=$new_bin->[$num_new_bins-1];
	}
	else {
		$minmax=$old_bin->[$num_old_bins-1];
	}
# ------------------------------------------------	

	my $k,
	my $j;
	my @re_bin;
#	$re_bin[$j] = new set of bins for new set of values excluding 0.0 values.
# Example:
# new bins            [ * * 3 4 5 6 7 8 9 ]
# maxmin              [ * * 3 * * * * * * ]
# minmax              [ * * * * * * 7 * * ]
# re bins             [ * * 3 4 5 6 7 * * ]
	$j=0;
	for ($k=0;$k<$num_new_bins;$k++) {
		if ( (($new_bin->[$k]) >= $maxmin) && (($new_bin->[$k])<=$minmax) ) {
			$re_bin[$j]=$new_bin->[$k];
			$j=$j+1;
		}
	}
	my $jsave=$j;
# ------------------------------------------------	

	my @inter_value;

	my @l,$r1,$r2,@inter_value;
	for ($k=0;$k<$num_old_bins-1;$k++) {
		for ($l=0;$l<$j-1;$l++) {
			$r2=log($re_bin[$l+1])-log($re_bin[$l]);
			if ($re_bin[$l] <= $old_bin->[$k]) {
				if ($re_bin[$l+1] > $old_bin->[$k]) {
					if ($re_bin[$l+1] >= $old_bin->[$k+1]) {
						$r1=log($old_bin->[$k+1])-log($old_bin->[$k]);
					}	
					else {
						$r1=log($re_bin[$l+1])-log($old_bin->[$k]);
					}	
					$inter_value[$l]=$inter_value[$l] + $old_value->[$k]*($r1/$r2);
				}
			}
			else {
				if ($re_bin[$l] < $old_bin->[$k+1]) {
					if ($re_bin[$l+1] <= $old_bin->[$k+1]) {
						$r1=log($re_bin[$l+1])-log($re_bin[$l]);
					}	
					else {
						$r1=log($old_bin->[$k+1])-log($re_bin[$l]);
					}	
					$inter_value[$l]=$inter_value[$l] + $old_value->[$k]*($r1/$r2);
				}
			}			
		}
	}

	$j=0;
	for ($k=0;$k<$num_new_bins-1;$k++) {
		if ( (($new_bin->[$k]) >= $maxmin) && (($new_bin->[$k])<=$minmax) && $j<=$jsave-2 ) {
			$new_value[$k]=$inter_value[$j];
			$j=$j+1;
		}
		else {
			$new_value[$k]=0;
		}
	}

	return;
}
1;
