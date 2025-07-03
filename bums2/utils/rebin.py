#The following will be the python equivalent of rebin.pl. It will still follow the same fillfill subroutine pulled from MAXED
from math import log
from typing import List

#Rebin will take an inputted spectrum (old_edges, old_values) and apply a new energy grid (new_edges),
#using logarithmic interpolative weighting in space.

class Rebin:
    def __init__(self, old_edges: List[float], old_values: List[float], new_edges: List[float]):
        # if len(old_edges) != len(old_values):
        #     raise ValueError("old_edges and old_values must have the same length")
        self.old_edges = old_edges
        self.old_values = old_values
        self.new_edges = new_edges

    def transform(self) -> List[float]:
        n_old = len(self.old_edges)
        n_new = len(self.new_edges)

        # Choose range of new bin values
        # Example:
        # new bins            [ * * 3 4 5 6 7 8 9 ]
        # old bins            [ 1 2 3 4 5 6 7 * * ]
        # new bin value range [ * * 3 4 5 6 7 * * ]
        maxmin = max(self.old_edges[0], self.new_edges[0])
        minmax = min(self.old_edges[-1], self.new_edges[-1])

        #Build a subset of new_edges that lie inside the new bounds [maxmin, minmax]
        #	$re_bin[$j] = new set of bins for new set of values excluding 0.0 values.
        # Example:
        # new bins            [ * * 3 4 5 6 7 8 9 ]
        # maxmin              [ * * 3 * * * * * * ]
        # minmax              [ * * * * * * 7 * * ]
        # re bins             [ * * 3 4 5 6 7 * * ]
        re_bin = [e for e in self.new_edges if maxmin <= e <= minmax]
        jmax = len(re_bin)
        #Allocate intermediate accumulation array
        inter_value = [0.0] * (jmax-1)

        #Loop over the old bins and accumulate into each re_bin interval
        for k in range(n_old - 1):
            e_old_lo = self.old_edges[k]
            e_old_hi = self.old_edges[k + 1]
            val      = self.old_values[k]

            for j in range(jmax - 1):
                e_lo = re_bin[j]
                e_hi = re_bin[j + 1]
                r2   = log(e_hi) - log(e_lo)
                if r2 <= 0:
                    continue

                 # Perl’s “if re_bin[l] <= old_bin[k]”
                if e_lo <= e_old_lo:
                    # Perl’s “if re_bin[l+1] > old_bin[k]”
                    if e_hi > e_old_lo:
                        # Perl’s inner test: does the entire old‐bin fit?
                        if e_hi >= e_old_hi:
                            r1 = log(e_old_hi) - log(e_old_lo)
                        else:
                            r1 = log(e_hi)      - log(e_old_lo)
                        inter_value[j] += val * (r1 / r2)

                # Perl’s “else { if re_bin[l] < old_bin[k+1] }”
                else:
                    if e_lo < e_old_hi:
                        # Perl’s test for upper edge
                        if e_hi <= e_old_hi:
                            r1 = log(e_hi)      - log(e_lo)
                        else:
                            r1 = log(e_old_hi)  - log(e_lo)
                        inter_value[j] += val * (r1 / r2)

        new_values = [99.0]*n_new
        j = 0
        for k in range(n_new-1):
            e = self.new_edges[k]
            if maxmin <= e <= minmax and j < len(inter_value):
                new_values[k] = inter_value[j]
                j += 1
            else:
                new_values[k] = 0.0
        formatted = ", ".join(f"{v:.4e}" for v in new_values)
        return new_values
                    