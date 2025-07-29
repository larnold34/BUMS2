      PROGRAM MAXED
C
C     MAXED, A COMPUTER CODE FOR THE DECONVOLUTION OF MULTISPHERE
c     NEUTRON SPECTROMETER DATA USING THE MAXIMUM ENTROPY METHOD"
C
C     For more information on MAXED, see the report "MAXED, A COMPUTER
C     CODE FOR THE DECONVOLUTION OF MULTISPHERE NEUTRON SPECTROMETER
C     DATA USING THE MAXIMUM ENTROPY METHOD", Technical Report EML-595,
C     U.S. Department of Energy, New York,NY (1998).  This report can be
C     downloaded from the EML website at http://www.eml.doe.gov, or it
C     can be obtained directly from one of the authors by e-mailing a
C     request to Marcel Reginatto (mreg@eml.doe.gov) or Paul Goldhagen
C     (goldhagn@eml.doe.gov).
C
C     Revised on 5/19/98
C     lf90 maxed -fix -vax -dbl -o3 -bind
C
C     DISCLAIMER
C     "This report was prepared as an account of work sponsored by an
C     agency of the United States Government.  Neither the United States
C     Government nor any agency thereof, nor any of their employees,
C     makes any warranty, express or implied, or assumes any legal
C     liability or responsibility for the accuracy, completeness, or
C     usefulness of any information, apparatus, product, or process
C     disclosed, or represents that its use would not infringe privately
C     owned rights.  Reference herein to any specific commercial
C     product, process, or service by trade name, trademark,
C     manufacturer, or otherwise, does not necessarily constitute or
C     imply its endorsement, recommendation, or favoring by the United
C     States Government or any agency thereof.  The views and opinions
C     of authors expressed herein do not necessarily state or reflect
C     those of the United States Government or any agency thereof."
C
      INTEGER IQ2
      INTEGER MP1,NI,I,K,L,M,MMM,NMAX,N0,N0M1,N1,NB1,N,NB,IQ,ISCF,KMAX
      INTEGER IQDS,IQBS
      REAL C1,CZ,C2,FLUX,OMEGA,C3
      REAL MINMAX, MAXMIN
      REAL SCF,FSCF
      INTEGER RFN(100)      
      REAL D(100),S(100),E(100)
      REAL FI(1000),FIL(1000),FOUT(1000),FL(1000),FBDS(1000),FBDSL(1000)
      REAL ENBR(1000),ENBZKL(1000),ZKL(1000),ENB0(1000),ENBF(1000)
      REAL FBRF(1000),FBRFL(1000)
      REAL MM(10000)
      REAL EDSP(100)
      REAL RES (100,1000)
      REAL B(100,1000)
      REAL LAMBDA(30)
      CHARACTER DH*12, EBH*12, EH*8, UNITS*10
	  DOUBLE PRECISION T,RT,EPS 
      INTEGER MAXEVAL,NT
      COMMON S,D,FI,MM,FLUX,OMEGA,NB,M,N,N0,MP1 
      COMMON /BUMS/ T,RT,EPS,NT

      EPS = 1.0D-6
      NT = 5
      MAXEVAL = 100
C
C     
C            
C      PRINT*,' NAME OF FILE WITH INPUT DATA? : '
C      READ*,DH
      DH='input_data'
c      PRINT*,' NAME OF FILE WITH RESPONSE FUNCTION? : '
C      READ*,EBH
      EBH='response'
c      PRINT*,' NAME OF OUTPUT FILE? (USE 8 CHARACTERS OR LESS) : '
C      READ*,EH
      EH='OUT'
      PRINT*,' '
C
C     Read in the input data from the files DH and EBH
C     (1) M is the number of measurements.
C     (2) N0 is the number of energy bin edges used for the default
C         spectrum.
C     (3) The RFN are the detector numbers.
C     (4) The D(I) are the measured data.
C     (5) The S(I) are the errors assigned to each measurement.  
C     (6) The ENBZKL(K) are the energy bin edges of the default
C     spectrum, and the ZKL(K) the values of the default spectrum.
C     ZKL(K) is the value of the default spectrum of the bin that is
C     bounded by bin edges ENBZKL(K1) and ENBZKL(K+1).  There are N0
C     energy bins, and N0-1 values of ZKL(K).  The program reads in an
C     extra value of ZKL(K), the last one (which is ZKL(N0)).  This
C     value is not used by the program, and ZKL(N0) is usually set to
C     zero in the input file.
C     (7) MMM is the number of detectors in the response function file. 
C     (8) N1 is the number of energy bin edges used in the calculation
C     of the response function.
C     (9) UNITS are the units of the response function.
C     (10) The ENBR(L) are energy bin edges of the response function.
C     (11) The RES(K,L) are the values of the response function.
C
      OPEN (11, FILE=DH, STATUS='OLD')
	READ (11,FMT=*) M,N0
	DO 1 I=1,M
	  READ (11,FMT=*) RFN(I),D(I),S(I)
1       CONTINUE
	DO 2 K=1,N0
	  READ (11,FMT=*) ENBZKL(K),ZKL(K)
2       CONTINUE
      READ (11,FMT=*) IQ,IQ2
      READ (11,FMT=*) T,RT
      CLOSE (11)
C
c      PRINT*,' FORM OF THE DEFAULT SPECTRUM? (1, 2, OR 3) : '
c      PRINT*,' 1: (n fluence rate per bin)/(width of bin in E(MeV)) '
c      PRINT*,'     ~ dPHI/dE '
c      PRINT*,' 2: (n fluence rate per bin)/(width of bin in ln(E/MeV))'
c      PRINT*,'     ~ dPHI/dL ~ E*dPHI/dE  '
c      PRINT*,' 3: (n fluence rate per bin)'
c      PRINT*,' '
C
C      READ*,IQ
      IQDS = IQ
      IF (IQ .EQ. 1) THEN
        KMAX = N0 - 1
        DO 100 K=1,KMAX
          ZKL(K) = ZKL(K)*(ENBZKL(K+1)-ENBZKL(K))
100     CONTINUE
      ELSE IF (IQ .EQ. 2) THEN 
        KMAX = N0 - 1
        DO 102 K=1,KMAX
          ZKL(K) = ZKL(K)*(LOG(ENBZKL(K+1))-LOG(ENBZKL(K)))
102     CONTINUE
      END IF
C
      OPEN (12, FILE=EBH, STATUS='OLD')
	READ (12,FMT=*) MMM  
	READ (12,FMT=*) N1  
	READ (12,FMT=*) UNITS         
	NB1 = N1 - 1
	READ (12,FMT=*) ENBR(1)
	DO 3 L=1,NB1
	  READ (12,FMT=*) ENBR(L+1),(RES(K,L), K=1,MMM)
3       CONTINUE
      CLOSE (12)         
C
      MP1 = M + 1
C
C     Create the fine bin structure
C
      NMAX = N0 + N1     
      CALL MKEBINS(ENBZKL,ENBR,ZKL,NMAX,N0,N1,ENB0,N)
      DO 5 K=1,N
	ENBF(K) = ENB0(K)
5     CONTINUE
C
c      PRINT*,' BIN STRUCTURE FOR THE DECONVOLUTION? (0, 1, 2 OR 3) :'
c      PRINT*,' 0 - FINE BIN STRUCTURE ' 
c      PRINT*,' 1 - FOUR BINS PER DECADE '
c      PRINT*,' 2 - BIN STRUCTURE OF THE DEFAULT SPECTRUM '
c      PRINT*,' 3 - BIN STRUCTURE OF THE RESPONSE FUNCTION '
c      PRINT*,' '
C
C     Re-bin to the bin structure chosen for the deconvolution
C
C      READ*,IQ
      IQ=IQ2
      IQBS = IQ
      IF (IQ .EQ. 0) THEN 
	NB = N - 1       
	CALL FILLFIL(ENBZKL,ZKL,N,N0,NB,ENBF,FI) 
	CALL RESPONSEL(RES,RFN,B,ENBF,ENBR,M,MMM,N,NB,N1,NB1)
      ELSE IF (IQ .EQ. 1) THEN
	CALL MKEBINS4PD(ENBF,N)
	NB = N - 1
	CALL FILLFIL(ENBZKL,ZKL,N,N0,NB,ENBF,FI) 
	CALL RESPONSEL(RES,RFN,B,ENBF,ENBR,M,MMM,N,NB,N1,NB1)
      ELSE IF (IQ .EQ. 2) THEN
	N = N0
	NB = N - 1
	DO 6 K=1,NB
	  ENBF(K) = ENBZKL(K)
	  FI(K) = ZKL(K)
6       CONTINUE
	ENBF(N) = ENBZKL(N)
	CALL RESPONSEL(RES,RFN,B,ENBF,ENBR,M,MMM,N,NB,N1,NB1)
      ELSE IF (IQ .EQ. 3) THEN
	MAXMIN = ENBZKL(1)
	IF (MAXMIN .LT. ENBR(1)) THEN
	  MAXMIN = ENBR(1)
	END IF
	MINMAX = ENBZKL(N0)
	IF (MINMAX .GT. ENBR(N1)) THEN
	  MINMAX = ENBR(N1)
	END IF
	J = 0
	DO 7 K=1,N1
	  IF (ENBR(K) .GE. MAXMIN) THEN
	    IF (ENBR(K) .LE. MINMAX) THEN
	      J = J + 1
	      ENBF(J) = ENBR(K)
	    END IF
	  END IF
7       CONTINUE
	N = J
	NB = N - 1
	CALL FILLFIL(ENBZKL,ZKL,N,N0,NB,ENBF,FI) 
	CALL RESPONSEL(RES,RFN,B,ENBF,ENBR,M,MMM,N,NB,N1,NB1)
      END IF
C
C     Find the scale factor that minimizes the chi-square of the
C     default spectrum
C
      CALL SCALEFI(D,S,B,M,NB,FI,SCF)
      FSCF = 1.0
C
c      PRINT*,' SCALE FACTOR/DEFAULT SPEC. FOR BEST FIT = ',SCF
c      PRINT*,' '                            
C      PRINT*,' DO YOU WANT TO SCALE THE DEFAULT SPEC. ? (YES=1, NO=0) '
C      PRINT*,' '
C      READ*,ISCF
      ISCF=1
      IF (ISCF .EQ. 1) THEN
        FSCF = SCF
c        PRINT*,' DO YOU WANT TO CHANGE THE SCALE FACTOR ? (YES=1, NO=0)'
c        PRINT*,' '
C        READ*,IQ        
        IQ=0
c        IF (IQ .EQ. 1) THEN
c          PRINT*,' ENTER A VALUE FOR THE SCALE FACTOR : '
c          PRINT*,' '
c          READ*,FSCF 
c        END IF
        DO 8 K=1,NB
          FI(K) = FSCF*FI(K)
8       CONTINUE
      END IF
C
C     Calculate the chi square of the default spectrum.
C 
      C1 = 0.0
      DO 11 I=1,M
        EDSP(I) = 0.0
        DO 9 K=1,NB
          EDSP(I) = EDSP(I)+B(I,K)*FI(K)  
