#The following script is intended to conduct unit testing with dose.py function
import unittest
from bums2.utils.dose import DoseConverter

class TestDoseConverter(unittest.TestCase):
    #Overall, this unit test will be making sure the various conditionals within dfact actually work as intended
    def setUp(self):
        self.dc  = DoseConverter()

    def test_neutron_lower_bound_ic10(self):
        #ic == 10, it = 1 (<5), energy below table -> returns fct_n_1[0]
        e_lo = self.dc._elim_n_1[0] * 0.5
        plain = self.dc.dfact(particle_id=1, ic=10, energy=e_lo, interp_method=1, units=1, acr=1.0)

        self.assertAlmostEqual(plain, self.dc._fct_n_1[0], places=12)

    def test_neutron_upper_bound_ic10(self):
        #ic == 10, it = 1 (<5), energy above table -> returns fct_n_1[-1]
        e_hi = self.dc._elim_n_1[-1] * 100
        plain = self.dc.dfact(particle_id=1, ic=10, energy=e_hi, interp_method=1, units=1, acr=1.0)

        self.assertAlmostEqual(plain, self.dc._fct_n_1[-1], places=12)

    def test_ic20_interpolation_and_anlytic(self):
        #Going through all the conditions for ic == 20 is pointless. We will just look at a few cases
        #Primarily when it < 5 or it == 5
        #This first test will look to make sure a number is outputted when using interpolate
        tbl = self.dc.dfact(particle_id=1, ic=20, energy=0.5, interp_method=2, units=1, acr=1.0)
        self.assertIsInstance(tbl, float)

        #This second test will look at the analytical section, assuming the energy is 0.02
        ana = self.dc.dfact(particle_id=1, ic=20, energy=0.02, interp_method=5, units=1, acr=1.0)

        #After running through the conditionals manually, the expected answer should be roughly 0.03145
        self.assertAlmostEqual(ana, 6.152e-6, delta=1e-3)
    
    def test_ic3x_branches(self):
        #Similar to the ic == 20 test, will look at when it < 5 and when it == 5
        v1 = self.dc.dfact(1, 32, 1e-4, 3, 1, 1)
        self.assertIsInstance(v1, float)

        v2 = self.dc.dfact(1, 33, 0.5, 5, 1, 1)
        self.assertIsInstance(v2, float)

    def test_ic40_interpolation(self):
        v = self.dc.dfact(1, 40, 1e-6, 2, 1, 1)
        self.assertIsInstance(v, float)


    def test_unit_conversion(self):
        #Same set up as the previous test with a random energy, will call twice
        #One call will use units=1 which is rem and the other will use units=2 which is Sv
        e = self.dc._elim_n_1[2]
        rem = self.dc.dfact(1, 10, e, 1, 1, 1)
        sv = self.dc.dfact(1, 10, e, 1, 2, 1)

        self.assertAlmostEqual(sv, rem / 100.0, places=12)

    def test_acr_negative_changes_value(self):
        #This test is to see if the correction factor is needed if using the previous inputs but acr=-1.0
        e = self.dc._elim_n_1[3]
        a1 = self.dc.dfact(1, 10, e, 1, 1, 1)
        a2 = self.dc.dfact(1, 10, e, 1, 1, -1)

        self.assertNotAlmostEqual(a1, a2, places=12)

    def test_interpolate_methods(self):
        #This test is meant to flag the error when it >= 5, which is not allowed
        with self.assertRaises(ValueError):
            self.dc.dfact(1, 10, 1e-6, 5, 1, 1)
    
    def test_unknown_particle(self):
        #This will see if the error for an unknown particle is flagged
        with self.assertRaises(ValueError):
            self.dc.dfact(99, 10, 1e-6, 1, 1, 1)

if __name__ == '__main__':
    unittest.main()