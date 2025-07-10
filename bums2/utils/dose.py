#This script will be the combination between ede.pl and dfact.pl
#ede.pl was in charge of doing the energy to dose conversion
#dfact.pl was in charge of doing dose conversion factor logic
from math import log, exp, log10
from typing import List
from bums2.utils.interpolate import Interpolator

class DoseConverter:
    #  Take from function dfact from MCNPX 2.1.6 
#
#ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
#
#       returns tissue equivalent fluence to dose conversion factor in
#             (rem/hr)/(particles/cm^2-sec)
#       id=particle id number
#               1=neutron
#               2=photon
#               3=electron
#               4=positron
#       ic=choice of conversion factor
#         (feel free to add others, just try to stay consistent with
#           variable names and numbering system)
#             Note:  10 and 20 are Dose Equivalent (H): absorbed dose at
#                     "point" in tissued weighted by a distribution of
#                     quality factors (Q) related to the LET distributio
#                     of radiation at that point.
#                    30's are Equivalent Dose (H_t): based on an average
#                     absorbed dose in the tissue or organ (D_t) and wei
#                     by the radiation weighting factor (w_r), summed ov
#                     all component radiations
#         neutrons:
#                   10 = ICRP-21 1971
#                   20 = NCRP-38 1971, ANSI/ANS-6.1.1-1977
#                   31 = ANSI/ANS-6.1.1-1991 (AP anterior-posterior)
#                   32                       (PA posterior-anterior)
#                   33                       (LAT side exposure)
#                   34                       (ROT normal to length &
#                                                rotationally symmetric)
#                   40 = ICRP-74 1996 ambient dose equivalent
#
#         photons:  10 = ICRP-21 1971
#                   20 = Claiborne & Trubey, ANSI/ANS 6.1.1-1977
#                   31 = ANSI/ANS-6.1.1-1991 (AP anterior-posterior)
#                   32                       (PA posterior-anterior)
#                   33                       (LAT side exposure)
#                   34                       (ROT normal to length &
#                                                rotationally symmetric)
#                   35                       (ISO isotropic)
#       en=particle energy
#       it=interpolation method
#         1 = logarythmic(x)-linear(y) interpolation
#         2 = linear interpolation
#         3 = linear(x)-log(y) interpolation
#         4 = log-log interpolation
#         5 = recommended analytic parametarization
#              (not available for ic=10 and ic = 40)
#       iu=units of dfact
#         1 = (rem/hr)(particles/cm^2-sec)
#         2 = (seiverts/hr)(particles/cm^2-sec)
#       acr=normalize factor for neutron dose
#      -1.0 =  normalize dfact to Q=20 by dividing out parametric form
#            Q (or w_r)=5.0+17.0*exp(-(ln(2E))*2/6)
#            from ICRP60 (1990) paragraph A12
#      -2.0 =  apply LAMPF albatross correction factors
#            (use this with ic=10 per work by WNR)
#      dfact will be multiplied by any factor greater or equal to 0.0
#            e.g., acr=1.0 means no change
#
#cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
#
    def __init__(self):
        #All of the following are the tables from dfact.pl
        self._elim_n_1=[2.5e-8,1.0e-7,1.0e-6,1.0e-5,1.0e-4,1.0e-3,1.0e-2,
      1.0e-1,5.0e-1,1.0,2.0,5.0,10.0,20.0,50.0,100.0,200.0,500.0,
      1000.0,2000.0,3000.0]
        
        self._fct_n_1=[3.85e-6,4.17e-6,4.55e-6,4.35e-6,4.17e-6,3.70e-6,
      3.57e-6,2.08e-5,7.14e-5,1.18e-4,1.43e-4,1.47e-4,1.47e-4,
      1.54e-4,1.64e-4,1.79e-4,1.96e-4,2.78e-4,4.55e-4,6.24e-4,
      7.14e-4]
        
        self._q_n_1=[2.3,2.0,2.0,2.0,2.0,2.0,2.0,7.4,11.0,10.6,9.3,7.8,
      6.8,6.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
        
        self._elim_n_2=[2.5e-8,1.0e-7,1.0e-6,1.0e-5,1.0e-4,1.0e-3,1.0e-2,
     1.0e-1,5.0e-1,1.0,2.5,5.0,7.0,10.0,14.0,20.0,40.0,60.0,100.0,
     200.0,300.0,400.0]
        
        self._fct_n_2=[3.67e-6,3.67e-6,4.46e-6,4.54e-6,4.18e-6,3.76e-6,
     3.56e-6,2.17e-5,9.26e-5,1.32e-4,1.25e-4,1.56e-4,1.47e-4,
     1.47e-4,2.08e-4,2.27e-4,2.5E-4,2.27e-4,1.78e-4,1.92e-4,
     2.27e-4,2.5e-4]
        
        self._q_n_2=[2.0,2.0,2.0,2.0,2.0,2.0,2.5,7.5,11.0,11.0,9.0,8.0,
     7.0,6.5,7.5,8.0,7.0,5.5,4.0,3.5,3.5,3.5]
        
        self._elim_n_3=[2.5e-8,1.0e-7,1.0e-6,1.0e-5,1.0e-4,1.0e-3,1.0e-2,
     2.0e-2,5.0e-2,1.0e-1,2.0e-1,5.0e-1,1.0,1.5,2.0,3.0,4.0,5.0,
     6.0,7.0,8.0,10.0,14.0]
        
        self._fct_n_3=[[4.0,4.4,4.82,4.46,4.14,3.83,4.53,5.87,10.9,19.8,
     38.6,87.0,143.0,183.0,214.0,264.0,300.0,327.0,347.0,365.0,
     380.0,410.0,480.0],
     [2.6,2.7,2.81,2.78,2.63,2.49,2.58,2.79,3.64,5.69,8.6,30.8,
     53.5,85.8,120.0,174.0,215.0,244.0,265.0,283.0,296.0,321.0,
     415.0],
     [1.3,1.4,1.43,1.33,1.27,1.19,1.27,1.46,2.14,3.57,6.94,18.7,
     33.3,52.1,71.8,105.0,131.0,151.0,167.0,181.0,194.0,218.0,
     280.0],
     [2.3,2.4,2.63,2.48,2.33,2.18,2.41,2.89,4.7,8.15,15.3,38.8,
     65.7,93.7,120.0,162.0,195.0,219.0,237.0,253.0,266.0,292.0,
     365.0]]
        
        self._ana_n_3_lo=[
     [3.430895e+0,7.725710e-1,9.834081e-2,4.903466e-3,8.149667e-5],
     [3.687778e+0,1.240448e+0,1.888331e-1,1.164621e-2,2.516630e-4],
     [8.677172e-1,2.290812e-1,2.457221e-2,7.646448e-4,0.0],
     [2.436148e+0,6.502219e-1,8.819417e-2,4.752092e-3,8.782611e-5]]
        
        self._ana_n_3_md=[
     [0.0,0.0,0.0,0.0,0.0],
     [3.965468e+0,1.012777e+0,3.608077e-1,-5.689570e-2,-2.047265e-1],
     [0.0,0.0,0.0,0.0,0.0],
     [0.0,0.0,0.0,0.0,0.0]]
        
        self._ana_n_3_hi=[
     [4.952167e+0,6.644235e-1,-1.017445e-1,-1.496004e-3,3.636748e-3],
     [3.965468e+0,1.078553e+0,3.607919e-1,-4.288176e-1,9.411842e-2],
     [3.577644e+0,1.005248e+0,-4.227422e+0,-2.054736e-2,4.461858e-4],
     [4.216783e+0,8.470534e-1,-6.771566e-2,-1.213208e-2,1.829400e-3]]
#
#   ICRP-74, 1996
#
        self._elim_n_4=[
     1.E-09,1.E-08,2.53E-08,1.E-07,2.E-07,5.E-07,1.E-06,2.E-06,
     5.E-06,1.E-05,2.E-05,5.E-05,1.E-04,2.E-04,5.E-04,1.E-03,
     2.E-03,5.E-03,0.01,0.02,0.03,0.05,0.07,0.1,0.15,0.2,0.3,0.5,
     0.7,0.9,1.,1.2,2.,3.,4.,5.,6.,7.,8.,9.,10.,12.,14.,15.,16.,
     18.,20.,30.,50.,70.,100.,125.,150.,175.,201.]

        self._fct_n_4=[
     2.376E-06,3.240E-06,3.816E-06,4.644E-06,4.860E-06,4.896E-06,
     4.788E-06,4.644E-06,4.320E-06,4.068E-06,3.816E-06,3.564E-06,
     3.384E-06,3.204E-06,2.988E-06,2.844E-06,2.772E-06,2.880E-06,
     3.780E-06,5.976E-06,8.532E-06,1.480E-05,2.160E-05,3.168E-05,
     4.752E-05,6.120E-05,8.388E-05,1.159E-04,1.350E-04,1.440E-04,
     1.498E-04,1.530E-04,1.512E-04,1.483E-04,1.469E-04,1.458E-04,
     1.440E-04,1.458E-04,1.472E-04,1.512E-04,1.584E-04,1.728E-04,
     1.872E-04,1.944E-04,1.998E-04,2.052E-04,2.160E-04,1.854E-04,
     1.440E-04,1.188E-04,1.026E-04,9.360E-05,8.820E-05,9.000E-05,
     9.360E-05]

        self._n_1=21
        self._n_2=22
        self._n_3=23
        self._n_4=55
    
    def dfact(self,
              particle_id: int,
              ic: int,
              energy: float,
              interp_method: int,
              units: int,
              acr: float
              ) -> float:
        if particle_id == 1:
            return self._neutron_dfact(ic, energy, interp_method, units, acr)
        if particle_id == 2:
            return self._photon_dfact(ic, energy, interp_method, units, acr)
        if particle_id == 3:
            return self._electron_dfact(ic, energy, interp_method, units, acr)
        if particle_id == 4:
            return self._positron_dfact(ic, energy, interp_method, units, acr)
        else:
            raise ValueError(f"Unknown particle id {particle_id}")
        
    def _neutron_dfact(self, ic, E, it, iu, acr) -> float:
        if ic == 10:
            if it < 5:
                df = self._interpolate(it, E, self._elim_n_1, self._fct_n_1)

            else:
                raise ValueError(f"it={it} not supported for ic={ic}")

        elif ic == 20:
            if it < 5:
                df = self._interpolate(it, E, self._elim_n_2, self._fct_n_2)

            elif it == 5:
                X = log(E)
                if (E <= 1.0e-7):
                    df=-1.2514e+1
                elif(E > 1.0e-7 and E <= 1.0e-2):
                    df = -1.2210e+1 + 1.7165e-1 * X + 2.6034e-2 * X**2 + 1.0273e-3* X**3
                elif(E > .01 and E <= .1):
                    df = -8.9302 + 7.8440e-1* X
                elif(E > .1 and E <= .5):
                    df = -8.6632 + 9.0037e-1 * X
                elif(E > .5 and E <= 1.0):
                    df= -8.9359 + 5.0696e-1 * X
                elif(E > 1.0 and E <= 2.5):
                    df= -8.9359 - 5.5979e-2 * X
                elif(E > 2.5 and E <= 5.0):
                    df= -9.2822 + 3.2193e-1 * X
                elif(E > 5.0 and E <= 7.0):
                    df= -8.47441 - 1.8018e-1 * X
                elif(E > 7.0 and E <= 10.0):
                    df= -8.8247
                elif(E > 10.0 and E <= 14.0):
                    df= -1.1208e+1 + 1.0352 * X
                elif(E > 14.0):
                    df= -9.1202 + 2.4395e-1 * X
                else:
                    raise ValueError(f"it={it} not supported for ic={ic}")
                df = exp(df)

        elif(ic > 30 and ic < 35):
            index = ic - 31
            if it < 5:
                df = self._interpolate(it, E, self._elim_n_3, self._fct_n_3[index])
                df *= 1.0e-12 * 100.0 * 3600.0

            elif it == 5:
                X = log(E)
                df = 0.0
                for i in range(5):
                    if index != 1:
                        coeffs = (self._ana_n_3_lo if E <= 0.01 else self._ana_n_3_hi)[index]
                    else:
                        if E <= 0.2:
                            coeffs = self._ana_n_3_lo[index]
                        elif E <= 1.0:
                            coeffs = self._ana_n_3_md[index]
                        else:
                            coeffs = self._ana_n_3_hi[index]
                    df += coeffs[i] * X**i  
                df = exp(df) * 1.0e-12 * 100.0 * 3600.0
            else:
                raise ValueError(f"it={it} not supported for ic={ic}")

        elif ic == 40:
            if it < 5:
                df = self._interpolate(it, E, self._elim_n_4, self._fct_n_4)

            else:
                raise ValueError(f"it={it} not supported for ic={ic}")
        else:
            raise ValueError(f"Unknown neutron ic={ic}")
        
        
        #rem to sv conversion
        if iu == 2:
            df /= 100.0
        
        #Correction factors from dfact.pl
        if acr == -1.0:
            df *= 20.0 / (5.0 + 17.0*exp(-1.0*(log(2.0*E))**2/6.0))
        elif acr == -2.0:
            if E < 0.25:
                df = df * 2.5
            else:
                X = log10(E)
                df *= (1.4229 - 1.152*X + 0.78732*X**2 - 0.24341*X**3)
        else:
            df *= acr
        return df
    
    def _interpolate(self, it: int, E: float, X: List[float], Y: List[float]):
        if len(X) != len(Y):
            raise ValueError("X and Y must be the same length")
        
        if E < X[0]:
            return Y[0]
        
        if E >= X[-1]:
            return Y[-1]
        
        else:
            if it == 1:
                return Interpolator.log_linear(E, X, Y)
            elif it == 2:
                return Interpolator.linear(E, X, Y)
            elif it == 3:
                return Interpolator.linear_log(E, X, Y)
            elif it == 4:
                return Interpolator.log_log(E, X, Y)
            else:
                raise ValueError(f"Invalid interpolation type: it={it}")
    
    
#There is currently no ede function due to the fact that it is never actually used in original BUMS
#It is required in a couple of siles, but is only ever called once, and that line was commentted out before any edits were being dont to the repo
#This script/function will be ignored.
        
