#!/usr/bin/perl

sub RANMAR {
	local *U=shift;
	local *C=shift;
	local *CD=shift;
	local *CM=shift;
	local *I97=shift;
	local *J97=shift;

#	print "U(I97)=$U[$I97] U(J97)=$U[$J97] C=$C CD=$CD CM=$CM I97=$I97 J97=$J97\n";

	$uni = $U[$I97] - $U[$J97];
	if($uni<0.0) {$uni = $uni + 1.0;}
	$U[$I97] = $uni;
	$I97 = $I97 - 1;
	if($I97==0) {$I97 = 97;}
	$J97 = $J97 - 1;
	if($J97==0) {$J97 = 97;}
	$C = $C - $CD;
	if($C<0.0) {$C = $C + $CM;}
	$uni = $uni - $C;
	if($uni<0.0) {$uni = $uni + 1.0;}

#	print "UNI = $uni\n";

	return $uni;
}
1;
