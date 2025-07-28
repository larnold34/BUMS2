#The following script will be doing the same logic as sum_data.pl
import numpy as np
from dataclasses import dataclass
from typing import Sequence, Mapping, Optional

from bums2.utils.dose import DoseConverter
from bums2.core.config import Bums2Config

@dataclass
#All the parameters needed for the sum_data, cause there is never enough parameters
class Summary:
    splplt: np.ndarray
    spc: np.ndarray
    spl: np.ndarray
    sumspc: float
    rem: np.ndarray
    sumrem: float
    #rad: np.ndarray
    #sumrad: float
    pcterr: np.ndarray
    perror: float
    prem: np.ndarray
    aveen: Optional[float]
    tld: float
    han: float
    nutrk: float
    nta: float
    a70: float

#The actual calculations
class SummaryCalculator:
    def __init__(self,
                 ce: Sequence[float],
                 wdleth: Sequence[float],
                 spli: Sequence[float],
                 spl: Sequence[float],
                 alethnew: np.ndarray,
                 bce: Sequence[float],
                 bcc: Sequence[float],
                 errbce: Sequence[float],
                 cal: float,
                 df: DoseConverter,
                 cfg: Bums2Config,
                 ctld:   Optional[np.ndarray] = None,
                 chan:   Optional[np.ndarray] = None,
                 cnutrk: Optional[np.ndarray] = None,
                 cnta:   Optional[np.ndarray] = None,
                 ca70:   Optional[np.ndarray] = None):
        self.ce = ce
        self.wdleth = wdleth
        self.spli = spli
        self.spl = spl
        self.alethnew = alethnew
        self.bce = bce
        self.bcc = bcc
        self.errbce = errbce
        self.cal = cal
        self.df = df
        self.cfg = cfg

        self.ctld = ctld or np.zeros_like(ce)
        self.chan = chan or np.zeros_like(ce)
        self.cnutrk = cnutrk or np.zeros_like(ce)
        self.cnta = cnta or np.zeros_like(ce)
        self.ca70 = ca70 or np.zeros_like(ce)

        self.num_det = self.bce.size
        self.num_grp = self.spl.size

        N = self.spli.shape[0]
        self.splplt = np.zeros((N, 1), dtype=self.spli.dtype)

    def compute(
            self,
            alg: str,
            start_spec: str,
            iter_count: int,
            tempij: float
    ) -> Summary:
        #Apply inverse transform of spectrum and matrix if not MAXED or SAND
        if not (alg.upper() in ("MAXED","SANDII")):
            for i in range(self.num_grp):
                self.spl[i] *= self.spli[i]

        pcterr = np.zeros_like(self.bce)
        perror = 0.0
        if start_spec.upper().startswith("MAXIET") or iter_count != 0:
            #There is a line in the original that updates hgte_best as $hgtem=0.5*$hgtem/$spmx;
            #However this is not used outside of maxiet and is not called in the output file
            #Not sure why this is done at all, just another pointless line
            sumerr = 0               
            for i in range(self.num_det):
                pcterr[i] = 100 * (self.bcc[i] - self.bce[i]) / self.bce[i]
                sumerr += pcterr[i]**2
            perror = (sumerr / self.num_det)**0.5

        #sumrad will be removed cause of below
        sumspc = sumnta = sumrem = sumexs = sumtld = sumhan = sumntr = suma70 = 0.0
        print(f"DEBUG: spl before summation for summary = {self.spl}")
        spc = np.zeros(self.num_grp)
        rem = np.zeros(self.num_grp)
        #rad = np.zeros(self.num_grp)
        prem = np.zeros(self.num_grp)
        splplt = np.zeros((self.num_grp, 1))

        hour_sec = 1/3600
        for i in range(self.num_grp):
                
            crem_i = self.df.dfact(
                    particle_id=1,
                    ic=40,
                    energy=self.ce[i],
                    interp_method=1,
                    units=1,
                    acr=hour_sec
                )

            self.spl[i] *= self.cal
            splplt[i, self.cfg.kx-1] = self.spl[i]
            spc[i] = self.spl[i] * self.wdleth[i]
            sumspc += spc[i]

            rem[i] = crem_i * spc[i]
            sumrem += rem[i]
            if rem[i] < 1.0e-37: rem[i] = 0

                #Originally rad was $rad[$i]=$crad[$i]*$spc[$i];, however $crad was never initialized anywhere in the original perl
                #The only line that had crad in it was commentted out by the original creator as #      $crad[$i]= &ede($ce[$i]); 
                #This is also the only instance of ede.pl being called, no comments or anything on to why this was the case
                #Since crad is undefined, perl would just make it zero, which means rad will always be zero?
                #These parameters eventually amount to nothing, never called and always set to zero
                #These lines will be commentted out unless it turns out something actually uses them
                # rad[i] *= spc[i]
                # sumrad += rad[i]
                # if rad[i] < 1.0e-37: rad[i] = 0

            sumexs += self.ce[i] * spc[i]
            sumtld += self.ctld[i] * spc[i]
            sumhan += self.chan[i] * spc[i]
            sumntr += self.cnutrk[i] * rem[i]
            sumnta += self.cnta[i] * rem[i]
            suma70 += self.ca70[i] * spc[i]

        if sumspc - spc[1] > 0:
            aveen = (sumexs - self.ce[1] * spc[1]) / (sumspc - spc[1])
            
        if sumrem > 0:
            sumtld = (sumtld/sumrem) / 4.155e6
            sumhan = (sumhan/sumrem) / 2.085e6
            sumntr = (sumntr/sumrem) / 0.56905
            sumnta = (sumnta/sumrem) / 7.9607
            suma70 = (suma70/sumrem) / 4.4079e6

            for i in range(self.num_grp):
                prem[i] = 100 * (rem[i]/sumrem)

        return Summary(
                splplt= splplt,
                spc= spc,
                spl= self.spl,
                sumspc= sumspc,
                rem= rem,
                sumrem= sumrem,
                pcterr= pcterr,
                perror= perror,
                prem = prem,
                aveen= aveen,
                tld= sumtld,
                han= sumhan,
                nutrk= sumntr,
                nta= sumnta,
                a70= suma70
            )


                
                

        

