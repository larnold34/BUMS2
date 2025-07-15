#Simple unittest test cases for mkebins4pd.py in the MAXED directory
import unittest
import numpy as np
from bums2.FORTRAN_METHODS.MAXED.bins.mkebins4pd import LogEnergyBinsPD

class TestLogEnergyBinsPD(unittest.TestCase):
    def test_bin_count(self):
        input_range = [1e-13, 1e-9]
        pd = LogEnergyBinsPD(input_range)
        bins = pd.generate_bins()
        
        expected_n = pd._nint(4.0 * np.log10(bins[-1] / bins[0])) + 1
        self.assertEqual(len(bins), expected_n)

    def test_log_spacing(self):
        input_range = (1e-13, 1e-9)
        pd = LogEnergyBinsPD(input_range)
        bins = pd.generate_bins()
        ratio = pd.TPOQ

        for i in range(1, len(bins)):
            expected = bins[i-1] * ratio
            self.assertAlmostEqual(bins[i], expected, places=6)

    def test_min_max_containment(self):
        input_range = (1e-13, 1e-9)
        pd = LogEnergyBinsPD(input_range)
        bins = pd.generate_bins()

        self.assertLessEqual(input_range[0], bins[0])
        self.assertGreaterEqual(input_range[1], bins[-1])

    def test_nint_rounding(self):
        pd = LogEnergyBinsPD([1e-13, 1e-9])
        self.assertEqual(pd._nint(1.2), 1)
        self.assertEqual(pd._nint(1.5), 2)
        self.assertEqual(pd._nint(0.4), 0)
        self.assertEqual(pd._nint(0.6), 1)

    def test_bin_monotonicity(self):
        pd = LogEnergyBinsPD([1e-13, 1e-9])
        bins = pd.generate_bins()
        self.assertTrue(np.all(np.diff(bins) > 0))

if __name__ == "__main__":
    unittest.main()