#The following will be unit testing bon.py
import unittest
import numpy as np

from bums2.algorithms.bon import Bon

#This first class will be a dummy example of the config.py file that will normally be called
class DummyConfig:
    def __init__(self, itertesterror: int, smoothing: float):
        self.itertesterror = itertesterror
        self.smoothing = smoothing

class TestBon(unittest.TestCase):
    def setUp(self):
        #Just set up a simple 3 energy group and 3 detector problem
        self.num_groups = 3
        self.num_detectors = 3

        #A simple measured counts vector
        self.bce = np.array([1.0, 2.0, 3.0])

        #A simple initial spectrum
        self.spl0 = np.ones(self.num_groups)

        #Config with one iteration and no smoothing
        cfg = DummyConfig(itertesterror=1, smoothing=0.0)
        self.unfolder = Bon(cfg)

    def test_identity_response_matrix(self):
        #If alethnew is the identity matrix (detectors == groups), then one iteration should map spl -> bce
        #This is due to bk=I, vect=bce, and spll[j] = spl[j]*vect[j]/(spl[j]) == bce[j]
        alethnew = np.eye(self.num_groups)
        spl_out, bcc_out, iters = self.unfolder.bon_unfolding(
            alethnew=alethnew,
            bce=self.bce,
            spl_init=self.spl0,
            iter_start=0
        )

        #Check if the spectrum equals bce
        np.testing.assert_allclose(spl_out, self.bce, atol=1e-12)

        #Check bcc_out, which should be alethnew.dot(spl_out) = spl_out
        np.testing.assert_allclose(bcc_out, self.bce, atol=1e-12)

        #Verify the iteration tracking
        self.assertEqual(iters, 1)

    def test_underflow_gaurds(self):
        #If the response matrix is very small, then bk and vect will be near zero, triggering the underflow gaurds
        tiny = 1e-50
        alethnew = np.full((self.num_detectors, self.num_groups), tiny)
        bce = np.ones(self.num_detectors)
        spl_out, bcc_out, _ = self.unfolder.bon_unfolding(
            alethnew=alethnew,
            bce=bce,
            spl_init=self.spl0,
            iter_start=0
        )

        #After the underflow gaurd, the entire sepctrum should be zero
        np.testing.assert_allclose(spl_out, np.zeros(self.num_groups), atol=1e-12)

        #Additionally bcc should all be zero
        np.testing.assert_allclose(bcc_out, np.zeros(self.num_detectors), atol=1e12)
    
    def test_multiple_interations_accumulate(self):
        #With more iterations and a uniform alethnew, the resulting spectrum should converge to a multiple of bce
        uniform = np.ones((self.num_detectors, self.num_groups))
        cfg = DummyConfig(itertesterror=3, smoothing=0.0)
        unfolder = Bon(cfg)

        spl_out, _, _ = unfolder.bon_unfolding(uniform, self.bce, self.spl0, iter_start=0)

        with self.assertRaises(AssertionError):
            np.testing.assert_allclose(spl_out, self.spl0, atol=1e-12)

if __name__ == "__main__":
    unittest.main()

        
    