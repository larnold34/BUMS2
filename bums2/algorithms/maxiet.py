#The following script will apply the maxiet initial spectrum algorithm
#This script is a more modular approach as opposed to the 300-line beast the original is
import numpy as np
from typing import Tuple

from bums2.core.config import Bums2Config

class maxiet:
    def __init__(self, cfg: Bums2Config):
        self.tempij = cfg.tempij
        self.tempi = cfg.tempi
        self.shape = cfg.shape
        self.pertmp = cfg.perturbation
        self.perslp = cfg.perslp
        self.perthm = cfg.perthm
        self.pere = cfg.pere
        self.slpmin = cfg.slpmin
        self.slpmax = cfg.slpmax
        self.themmin = cfg.themmin
        self.themmax = cfg.themmax                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        self.whtbce = None #set during run time
        self.cfg = cfg

        
    def maxiet_spectrum(
            self,
            ce: np.ndarray,
            bce: np.ndarray,
            aleth: np.ndarray,
            errbce: np.ndarray,
            whtbce: np.ndarray,
            out
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        #The 5 nested loops will be made in sequence through various functions
        #The overall structure is as follows:
        #1. Outer do loop over temperature(level 1)
        #2. Middle do loop over slope and therm(level 2)
        #3. Inner loops(3, 4, 5) that build and fit spli[]
        #4. Final build of spectrum with best parameters

        num_det, num_groups = aleth.shape
        self.whtbce = whtbce

        #Initialize
        spli = np.zeros_like(ce)
        splmax = np.zeros_like(ce)
        

        slope_i = self.cfg.slopei
        therm_i = self.cfg.thermi
        temp = self.tempi

        #Error trackers
        hgte_best = 0.0
        slope_best = slope_i
        therm_best = therm_i

        print("-"*80, file=out)
        print("Running MAXIET fit algorithm.", file=out)
        print("Temp  Shape HGTE    SLOPE  THERM    ERROR", file=out)
        print("----  ----- ------  -----  ------   ------", file=out)

        a4 = 1
        # ─── LEVEL 1 LOOP ─────────────────────────────────────────────────────────
        while a4 > 0.5:
            slpmin = self.slpmin
            slpmax = self.slpmax
            errore = np.inf
            temp = self.tempi
            errorm = errore
            test2 = True
            # ─── LEVEL 2 LOOP ─────────────────────────────────────────────────────────
            while test2:
                slope = slope_i
                therm = therm_i
                spmx = 0.0

                #Build the Maxwellian
                splmax, spmx = self._compute_maxwellian(ce, temp, spmx)

                #Calculate 1/E spectrum
                errore = np.inf
                hgte = spmx * self.pere
                errort = np.inf
                hgte = hgte / self.pere

                #Build and fit the 1/E + Maxwellian spectrum
                spli, hgte, slope_e, therm_e, err_e, bcc = self._fit_1overE_plus_max(ce, 
                                                                                    aleth, 
                                                                                    bce, 
                                                                                    errbce, 
                                                                                    splmax, 
                                                                                    hgte, 
                                                                                    slope, 
                                                                                    therm,  
                                                                                    errort, 
                                                                                    errore, 
                                                                                    slpmax)

                #Calculate the percent error on fit
                perror = 100 * (err_e/num_det)**.5

                #Write best values of fit to terminal
                print(
                    f"{temp:>4.2f}  "
                    f"{self.shape:>4.2f} "
                    f"{hgte:>6.4f}    "
                    f"{slope_e:>4.2f}  "
                    f"{therm_e:>7.3f}    "
                    f"{perror:>7.3f}",
                    file=out
                )

                test2 = False
                #If the fit is better, store the new variables
                if err_e < errorm:
                    tempm = temp
                    errorm = err_e
                    hgte_best = hgte
                    slope_best = slope_e
                    therm_best = therm_e

                    #Update Maxwellian temperature if needed
                    #Return and search for better parameters if maxwellian temp is in range
                    if self.pertmp != 0:
                        temp = temp - self.pertmp
                        if temp > self.pertmp:
                            test2 = True
                        else:
                            test2 = False
                else:
                    test2 = False
            #End of level 2
            a1 = int(slope_best == slope_i and slope_i > slpmin)
            a2 = int(therm_best == therm_i and therm_i >= self.themmin)
            a3 = int(tempm == self.tempi and tempm < (self.tempij + 10*self.pertmp))
            if self.pertmp == 0:
                a3 = 0

            if a1: slope_i -= 10*self.perslp
            if a2: therm_i /= self.perthm**3
            if a3: self.tempi += 3*self.pertmp
            a4 = a1 + a2 + a3
        #end of level 1
        #Build the final spectrum
        spmx = 0.0
        for i in range(num_groups):
            splmax[i] = (ce[i]**1.5)*np.exp(-ce[i]/tempm)
            if splmax[i] > spmx:
                spmx = splmax[i]
            if spmx != splmax[i]:
                splmax[i] = (spmx**self.shape) * (splmax[i]**(1.0-self.shape))
                if splmax[i] < splmax[i-1] * self.shape:
                    splmax[i] = splmax[i-1] * self.shape
        
        for i in range(num_groups):
            spli[i] = hgte_best * ce[i]**slope_best
        
        for i in range(num_groups):
            if spli[i] >= splmax[i]:
                spli[i] = (spli[i]+splmax[i]*0.5)
            else:
                isave = i
                i = num_groups+1

        for j in range(isave, num_groups):
            spli[j] = splmax[j]

        spli[0] = spli[1] * therm_best
        return spli, tempm
                
   
    #This first function will apply the actual logic within the nested loop for generating the Maxwellian
    def _compute_maxwellian(self, ce: np.ndarray, temp: float, spmx: float) -> Tuple[np.ndarray, float]:
        #Loop 2 fills splmax into all the bins applies a shape factor correction
        splmax = np.empty_like(ce)
        for i, e in enumerate(ce):
            val = e**1.5 * np.exp(-e/temp)
            if val > spmx:
                spmx = val
            else:
                val = spmx**self.shape * val**(1.0 - self.shape)
                val = max(val, splmax[i-1] * self.shape)
            splmax[i] = val
        return splmax, spmx
    
    #This next function will apply the logic of the inner loops
    #It will combine the 1/E spectrum and the Maxwellian by calling a helper function
    #Then it will keep sweeping to find the best parameters before returning to level 2
    def _fit_1overE_plus_max(
            self,
            ce: np.ndarray,
            aleth: np.ndarray,
            bce: np.ndarray,
            errbce: np.ndarray,
            splmax: np.ndarray,
            hgte: float,
            slope: float,
            therm: float,
            errort: float,
            errore: float,
            slpmax: float
        ) -> Tuple[np.ndarray, float, float, float, float]:
        num_det, num_groups = aleth.shape

        #Initialize
        # err_best = np.inf
        slope_e = slope
        therm_e = therm
        bcc = np.zeros_like(ce)

        while True: #level 3
            
            while True: #level 4

                spli, hgte, h = self._1overE_plus_max(ce, num_groups, slope, splmax, hgte)

                for j in range(h, num_groups):
                    spli[j] = splmax[j]

                #Adjust thermal energy bin
                spli[0] = spli[1] * therm

                #Calculate sphere response and sum from spectrum
                for m in range(num_det):
                    bcc[m] = 0
                    for j in range(num_groups):
                        bcc[m] = bcc[m] + aleth[m, j] * spli[j]

#-------------------------------------------------------------
# Old scaling method
#                               calculate sums of sphere data   
#				$sumbce=0;   
#				$sumbcc=0;   
#				for ($i=0;$i<$num_det;$i++){
#					$sumbce=$sumbce+$bce[$i]; 
#					$sumbcc=$sumbcc+$bcc[$i];
#					print "det=$i sumbce=$sumbce sumbcc=$sumbcc",br;
#				}
#                                normalize calculated sphere responses     
#                                to experimental data  
#				$rnorm=$sumbce/$sumbcc;  
#				print "rnorm=$rnorm",br;
# -------------------------------------------------

                #Least squares fit scaling
                sum1, sum2 = 0.0, 0.0

                for i in range(num_det):
                    sum1 += (bce[i] * bcc[i]) / errbce[i]**2
                    sum2 += (bcc[i]**2) / errbce[i]**2
                
                rnorm = sum1/sum2

                #Normalize the exepectd Bonner sphere counts
                for i in range(num_det):
                    bcc[i] = bcc[i] * rnorm

                #Calulate the error on fit 
                error = 0

                for i in range(num_det):
                    err = (bcc[i] - bce[i]) / bce[i]
                    error = error + self.whtbce[i] * err**2

                test3 = False
                if error < errort:
                    errort = error
                    hgte = hgte / self.pere
                    test3 = True
                if not test3:
                    break
                
            #End of level 4
            hgte *= self.pere

            #Save best fit values
            if errort < errore:
                errore = errort
                hgtee = hgte
                therm_e = therm
                slope_e = slope
                mx = 0.0

            #Update the slope
            if slope < slpmax:
                slope += self.perslp
            if mx == 1:
                slope = slope_e
            

            #Update thermal bin
            therm = therm_e * self.perthm
            test1 = False
            if therm < self.themmax:
                if mx == 0:
                    therm = therm_e
                mx += 1
                if mx <= 10:
                    hgte = hgte * self.pere * (1.0 + 10 * self.perslp)
                    if mx == 1:
                        hgte = hgtee * self.pere * self.perthm

                    #Reset the error for better fit parameters
                    errort = np.inf
                else:
                    test1 = True
            else:
                test1 = True
            
            if test1:
                break
        #End of level 3
        return spli, hgtee, slope_e, therm_e, errore, bcc
    
    #This next function will be applying the inner loop 5
    def _1overE_plus_max(self, ce: np.ndarray, num_groups: float, slope: float, splmax: np.ndarray, hgte: float) -> Tuple[np.ndarray, np.ndarray, float]:
        spli = np.zeros_like(ce)
        while True: #level 5
            crossed = False

            for i in range(num_groups):
                spli[i] = hgte * ce[i] ** slope

            #Combine the Maxwellian and the 1/E spectra
            for i in range(num_groups):
                if spli[i] < splmax[i]:
                    h = i
                    i = num_groups+1
                    crossed = True
                else:
                    spli[i] = (spli[i] + splmax[i]) * 0.5
                
            if not crossed:
                hgte = hgte / self.pere
            else:
                break
        #End or level 5
        return spli, hgte, h




            
    

    
