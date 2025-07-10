#The following will be testing maxiet.py
import numpy as np
import unittest

from bums2.algorithms.maxiet import maxiet
from bums2.core.config import Bums2Config

#This first class will be just making dummy variables
class DummyConfig(Bums2Config):
    def __init__(self):
        #Only really setting the inputs maxiet needs
        super().__init__(
            max_energy= 1.0,
            iter= 0, 
            itertesterror= 1,
            endtesterror= 0,
            tempij= 2.0,
            smoothing= 0.1,
            shape= 1.0,
            pertubation= 0.5,
            cal_factor= 0.01,
            matrix_name= "",
            start_spec= "",
            alg = "maxiet"
        )

        cfg = Bums2Config.from_dict(self.__dict__)

        #Copy back any computed values
        for k, v in cfg.__dict__.items():
            setattr(self, k, v)

#The actual testing class
class TestMaxietFunctions(unittest.TestCase):
    def setUp(self):
        self.cfg = DummyConfig()
        self.algo = maxiet(self.cfg)
    
    def test_compute_maxwellian_spmx_less(self):
        ce = np.array([1.0, 2.0, 3.0])
        temp = 2.0

        #Since ce is bigger during each iteration, val will always be greater than spmx
        expected = ce**1.5 * np.exp(-ce/temp)
        splmax, spmx = self.algo._compute_maxwellian(ce, temp, spmx=0.0)

        #Verify that the outputs are correct
        np.testing.assert_allclose(splmax, expected, rtol=1e-12, atol=0)

        #spmx should be equal to the last entry within the output of splmax, since both store val
        self.assertEqual(spmx, expected[-1])

    def test_comput_maxwellian_shape_apply(self):
        #If the ce order is reverted from the previous test, than spmx > val
        #This will trigger the else statement, which will then apply the shape correction
        ce = np.array([3.0, 2.0, 1.0])
        temp = 2.0

        splmax, spmx = self.algo._compute_maxwellian(ce, temp, spmx=0.0)

        #The first run with val will be greater than spmx, which starts at zero
        #This should set spmx to around 1.159 and it should not change
        #After running the whole loop and the shape being equal to 1, splmax should be [1.159, 1.159, 1.159]
        self.assertAlmostEqual(spmx, 1.159, delta=1e-3)
        np.testing.assert_allclose(splmax, [1.159, 1.159, 1.159], atol=1e-3)

    def test_1overE_plus_max_simple(self):
        #ce is set so that spli < splmax and break from the loop immediately
        ce = np.array([1.0, 2.0, 3.0])
        num_g = 2 
        slope = 1.0
        hgte = 2.0
        splmax =np.array([3.0, 3.0, 3.0])

        #Running with these inputs and using spli[i] = hgte * ce[i] ** slope, then spli should be [2, 4, 6]
        #This would mean that crossed would be made true, but the loop will continue
        #So spli in the end would be [2, 3.5, 4.5] since the condition is not checked until after the loop

        spli, new_hgte, h = self.algo._1overE_plus_max(ce, num_g, slope, splmax, hgte)

        np.testing.assert_allclose(spli, [2, 3.5, 4.5])
                                   
        #The loop condition would be triggered on i=0, so h will be set to 0
        self.assertEqual(h, 0)

        #Since crossed was set to true on iteration 0, then hgte will never update and the loop would break at level 5
        self.assertEqual(new_hgte, hgte)

if __name__ == "__main__":
    unittest.main()
        