9       CONTINUE
        C1 = C1+((D(I)-EDSP(I))**2)/(S(I)**2)
11    CONTINUE
C
      CZ = C1
C
      PRINT*,' CHI SQUARE/DEFAULT SPECTRUM  = ',CZ
      PRINT*,' '                          
C
C     Sum the default spectrum over all bins
C
      FLUX = 0.0
      DO 12 K=1,NB
	FLUX = FLUX + FI(K)
12    CONTINUE
C
C     Start the maximum entropy deconvolution
C
      OMEGA = FLOAT(M)
C
      DO 19 I=1,M
	DO 18 K=1,NB
	   MM(NB*(I-1)+K) = B(I,K)
18      CONTINUE
19    CONTINUE
C
c      PRINT*,' CALLING MINIMIZATION SUBROUTINE SIMANN'
c      PRINT*,' '
      CALL SIMANN(M,LAMBDA,MAXEVAL)
C
      PRINT*,' CURRENT VALUES OF LAMBDAS: '
      DO 62 I=1,M
	PRINT*, I, LAMBDA(I)
62    CONTINUE
      PRINT*,' '    
C
C     Calculate the solution spectrum and its chi-square
C
      CALL CALCFOUT(LAMBDA,FOUT)
C
      C2 = 0.0
      DO 66 I=1,M
	E(I) = 0.0
	DO 64 K=1,NB
	  E(I) = E(I)+B(I,K)*FOUT(K)  
64      CONTINUE
	C2 = C2+((D(I)-E(I))**2)/(S(I)**2)
66    CONTINUE
C                                    
      PRINT*,' CHI SQUARE/MAXIMUM ENTROPY  = ',C2
      PRINT*,' '                         
C
      PRINT*,' TOTAL NEUTRON FLUENCE RATE/DEFAULT SPECTRUM  = ',FLUX
      PRINT*,' '                         
C
C     Sum the solution spectrum over all bins
C
      FLUX = 0.0
      DO 68 K=1,NB
	FLUX = FLUX + FOUT(K)
68    CONTINUE
C
      PRINT*,' TOTAL NEUTRON FLUENCE RATE/SOLUTION SPECTRUM = ',FLUX
      PRINT*,' '                       
C
      CALL LETHAR(FI,FOUT,ENBF,N,NB,FIL,FL)
C
C     Re-bin the solution spectrum
C
      N0M1 = N0 - 1
      CALL REBINFFL(N0M1,D,S,B,FL,ENBF,ENBZKL,C1,FBDS,FBDSL,M,NB)    
C                 
      PRINT*,' CHI SQUARE AFTER REBINNING TO THE BIN STRUCTURE OF THE '
      PRINT*,' DEFAULT SPECTRUM            = ',C1
      PRINT*,' '
C
      CALL REBINFFL(NB1,D,S,B,FL,ENBF,ENBR,C3,FBRF,FBRFL,M,NB)    
C                 
      PRINT*,' CHI SQUARE AFTER REBINNING TO THE BIN STRUCTURE OF THE '
      PRINT*,' RESPONSE FUNCTION           = ',C3
      PRINT*,' '
C
      CALL OUTPUT(D,S,E,EH,ENBF,FI,FOUT,FIL,FL,FBDSL,FBRFL,CZ,C1,UNITS,
     $ LAMBDA,DH,EBH,C2,NI,M,NB,MP1,RFN,EDSP,ISCF,SCF,FSCF,C3,IQDS,IQBS)
C
C     The SAND-II option:
C
c      PRINT*,' DO YOU WANT TO RUN THE SAND-II ALGORITHM? (YES=1, NO=0)'
c      READ*,IQ
      IQ=0
      IF (IQ .EQ. 1) THEN
        CALL SAND2(M,N,NB,N0,N1,D,S,FI,B,ENBF,ENBZKL,ENBR,RFN,EH,DH,SCF
     1,FSCF,IQDS,IQBS,EBH,UNITS,CZ)
      END IF
C                                                                  
      END
C
C     *****************************************************************
C                     
      SUBROUTINE MKEBINS(ENBZKL,ENBR,ZKL,NMAX,N0,N1,ENB0,N)
C
      INTEGER K,N,N0,N1,NMAX
      REAL MAXMIN, MINMAX 
      REAL ENBZKL(*),ENBR(*)
      REAL ZKL(*) ! added for BUMS 2
      REAL SORT(NMAX),ENB0(*)
C      
C     Set ENB0(K)=0.0, fill the array SORT(K) with ENBZKL(K), ENBR(K)
C
      DO 10 K=1,N0
	ENB0(K) = 0.0
	SORT(K) = ENBZKL(K)
10    CONTINUE
      DO 20 K=1,N1
	ENB0(K+N0) = 0.0
	SORT(K+N0) = ENBR(K)
