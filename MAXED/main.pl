#!/usr/bin/perl

require "calcfout.pl";
require "hpsort.pl";
require "maxed.pl";
require "prt.pl";
require "responsel.pl";
require "scalefi.pl";
require "fcn.pl";
require "lethar.pl";
require "mkebins.pl";
require "mkebins4pd.pl";
require "prtvec.pl";
require "ranmar.pl";
require "rmarin.pl";
require "sa.pl";
require "simann.pl";
require "fillfil.pl";
require "exprep.pl";

#     PROGRAM MAXED
#
#     MAXED, A COMPUTER CODE FOR THE DECONVOLUTION OF MULTISPHERE
#     NEUTRON SPECTROMETER DATA USING THE MAXIMUM ENTROPY METHOD"
#
#     For more information on MAXED, see the report "MAXED, A COMPUTER
#     CODE FOR THE DECONVOLUTION OF MULTISPHERE NEUTRON SPECTROMETER
#     DATA USING THE MAXIMUM ENTROPY METHOD", Technical Report EML-595,
#     U.S. Department of Energy, New York,NY (1998).  This report can be
#     downloaded from the EML website at http://www.eml.doe.gov, or it
#     can be obtained directly from one of the authors by e-mailing a
#     request to Marcel Reginatto (mreg@eml.doe.gov) or Paul Goldhagen
#     (goldhagn@eml.doe.gov).
#
#     Revised on 5/19/98
#     lf90 maxed -fix -vax -dbl -o3 -bind
#
#     DISCLAIMER
#     "This report was prepared as an account of work sponsored by an
#     agency of the United States Government.  Neither the United States
#     Government nor any agency thereof, nor any of their employees,
#     makes any warranty, express or implied, or assumes any legal
#     liability or responsibility for the accuracy, completeness, or
#     usefulness of any information, apparatus, product, or process
#     disclosed, or represents that its use would not infringe privately
#     owned rights.  Reference herein to any specific commercial
#     product, process, or service by trade name, trademark,
#     manufacturer, or otherwise, does not necessarily constitute or
#     imply its endorsement, recommendation, or favoring by the United
#     States Government or any agency thereof.  The views and opinions
#     of authors expressed herein do not necessarily state or reflect
#     those of the United States Government or any agency thereof."
#
my $MP,$NI,$I,$K,$L,$MMM,$NMAX,$N0M1,$N1,$NB1,$IQ,$ISCF,$KMAX,$IQDS,$IQBS;
my $C1,$CZ,$C2,$C3,$MINMAX,$MAXMIN,$SCF,$FSCF;
my @RFN,@E,@FIL,@FOUT,@FL,@FBDS,@FBDSL,@ENBR,@ENBZKL,@ZKL,@ENB0,@ENBF;
my @FBRF,@FBRFL,@EDSP,@RES,@B,@LAMBDA,$DH,$EBH,$EH,$UNITS;
my @DUMMY,$DUMMY;

local ($S,$D,$FI,$MM,$FLUX,$OMEGA,$N,$N0,$MP1);

#      COMMON S,D,FI,MM,FLUX,OMEGA,NB,M,N,N0,MP1  

#      print " NAME OF FILE WITH INPUT DATA? :",br;
      $DH="input.csv";
#      print *,' NAME OF FILE WITH RESPONSE FUNCTION? : '
      $EBH="Rf.csv";
#      print *,' NAME OF OUTPUT FILE? (USE 8 CHARACTERS OR LESS) : '
      $EH="out";
#
#     Read in the input data from the files DH and EBH
#     (1) M is the number of measurements.
#     (2) N0 is the number of energy bin edges used for the default
#         spectrum.
#     (3) The RFN are the detector numbers.
#     (4) The D(I) are the measured data.
#     (5) The S(I) are the errors assigned to each measurement.  
#     (6) The ENBZKL(K) are the energy bin edges of the default
#     spectrum, and the ZKL(K) the values of the default spectrum.
#     ZKL(K) is the value of the default spectrum of the bin that is
#     bounded by bin edges ENBZKL(K1) and ENBZKL(K+1).  There are N0
#     energy bins, and N0-1 values of ZKL(K).  The program reads in an
#     extra value of ZKL(K), the last one (which is ZKL(N0)).  This
#     value is not used by the program, and ZKL(N0) is usually set to
#     zero in the input file.
#     (7) MMM is the number of detectors in the response function file. 
#     (8) N1 is the number of energy bin edges used in the calculation
#     of the response function.
#     (9) UNITS are the units of the response function.
#     (10) The ENBR(L) are energy bin edges of the response function.
#     (11) The RES(K,L) are the values of the response function.
#
    open(DH,"$DH");
		$input=<DH>;
		($M,$N0)=split(/,/,$input);
		chomp($N0);

	for($I=1;$I<$M+1;$I++){
		$input=<DH>;
		($RFN[$I],$D[$I],$S[$I])=split(/,/,$input);
		chomp($S[$I]);
	}

	for($K=1;$K<$N0+1;$K++){
		$input=<DH>;
		($ENBZKL[$K],$ZKL[$K])=split(/,/,$input);
		chomp($ZKL[$K]);
	}
	close(DH);      

