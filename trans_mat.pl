#!/usr/bin/perl
sub trans_mat{
#                           transform matrix to constant initial spectrum
my $i;
my $k;

for ($i=0;$i<$num_groups;$i++){
	for ($k=0;$k<$num_det;$k++){
  		$alethnew[$k][$i]=$aleth[$k][$i]*$spli[$i];

	}
}

for ($i=0;$i<$num_groups;$i++){
	$spl[$i]=1;
} 
}
1;
