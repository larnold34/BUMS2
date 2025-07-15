#Simple unittest test cases for fillfil.py in the MAXED directory
import unittest
import numpy as np
from bums2.FORTRAN_METHODS.MAXED.bins.fillfil import SpectrumBinFiller

class TestSpectrumBinFiller(unittest.TestCase):

    def test_basic_mapping(self):
        enbzkl = [1.0, 2.0, 4.0]
        zkl = [10.0, 20.0]
        enbf = [1.0, 2.5, 5.0]
        filler = SpectrumBinFiller(enbzkl, zkl, enbf)
        fi = filler.fill()

        self.assertEqual(len(fi), len(enbf) - 1)
        self.assertTrue(np.all(fi > 0))

    def test_no_overlap_gives_zero(self):
        enbzkl = [100.0, 200.0, 400.0]
        zkl = [10.0, 20.0]
        enbf = [1.0, 2.0, 3.0]
        filler = SpectrumBinFiller(enbzkl, zkl, enbf)
        fi = filler.fill()
        self.assertTrue(np.allclose(fi, 0.0, atol=1e-10))

    def test_full_overlap_integrity(self):
        enbzkl = [1.0, 2.0, 4.0, 8.0]
        zkl = [5.0, 10.0, 15.0]
        enbf = [1.0, 2.0, 4.0, 8.0]
        filler = SpectrumBinFiller(enbzkl, zkl, enbf)
        fi = filler.fill()
        self.assertTrue(np.all(fi > 0)) 

    def test_partial_overlap(self):
        enbzkl = [3.0, 4.0, 5.0]
        zkl = [10.0, 20.0]
        enbf = [1.0, 3.5, 10.0]

        filler = SpectrumBinFiller(enbzkl, zkl, enbf)
        fi = filler.fill()
        self.assertEqual(len(fi), 2)
        self.assertTrue(np.all(fi > 0))
        self.assertNotAlmostEqual(fi[0], fi[1], places=6)



    def test_output_length_matches(self):
        enbzkl = [1.0, 2.0, 3.0]
        zkl = [1.0, 1.0]
        enbf = [1.0, 1.5, 2.5, 3.5]
        filler = SpectrumBinFiller(enbzkl, zkl, enbf)
        fi = filler.fill()
        self.assertEqual(len(fi), len(enbf) - 1)

if __name__ == '__main__':
    unittest.main()
