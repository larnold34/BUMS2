#Simple test cases for fcn.py within the MAXED directory
import numpy as np
import unittest

from bums2.FORTRAN_METHODS.MAXED.annealing.fcn import ObjectiveFunction
from bums2.FORTRAN_METHODS.MAXED.utils.NumberUtils import NumberUtils


class TestObjectiveFunction(unittest.TestCase):
    def test_basic_eval(self):
        mm = np.array([[0.1, 0.2], [0.3, 0.4]])
        fi = np.array([1.0, 2.0])
        s = np.array([0.1, 0.1])
        d = np.array([0.5, 0.5])
        omega = 0.5
        flux = 1.0
        lambdas = np.array([1.0, 1.0])

        f = ObjectiveFunction(mm, fi, s, d, omega, flux)
        result = f(lambdas)

        self.assertIsInstance(result, float)
        self.assertFalse(np.isnan(result))

    def test_zero_lambda_returns_flux_minus_dot(self):
        mm = np.array([[0.1, 0.2], [0.3, 0.4]])
        fi = np.array([1.0, 2.0])
        s = np.array([0.1, 0.2])
        d = np.array([0.5, 0.6])
        omega = 0.5
        flux = 1.0
        lambdas = np.zeros(2)

        f = ObjectiveFunction(mm, fi, s, d, omega, flux)
        result = f(lambdas)

        #sum1 usually uses exp values, but since those values are determined using the zero power, it should all be one
        expected = -np.dot(fi, np.ones_like(fi)) + flux
        self.assertAlmostEqual(result, expected, places=6)

    def test_large_negative_lambda_exprep_behavior(self):
        mm = np.array([[50, 100], [75, 150]])
        fi = np.array([1.0, 1.0])
        s = np.array([1.0, 1.0])
        d = np.array([0.5, 0.5])
        omega = 0.5
        flux = 1.0
        lambdas = np.array([-10.0, -10.0])

        f = ObjectiveFunction(mm, fi, s, d, omega, flux)
        result = f(lambdas)

        self.assertIsInstance(result, float)
        self.assertFalse(np.isnan(result))

    def test_negative_lambda_penalizes_f(self):
        mm = np.array([[0.1, 0.2], [0.3, 0.4]])
        fi = np.array([1.0, 2.0])
        s = np.array([0.1, 0.1])
        d = np.array([0.5, 0.5])
        omega = 0.5
        flux = 1.0
        lambdas_pos = np.array([1.0, 1.0])
        lamdbas_neg = np.array([-1.0, -1.0])

        f = ObjectiveFunction(mm, fi, s, d, omega, flux)
        result_pos = f(lambdas_pos)
        result_neg = f(lamdbas_neg)

        self.assertNotEqual(result_pos, result_neg)

if __name__ == "__main__":
    unittest.main()