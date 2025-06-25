#The following script will fill the role of Interpolat.pm and IntervalSearch.pm
#Both have been combined here just for simplicity
from math import log, exp
from typing import List, Callable, Optional
import bisect

# #This first calls will be the python version of IntervalSearch
class IntervalSearch:
    _last = 0

    @staticmethod
    def search(x, sequence):
        n = len(sequence)
        # Empty sequence
        if n == 0:
            return -1

        # Single‐point sequence
        if n == 1:
            IntervalSearch._last = 0
            return 0 if x >= sequence[0] else -1

        # x below first
        if x < sequence[0]:
            IntervalSearch._last = 0
            return -1

        # x at or above last
        if x >= sequence[-1]:
            IntervalSearch._last = n - 1
            return n - 1

        # Start from last result (for locality)
        ilo = IntervalSearch._last
        if ilo > n - 2:
            ilo = n - 2
        ihi = ilo + 1

        # ======= doubling phase downwards =======
        step = 1
        while x < sequence[ilo]:
            ihi = ilo
            ilo = max(0, ilo - step)
            if ilo == 0:
                break
            step *= 2

        # ======= doubling phase upwards =======
        step = 1
        while x >= sequence[ihi]:
            ilo = ihi
            ihi = min(n - 1, ihi + step)
            if ihi == n - 1:
                break
            step *= 2

        # ======= bisection phase =======
        # at this point sequence[ilo] <= x < sequence[ihi]
        max_iters = n.bit_length() + 2
        for _ in range(max_iters):
            middle = (ilo + ihi) // 2
            if middle == ilo:
                IntervalSearch._last = ilo
                return ilo
            if x < sequence[middle]:
                ihi = middle
            else:
                ilo = middle

        # fallback if something odd happened
        IntervalSearch._last = ilo
        return ilo


#This next class will be the python version of Interpolate.pm
class Interpolator:


    @staticmethod
    def derivatives(X: List[float], Y: List[float]) -> List[float]:
        n = len(X)
        if n != len(Y) or n < 2:
            return []
        if n == 2:
            slope = (Y[1]-Y[0]) / (X[1]-X[0])
            return [slope, slope]

        deriv = [0.0]*n

        #Determine the interior derivatives
        for i in range(1, n-1):
            xi, xj, xk = X[i-1], X[i], X[i+1]
            yi, yj, yk = Y[i-1], Y[i], Y[i+1]
            r1 = (xk - xj)**2 + (yk - yj)**2
            r2 = (xj - xi)**2 + (yj - yi)**2
            deriv[i] = ((yj-yi)*r1 + (yk-yj)*r2) / ((xj-xi)*r1 + (xk-xj)*r2)

        #Determine the endpoint derivatives
        for i, j in((0,1), (n-1, n-2)):
            slope = (Y[j]-Y[i]) / (X[j]-X[i])
            d_neigh = deriv[i]
            if (slope >= 0 and slope >= d_neigh) or (slope <= 0 and slope <= d_neigh):
                deriv[i] = 2*slope - d_neigh
            else:
                deriv[i] = slope + (abs(slope)*(slope - d_neigh)) / (abs(slope)+abs(slope - d_neigh))
        return deriv
    
    @staticmethod
    def constant(x: float, X: List[float], Y: List[float]) -> float:
        j = IntervalSearch.search(x, X)
        if j < 0:
            return Y[0]
        if j >= len(Y):
            return Y[-1]
        return Y[j]
    
    @staticmethod
    def linear(x: float, X: List[float], Y: List[float]) -> float:
        j = IntervalSearch.search(x, X)
        j = max(0, min(j, len(X)-2))
        k = j + 1
        slope = (Y[k]-Y[j]) / (X[k]-X[j])
        return slope*(x - X[j]) + Y[j]
    
    @staticmethod
    def log_linear(x: float, X: List[float], Y: List[float]) -> float:
        j = IntervalSearch.search(x, X)
        j = max(0, min(j, len(X)-2))
        k = j + 1
        slope = (Y[k]-Y[j]) / (log(X[k])-log(X[j]))
        return slope*(log(x) - log(X[j])) + Y[j]
    
    @staticmethod
    def linear_log(x: float, X: List[float], Y: List[float]) -> float:
        j = IntervalSearch.search(x, X)
        j = max(0, min(j, len(X)-2))
        k = j + 1
        slope = (log(Y[k])-log(Y[j])) / (X[k]-X[j])
        return exp(slope*(x - X[j])) + Y[j]
    
    @staticmethod
    def log_log(x: float, X: List[float], Y: List[float]) -> float:
        j = IntervalSearch.search(x, X)
        j = max(0, min(j, len(X)-2))
        k = j + 1
        slope = (log(Y[k])-log(Y[j])) / (log(X[k])-log(X[j]))
        return exp(slope*(log(x) - log(X[j]))) + Y[j]
    
    @staticmethod
    def robust(x: List[float], X: List[float], Y: List[float], dY: List[float]=None) -> float:
        if dY is None:
            dY = Interpolator.derivatives(X,Y)
        j = IntervalSearch.search(x, X)
        j = max(0, min(j, len(X)-2))
        k = j + 1

        xj, xk = X[j], X[k]
        yj, yk = Y[j], Y[k]
        slope = (yk - yj)/(xk - xj)

        y0 = yj + slope*(x-xj)
        dely0 = yj + dY[j]*(x-xj) - y0
        dely1 = yk + dY[k]*(x-xk) - y0
        sign = dely0*dely1

        if sign == 0:
            return y0
        if sign > 0:
            return y0 + sign/(dely0 + dely1)
        x_tmp = 2*x - xj - xk
        return y0 + sign*x_tmp/((dely0 - dely1)*(xk - xj))



