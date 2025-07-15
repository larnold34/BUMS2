#Simple unittest test cases for the scaling.py file in the MAXED directory
import unittest
import numpy as np

from bums2.FORTRAN_METHODS.MAXED.spec_scaling.scaling import SpectrumScaler

class TestSpectrumScaler(unittest.TestCase):
    def setUp(self):
        self.mm = [0.5, 0.4, 0.3,
                   0.6, 0.7, 0.8]
        self.fi = [1.0, 1.0, 1.0]
        self.enbf = [1.0, 2.0, 4.0, 8.0]
        self.scaler = SpectrumScaler(mm=self.mm, fi=self.fi, enbf=self.enbf)

    def test_calc_fout_basic(self):
        lambdas = [0.1, 0.2]
        fout = self.scaler.calc_fout(lambdas, m=2, nb=3)

        # Expected manually:
        # sum2_j = λ1 * B[0,j] + λ2 * B[1,j]
        # B = [[0.5, 0.4, 0.3],
        #      [0.6, 0.7, 0.8]]

        expected = [
            1.0 * np.exp(-(0.1 * 0.5 + 0.2 * 0.6)),
            1.0 * np.exp(-(0.1 * 0.4 + 0.2 * 0.7)),
            1.0 * np.exp(-(0.1 * 0.3 + 0.2 * 0.8))
        ]

        for f, e in zip(fout, expected):
            self.assertAlmostEqual(f, e, places=6)

    def test_scale_fi_matches_manual(self):
        fi = np.array([1.0, 2.0, 3.0])
        b = np.array(self.mm).reshape(2, 3)
        d = np.array([5.0, 10.0])
        s = np.array([1.0, 1.0])

        eig = np.dot(b, fi)
        expected = np.sum((d * eig) / (s ** 2)) / np.sum((eig ** 2) / (s ** 2))
        result = self.scaler.scale_fi(d, s, b, fi)

        self.assertAlmostEqual(result, expected, places=6)

    def test_lethargy_normalization_log_bins(self):
        fi = [1.0, 2.0, 3.0]
        fout = [0.9, 1.8, 3.6]
        fil, fl = self.scaler.lethargy_normalize(fi, fout)

        expected_fil = [f / np.log(self.enbf[i + 1] / self.enbf[i]) for i, f in enumerate(fi)]
        expected_fl = [f / np.log(self.enbf[i + 1] / self.enbf[i]) for i, f in enumerate(fout)]

        for a,b in zip(fil, expected_fil):
            self.assertAlmostEqual(a, b, places=6)
        for a,b in zip(fl, expected_fl):
            self.assertAlmostEqual(a, b, places=6)

    def test_output_shapes(self):
        fout = self.scaler.calc_fout([0.1, 0.2], m=2, nb=3)
        self.assertEqual(len(fout), 3)

        fil, fl = self.scaler.lethargy_normalize(self.fi, fout)
        self.assertEqual(len(fil), 3)
        self.assertEqual(len(fl), 3)

if __name__ == "__main__":
    unittest.main()