#
#      print *,' FORM OF THE DEFAULT SPECTRUM? (1, 2, OR 3) : '
#      print *,' 1: (n fluence rate per bin)/(width of bin in E(MeV)) '
#      print *,'     ~ dPHI/dE '
#      print *,' 2: (n fluence rate per bin)/(width of bin in ln(E/MeV))'
#      print *,'     ~ dPHI/dL ~ E*dPHI/dE  '
#      print *,' 3: (n fluence rate per bin)'
#      print *,' '
#
	$IQ=1;
	$IQDS = $IQ;
	if ($IQ==1) {
        $KMAX = $N0 - 1;
		for($K=1;$K<$KMAX+1;$K++){
			$ZKL[$K] = $ZKL[$K]*($ENBZKL[$K+1]-$ENBZKL[$K])
		}
	}
	elsif ($IQ==2) {  
		$KMAX = $N0 - 1;
		for($K=1;$K<$KMAX+1;$K++){
			$ZKL[$K] = $ZKL[$K]*(log($ENBZKL[$K+1])-log($ENBZKL[$K]));
		}
	}
#
	open(EBH,"$EBH");
	$MMM=<EBH>;
	chomp($MMM);
	$N1=<EBH>;
	chomp($N1);
	$UNITS=<EBH>;
	chomp($UNITS);
	$NB1 = $N1 - 1;
	$ENBR[1]=<EBH>;
	chomp($ENBR[1]);
	for($L=1;$L<$NB1+1;$L++){
			$input=<EBH>;
			($ENBR[$L+1],$DUMMY)=split(/,/,$input,2);
			chomp($DUMMY);
			@DUMMY=split(/,/,$DUMMY);
		for($K=1;$K<$MMM+1;$K++){
			$RES[$K][$L]=shift @DUMMY;
		}
	}
	close(EBH);
	$DUMMY="";
	@DUMMY=();
#
	$MP1 = $M + 1;
#
#     Create the fine bin structure
#
	$NMAX = $N0 + $N1;
print "Entering MKEBINS\n";
	&MKEBINS(\@ENBZKL,\@ENBR,\@ZKL,\$NMAX,\$N0,\$N1,\@ENB0,\$N);     

	for($K=1;$K<$N+1;$K++){
		$ENBF[$K] = $ENB0[$K];
	}
#
#      print *,' BIN STRUCTURE FOR THE DECONVOLUTION? (0, 1, 2 OR 3) :'
#      print *,' 0 - FINE BIN STRUCTURE ' 
#      print *,' 1 - FOUR BINS PER DECADE '
#      print *,' 2 - BIN STRUCTURE OF THE DEFAULT SPECTRUM '
#      print *,' 3 - BIN STRUCTURE OF THE RESPONSE FUNCTION '
#      print *,' '
#
#     Re-bin to the bin structure chosen for the deconvolution
#
      $IQ=3;
      $IQBS = $IQ;
	if ($IQ== 0) { 
		$NB = $N - 1;       
print "Entering FILLFIL 1 \n";
		&FILLFIL(\@ENBZKL,\@ZKL,\$N,\$N0,\$NB,\@ENBF,\@FI); 
print "Entering RESPONSEL 1\n";
		&RESPONSEL(\@RES,\@RFN,\@B,\@ENBF,\@ENBR,\$M,\$MMM,\$N,\$NB,\$N1,\$NB1);
	}
    elsif ($IQ==1) {
print "Entering MKEBINS4PD 1\n";
		&MKEBINS4PD(\@ENBF,\$N);
		$NB = $N - 1;
print "Entering FILLFIL 2 \n";
		&FILLFIL(\@ENBZKL,\@ZKL,\$N,\$N0,\$NB,\@ENBF,\@FI);
print "Entering RESPONSEL 2\n";
		&RESPONSEL(\@RES,\@RFN,\@B,\@ENBF,\@ENBR,\$M,\$MMM,\$N,\$NB,\$N1,\$NB1);
	}
    elsif ($IQ==2) {
		$N = $N0;
		$NB = $N - 1;
		for ($K=1;$K<$NB+1;$K++){
	  		$ENBF[$K] = $ENBZKL[$K];
	  		$FI[$K] = $ZKL[$K];
		}
		$ENBF[$N] = $ENBZKL[$N];
print "Entering RESPONSEL 3\n";
		&RESPONSEL(\@RES,\@RFN,\@B,\@ENBF,\@ENBR,\$M,\$MMM,\$N,\$NB,\$N1,\$NB1);
	}
    elsif ($IQ==3) {
		$MAXMIN = $ENBZKL[1];
		if ($MAXMIN<$ENBR[1]) {
	  		$MAXMIN = $ENBR[1];
		}
		$MINMAX = $ENBZKL[$N0];
		if ($MINMAX>$ENBR[$N1]) {
	  		$MINMAX = $ENBR[$N1];
		}
		$J = 0;

		for ($K=1;$K<($N1+1);$K++){
	  		if ($ENBR[$K]>= $MAXMIN) {
	    		if ($ENBR[$K]<=$MINMAX) {
	      			$J = $J + 1;
	      			$ENBF[$J] = $ENBR[$K];
	    		}
			}
		}

		$N = $J;
		$NB = $N - 1;
		$N2=$N1+1;
print "Entering FILLFIL 3 \n";
print "N1=$N1\nNB=$NB\n";
		&FILLFIL(\@ENBZKL,\@ZKL,\$N,\$N0,\$NB,\@ENBF,\@FI); 
print "Entering RESPONSEL 4 \n";
		&RESPONSEL(\@RES,\@RFN,\@B,\@ENBF,\@ENBR,\$M,\$MMM,\$N,\$NB,\$N1,\$NB1);
	}
