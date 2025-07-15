#Simple unittest test cases for mkebins.py in the MAXED directory
import unittest
from bums2.FORTRAN_METHODS.MAXED.bins.mkebins import MergedEnergyBins

class TestMergedEnergyBins(unittest.TestCase):
    def test_basic_merge(self):
        enbzkl = [1.0, 2.0, 3.0, 4.0]
        enbr = [2.5, 3.5, 4.5, 5.0]
        nmax = 20

        merger = MergedEnergyBins(enbzkl, enbr, nmax)
        enb0, n = merger.merge_and_filter()

        expected = [2.5, 3.0, 3.5, 4.0]
        for a, b in zip(enb0, expected):
            self.assertAlmostEqual(a, b, places=6)
        self.assertEqual(n, len(expected))

    def test_no_overlap(self):
        enbzkl = [1.0, 2.0, 3.0]
        enbr = [2.0, 3.0, 4.0]

        merger = MergedEnergyBins(enbzkl, enbr, nmax=10)
        enb0, n = merger.merge_and_filter()

        expected = [2.0, 3.0]
        for a, b in zip(enb0, expected):
            self.assertAlmostEqual(a, b, places=6)
        self.assertEqual(n, 2)

    def test_full_overlap(self):
        enbzkl = [2.0, 3.0, 4.0]
        enbr = [1.0, 2.5, 3.5, 4.5]

        merger = MergedEnergyBins(enbzkl, enbr, nmax=10)
        enb0, n = merger.merge_and_filter()

        expected = [2.0, 2.5, 3.0, 3.5, 4.0]
        for a, b in zip(enb0, expected):
            self.assertAlmostEqual(a, b, places=6)

    def test_sorted_output(self):
        enbzkl = [1.0, 3.0, 5.0]
        enbr = [2.0, 4.0, 6.0]

        merger = MergedEnergyBins(enbzkl, enbr, nmax=10)
        enb0, _ = merger.merge_and_filter()
        self.assertTrue(all(enb0[i] < enb0[i+1] for i in range(len(enb0) - 1)))

if __name__ == "__main__":
    unittest.main()