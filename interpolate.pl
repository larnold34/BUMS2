#!/usr/bin/perl


sub interpolate{

use Math::Interpolate qw(linear_interpolate log_linear_interpolate linear_log_interpolate log_log_interpolate);

  my $it = shift;
  return unless defined($it);

  my $en = shift;
  return unless defined($en);

  my $X = shift;
  return unless defined($X);
  return unless ref($X);

  my $Y = shift;
  return unless defined($Y);
  return unless ref($Y);


  my $num_x = @$X;
  my $num_y = @$Y;
  return unless $num_x == $num_y;
  
	if ($en<$X->[0]){
       	 $dfact=$Y->[0];
   	}
   	elsif ($en>=$X->[$num_x-1]){
       	$dfact=$Y->[$num_y-1];
	}
	else{
		if ($it==1){
			$dfact = log_linear_interpolate($en, $X, $Y)
		}
		elsif ($it==2){
			$dfact = linear_interpolate($en, $X, $Y)
		}
		elsif ($it==3){
			$dfact = linear_log_interpolate($en, $X, $Y)
		}
		elsif ($it==4){
			$dfact = log_log_interpolate($en, $X, $Y)
		}
   	 	else{
			print "ERROR - it not valid in sub interpolate\n";
		}
	}
	$dfact;
}
1;
