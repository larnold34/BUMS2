#This will be the python version of prtvec.pl from the MAXED directory

#      SUBROUTINE PRTVEC(VECTOR,NCOLS,NAME)
#  This subroutine prints the double precision vector named VECTOR.
#  Elements 1 thru NCOLS will be printed. NAME is a character variable
#  that describes VECTOR. Note that if NAME is given in the call to
#  PRTVEC, it must be enclosed in quotes. If there are more than 10
#  elements in VECTOR, 10 elements will be printed on each line.

class VectorPrinter:
    #Print out a vector with a given name, formatting up to 10 elements per line, mirroring the original Perl
    @staticmethod
    def print_vector(name: str, vector):
        #prints the vector values 1..len(vector) with the given name.
        n = len(vector)
        print(f"\n                         {name}")

        for start in range(0, n, 10):
            end = min(start + 10, n)
            line_vals = [f"{vector[i]:12.5g}" for i in range(start, end)]
            print(" ".join(line_vals))