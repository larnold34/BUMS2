#The following will be unit testing spunit.py
import unittest
import numpy as np

from bums2.algorithms.spunit import spunit


#This initial class will be creating dummy variables that would normally be within config.py
class DummyConfig:
    def __init__(self, itertesterror, smoothing):
        self.itertesterror = itertesterror
        self.smoothing = smoothing

class TestSpunit(unittest.TestCase):
    def setUp(self):
        #Make a small response matrix, so in this case 3 energy bins and 2 detectors
        self.num_groups = 3
        self.num_detectors = 2

        #alethnew[m][j] is the response matrix in terms of lethargy. m is the detector index and j is the energy index
        self.alethnew = np.ones((self.num_detectors, self.num_groups))

        #bce is the inputted measured counts and bcc is the expected counts from the initial spectrum
        self.bce = np.array([1.0, 2.0])
        self.bcc = np.array([1.0, 2.0])

        #starting spectrum spl and intermediate spll
        self.spl = np.ones(self.num_groups) * 5.0
        self.spll = np.zeros(self.num_groups)

        #no smoothing and one extra iteration
        cfg = DummyConfig(itertesterror=1, smoothing=0.0)
        self.unfolder = spunit(cfg)


    def test_zero_smoothing(self):
        #With smoothing=0 and a unifrom alethnew, the first pass should leave spl unchanged since detectors / bins is symmetrical
        spl_out, bcc_out, _ = self.unfolder.spunit_unfold(
            alethnew=self.alethnew,
            bce=self.bce,
            bcc_init=self.bcc,
            spl_init=self.spl.copy()
        )
        
        #Check if the output is unchanged
        np.testing.assert_allclose(spl_out, self.spl, atol=1e-12)

        #New bcc is the sum over times (alethnew[m,j]*spl[j])
        #In this test case, alethnew is 1, so bcc_out=sum(spl[j]) = 5*3 = 15
        np.testing.assert_allclose(bcc_out, [15.0, 15.0], atol=1e-12)

    def test_underflow_zeroing(self):
        #This is to test the condtional set for when spll is <e-37
        tiny_alethnew = np.full((self.num_detectors, self.num_groups), 1.0e-40)
        bce = np.ones(self.num_detectors)
        bcc = np.ones(self.num_detectors)
        spl = np.ones(self.num_groups)
        spl_out, _, _ = self.unfolder.spunit_unfold(
            alethnew=tiny_alethnew,
            bce=bce,
            bcc_init=bcc,
            spl_init=spl,
            iter_start=1 #In this case iter_start needs to be specified since ss and alethnew will be equally as small
        )

        np.testing.assert_allclose(spl_out, np.zeros(self.num_groups), atol=1e-12)

if __name__ == "__main__":
    unittest.main()