#This file will be the equivalent of responsel.pl from the oringinal MAXED directory
import numpy as np

class ResponseMapper:
    def __init__(self, res, rfn, enbf, enbr, m, nb, nb1):
        self.RES = np.array(res)
        self.RFN = np.array(rfn)
        self.ENBF = np.array(enbf)
        self.ENBR = np.array(enbr)
        self.M = m
        self.NB = nb
        self.NB1 = nb1

        self.B = np.zeros((self.M, self.NB))

    def map_response(self):
        for k in range(self.NB1):
            for l in range(self.NB):
                r2 = np.log(self.ENBR[l + 1]) - np.log(self.ENBF[l])

                if self.ENBF[l] <= self.ENBR[k] < self.ENBF[l + 1]:
                    if self.ENBF[l + 1] >= self.ENBR[k + 1]:
                        r1 =  np.log(self.ENBR[k + 1]) - np.log(self.ENBR[k])

                        for i in range(self.M):
                            J = self.RFN[i]-1
                            self.B[i, l] += self.RES[J, k] * r1/r2

                    elif self.ENBF[l + 1] < self.ENBR[k + 1]:
                        r1 = np.log(self.ENBF[l + 1]) - np.log(self.ENBR[k])

                        for i in range(self.M):
                            J = self.RFN[i]
                            self.B[i, l] += self.RES[J, k] * r1/r2
                
                elif self.ENBR[k] < self.ENBF[l] < self.ENBR[k + 1]:
                    if self.ENBF[l + 1] <= self.ENBR[k + 1]:
                        r1 = np.log(self.ENBF[l + 1]) - np.log(self.ENBF[l])

                        for i in range(self.M):
                            J = self.RFN[i]
                            self.B[i, l] += self.RES[J, k] * r1/r2
                    
                    elif self.ENBF[l + 1] > self.ENBR[k + 1]:
                        r1 = np.log(self.ENBR[k + 1]) - np.log(self.ENBF[l])

                        for i in range(self.M):
                            J = self.RFN[i]
                            self.B[i, l] += self.RES[J, k] * r1/r2
        return self.B



        