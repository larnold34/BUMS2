#The following script is intended to conduct unit testing with rebin.py functions
import unittest
from bums2.utils.rebin import Rebin


class TestRebin(unittest.TestCase):

    #the rebinning logic is heavily dependent on maxmin and minmax determining the new range, new_edges does not determine the new intervals

    def test_identity_rebin(self):
        #When new_bin == old_bin, each new_value should equal the corresponding old_value
        old_bin = [1.0, 2.0, 3.0, 4.0]
        old_value = [10.0, 20.0, 30.0, 40.0]
        new_bin = [1.0, 2.0, 3.0, 4.0]

        #num_new_bins = len(new_bin), num_old_bins = len(old_bin)
        rebinner = Rebin(old_bin, old_value, new_bin)
        out = rebinner.transform()

        #There should be 4 output bins (len(new_bin)), values at indices 0-2 come from the old_value
        #Since there is no overlap between the final value and the new bins, it should be 0.0
        self.assertEqual(out, [10.0, 20.0, 30.0, 0.0])

    def test_constant_spectrum(self):
        #All constant old_values should translate to all constant new_values across the overlap region
        old_edges = [1.0, 10.0, 100.0]
        old_values = [5.0, 5.0, 5.0]
        new_edges = [1.0, 10.0, 100.0, 1000.0]

        rebinner = Rebin(old_edges, old_values, new_edges)
        out = rebinner.transform()

        #The following intervals have overlap [1-10] and [10-100], which means only 2 of the new bins will carry over the 5.0
        self.assertEqual(out, [5.0, 5.0, 0.0, 0.0])

    def test_no_overlap(self):
        #If there is no overlap between the original energy binning and the new one, then the output should be all 0.0
        old_edges = [100.0, 200.0]
        old_values = [1.0, 2.0]
        new_edges = [1.0, 2.0, 3.0]

        rebinner = Rebin(old_edges, old_values, new_edges)
        out = rebinner.transform()

        self.assertEqual(out, [0.0, 0.0, 0.0])

    def test_partial_overlap(self):
        #Only a few of the bins from the old binning overlap with the new binning, these values should be picked up
        #All regions with no overlap should still output a zero
        old_edges = [1.0, 2.0, 4.0]
        old_values = [10.0, 20.0, 30.0]
        new_edges = [0.5, 1.5, 3.0, 5.0]

        rebinner = Rebin(old_edges, old_values, new_edges)
        out = rebinner.transform()

        #There is only overlap inside the interval [1.5-3], which means only bin 1 will have a value greater than 0
        self.assertEqual(out[0], 0.0)
        self.assertEqual(out[3], 0.0)
        self.assertGreater(out[1], 0.0)
        self.assertEqual(out[2], 0.0)
    
    def test_mismatch_length(self):
        with self.assertRaises(ValueError):
            Rebin([1.0, 2.0, 3.0], [10.0, 20.0], [1.0, 2.0, 3.0]).transform()

if __name__ == '__main__':
    unittest.main()