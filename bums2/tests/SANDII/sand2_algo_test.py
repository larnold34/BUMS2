#Simple unittest test cases for the sand2 solver 
import unittest
import numpy as np
from bums2.FORTRAN_METHODS.SAND2.sand2_algo import Sand2Solver

class TestSand2Solver(unittest.TestCase):

    def setUp(self):
        # Simple test case with known behavior
        self.B = np.array([
            [1.0, 0.5],
            [0.5, 1.0]
        ])
        self.D = np.array([1.7, 1.5])
        self.S = np.array([0.1, 0.1])
        self.FI = np.array([1.0, 1.0])

    def test_converges_fractional_deviation(self):
        solver = Sand2Solver(self.B, self.D, self.S, self.FI, max_iter=100, chi_fac=0, dev=1e-4)
        spectrum = solver.run()
        self.assertTrue(solver.get_iterations() < 100)
        self.assertIsNotNone(spectrum)

    def test_converges_chi_squared(self):
        solver = Sand2Solver(self.B, self.D, self.S, self.FI, max_iter=100, chi_fac=1)
        spectrum = solver.run()
        self.assertLessEqual(solver.get_chi_squared(), len(self.D))

    def test_chi_squared_accuracy(self):
        solver = Sand2Solver(self.B, self.D, self.S, self.FI, chi_fac=1)
        spectrum = solver.run()
        chi2 = solver.get_chi_squared()
        # Recalculate manually
        expected = self.B @ spectrum
        chi2_manual = np.sum(((self.D - expected) / self.S)**2)
        self.assertAlmostEqual(chi2, chi2_manual, places=5)

    def test_spectrum_update(self):
        solver = Sand2Solver(self.B, self.D, self.S, self.FI, chi_fac=1)
        spectrum = solver.run()
        self.assertFalse(np.allclose(spectrum, self.FI))  # Should not be the same as initial FI

    def test_iteration_limit_respected(self):
        # Use impossible dev condition to force max_iter to hit
        solver = Sand2Solver(self.B, self.D, self.S, self.FI, max_iter=5, chi_fac=0, dev=1e-50)
        spectrum = solver.run()
        self.assertEqual(solver.get_iterations(), 5)

if __name__ == "__main__":
    unittest.main()