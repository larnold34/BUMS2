#!/usr/bin/perl  

sub plot{

use Chart::Graph qw(gnuplot);
$Chart::Graph::debug = 0; 

mkdir ("/var/www/html/tmp", 0755);
mkdir ("/var/www/html/tmp/notezy", 0755);

$data1_file="/var/www/html/tmp/notezy/data1.$$";
$data2_file="/var/www/html/tmp/notezy/data2.$$";
$gif_file="gif_file$$.gif";

open(OUT,">$data1_file");
		print OUT "$eend[$0] $spl[0]\n";
	for ($i=1;$i<$num_groups+1;$i++){
		print OUT "$eend[$i] $spl[$i-1] \n";
   }
close(OUT);

open(OUT,">$data2_file");
		print OUT "$eend[$0] $splstart[0]\n";
	for ($i=1;$i<$num_groups+1;$i++){
		print OUT "$eend[$i] $splstart[$i-1]\n";
   }
close(OUT);


    gnuplot({"title" => "Bonner Sphere Unfolding",
             "x-axis label" =>"Neutron Energy (MeV)",
             "y-axis label" =>"Neutron Flux per Unit Lethergy (n/cm2/lethargy)",
             "logscale x" => "1",
             "logscale y" => "1",
             "output file" => "/var/www/html/tmp/notezy/$gif_file"},
				[{"title" => "Unfolded Spectrum", 
	      	"style" => "fsteps",
	      	"type" => "file"},
				"$data1_file"], 
				[{"title" => "Starting Spectrum", 
	      	"style" => "fsteps",
	      	"type" => "file"},
				"$data2_file"],) ;

# print `rm $data1_file`;
# print `rm $data2_file`;
chmod (0755, "/var/www/html/tmp/notezy/$gif_file");
}
1;

