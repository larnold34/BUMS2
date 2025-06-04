#!/usr/bin/perl

$y=2;
$x[1]=1;
print "Main x=$x[1] y=$y\n";

(*j,*k,*l)=&sub1(\@x,\$y,\@z);
print "Main x=$j[1] y=$k z=$l[1]\n";

sub sub1{
	local *v=shift;
	local *u=shift;
	local *w=shift;

	print "Sub 1 x=$v[1] y=$u\n";
	
	$u=11;
	$v[1]=10;
	$w[1]=12;
	$w[2]=13;
	print "Sub 1 x=$v[1] y=$u z=$w[1]\n";
	
	&sub2(\@v,\$u,\@w);

	print "Sub 1 x=$v[1] y=$u z=$w[1]\n";

	return (\@v,\$u,\@w);
}

sub sub2{
	local (*a,*b,*c)=@_;
	
	$a[1]=20;
	$b=21;
	$c[1]=22;
	return;
}
