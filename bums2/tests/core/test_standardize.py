#The following script is intended to conduct unit testing with standardize.py functions
import unittest
from math import isclose
import numpy as np
from bums2.core.standardize import Standardize

class TestStandardize(unittest.TestCase):

    def test_scale_factor_perfect(self):
        #if response_applied == measured, f should be 1.0
        measured = [2.0, 4.0, 6.0]
        response = [2.0, 4.0, 6.0]

        sf = Standardize.scale_factor(measured, response)
        self.assertEqual(sf, 1.0)

    def test_scale_factor_nontriviall(self):
        #Recall that scale factor is sum(measured_i * response_i) / sum(response_i^2)
        measured = [1.0, 2.0, 3.0]
        response = [2.0, 4.0, 6.0]

        #Using the initial logic, numerator should be 28 and the denominator should be 56
        expected = 28 / 56
        self.assertEqual(Standardize.scale_factor(measured, response), expected)

    def test_chi_squared_basic(self):
        measured = [1.0, 2.0, 3.0]
        model = [1.1, 1.9, 3.2]
        errors = [0.1, 0.2, 0.3]

        #Recall that chi squared is sum[(measured_i - model_i)^2 / error_i^2]
        #Using that logic the expected solution should be as seen below
        expected = ((1.0-1.1)**2) / (0.1**2) + ((2.0-1.9)**2) / (0.2**2) + ((3.0-3.2)**2) / (0.3**2)
        self.assertEqual(Standardize.chi_squared(measured, model, errors), expected)
    
    def test_chi_squared_bad_error(self):
        with self.assertRaises(ValueError):
            Standardize.chi_squared([1], [1], [0])
    
    def test_fit_error_positive(self):
        measured = [10.0, 5.0, 0.0]
        model = [11.0, 4.0, 3.0]
        weights = [1.0, 2.0, 3.0]

        #Recall that each error is found by doing model-measured/measured
        #since measured[2] is zero, this should flag the else and make the error 100.0
        #The error is built as total += w * err * err

        expected = 1*((11-10)/10)**2 + 2*((4-5)/5)**2 + 3*(100.0)**2
        self.assertEqual(Standardize.fit_error(measured, model, weights), expected)

    def test_normalize_indentity(self):
        #Lets say that the response matrix is the 2x2 identity matrix
        #initial=[1.0,1.0], measured=[10.0,10.0] -> scaled -> [10.0, 10.0]
        initial = [1.0, 1.0]
        response_matrix =[
            [1.0, 0.0],
            [0.0, 1.0],
        ]
        measured = [10.0, 10.0]
        out = Standardize().normalize(initial, response_matrix, measured)

        self.assertEqual(out, [10.0, 10.0])

    def test_normalize_no_response(self):
        #Since the model would be all zero, scale factor should flag the divide by zero error
        initial = [1.0, 2.0]
        response = [
            [0.0, 0.0],
            [0.0, 0.0],
        ]
        measured = [5.0, 5.0]
        with self.assertRaises(ValueError):
            Standardize().normalize(initial, response, measured)

    def test_trans_mat_uniform_scaling(self):
        aleth = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0]
        ])
        spli = np.array([10.0, 100.0, 1000.0])

        #Expected[k, i] = aleth[k, i] * spli[i]
        expected = np.array([
            [10.0, 200.0, 3000.0],
            [40.0, 500.0, 6000.0]
        ])
        out, spl = Standardize.trans_mat(aleth, spli)
        np.testing.assert_array_equal(out, expected)

    def test_trans_mat_zero_spectrum(self):
        aleth = np.random.random((3,4))
        spli = np.zeros(4)
        #Zero spectrum means that the transformed matrix should all be zero
        out, spl = Standardize.trans_mat(aleth, spli)
        np.testing.assert_array_equal(out, np.zeros_like(aleth))

    def test_cal_response_simple_dot(self):
        #cal_response computes bcc[m] = sum_j alethnew[m,j] * spl[j]
        alethnew = np.array([
            [1.0, 0.0, 2.0],
            [0.5, 0.5, 0.5]
        ])

        spl = np.array([10.0, 20.0, 30.0])
        #row 0: 1*10 + 0*20 + 2*30 = 70
        #row 1: 0.5*10 + 0.5*20 + 0.5*30.0 = 30
        expected = np.array([70.0, 30.0])
        out = Standardize.cal_response(alethnew, spl)

        np.testing.assert_allclose(out, expected)

    def test_cal_response_empty(self):
        alethnew = np.zeros((5,5))
        spl = np.random.random(5)
        # zero matrix → zero bcc
        out = Standardize.cal_response(alethnew, spl)
        np.testing.assert_array_equal(out, np.zeros(5))

if __name__ == "__main__":
    unittest.main()