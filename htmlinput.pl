#!/usr/bin/perl
sub htmlinput{

# Read in variables

$rmtx=param('matrix');
$unfold=param('alg');
$tstper=param('endtesterror');
$smo=param('smoothing');
$cal=param('cal_factor');
$itrtst=param('itertesterror');
$itrmax=param('iter');
$tempij=param('tempij');
$shape=param('shape');
$pertmp=param('perturbation');
$matrix_file=param('matrix');
$max_energy=param('max_energy');



$use_det_bare=param('bare');
$use_det_barecd=param('barecd');
$use_det_2inch=param('2inch');
$use_det_2inchcd=param('2inchcd');
$use_det_3inch=param('3inch');
$use_det_3inchcd=param('3inchcd');
$use_det_5inch=param('5inch');
$use_det_5inchcd=param('5inchcd');
$use_det_8inch=param('8inch');
$use_det_10inch=param('10inch');
$use_det_12inch=param('12inch');
$use_det_15inch=param('15inch');
$use_det_18inch=param('18inch');

$count_bare=param('bare_counts');
$count_barecd=param('barecd_counts');
$count_2inch=param('2_inch_counts');
$count_2inchcd=param('2_inch_cd_counts');
$count_3inch=param('3_inch_counts');
$count_3inchcd=param('3_inch_cd_counts');
$count_5inch=param('5_inch_counts');
$count_5inchcd=param('5_inch_cd_counts');
$count_8inch=param('8_inch_counts');
$count_10inch=param('10_inch_counts');
$count_12inch=param('12_inch_counts');
$count_15inch=param('15_inch_counts');
$count_18inch=param('18_inch_counts');

$count_error_bare=param('bare_counts_error');
$count_error_barecd=param('barecd_counts_error');
$count_error_2inch=param('2_inch_counts_error');
$count_error_2inchcd=param('2_inch_cd_counts_error');
$count_error_3inch=param('3_inch_counts_error');
$count_error_3inchcd=param('3_inch_cd_counts_error');
$count_error_5inch=param('5_inch_counts_error');
$count_error_5inchcd=param('5_inch_cd_counts_error');
$count_error_8inch=param('8_inch_counts_error');
$count_error_10inch=param('10_inch_counts_error');
$count_error_12inch=param('12_inch_counts_error');
$count_error_15inch=param('15_inch_counts_error');
$count_error_18inch=param('18_inch_counts_error');



}
1;