#
#     Find the scale factor that minimizes the chi-square of the
#     default spectrum
#
print "Entering SCALEFI 1 \n";
	$SCF=&SCALEFI(\@D,\@S,\@B,\$M,\$NB,\@FI);
	$FSCF = 1.0;
#
	printf " SCALE FACTOR/DEFAULT SPEC. FOR BEST FIT = %13.7E",$SCF;
	print "\n";
#      print br;                            
	print " DO YOU WANT TO SCALE THE DEFAULT SPEC. ? (YES=1, NO=0) 0";
	print "\n";
#	print br;
	$ISCF=0;
	if ($ISCF==1) {
		$FSCF = $SCF;
		print " DO YOU WANT TO CHANGE THE SCALE FACTOR ? (YES=1, NO=0) 0";
		print "\n";
#		print br; 
		$IQ=0;        
		if ($IQ==1) {
			print " ENTER A VALUE FOR THE SCALE FACTOR : 1";
			print "\n";
#			print br;
			$FSCF=1; 
		}
		for ($K=1;$K<$NB+1;$K++){
			$FI[$K] = $FSCF*$FI[$K];
		}
	}
#
#     Calculate the chi square of the default spectrum.
# 
	$C1 = 0.0;
	for ($I=1;$I<$M+1;$I++){
		$EDSP[$I] = 0.0;
		for ($K=1;$K<$NB+1;$K++){
			$EDSP[$I] = $EDSP[$I]+$B[$I][$K]*$FI[$K];
		}  
		$C1 = $C1+(($D[$I]-$EDSP[$I])**2)/($S[$I]**2);
	}
#
	$CZ = $C1;
#
	print " CHI SQUARE/DEFAULT SPECTRUM  = $CZ";
	print "\n";
#	print br;                          
#
#     Sum the default spectrum over all bins
#
	$FLUX = 0.0;
	for ($K=1;$K<$NB+1;$K++){
		$FLUX = $FLUX + $FI[$K];
	}
	$T=1;
	$RT=0.85;

	for($i=0;$i<$M+1;$i++){
		for ($k=0;$k<$NB;$k++){
			$MM[$NB*($i)+($k+1)] = $B->[$i][$k];
		}
	}
	
print "Entering maxed T=$T\n";
	(*LAMBDA)=&maxed(\$M,\$T,\$RT,\$M,\$NB,\@MM,\@FI,\@S,\@D,\$OMEGA,\$FLUX);

print "Entering CALCFOUT \n";
(*FOUT)=&CALCFOUT(\@LAMBDA);

	$C2 = 0.0;
	for($I=1;$I<$M+1;$I++){
		$E[$I] = 0.0;
		for($K=1;$K<$NB+1;$K++){
			$E[$I] = $E[$I]+$B[$I][$K]*$FOUT[$K];
		}  
		$C2 = $C2+(($D[$I]-$E[$I])**2)/($S[$I]**2);
	}

                                    
	print " CHI SQUARE/MAXIMUM ENTROPY  = $C2",br;
	print "  ",br;                         
	print " TOTAL NEUTRON FLUENCE RATE/DEFAULT SPECTRUM  = $FLUX",br;
	print "  ",br;                         

#     Sum the solution spectrum over all bins

	$FLUX = 0.0;
	for($K=1;$K<$NB+1;$K++){
		$FLUX = $FLUX + $FOUT[$K];
	}

	print " TOTAL NEUTRON FLUENCE RATE/SOLUTION SPECTRUM = $FLUX",br;
	print "  ",br;                       

print "Entering LETHAR \n";
	&LETHAR(\@FI,\@FOUT,\@ENBF,\$N,\$NB,\@FIL,\@FL);


