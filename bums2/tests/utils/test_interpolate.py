#The following script is intended to conduct unit testing with interpolate.py functions
import math
import unittest
from bums2.utils.interpolate import Interpolator

class TestInterpolator(unittest.TestCase):
    def setUp(self):
        self.ip = Interpolator()

        #A simple dataset
        self.x = [1.0, 2.0, 4.0, 8.0]
        self.y = [10.0, 20.0, 40.0, 80.0]

    #Test the derivative function with 2 points
    def test_derivatives_two_points(self):
        d = self.ip.derivatives([1, 2], [3, 7])
        #Derivatives only runs if there is at least 2 points
        #It returns the slope in an array equal to len(d), it will just repeat the number
        self.assertEqual(len(d), 2) #Make sure there are 2 points
        self.assertAlmostEqual(d[0], 4.0) #this is the correct solution
        self.assertAlmostEqual(d[1], 4.0) #this checks that d is being filled in properly

    #test the derivative function with multiple points
    def test_derivatives_multi(self):
        d = self.ip.derivatives(self.x, self.y)
        self.assertAlmostEqual(d[1], 10.0, places=6) #this will check that the slope of the interior points equals the expected value

    #test the constant function, which will also test IntervalSearch in the process
    def test_constant_interpolate(self):
        #below range -> first y
        self.assertEqual(self.ip.constant(0.5, self.x, self.y), 10.0)

        #inside range -> picks the lower bracket of interior points
        self.assertEqual(self.ip.constant(3.0, self.x, self.y), 20.0)

        #above range -> last y
        self.assertEqual(self.ip.constant(10.0, self.x, self.y), 80.0)
    
    #test the linear interpolate function
    def test_linear_interpolate(self):
        #Will set x=3, which means interval search should flag between the points (2,20) and (4,40)
        #With this in mind, the calculated slope should be 10 and the interpolated value should be 30
        y = self.ip.linear(3.0, self.x, self.y)
        self.assertAlmostEqual(y, 30.0)
        # self.assertEqual(slope, 10.0)
    
    #test the log_linear interpolate function
    def test_log_linear_interpolate(self):
        #Will set x=3, which means interval search should flag between the points (2,20) and (4,40)
        #With this in mind, the calculated slope should be roughly 28.854 and the interpolated value should be roughly 31.699
        #Will also test to make sure a number is actually outputted
        y = self.ip.log_linear(3.0, self.x, self.y)
        self.assertIsInstance(y, float)
        # self.assertIsInstance(slope, float)

        self.assertAlmostEqual(y, 31.699, delta=1e-3)
        # self.assertAlmostEqual(slope, 28.854, delta=1e-3)
    
    #test the linear_log interpolate function
    def test_linear_log_interpolate(self):
        #Will set x=3, which means interval search should flag between the points (2,20) and (4,40)
        #With this in mind, the calculated slope should be roughly 0.346 and the interpolated value should be roughly 21.414
        #Will also test to make sure a number is actually outputted
        y = self.ip.linear_log(3.0, self.x, self.y)
        self.assertIsInstance(y, float)

        self.assertAlmostEqual(y, 21.414, delta=1e-3)
        # self.assertAlmostEqual(slope, 0.346, delta=1e-3)

    #test the log_log interpolate funtion
    def test_log_log_interpolate(self):
        #Will set x=3, which means interval search should flag between the points (2,20) and (4,40)
        #With this in mind, the calculated slope should be 1 and the interpolated value should be roughly 21.5
        #Will also test to make sure a number is actually outputted
        y = self.ip.log_log(3.0, self.x, self.y)
        self.assertIsInstance(y, float)

        # self.assertAlmostEqual(slope, 1)
        self.assertEqual(y, 21.5)
    
    #test the robust function
    def test_robust_interpolate(self):
        #Will test how robust works, by comparing with the linear interpolation function, both functions should be roughly the same
        y_rob = self.ip.robust(3.0, self.x, self.y)
        y_lin = self.ip.linear(3.0, self.x, self.y)

        self.assertAlmostEqual(y_rob, y_lin, places=6)
        # self.assertAlmostEqual(dy_rob, dy_lin, places=6)
        
if __name__ == '__main__':
    unittest.main()