20    CONTINUE
C
C     Use the subroutine HPSORT (taken from "NUMERICAL RECIPES IN 
c     FORTRAN", page 329) to sort the array SORT in ascending order.
C
      CALL HPSORT(NMAX,SORT)
C
C     Find the lowest and highest bin edges common to both sets of
C     energy bins
C
      MAXMIN = ENBZKL(1)
      IF (MAXMIN .LT. ENBR(1)) THEN
	MAXMIN = ENBR(1)
      END IF
C
      MINMAX = ENBZKL(N0)
      IF (MINMAX .GT. ENBR(N1)) THEN
	MINMAX = ENBR(N1)
      END IF
C
C     Fill the array ENB0(K) with those elements of SORT(K) that are:
C     (1) not smaller than than MAXMIN, (2) not larger than MINAMX, and
C     (3) do not repeat. 
C
      ENB0(1) = MAXMIN  
C      
      N = 1
      DO 30 I=1,NMAX
      IF (SORT(I) .GT. MAXMIN) THEN
	IF (SORT(I) .LE. MINMAX) THEN
	  IF (SORT(I) .GT. ENB0(N)) THEN
	    N = N + 1
	    ENB0(N) = SORT(I)
	  END IF
	END IF
      END IF
30    CONTINUE
C
      RETURN
      END
C
C     *****************************************************************
C
      SUBROUTINE MKEBINS4PD(ENBF,N)

      INTEGER N
      DOUBLE PRECISION EMIN,EMAX,EMEV,TPOQ
      REAL ENBF(1000)

C     Note: 10 to the power 0.25 equals 1.778279410

      TPOQ = 1.778279410
      EMEV = 1.3113526E-14

C     Find lowest and highest energy bins

      DO 10 K=1,80
	EMEV = EMEV*TPOQ
	IF (ENBF(N) .GE. EMEV) THEN
	  EMAX = EMEV
	END IF
10    CONTINUE

      DO 20 K=1,80
	EMEV = EMEV/TPOQ
	IF (ENBF(1) .LE. EMEV) THEN
	  EMIN = EMEV
	END IF
20    CONTINUE

C     Fill out the array

      DO 25 I=1,N
	ENBF(I) = 0.0 
25    CONTINUE        

      N = NINT(4.0*LOG10(EMAX/EMIN)) + 1

      ENBF(1) = EMIN
      DO 30 I=2,N
	ENBF(I) = ENBF(I-1)*TPOQ
30    CONTINUE

      RETURN
      END
C
C     *****************************************************************
C
      SUBROUTINE FILLFIL(ENBZKL,ZKL,N,N0,NB,ENBF,FI)
C
      INTEGER K,L,NB,N,N0M1,N0
      REAL R1,R2
      REAL ENBF(1000),ENBZKL(1000)
      REAL FI(1000),FIL(1000),ZKL(1000),ZKLL(1000)
C
      N0M1 = N0 - 1
C
      DO 2 K=1,N
	FIL(K) = 0.0
2     CONTINUE
C
      DO 10 K=1,N0M1
	ZKLL(K) = ZKL(K)/(LOG(ENBZKL(K+1)) - LOG(ENBZKL(K)))  
10    CONTINUE        
C
      DO 60 K=1,N0M1  
	DO 50 L=1,NB
	  R2 = LOG(ENBF(L+1)) - LOG(ENBF(L)) 
	  IF (ENBF(L) .LE. ENBZKL(K)) THEN
	    IF (ENBF(L+1) .GT. ENBZKL(K)) THEN 
	      IF (ENBF(L+1) .GE. ENBZKL(K+1)) THEN
		R1 = LOG(ENBZKL(K+1)) - LOG(ENBZKL(K))
		FIL(L) = FIL(L) + ZKLL(K)*(R1/R2)
	      ELSE IF (ENBF(L+1) .LT. ENBZKL(K+1)) THEN
		R1 = LOG(ENBF(L+1)) - LOG(ENBZKL(K))
		FIL(L) = FIL(L) + ZKLL(K)*(R1/R2)
	      END IF
	    END IF
	  ELSE IF (ENBF(L) .GT. ENBZKL(K)) THEN
	    IF (ENBF(L) .LT. ENBZKL(K+1)) THEN 
	      IF (ENBF(L+1) .LE. ENBZKL(K+1)) THEN
		R1 = LOG(ENBF(L+1)) - LOG(ENBF(L))
		FIL(L) = FIL(L) + ZKLL(K)*(R1/R2)
	      ELSE IF (ENBF(L+1) .GT. ENBZKL(K+1)) THEN
		R1 = LOG(ENBZKL(K+1)) - LOG(ENBF(L))
		FIL(L) = FIL(L) + ZKLL(K)*(R1/R2)
	      END IF
	    END IF         
	  END IF
50      CONTINUE
60    CONTINUE     
C
      DO 80 K=1,NB
	FI(K) = FIL(K)*(LOG(ENBF(K+1)) - LOG(ENBF(K)))  
80    CONTINUE        
C
      RETURN
      END
C
C     *****************************************************************
C
      SUBROUTINE RESPONSEL(RES,RFN,B,ENBF,ENBR,M,MMM,N,NB,N1,NB1)
C
      INTEGER M,N,NB,N1,NB1,MMM
      INTEGER RFN(*)
      REAL RES(100,1000),B(100,1000)
      REAL ENBF(*),ENBR(*)
C
      DO 4 I=1,M
	DO 2 K=1,NB
	  B(I,K) = 0.0
2       CONTINUE
4     CONTINUE
C
      DO 60 K=1,NB1  
	DO 50 L=1,NB
	  R2 = LOG(ENBF(L+1)) - LOG(ENBF(L))   
	  IF (ENBF(L) .LE. ENBR(K)) THEN
	    IF (ENBF(L+1) .GT. ENBR(K)) THEN 
	      IF (ENBF(L+1) .GE. ENBR(K+1)) THEN
		R1 = LOG(ENBR(K+1)) - LOG(ENBR(K))  
		DO 12 I=1,M
		  J = RFN(I)
		  B(I,L) = B(I,L) + RES(J,K)*(R1/R2) 
12              CONTINUE
	      ELSE IF (ENBF(L+1) .LT. ENBR(K+1)) THEN
		R1 = LOG(ENBF(L+1)) - LOG(ENBR(K))
		DO 14 I=1,M
		  J = RFN(I)
		  B(I,L) = B(I,L) + RES(J,K)*(R1/R2)
14              CONTINUE
	      END IF
	    END IF
	  ELSE IF (ENBF(L) .GT. ENBR(K)) THEN
	    IF (ENBF(L) .LT. ENBR(K+1)) THEN 
	      IF (ENBF(L+1) .LE. ENBR(K+1)) THEN
		R1 = LOG(ENBF(L+1)) - LOG(ENBF(L))
		DO 16 I=1,M
		  J = RFN(I)
		  B(I,L) = B(I,L) + RES(J,K)*(R1/R2)
16              CONTINUE
	      ELSE IF (ENBF(L+1) .GT. ENBR(K+1)) THEN
		R1 = LOG(ENBR(K+1)) - LOG(ENBF(L))
		DO 18 I=1,M
		  J = RFN(I)
		  B(I,L) = B(I,L) + RES(J,K)*(R1/R2)
18              CONTINUE
	      END IF
	    END IF         
	  END IF
50      CONTINUE
60    CONTINUE     
C
      RETURN
      END
C
C     *****************************************************************
C                     
      SUBROUTINE SCALEFI(D,S,B,M,NB,FI,SCF)
C
      INTEGER I,K,M,NB
      REAL SUM1, SUM2, SCF
      REAL D(*),S(*),EIG(M),B(100,100),FI(*)
C
C     Convolve the default spectrum with the response functions
C
      DO 30 I=1,M
	EIG(I) = 0
	DO 20 K=1,NB
	  EIG(I) = EIG(I) + B(I,K)*FI(K) 
20      CONTINUE
30    CONTINUE
C
C     Scale the default spectrum so that the chi-square is a minimum
C
      SUM1 = 0.0
      SUM2 = 0.0
      DO 40 I=1,M
	SUM1 = SUM1 + (D(I)*EIG(I))/(S(I)**2)
	SUM2 = SUM2 + (EIG(I)**2)/(S(I)**2)
40    CONTINUE
C
      SCF = SUM1/SUM2
C
      RETURN
      END
C
C     *****************************************************************
C
      SUBROUTINE LETHAR(FI,FOUT,ENBF,N,NB,FIL,FL) 
C
      INTEGER K,NB,N
      REAL Z
      REAL FI(*),FOUT(*),ENBF(*),FIL(*),FL(*)
C
      DO 10 K=1,NB
	Z = LOG(ENBF(K+1)) - LOG(ENBF(K)) 
	FIL(K) = FI(K)/Z
	FL(K) = FOUT(K)/Z    
10    CONTINUE        
C
      RETURN
      END
C
C     **********************************************************
C
      SUBROUTINE REBINFFL(N0M1,D,S,B,FL,ENBF,ENBZKL,C1,FB,FBL,M,NB)
C
      INTEGER I,K,L,M,NB
      REAL R1,C1,WB,FDL
      REAL FL(*),FB(*),FBL(*),ENBF(*),ENBZKL(*)
      REAL D(M),S(M),E(M),B(100,1000)
C
C     Create the the array FDL(L) by averaging the FL(K) weighted by
C     the width of each bin in units of lethargy
C     Fill the array FBL(K) using the FDL(L)
C
      DO 30 L=1,N0M1
	FDL = 0.0
	WB = 0.0
	DO 20 K=1,NB
	  IF (ENBF(K) .GE. ENBZKL(L)) THEN
	    IF (ENBF(K) .LT. ENBZKL(L+1)) THEN 
	      R1 = LOG(ENBF(K+1)) - LOG(ENBF(K))
	      FDL = FDL + FL(K)*R1
	      WB = WB + R1
	    END IF         
	  END IF
20      CONTINUE
	FDL = FDL/WB
	DO 25 K=1,NB
	  IF (ENBF(K) .GE. ENBZKL(L)) THEN 
	    FBL(K) = FDL
	  END IF
25      CONTINUE
30    CONTINUE
C
C     Recalculate the FB(K)
C
      DO 70 K=1,NB
	FB(K) = FBL(K)*( LOG(ENBF(K+1)) - LOG(ENBF(K)) ) 
70    CONTINUE
C
C     Calculate the final chi-square after the rebinning
C
      C1 = 0.0
      DO 180 I=1,M
	E(I) = 0.0
	DO 170 K=1,NB
	  E(I) = E(I)+B(I,K)*FB(K)  
170     CONTINUE
	C1 = C1+((D(I)-E(I))**2)/(S(I)**2)
180   CONTINUE
C
      RETURN
      END
C
C     *****************************************************************
C
      SUBROUTINE OUTPUT(D,S,E,EH,ENBF,FI,FOUT,FIL,FL,FBDSL,FBRFL,CZ,C1,
     $ UNTS,LAMBDA,DH,EBH,C2,NITER,M,NB,MP1,RFN,EDSP,ISCF,SCF,FSCF,C3,
     $ IQDS,IQBS)
C
      INTEGER I,M,NB,MP1,NITER,IQDS,IQBS
      INTEGER RFN(*)
      INTEGER ISCF
      REAL CZ,C1,C2,C3
      REAL D(*),S(*),E(*),ERR(M),PERR(M)
      REAL ENBF(*),FI(*),FOUT(*),FBDSL(*),FIL(*),FL(*),FBRFL(*)
      REAL LAMBDA(30)
      REAL SCF,FSCF,RTIO
      REAL EDSP(*),ERRDSP(M),PERRDSP(M)
      CHARACTER EH*8,CH*12,TH*12,UNTS*10,DH*12,EBH*12 
C
      DO 905 I=1,M
	ERR(I) = (E(I)-D(I))/S(I)
	PERR(I) = (E(I)-D(I))/D(I)
        ERRDSP(I) = (EDSP(I)-D(I))/S(I)
        PERRDSP(I) = (EDSP(I)-D(I))/D(I)
905   CONTINUE
C
      CH = 'OUT.OUT'
      TH = 'OUT.TBL'
C
      OPEN (10, FILE=CH, STATUS='NEW')
      OPEN (14, FILE=TH, STATUS='NEW') 
C
      WRITE (10,908) DH
908   FORMAT(2X,'Input File ',A)
      WRITE (10,910)
910   FORMAT(2X,'E (in MeV)  fl/t (I)    fl/t (F)    fl/t/L (I)  fl/t/L 
     1(F)  RB:Resp.F.  RB:Def.Sp.  (I)/(F)')
C
      DO 920 K=1,NB
        RTIO = 0.0
        IF (FOUT(K) .GT. 0.0) THEN
          RTIO = FI(K)/FOUT(K)
        END IF
        WRITE (10,930) ENBF(K),FI(K),FOUT(K),FIL(K),FL(K),FBRFL(K),
     1FBDSL(K),RTIO
920   CONTINUE
930   FORMAT(1P,8(2X,E10.4))  
      WRITE (10,931) ENBF(NB+1)
931   FORMAT( 2X,E10.4)
C
      WRITE (14, 933) 
933   FORMAT(/2X,'Deconvolution Using the Maximum Entropy Algorithm')
C
      WRITE (14, 941) DH
941   FORMAT(/2X,'File with Input Data : ',A)
      WRITE (14,943) EBH
943   FORMAT(2X,'File with Response Function: ',A)
      WRITE (14,945) CH
945   FORMAT(2X,'Spectra is Stored in File : ',A)
      WRITE (14,946) UNTS
946   FORMAT(/2X,'Response Function in Units of: ',A)
      WRITE (14, 949) CZ  
949   FORMAT(/2X,'Chi Square Using the Default Spectrum  = ',1P,E8.2)   
      WRITE (14, 950) C2
950   FORMAT(2X,'Final Chi Square (No Rebinning) = ',F8.2)
      WRITE (14, 951) C1
951   FORMAT(2X,'Final Chi Square (Default Spectrum bins) = ',F8.2)
      WRITE (14, 952) C3
952   FORMAT(2X,'Final Chi Square (Response Function bins) = ',F8.2)
      WRITE (14, 954) 
954   FORMAT(/2X,'*** RESULTS FOR THE THE FINAL SPECTRUM: ***')
      WRITE (14, 956) 
956   FORMAT(/2X,'NUM/DET   CTS/MEAS  CTS/CALC  (E-D)/S=  (E-D)/D=')
      DO 960 I=1,M
	WRITE (14, 958) RFN(I),D(I),E(I),ERR(I),PERR(I)
958     FORMAT(2X,I8,2X,1P,E8.2,2X,E8.2,2X,0P,F8.3,2X,F8.3)
960   CONTINUE
      WRITE (14, 961) 
961   FORMAT(/2X,'*** RESULTS FOR THE DEFAULT SPECTRUM: ***')
      WRITE (14, 962) 
962   FORMAT(/2X,'NUM/DET   CTS/MEAS  CTS/CALC  (E-D)/S=  (E-D)/D=')
      DO 964 I=1,M
        WRITE (14, 963) RFN(I),D(I),EDSP(I),ERRDSP(I),PERRDSP(I)
963     FORMAT(2X,I8,2X,1P,E8.2,2X,E8.2,2X,0P,F8.3,2X,F8.3)
964   CONTINUE
      WRITE (14, 966)
966   FORMAT(/2X,'    NUM/DET  LAMBDA')
      DO 970 I=1,M
        WRITE (14, 968) RFN(I),LAMBDA(I)
968     FORMAT(2X,I8,5X,1P,E10.3)
970   CONTINUE
      WRITE (14, 974) SCF
974   FORMAT(/2X,'Scaling Factor/Default Spectrum for best fit = ',1P,E1
     10.4)
      WRITE (14, 975) FSCF
975   FORMAT(2X,'Scaling Factor/Default Spectrum used = ',1P,E10.4)
C
      IF (IQDS .EQ. 1) THEN
        WRITE (14, 977)
      ELSE IF (IQDS .EQ. 2) THEN
        WRITE (14, 978)
      ELSE IF (IQDS .EQ. 3) THEN
        WRITE (14, 979)
      END IF
977   FORMAT(/2X,'Default Spectrum Format: ~ dF/dE ')
978   FORMAT(/2X,'Default Spectrum Format: ~ E*dF/dE ')
979   FORMAT(/2X,'Default Spectrum Format: n Fluence Rate per Bin')
C
      IF (IQBS .EQ. 0) THEN
        WRITE (14, 981)
      ELSE IF (IQDS .EQ. 1) THEN
        WRITE (14, 982)
      ELSE IF (IQDS .EQ. 2) THEN
        WRITE (14, 983)
      ELSE IF (IQDS .EQ. 3) THEN
        WRITE (14, 984)
      END IF
981   FORMAT(/2X,'Bin Structure Used : Fine Bin Structure ')
982   FORMAT(/2X,'Bin Structure Used : Four Bins per Decade ')
983   FORMAT(/2X,'Bin Structure Used : Default Spectrum Bin Structure')
984   FORMAT(/2X,'Bin Structure Used : Response Function Bin Structure')
C
      CLOSE (10, STATUS='KEEP')
      CLOSE (14, STATUS='KEEP')   
C
c      PRINT*,'  NAME OF OUTPUT FILE : ',CH
c      PRINT*,' '
C
      RETURN
      END
C
C     *****************************************************************
C
      SUBROUTINE hpsort(n,ra)
      INTEGER n
      REAL ra(n)
      INTEGER i,ir,j,l
      REAL rra
      if (n.lt.2) return
      l=n/2+1
      ir=n
10    continue
	if(l.gt.1)then
	  l=l-1
	  rra=ra(l)
	else
	  rra=ra(ir)
	  ra(ir)=ra(1)
	  ir=ir-1
	  if(ir.eq.1)then
	    ra(1)=rra
	    return
	  endif
	endif
	i=l
	j=l+l
20      if(j.le.ir)then
	  if(j.lt.ir)then
	    if(ra(j).lt.ra(j+1))j=j+1
	  endif
	  if(rra.lt.ra(j))then
	    ra(i)=ra(j)
	    i=j
	    j=j+j
	  else
	    j=ir+1
	  endif
	goto 20
	endif
	ra(i)=rra
      goto 10
      END
C  (C) Copr. 1986-92 Numerical Recipes Software %-,.

C     *****************************************************************

      SUBROUTINE CALCFOUT(LAMBDA,FOUT)

      INTEGER I,J,NB,M,N,N0,MP1
      REAL SUM2,FLUX,OMEGA
      REAL LAMBDA(30),S(100),D(100),FI(1000),MM(10000),FOUT(*),B(M,NB)

      COMMON S,D,FI,MM,FLUX,OMEGA,NB,M,N,N0,MP1    

      DO 6 I=1,M
	DO 4 J=1,NB
	  B(I,J) = MM(NB*(I-1)+J)
4       CONTINUE
6     CONTINUE

      DO 12 J=1,NB
	SUM2 = 0.0
	DO 10 I=1,M
	  SUM2 = SUM2 + LAMBDA(I)*B(I,J)    
10      CONTINUE
	FOUT(J) = FI(J)*EXP(-SUM2)
12    CONTINUE

      RETURN 
      END
C
C     *****************************************************************
C
      SUBROUTINE SAND2(M,N,NB,N0,N1,D,S,FI,B,ENBF,ENBZKL,ENBR,RFN,EH,DH,
     1SCF,FSCF,IQDS,IQBS,EBH,UNITS,CZ)

      INTEGER I,J,M,NB,MAXITER,NITER,IQ
      INTEGER N,N0,N0M1,N1,NB1,IQDS,IQBS
      INTEGER RFN(M)
      REAL DEV,DEVJ,MAXDEV,CS,C1,C3,RTIO,CSQ,SCF,FSCF,CZ
      REAL D(M),S(M),E(M),R(M),SUM1(NB),SUM2(NB)
      REAL FI(NB),FS(NB),FSNEW(NB),B(100,1000),W(M,NB)
      REAL FIL(NB),FL(NB),ENBF(N),ENBZKL(N0),FBDS(NB),FBDSL(NB)
      REAL ENBR(N1),FBRF(NB),FBRFL(NB)
      REAL ERR(M),PERR(M)
      CHARACTER EH*8,CH*12,DH*12,SH*12,EBH*12,UNITS*10

      PRINT*,'  STARTING SAND-II DECONVOLUTION '
      PRINT*,' '
      PRINT*,'  ENTER THE MAXIMUM NUMBER OF ITERATIONS : '
      READ*,MAXITER
      PRINT*,' '
      PRINT*,' CHOOSE A CONVERGENCE CRITERIA: (0 OR 1) :'
      PRINT*,' 0 - MAXIMUM FRACTIONAL DEVIATION IN ANY BIN ' 
      PRINT*,' 1 - CHI SQUARE VALUE '
      PRINT*,' '
      READ*,IQ
      IF (IQ .EQ. 0) THEN
        PRINT*,'  ENTER THE MAXIMUM ALLOWED FRACTIONAL DEVIATION : '
        READ*,DEV
        PRINT*,' '
      END IF
C
C     The SAND-II iterative procedure
C
      NITER = 0
C
      DO 6 J=1,NB
        FS(J) = FI(J)
6     CONTINUE
C
100   DO 10 I=1,M
        E(I) = 0.0
        DO 8 J=1,NB
          E(I) = E(I)+B(I,J)*FS(J)
8       CONTINUE
        R(I) = D(I)/E(I)
10    CONTINUE                   
C
      DO 14 I=1,M
        DO 12 J=1,NB
          W(I,J) = B(I,J)*FS(J)/E(I)
12      CONTINUE
14    CONTINUE
C
      DO 18 J=1,NB
        SUM1(J) = 0.0
        SUM2(J) = 0.0
        DO 16 I=1,M
          SUM1(J) = SUM1(J) + W(I,J)*LOG(R(I))
          SUM2(J) = SUM2(J) + W(I,J)
16      CONTINUE
18    CONTINUE
C
      DO 20 J=1,NB
        FSNEW(J) = FS(J)*EXP(SUM1(J)/SUM2(J))
20    CONTINUE
C
      NITER = NITER + 1
C
      DO 28 I=1,M
        E(I) = 0.0
        DO 26 J=1,NB
          E(I) = E(I)+B(I,J)*FSNEW(J)
26      CONTINUE
        R(I) = D(I)/E(I)
28    CONTINUE
C
C     Check the chi-square if required
C
      IF (IQ .EQ. 1) THEN
        CSQ = 0.0
        DO 30 I=1,M
          CSQ = CSQ+((D(I)-E(I))**2)/(S(I)**2)
30      CONTINUE
        IF (CSQ .LE. M) THEN
          GO TO 900
        END IF
      END IF
C
C     If error is small enough, stop
C
      IF (IQ .EQ. 0) THEN
        MAXDEV = ABS(FSNEW(1)-FS(1))/FS(1)
        DO 33 I=1,NB
          DEVJ = ABS(FSNEW(J)-FS(J))/FS(J)
          IF (DEVJ .GT. MAXDEV) THEN
            MAXDEV = DEVJ
          END IF
33      CONTINUE
        IF (MAXDEV .LE. DEV) THEN
          GO TO 900
        END IF
      END IF
C
C     If it reaches the maximum number of iterations, stop
C
      IF (NITER. GE. MAXITER) THEN
        GO TO 900
      END IF
C
      DO 34 J=1,NB
        FS(J) = FSNEW(J)
34    CONTINUE
      GO TO 100
C
C     If finished, calculate relevant quantities
C
900   CS = 0.0
      DO 66 I=1,M
	E(I) = 0.0
        DO 64 J=1,NB
          E(I) = E(I)+B(I,J)*FSNEW(J)  
64      CONTINUE
        CS = CS+((D(I)-E(I))**2)/(S(I)**2)
66    CONTINUE
C                                    
      PRINT*,' CHI SQUARE/SAND-II  = ',CS
      PRINT*,' '                         
C
      CALL LETHAR(FI,FSNEW,ENBF,N,NB,FIL,FL)
C
      N0M1 = N0 - 1 
      CALL REBINFFL(N0M1,D,S,B,FL,ENBF,ENBZKL,C1,FBDS,FBDSL,M,NB)    
C                 
      PRINT*,' CHI SQUARE AFTER REBINNING TO THE BIN STRUCTURE OF THE '
      PRINT*,' DEFAULT SPECTRUM            = ',C1
      PRINT*,' '
C
      NB1 = N1 - 1
      CALL REBINFFL(NB1,D,S,B,FL,ENBF,ENBR,C3,FBRF,FBRFL,M,NB)    
C                 
      PRINT*,' CHI SQUARE AFTER REBINNING TO THE BIN STRUCTURE OF THE '
      PRINT*,' RESPONSE FUNCTION           = ',C3
      PRINT*,' '
C
      DO 905 I=1,M
	ERR(I) = (E(I)-D(I))/S(I)
	PERR(I) = (E(I)-D(I))/D(I)
905   CONTINUE
C      
      CH = EH//'.SII'
C
      OPEN (10, FILE=CH, STATUS='NEW')
C
      WRITE (10,908)
908   FORMAT('*SAND-II*')
      WRITE (10,910)
910   FORMAT(2X,'E (in MeV)  fl/t (I)    fl/t (F)    fl/t/L (I)  fl/t/L 
     1(F)  RB:Resp.F.  RB:Def.Sp.  (I)/(F)')
C
      DO 920 K=1,NB
        RTIO = 0.0
        IF (FSNEW(K) .GT. 0.0) THEN
          RTIO = FI(K)/FSNEW(K)
        END IF
        WRITE (10,930) ENBF(K),FI(K),FSNEW(K),FIL(K),FL(K),FBRFL(K),
     1FBDSL(K),RTIO
920   CONTINUE
930   FORMAT(1P,8(2X,E10.4))  
      WRITE (10,931) ENBF(NB+1)
931   FORMAT( 2X,E10.4)
C
      SH = EH//'.TS2'
C
      OPEN (12, FILE=SH, STATUS='NEW')
C
      WRITE (12, 932) 
932   FORMAT(/2X,'Deconvolution Using the SAND-II Algorithm')
C
      WRITE (12, 933) DH
933   FORMAT(/2X,'File with Input Data : ',A)
      WRITE (12,934) EBH
934   FORMAT(2X,'File with Response Function: ',A)
      WRITE (12,935) CH
935   FORMAT(2X,'Spectra is Stored in File : ',A)
      WRITE (12,936) UNITS
936   FORMAT(/2X,'Response Function in Units of: ',A)
C
      IF (IQ .EQ. 0) THEN
        WRITE (12, 942) DEV
942     FORMAT(/2X,'Maximum Allowed Fractional Deviation = ',F6.4)
        WRITE (12, 943) MAXDEV
943     FORMAT(2X,'Final Fractional Deviation = ',F6.4)
      END IF
C
      WRITE (12, 946) MAXITER
946   FORMAT(/2X,'Maximum Number of Iterations = ',I5)
      WRITE (12, 947) NITER
947   FORMAT(2X,'Final Number of Iterations = ',I5)
C
      WRITE (12, 949) CZ
949   FORMAT(/2X,'Chi Square Using the Default Spectrum  = ',1P,E8.2)   
      WRITE (12, 950) CS
950   FORMAT(2X,'Final Chi Square (No Rebinning) = ',F8.2)
      WRITE (12, 951) C1
951   FORMAT(2X,'Final Chi Square (Default Spectrum bins) = ',F8.2)
      WRITE (12, 952) C3
952   FORMAT(2X,'Final Chi Square (Response Function bins) = ',F8.2)
      WRITE (12, 954)
C
954   FORMAT(/2X,'*** RESULTS FOR THE FINAL SPECTRUM: ***')
      WRITE (12, 956) 
956   FORMAT(/2X,'NUM/DET   CTS/MEAS  CTS/CALC  (E-D)/S=  (E-D)/D=')
      DO 960 I=1,M
        WRITE (12, 958) RFN(I),D(I),E(I),ERR(I),PERR(I)
958     FORMAT(2X,I8,2X,1P,E8.2,2X,E8.2,2X,0P,F8.3,2X,F8.3)
960   CONTINUE
C
      WRITE (12, 974) SCF
974   FORMAT(/2X,'Scaling Factor/Default Spectrum for best fit = ',1P,E1
     10.4)
      WRITE (12, 975) FSCF
975   FORMAT(2X,'Scaling Factor/Default Spectrum used = ',1P,E10.4)
C
      IF (IQDS .EQ. 1) THEN
        WRITE (12, 977)
      ELSE IF (IQDS .EQ. 2) THEN
        WRITE (12, 978)
      ELSE IF (IQDS .EQ. 3) THEN
        WRITE (12, 979)
      END IF
977   FORMAT(/2X,'Default Spectrum Format: ~ dF/dE ')
978   FORMAT(/2X,'Default Spectrum Format: ~ E*dF/dE ')
979   FORMAT(/2X,'Default Spectrum Format: n Fluence Rate per Bin')
C
      IF (IQBS .EQ. 0) THEN
        WRITE (12, 981)
      ELSE IF (IQDS .EQ. 1) THEN
        WRITE (12, 982)
      ELSE IF (IQDS .EQ. 2) THEN
        WRITE (12, 983)
      ELSE IF (IQDS .EQ. 3) THEN
        WRITE (12, 984)
      END IF
981   FORMAT(/2X,'Bin Structure Used : Fine Bin Structure ')
982   FORMAT(/2X,'Bin Structure Used : Four Bins per Decade ')
983   FORMAT(/2X,'Bin Structure Used : Default Spectrum Bin Structure')
984   FORMAT(/2X,'Bin Structure Used : Response Function Bin Structure')
C
      CLOSE (10, STATUS='KEEP')
      CLOSE (12, STATUS='KEEP')
C
      PRINT*,'  NAME OF OUTPUT FILE : ',CH
      PRINT*,' '
C
      RETURN
      END
C
C   ***************************************************************************
C
C   NOTE 1: The rest of this file contains a modification of the program
C   SIMANN.  The program was modified by Marcel Reginatto.  The
c   modifications include:
C   (1) A new function subroutine FCN was put in place of the original one.
C   (2) The values of some of the input parameters (such as MAX, T, RT)
C       have been changed
C
C   NOTE 2: All comments that follow are the ones that appeared in the
C   original (unmodified) version of SIMANN.  Be aware that some of these
C   comments are specific to the original function, and do not necessarily
C   apply to the function optimized in this modified version.
C
C   
C
C ABSTRACT:
C   Simulated annealing is a global optimization method that distinguishes
C   between different local optima. Starting from an initial point, the
C   algorithm takes a step and the function is evaluated. When minimizing a
C   function, any downhill step is accepted and the process repeats from this
C   new point. An uphill step may be accepted. Thus, it can escape from local
C   optima. This uphill decision is made by the Metropolis criteria. As the
C   optimization process proceeds, the length of the steps decline and the
C   algorithm closes in on the global optimum. Since the algorithm makes very
C   few assumptions regarding the function to be optimized, it is quite
C   robust with respect to non-quadratic surfaces. The degree of robustness
C   can be adjusted by the user. In fact, simulated annealing can be used as
C   a local optimizer for difficult functions.
C
C   This implementation of simulated annealing was used in "Global Optimization
C   of Statistical Functions with Simulated Annealing," Goffe, Ferrier and
C   Rogers, Journal of Econometrics, vol. 60, no. 1/2, Jan./Feb. 1994, pp.
C   65-100. Briefly, we found it competitive, if not superior, to multiple
C   restarts of conventional optimization routines for difficult optimization
C   problems.
C
C   For more information on this routine, contact its author:
C   Bill Goffe, bgoffe@whale.st.usm.edu
C
CC      PROGRAM SIMANN
C  This file is an example of the Corana et al. simulated annealing
C  algorithm for multimodal and robust optimization as implemented
C  and modified by Goffe, Ferrier and Rogers. Counting the above line
C  ABSTRACT as 1, the routine itself (SA), with its supplementary
C  routines, is on lines 232-990. A multimodal example from Judge et al.
C  (FCN) is on lines 150-231. The rest of this file (lines 1-149) is a
C  driver routine with values appropriate for the Judge example. Thus, this
C  example is ready to run.
C
C  To understand the algorithm, the documentation for SA on lines 236-
C  484 should be read along with the parts of the paper that describe
C  simulated annealing. Then the following lines will then aid the user
C  in becomming proficient with this implementation of simulated
C  annealing.
C
C  Learning to use SA:
C      Use the sample function from Judge with the following suggestions
C  to get a feel for how SA works. When you've done this, you should be
C  ready to use it on most any function with a fair amount of expertise.
C    1. Run the program as is to make sure it runs okay. Take a look at
C       the intermediate output and see how it optimizes as temperature
C       (T) falls. Notice how the optimal point is reached and how
C       falling T reduces VM.
C    2. Look through the documentation to SA so the following makes a
C       bit of sense. In line with the paper, it shouldn't be that hard
C       to figure out. The core of the algorithm is described on pp. 68-70
C       and on pp. 94-95. Also see Corana et al. pp. 264-9.
C    3. To see how it selects points and makes decisions about uphill
C       and downhill moves, set IPRINT = 3 (very detailed intermediate
C       output) and MAXEVL = 100 (only 100 function evaluations to limit
C       output).
C    4. To see the importance of different temperatures, try starting
C       with a very low one (say T = 10E-5). You'll see (i) it never
C       escapes from the local optima (in annealing terminology, it
C       quenches) & (ii) the step length (VM) will be quite small. This
C       is a key part of the algorithm: as temperature (T) falls, step
C       length does too. In a minor point here, note how VM is quickly
C       reset from its initial value. Thus, the input VM is not very
C       important. This is all the more reason to examine VM once the
C       algorithm is underway.
C    5. To see the effect of different parameters and their effect on
C       the speed of the algorithm, try RT = .95 & RT = .1. Notice the
C       vastly different speed for optimization. Also try NT = 20. Note
C       that this sample function is quite easy to optimize, so it will
C       tolerate big changes in these parameters. RT and NT are the
C       parameters one should adjust to modify the runtime of the
C       algorithm and its robustness.
C    6. Try constraining the algorithm with either LB or UB.

      SUBROUTINE SIMANN(N,LAMBDA,MAXEVAL)

      PARAMETER (NEPS = 4)

      DOUBLE PRECISION  LB(N), UB(N), X(N), XOPT(N), C(N), VM(N),
     1                  FSTAR(NEPS), XP(N), T, EPS, RT, FOPT

      REAL LAMBDA(30)

      INTEGER  NACP(N), NS, NT, NFCNEV, IER, ISEED1, ISEED2,
     1         MAXEVL, IPRINT, NACC, NOBDS

      LOGICAL  MAX

      EXTERNAL FCN
      COMMON /BUMS/ T,RT,EPS,NT

C  Set underflows to zero on IBM mainframes.
C     CALL XUFLOW(0)

C  Set input parameters.
      MAX = .TRUE.
      IPRINT = 1
      ISEED1 = 1
      ISEED2 = 2
      NS=20
      DO 10, I = 1, N
	 LB(I) = -1.0D25
	 UB(I) =  1.0D25
	 C(I) = 2.0
10    CONTINUE

C  Initialize the X(I) to zero.
      DO 15, I=1,N
	X(I) = 0.0
15    CONTINUE

C  Set input values of the input/output parameters.
      T = 5.0
      DO 20, I = 1, N
	 VM(I) = 1.0
 20   CONTINUE

c      PRINT*,' T = '
C      READ*,T
      T=1
c      PRINT*,' RT (SUGGESTED VALUE = 0.85) = '
C      READ*,RT
      RT=0.85
	       
      WRITE(*,1000) N, MAX, T, RT, EPS, NS, NT, NEPS, MAXEVL, IPRINT,
     1              ISEED1, ISEED2

      CALL PRTVEC(X,N,'STARTING VALUES')
      CALL PRTVEC(VM,N,'INITIAL STEP LENGTH')
      CALL PRTVEC(LB,N,'LOWER BOUND')
      CALL PRTVEC(UB,N,'UPPER BOUND')
      CALL PRTVEC(C,N,'C VECTOR')
c      WRITE(*,'(/,''  ****   END OF DRIVER ROUTINE OUTPUT   ****''
c     1          /,''  ****   BEFORE CALL TO SA.             ****'')')      

      CALL SA(N,X,MAX,RT,EPS,NS,NT,NEPS,MAXEVAL,LB,UB,C,IPRINT,ISEED1,
     1        ISEED2,T,VM,XOPT,FOPT,NACC,NFCNEV,NOBDS,IER,
     2        FSTAR,XP,NACP)

      WRITE(*,'(/,''  ****   RESULTS AFTER SA   ****   '')')      
      CALL PRTVEC(XOPT,N,'SOLUTION')
      CALL PRTVEC(VM,N,'FINAL STEP LENGTH')
      WRITE(*,1001) FOPT, NFCNEV, NACC, NOBDS, T, IER

1000  FORMAT(/,' ',/,
     1       /,' NUMBER OF PARAMETERS: ',I3,'   MAXIMAZATION: ',L5,
     2       /,' INITIAL TEMP: ', G8.2, '   RT: ',G8.2, '   EPS: ',G8.2,
     3       /,' NS: ',I3, '   NT: ',I2, '   NEPS: ',I2,
     4       /,' MAXEVL: ',I10, '   IPRINT: ',I1, '   ISEED1: ',I4,
     5       '   ISEED2: ',I4)
1001  FORMAT(/,' OPTIMAL FUNCTION VALUE: ',G20.13
     1       /,' NUMBER OF FUNCTION EVALUATIONS:     ',I10,
     2       /,' NUMBER OF ACCEPTED EVALUATIONS:     ',I10,
     3       /,' NUMBER OF OUT OF BOUND EVALUATIONS: ',I10,
     4       /,' FINAL TEMP: ', G20.13,'  IER: ', I3)

      DO 25 I=1,N
	LAMBDA(I) = REAL(XOPT(I))
25    CONTINUE

      RETURN
      END


      SUBROUTINE SA(N,X,MAX,RT,EPS,NS,NT,NEPS,MAXEVL,LB,UB,C,IPRINT,
     1              ISEED1,ISEED2,T,VM,XOPT,FOPT,NACC,NFCNEV,NOBDS,IER,
     2              FSTAR,XP,NACP)

C  Version: 3.2
C  Date: 1/22/94.
C  Differences compared to Version 2.0:
C     1. If a trial is out of bounds, a point is randomly selected
C        from LB(i) to UB(i). Unlike in version 2.0, this trial is
C        evaluated and is counted in acceptances and rejections.
C        All corresponding documentation was changed as well.
C  Differences compared to Version 3.0:
C     1. If VM(i) > (UB(i) - LB(i)), VM is set to UB(i) - LB(i).
C        The idea is that if T is high relative to LB & UB, most
C        points will be accepted, causing VM to rise. But, in this
C        situation, VM has little meaning; particularly if VM is
C        larger than the acceptable region. Setting VM to this size
C        still allows all parts of the allowable region to be selected.
C  Differences compared to Version 3.1:
C     1. Test made to see if the initial temperature is positive.
C     2. WRITE statements prettied up.
C     3. References to paper updated.
C
C  Synopsis:
C  This routine implements the continuous simulated annealing global
C  optimization algorithm described in Corana et al.'s article
C  "Minimizing Multimodal Functions of Continuous Variables with the
C  "Simulated Annealing" Algorithm" in the September 1987 (vol. 13,
C  no. 3, pp. 262-280) issue of the ACM Transactions on Mathematical
C  Software.
C
C  A very quick (perhaps too quick) overview of SA:
C     SA tries to find the global optimum of an N dimensional function.
C  It moves both up and downhill and as the optimization process
C  proceeds, it focuses on the most promising area.
C     To start, it randomly chooses a trial point within the step length
C  VM (a vector of length N) of the user selected starting point. The
C  function is evaluated at this trial point and its value is compared
C  to its value at the initial point.
C     In a maximization problem, all uphill moves are accepted and the
C  algorithm continues from that trial point. Downhill moves may be
C  accepted; the decision is made by the Metropolis criteria. It uses T
C  (temperature) and the size of the downhill move in a probabilistic
C  manner. The smaller T and the size of the downhill move are, the more
C  likely that move will be accepted. If the trial is accepted, the
C  algorithm moves on from that point. If it is rejected, another point
C  is chosen instead for a trial evaluation.
C     Each element of VM periodically adjusted so that half of all
C  function evaluations in that direction are accepted.
C     A fall in T is imposed upon the system with the RT variable by
C  T(i+1) = RT*T(i) where i is the ith iteration. Thus, as T declines,
C  downhill moves are less likely to be accepted and the percentage of
C  rejections rise. Given the scheme for the selection for VM, VM falls.
C  Thus, as T declines, VM falls and SA focuses upon the most promising
C  area for optimization.
C
C  The importance of the parameter T:
C     The parameter T is crucial in using SA successfully. It influences
C  VM, the step length over which the algorithm searches for optima. For
C  a small intial T, the step length may be too small; thus not enough
C  of the function might be evaluated to find the global optima. The user
C  should carefully examine VM in the intermediate output (set IPRINT =
C  1) to make sure that VM is appropriate. The relationship between the
C  initial temperature and the resulting step length is function
C  dependent.
C     To determine the starting temperature that is consistent with
C  optimizing a function, it is worthwhile to run a trial run first. Set
C  RT = 1.5 and T = 1.0. With RT > 1.0, the temperature increases and VM
C  rises as well. Then select the T that produces a large enough VM.
C
C  For modifications to the algorithm and many details on its use,
C  (particularly for econometric applications) see Goffe, Ferrier
C  and Rogers, "Global Optimization of Statistical Functions with
C  Simulated Annealing," Journal of Econometrics, vol. 60, no. 1/2, 
C  Jan./Feb. 1994, pp. 65-100.
C  For more information, contact 
C              Bill Goffe
C              Department of Economics and International Business
C              University of Southern Mississippi 
C              Hattiesburg, MS  39506-5072 
C              (601) 266-4484 (office)
C              (601) 266-4920 (fax)
C              bgoffe@whale.st.usm.edu (Internet)
C
C  As far as possible, the parameters here have the same name as in
C  the description of the algorithm on pp. 266-8 of Corana et al.
C
C  In this description, SP is single precision, DP is double precision,
C  INT is integer, L is logical and (N) denotes an array of length n.
C  Thus, DP(N) denotes a double precision array of length n.
C
C  Input Parameters:
C    Note: The suggested values generally come from Corana et al. To
C          drastically reduce runtime, see Goffe et al., pp. 90-1 for
C          suggestions on choosing the appropriate RT and NT.
C    N - Number of variables in the function to be optimized. (INT)
C    X - The starting values for the variables of the function to be
C        optimized. (DP(N))
C    MAX - Denotes whether the function should be maximized or
C          minimized. A true value denotes maximization while a false
C          value denotes minimization. Intermediate output (see IPRINT)
C          takes this into account. (L)
C    RT - The temperature reduction factor. The value suggested by
C         Corana et al. is .85. See Goffe et al. for more advice. (DP)
C    EPS - Error tolerance for termination. If the final function
C          values from the last neps temperatures differ from the
C          corresponding value at the current temperature by less than
C          EPS and the final function value at the current temperature
C          differs from the current optimal function value by less than
C          EPS, execution terminates and IER = 0 is returned. (EP)
C    NS - Number of cycles. After NS*N function evaluations, each
C         element of VM is adjusted so that approximately half of
C         all function evaluations are accepted. The suggested value
C         is 20. (INT)
C    NT - Number of iterations before temperature reduction. After
C         NT*NS*N function evaluations, temperature (T) is changed
C         by the factor RT. Value suggested by Corana et al. is
C         MAX(100, 5*N). See Goffe et al. for further advice. (INT)
C    NEPS - Number of final function values used to decide upon termi-
C           nation. See EPS. Suggested value is 4. (INT)
C    MAXEVL - The maximum number of function evaluations. If it is
C             exceeded, IER = 1. (INT)
C    LB - The lower bound for the allowable solution variables. (DP(N))
C    UB - The upper bound for the allowable solution variables. (DP(N))
C         If the algorithm chooses X(I) .LT. LB(I) or X(I) .GT. UB(I),
C         I = 1, N, a point is from inside is randomly selected. This
C         This focuses the algorithm on the region inside UB and LB.
C         Unless the user wishes to concentrate the search to a par-
C         ticular region, UB and LB should be set to very large positive
C         and negative values, respectively. Note that the starting
C         vector X should be inside this region. Also note that LB and
C         UB are fixed in position, while VM is centered on the last
C         accepted trial set of variables that optimizes the function.
C    C - Vector that controls the step length adjustment. The suggested
C        value for all elements is 2.0. (DP(N))
C    IPRINT - controls printing inside SA. (INT)
C             Values: 0 - Nothing printed.
C                     1 - Function value for the starting value and
C                         summary results before each temperature
C                         reduction. This includes the optimal
C                         function value found so far, the total
C                         number of moves (broken up into uphill,
C                         downhill, accepted and rejected), the
C                         number of out of bounds trials, the
C                         number of new optima found at this
C                         temperature, the current optimal X and
C                         the step length VM. Note that there are
C                         N*NS*NT function evalutations before each
C                         temperature reduction. Finally, notice is
C                         is also given upon achieveing the termination
C                         criteria.
C                     2 - Each new step length (VM), the current optimal
C                         X (XOPT) and the current trial X (X). This
C                         gives the user some idea about how far X
C                         strays from XOPT as well as how VM is adapting
C                         to the function.
C                     3 - Each function evaluation, its acceptance or
C                         rejection and new optima. For many problems,
C                         this option will likely require a small tree
C                         if hard copy is used. This option is best
C                         used to learn about the algorithm. A small
C                         value for MAXEVL is thus recommended when
C                         using IPRINT = 3.
C             Suggested value: 1
C             Note: For a given value of IPRINT, the lower valued
C                   options (other than 0) are utilized.
C    ISEED1 - The first seed for the random number generator RANMAR.
C             0 .LE. ISEED1 .LE. 31328. (INT)
C    ISEED2 - The second seed for the random number generator RANMAR.
C             0 .LE. ISEED2 .LE. 30081. Different values for ISEED1
C             and ISEED2 will lead to an entirely different sequence
C             of trial points and decisions on downhill moves (when
C             maximizing). See Goffe et al. on how this can be used
C             to test the results of SA. (INT)
C
C  Input/Output Parameters:
C    T - On input, the initial temperature. See Goffe et al. for advice.
C        On output, the final temperature. (DP)
C    VM - The step length vector. On input it should encompass the
C         region of interest given the starting value X. For point
C         X(I), the next trial point is selected is from X(I) - VM(I)
C         to  X(I) + VM(I). Since VM is adjusted so that about half
C         of all points are accepted, the input value is not very
C         important (i.e. is the value is off, SA adjusts VM to the
C         correct value). (DP(N))
C
C  Output Parameters:
C    XOPT - The variables that optimize the function. (DP(N))
C    FOPT - The optimal value of the function. (DP)
C    NACC - The number of accepted function evaluations. (INT)
C    NFCNEV - The total number of function evaluations. In a minor
C             point, note that the first evaluation is not used in the
C             core of the algorithm; it simply initializes the
C             algorithm. (INT).
C    NOBDS - The total number of trial function evaluations that
C            would have been out of bounds of LB and UB. Note that
C            a trial point is randomly selected between LB and UB.
C            (INT)
C    IER - The error return number. (INT)
C          Values: 0 - Normal return; termination criteria achieved.
C                  1 - Number of function evaluations (NFCNEV) is
C                      greater than the maximum number (MAXEVL).
C                  2 - The starting value (X) is not inside the
C                      bounds (LB and UB).
C                  3 - The initial temperature is not positive.
C                  99 - Should not be seen; only used internally.
C
C  Work arrays that must be dimensioned in the calling routine:
C       RWK1 (DP(NEPS))  (FSTAR in SA)
C       RWK2 (DP(N))     (XP    "  " )
C       IWK  (INT(N))    (NACP  "  " )
C
C  Required Functions (included):
C    EXPREP - Replaces the function EXP to avoid under- and overflows.
C             It may have to be modified for non IBM-type main-
C             frames. (DP)
C    RMARIN - Initializes the random number generator RANMAR.
C    RANMAR - The actual random number generator. Note that
C             RMARIN must run first (SA does this). It produces uniform
C             random numbers on [0,1]. These routines are from
C             Usenet's comp.lang.fortran. For a reference, see
C             "Toward a Universal Random Number Generator"
C             by George Marsaglia and Arif Zaman, Florida State
C             University Report: FSU-SCRI-87-50 (1987).
C             It was later modified by F. James and published in
C             "A Review of Pseudo-random Number Generators." For
C             further information, contact stuart@ads.com. These
C             routines are designed to be portable on any machine
C             with a 24-bit or more mantissa. I have found it produces
C             identical results on a IBM 3081 and a Cray Y-MP.
C
C  Required Subroutines (included):
C    PRTVEC - Prints vectors.
C    PRT1 ... PRT10 - Prints intermediate output.
C    FCN - Function to be optimized. The form is
C            SUBROUTINE FCN(N,X,F)
C            INTEGER N
C            DOUBLE PRECISION  X(N), F
C            ...
C            function code with F = F(X)
C            ...
C            RETURN
C            END
C          Note: This is the same form used in the multivariable
C          minimization algorithms in the IMSL edition 10 library.
C
C  Machine Specific Features:
C    1. EXPREP may have to be modified if used on non-IBM type main-
C       frames. Watch for under- and overflows in EXPREP.
C    2. Some FORMAT statements use G25.18; this may be excessive for
C       some machines.
C    3. RMARIN and RANMAR are designed to be protable; they should not
C       cause any problems.

C  Type all external variables.
      DOUBLE PRECISION  X(*), LB(*), UB(*), C(*), VM(*), FSTAR(*),
     1                  XOPT(*), XP(*), T, EPS, RT, FOPT
      INTEGER  NACP(*), N, NS, NT, NEPS, NACC, MAXEVL, IPRINT,
     1         NOBDS, IER, NFCNEV, ISEED1, ISEED2
      LOGICAL  MAX

C  Type all internal variables.
      DOUBLE PRECISION  F, FP, P, PP, RATIO
      INTEGER  NUP, NDOWN, NREJ, NNEW, LNOBDS, H, I, J, M
      LOGICAL  QUIT

C  Type all functions.
      DOUBLE PRECISION  EXPREP
      REAL  RANMAR

C  Initialize the random number generator RANMAR.
      CALL RMARIN(ISEED1,ISEED2)

c      DO 5, I = 1, N
c	print *,"I=",I," LB=",LB(I)," UB=",UB(I)
c 5     CONTINUE


C  Set initial values.
      NACC = 0
      NOBDS = 0
      NFCNEV = 0
      IER = 99

      DO 10, I = 1, N
	 XOPT(I) = X(I)
	 NACP(I) = 0
10    CONTINUE

      DO 20, I = 1, NEPS
	 FSTAR(I) = 1.0D+20
20    CONTINUE 

C  If the initial temperature is not positive, notify the user and 
C  return to the calling routine.  
      IF (T .LE. 0.0) THEN
	 WRITE(*,'(/,''  THE INITIAL TEMPERATURE IS NOT POSITIVE. ''
     1             /,''  RESET THE VARIABLE T. ''/)')
	 IER = 3
	 RETURN
      END IF

C  If the initial value is out of bounds, notify the user and return
C  to the calling routine.
      DO 30, I = 1, N
	 IF ((X(I) .GT. UB(I)) .OR. (X(I) .LT. LB(I))) THEN
	    CALL PRT1
	    IER = 2
	    RETURN
	 END IF
30    CONTINUE

C  Evaluate the function with input X and return value as F.
      CALL FCN(N,X,F)

C  If the function is to be minimized, switch the sign of the function.
C  Note that all intermediate and final output switches the sign back
C  to eliminate any possible confusion for the user.
      IF(.NOT. MAX) F = -F
      NFCNEV = NFCNEV + 1
      FOPT = F
      FSTAR(1) = F
      IF(IPRINT .GE. 1) CALL PRT2(MAX,N,X,F)

C  Start the main loop. Note that it terminates if (i) the algorithm
C  succesfully optimizes the function or (ii) there are too many
C  function evaluations (more than MAXEVL).
100   NUP = 0
      NREJ = 0
      NNEW = 0
      NDOWN = 0
      LNOBDS = 0

      DO 400, M = 1, NT
	 DO 300, J = 1, NS
	    DO 200, H = 1, N

C  Generate XP, the trial value of X. Note use of VM to choose XP.
	       DO 110, I = 1, N
		  IF (I .EQ. H) THEN
c		     print *,"Starting RANMAR 1"
		     XP(I) = X(I) + (RANMAR()*2.- 1.) * VM(I)
c	    print *,"UNI=",UNI
c            print *,"I=",I," X=",X(I)," XP=",XP(I)," VM=",VM(I)

		  ELSE
		     XP(I) = X(I)
		  END IF

C  If XP is out of bounds, select a point in bounds for the trial.
		  IF((XP(I) .LT. LB(I)) .OR. (XP(I) .GT. UB(I))) THEN
		    XP(I) = LB(I) + (UB(I) - LB(I))*RANMAR()
		    LNOBDS = LNOBDS + 1
		    NOBDS = NOBDS + 1
		    IF(IPRINT .GE. 3) CALL PRT3(MAX,N,XP,X,FP,F)
c         print *,"##### XP=",XP(I)," F=",F," M=",M," J=",J," H=",H
		  END IF
c         print *,"##### XP=",XP(I)," F=",F," M=",M," J=",J," H=",H
110            CONTINUE

C  Evaluate the function with the trial point XP and return as FP.
	       CALL FCN(N,XP,FP)
c         print *,"#####  F=",F," M=",M," J=",J," H=",H," FP=",FP
	
	       IF(.NOT. MAX) FP = -FP
	       NFCNEV = NFCNEV + 1
	       IF(IPRINT .GE. 3) CALL PRT4(MAX,N,XP,X,FP,F)

C  If too many function evaluations occur, terminate the algorithm.
	       IF(NFCNEV .GE. MAXEVL) THEN
		  CALL PRT5
		  IF (.NOT. MAX) FOPT = -FOPT
		  IER = 1
		  RETURN
             END IF

C  Accept the new point if the function value increases.
c         print *," ##### FP=",FP," F=",F," M=",M," J=",J," H=",H
	       IF(FP .GE. F) THEN
		  IF(IPRINT .GE. 3) THEN
		     WRITE(*,'(''  POINT ACCEPTED'')')
		  END IF
		  DO 120, I = 1, N
		     X(I) = XP(I)
120               CONTINUE
		  F = FP
		  NACC = NACC + 1
		  NACP(H) = NACP(H) + 1
		  NUP = NUP + 1

C  If greater than any other point, record as new optimum.
		  IF (FP .GT. FOPT) THEN
		  IF(IPRINT .GE. 3) THEN
		     WRITE(*,'(''  NEW OPTIMUM'')')
		  END IF
		     DO 130, I = 1, N
			XOPT(I) = XP(I)
130                  CONTINUE
		     FOPT = FP
		     NNEW = NNEW + 1
		  END IF

C  If the point is lower, use the Metropolis criteria to decide on
C  acceptance or rejection.
	       ELSE
c		print *,"T=",T," FP=",FP," F=",F
		
		  P = EXPREP((FP - F)/T)
		  PP = RANMAR()
c		print *,"P=",P," PP=",PP," Z=",M," J=",J," H=",H

		  IF (PP .LT. P) THEN
c         print *,"Here ##### PP<P  M=",M," J=",J," H=",H
		     IF(IPRINT .GE. 3) CALL PRT6(MAX)
		     DO 140, I = 1, N
			X(I) = XP(I)
140                  CONTINUE
		     F = FP
		     NACC = NACC + 1
		     NACP(H) = NACP(H) + 1
		     NDOWN = NDOWN + 1
		  ELSE
		     NREJ = NREJ + 1
		     IF(IPRINT .GE. 3) CALL PRT7(MAX)
		  END IF
	       END IF

200         CONTINUE
300      CONTINUE

C  Adjust VM so that approximately half of all evaluations are accepted.
	 DO 310, I = 1, N
	    RATIO = DFLOAT(NACP(I)) /DFLOAT(NS)
	    IF (RATIO .GT. .6) THEN
	       VM(I) = VM(I)*(1. + C(I)*(RATIO - .6)/.4)
	    ELSE IF (RATIO .LT. .4) THEN
	       VM(I) = VM(I)/(1. + C(I)*((.4 - RATIO)/.4))
	    END IF
	    IF (VM(I) .GT. (UB(I)-LB(I))) THEN
	       VM(I) = UB(I) - LB(I)
	    END IF
310      CONTINUE

C	 IF(IPRINT .GE. 2) THEN
C	    CALL PRT8(N,VM,XOPT,X)
C	 END IF

	 DO 320, I = 1, N
	    NACP(I) = 0
320      CONTINUE

400   CONTINUE

C      IF(IPRINT .GE. 1) THEN
C	 CALL PRT9(MAX,N,T,XOPT,VM,FOPT,NUP,NDOWN,NREJ,LNOBDS,NNEW)
C      END IF

C  Check termination criteria.
      QUIT = .FALSE.
      FSTAR(1) = F
      IF ((FOPT - FSTAR(1)) .LE. EPS) QUIT = .TRUE.
      DO 410, I = 1, NEPS
	 IF (ABS(F - FSTAR(I)) .GT. EPS) QUIT = .FALSE.
410   CONTINUE

C  Terminate SA if appropriate.
      IF (QUIT) THEN
	 DO 420, I = 1, N
	    X(I) = XOPT(I)
420      CONTINUE
	 IER = 0
	 IF (.NOT. MAX) FOPT = -FOPT
	 IF(IPRINT .GE. 1) CALL PRT10
	 RETURN
      END IF

C  If termination criteria is not met, prepare for another loop.
      T = RT*T
      DO 430, I = NEPS, 2, -1
	 FSTAR(I) = FSTAR(I-1)
430   CONTINUE
      F = FOPT
      DO 440, I = 1, N
	 X(I) = XOPT(I)
440   CONTINUE

C  Loop again.
      GO TO 100

      END

      FUNCTION  EXPREP(RDUM)
C  This function replaces exp to avoid under- and overflows and is
C  designed for IBM 370 type machines. It may be necessary to modify
C  it for other machines. Note that the maximum and minimum values of
C  EXPREP are such that they has no effect on the algorithm.

      DOUBLE PRECISION  RDUM, EXPREP

      IF (RDUM .GT. 174.) THEN
	 EXPREP = 3.69D+75
      ELSE IF (RDUM .LT. -180.) THEN
	 EXPREP = 0.0
      ELSE
	 EXPREP = EXP(RDUM)
      END IF

      RETURN
      END

      subroutine RMARIN(IJ,KL)
C  This subroutine and the next function generate random numbers. See
C  the comments for SA for more information. The only changes from the
C  orginal code is that (1) the test to make sure that RMARIN runs first
C  was taken out since SA assures that this is done (this test didn't
C  compile under IBM's VS Fortran) and (2) typing ivec as integer was
C  taken out since ivec isn't used. With these exceptions, all following
C  lines are original.

C This is the initialization routine for the random number generator
C     RANMAR()
C NOTE: The seed variables can have values between:    0 <= IJ <= 31328
C                                                      0 <= KL <= 30081
      real U(97), C, CD, CM
      integer I97, J97
      common /raset1/ U, C, CD, CM, I97, J97
      if( IJ .lt. 0  .or.  IJ .gt. 31328  .or.
     *    KL .lt. 0  .or.  KL .gt. 30081 ) then
	  print '(A)', ' The first random number seed must have a value
     *between 0 and 31328'
	  print '(A)',' The second seed must have a value between 0 and
     *30081'
	    stop
      endif
      i = mod(IJ/177, 177) + 2
      j = mod(IJ    , 177) + 2
      k = mod(KL/169, 178) + 1
      l = mod(KL,     169)
c print *,"i=",i," j=",j," k=",k," l=",l
      do 2 ii = 1, 97
	 s = 0.0
	 t = 0.5
	 do 3 jj = 1, 24
	    m = mod(mod(i*j, 179)*k, 179)
	    i = j
	    j = k
	    k = m
	    l = mod(53*l+1, 169)
	    if (mod(l*m, 64) .ge. 32) then
	       s = s + t
	    endif
	    t = 0.5 * t
3        continue
	 U(ii) = s
2     continue
      C = 362436.0 / 16777216.0
      CD = 7654321.0 / 16777216.0
      CM = 16777213.0 /16777216.0
      I97 = 97
      J97 = 33
c print *,"U(I97)=",U(I97)," U(J97)=",U(J97)," C=",C," CD=",
c     1     CD," CM=",CM," I97=",I97," J97=",J97
      return
      end

      function ranmar()
      real U(97), C, CD, CM
      integer I97, J97
      common /raset1/ U, C, CD, CM, I97, J97
c         print *,"U(I97)=",U(I97)," U(J97)=",U(J97)," C=",C,
c     1   " CD=",CD," CM=",CM," I97=",I97," J97=",J97 
	 uni = U(I97) - U(J97)
	 if( uni .lt. 0.0 ) uni = uni + 1.0
	 U(I97) = uni
	 I97 = I97 - 1
	 if(I97 .eq. 0) I97 = 97
	 J97 = J97 - 1
	 if(J97 .eq. 0) J97 = 97
	 C = C - CD
	 if( C .lt. 0.0 ) C = C + CM
	 uni = uni - C
	 if( uni .lt. 0.0 ) uni = uni + 1.0
	 RANMAR = uni
      return
      END

      SUBROUTINE PRT1
C  This subroutine prints intermediate output, as does PRT2 through
C  PRT10. Note that if SA is minimizing the function, the sign of the
C  function value and the directions (up/down) are reversed in all
C  output to correspond with the actual function optimization. This
C  correction is because SA was written to maximize functions and
C  it minimizes by maximizing the negative a function.

      WRITE(*,'(/,''  THE STARTING VALUE (X) IS OUTSIDE THE BOUNDS ''
     1          /,''  (LB AND UB). EXECUTION TERMINATED WITHOUT ANY''
     2          /,''  OPTIMIZATION. RESPECIFY X, UB OR LB SO THAT  ''
     3          /,''  LB(I) .LT. X(I) .LT. UB(I), I = 1, N. ''/)')

      RETURN
      END

      SUBROUTINE PRT2(MAX,N,X,F)

      DOUBLE PRECISION  X(*), F
      INTEGER  N
      LOGICAL  MAX

      WRITE(*,'(''  '')')
      CALL PRTVEC(X,N,'INITIAL X')
C      IF (MAX) THEN
C	 WRITE(*,'(''  INITIAL F: '',/, G25.18)') F
C      ELSE
C	 WRITE(*,'(''  INITIAL F: '',/, G25.18)') -F
C      END IF

      RETURN
      END

      SUBROUTINE PRT3(MAX,N,XP,X,FP,F)

      DOUBLE PRECISION  XP(*), X(*), FP, F
      INTEGER  N
      LOGICAL  MAX

      WRITE(*,'(''  '')')
      CALL PRTVEC(X,N,'CURRENT X')
      IF (MAX) THEN
	 WRITE(*,'(''  CURRENT F: '',G25.18)') F
      ELSE
	 WRITE(*,'(''  CURRENT F: '',G25.18)') -F
      END IF
      CALL PRTVEC(XP,N,'TRIAL X')
      WRITE(*,'(''  POINT REJECTED SINCE OUT OF BOUNDS'')')

      RETURN
      END

      SUBROUTINE PRT4(MAX,N,XP,X,FP,F)

      DOUBLE PRECISION  XP(*), X(*), FP, F
      INTEGER  N
      LOGICAL  MAX

      WRITE(*,'(''  '')')
      CALL PRTVEC(X,N,'CURRENT X')
      IF (MAX) THEN
	 WRITE(*,'(''  CURRENT F: '',G25.18)') F
	 CALL PRTVEC(XP,N,'TRIAL X')
	 WRITE(*,'(''  RESULTING F: '',G25.18)') FP
      ELSE
	 WRITE(*,'(''  CURRENT F: '',G25.18)') -F
	 CALL PRTVEC(XP,N,'TRIAL X')
	 WRITE(*,'(''  RESULTING F: '',G25.18)') -FP
      END IF

      RETURN
      END

      SUBROUTINE PRT5

      WRITE(*,'(/,''  TOO MANY FUNCTION EVALUATIONS; CONSIDER ''
     1          /,''  INCREASING MAXEVL OR EPS, OR DECREASING ''
     2          /,''  NT OR RT. THESE RESULTS ARE LIKELY TO BE ''
     3          /,''  POOR.'',/)')

      RETURN
      END

      SUBROUTINE PRT6(MAX)

      LOGICAL  MAX

      IF (MAX) THEN
	 WRITE(*,'(''  THOUGH LOWER, POINT ACCEPTED'')')
      ELSE
	 WRITE(*,'(''  THOUGH HIGHER, POINT ACCEPTED'')')
      END IF

      RETURN
      END

      SUBROUTINE PRT7(MAX)

      LOGICAL  MAX

      IF (MAX) THEN
	 WRITE(*,'(''  LOWER POINT REJECTED'')')
      ELSE
	 WRITE(*,'(''  HIGHER POINT REJECTED'')')
      END IF

      RETURN
      END

      SUBROUTINE PRT8(N,VM,XOPT,X)

      DOUBLE PRECISION  VM(*), XOPT(*), X(*)
      INTEGER  N

      WRITE(*,'(/,
     1  '' INTERMEDIATE RESULTS AFTER STEP LENGTH ADJUSTMENT'',/)')
      CALL PRTVEC(VM,N,'NEW STEP LENGTH (VM)')
      CALL PRTVEC(XOPT,N,'CURRENT OPTIMAL X')
      CALL PRTVEC(X,N,'CURRENT X')
      WRITE(*,'('' '')')

      RETURN
      END

      SUBROUTINE PRT9(MAX,N,T,XOPT,VM,FOPT,NUP,NDOWN,NREJ,LNOBDS,NNEW)

      DOUBLE PRECISION  XOPT(*), VM(*), T, FOPT
      INTEGER  N, NUP, NDOWN, NREJ, LNOBDS, NNEW, TOTMOV
      LOGICAL  MAX

      TOTMOV = NUP + NDOWN + NREJ

      WRITE(*,'(/,
     1  '' INTERMEDIATE RESULTS BEFORE NEXT TEMPERATURE REDUCTION'',/)')
      WRITE(*,'(''  CURRENT TEMPERATURE:            '',G12.5)') T
      IF (MAX) THEN
	 WRITE(*,'(''  MAX FUNCTION VALUE SO FAR:  '',G25.18)') FOPT
	 WRITE(*,'(''  TOTAL MOVES:                '',I8)') TOTMOV
	 WRITE(*,'(''     UPHILL:                  '',I8)') NUP
	 WRITE(*,'(''     ACCEPTED DOWNHILL:       '',I8)') NDOWN
	 WRITE(*,'(''     REJECTED DOWNHILL:       '',I8)') NREJ
	 WRITE(*,'(''  OUT OF BOUNDS TRIALS:       '',I8)') LNOBDS
	 WRITE(*,'(''  NEW MAXIMA THIS TEMPERATURE:'',I8)') NNEW
      ELSE
	 WRITE(*,'(''  MIN FUNCTION VALUE SO FAR:  '',G25.18)') -FOPT
	 WRITE(*,'(''  TOTAL MOVES:                '',I8)') TOTMOV
	 WRITE(*,'(''     DOWNHILL:                '',I8)')  NUP
	 WRITE(*,'(''     ACCEPTED UPHILL:         '',I8)')  NDOWN
	 WRITE(*,'(''     REJECTED UPHILL:         '',I8)')  NREJ
	 WRITE(*,'(''  TRIALS OUT OF BOUNDS:       '',I8)')  LNOBDS
	 WRITE(*,'(''  NEW MINIMA THIS TEMPERATURE:'',I8)')  NNEW
      END IF
      CALL PRTVEC(XOPT,N,'CURRENT OPTIMAL X')
      CALL PRTVEC(VM,N,'STEP LENGTH (VM)')
      WRITE(*,'('' '')')

      RETURN
      END

      SUBROUTINE PRT10

c      WRITE(*,'(/,''  SA ACHIEVED TERMINATION CRITERIA. IER = 0. '',/)')

      RETURN
      END

      SUBROUTINE PRTVEC(VECTOR,NCOLS,NAME)
C  This subroutine prints the double precision vector named VECTOR.
C  Elements 1 thru NCOLS will be printed. NAME is a character variable
C  that describes VECTOR. Note that if NAME is given in the call to
C  PRTVEC, it must be enclosed in quotes. If there are more than 10
C  elements in VECTOR, 10 elements will be printed on each line.

      INTEGER NCOLS
      DOUBLE PRECISION VECTOR(NCOLS)
      CHARACTER *(*) NAME

      WRITE(*,1001) NAME

      IF (NCOLS .GT. 10) THEN
	 LINES = INT(NCOLS/10.)

	 DO 100, I = 1, LINES
	    LL = 10*(I - 1)
	    WRITE(*,1000) (VECTOR(J),J = 1+LL, 10+LL)
  100    CONTINUE

	 WRITE(*,1000) (VECTOR(J),J = 11+LL, NCOLS)
      ELSE
	 WRITE(*,1000) (VECTOR(J),J = 1, NCOLS)
      END IF

 1000 FORMAT( 10(G12.5,1X))
 1001 FORMAT(/,25X,A)

      RETURN
      END




      SUBROUTINE FCN(MDUMMY,LAMBDA,H)    

      INTEGER I,J,NB,M,N,N0,MP1
      DOUBLE PRECISION SUM1,SUM2,SUM3,SUM4
      REAL FLUX,OMEGA
      DOUBLE PRECISION LAMBDA(30),H
      DOUBLE PRECISION B(100,1000)
      REAL S(100),D(100),FI(1000),MM(10000)
      
      COMMON S,D,FI,MM,FLUX,OMEGA,NB,M,N,N0,MP1    

c	print *," N=",N," M=",M," NB",NB," OMEGA=",OMEGA," FLUX=",FLUX

      DO 6 I=1,M
	DO 4 J=1,NB
	  B(I,J) = DBLE(MM(NB*(I-1)+J))
4       CONTINUE
6     CONTINUE

      SUM1 = 0.0
      DO 12 J=1,NB
	SUM2 = 0.0
	DO 10 I=1,M
	  SUM2 = SUM2 + LAMBDA(I)*B(I,J)    
10      CONTINUE
	SUM1 = SUM1 + DBLE(FI(J))*DEXP(-SUM2)
12    CONTINUE

      SUM3 = 0.0
      SUM4 = 0.0
      DO 14 I=1,M
	SUM3 = SUM3 + (DBLE(S(I))*LAMBDA(I))**2
	SUM4 = SUM4 + LAMBDA(I)*DBLE(D(I))
c        print *,"SUM3=",SUM3," SUM4=",SUM4," S=",S(I),
c     1  " LAMBDA=",LAMBDA(I)," D=",D(I)
14    CONTINUE

c	print *," SUM1=",SUM1," SUM2=",SUM2," SUM3",SUM3," SUM4=",SUM4
c        print *," OMEGA=",OMEGA," FLUX=",FLUX

      H = -SUM1-DSQRT(DBLE(OMEGA)*SUM3)-SUM4+DBLE(FLUX)

c	print *,"In FCN F=",H

	

      RETURN 
      END
     
