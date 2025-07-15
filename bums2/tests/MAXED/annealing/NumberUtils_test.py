#Simple test cases for NumberUtils within the MAXED directory
import unittest
import numpy as np

from bums2.FORTRAN_METHODS.MAXED.utils.NumberUtils import NumberUtils

class TestNumberUtils(unittest.TestCase):
    def test_exprep_normal_range(self):
        self.assertAlmostEqual(NumberUtils.exprep(0.0), 1.0)
        self.assertAlmostEqual(NumberUtils.exprep(1.0), np.exp(1.0), places=6)
        self.assertAlmostEqual(NumberUtils.exprep(-1.0), np.exp(-1.0), places=6)

    def test_exprep_large_input(self):
        self.assertEqual(NumberUtils.exprep(1000.0), float('inf'))
        self.assertEqual(NumberUtils.exprep(701.0), float('inf'))

    def test_exprep_small_input(self):
        self.assertEqual(NumberUtils.exprep(-1000.0), 0.0)
        self.assertEqual(NumberUtils.exprep(-746.0), 0.0)

    def test_exprep_thresholds(self):
        self.assertGreater(NumberUtils.exprep(699.0), 0.0)
        self.assertGreater(NumberUtils.exprep(-744.0), 0.0)

    def test_random_number_range(self):
        rng = NumberUtils(seed1=1, seed2=2)
        for h in range(100):
            val = rng.RANMAR()
            self.assertTrue(0.0 <= val < 1.0)

    def test_random_sequence_repeatability(self):
        rng1 = NumberUtils(seed1=1, seed2=2)
        rng2 = NumberUtils(seed1=1, seed2=2)
        values1 = [rng1.RANMAR() for _ in range(10)]
        values2 = [rng2.RANMAR() for _ in range(10)]
        self.assertEqual(values1, values2)

    def test_invalid_seeds(self):
        with self.assertRaises(ValueError):
            NumberUtils(seed1=-1, seed2=2)
        with self.assertRaises(ValueError):
            NumberUtils(seed1=100000, seed2=0)
        with self.assertRaises(ValueError):
            NumberUtils(seed1=0, seed2=40000)

if __name__ == "__main__":
    unittest.main()