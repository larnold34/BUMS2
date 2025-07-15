#Simple unittest test cases for responsel_test in the MAXED directory
import unittest
import numpy as np

from bums2.FORTRAN_METHODS.MAXED.bins.responsel import ResponseMapper

class TestResponseMapper(unittest.TestCase):
    def test_basic_overlap(self):
        res = [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0]
        ]
        rfn = [0, 1]
        enbf = [1.0, 2.0, 4.0]
        enbr = [1.5, 2.5, 3.5, 4.5]

        mapper = ResponseMapper(res, rfn, enbf, enbr, m=2, nb=2, nb1=3)
        B = mapper.map_response()

        self.assertEqual(B.shape, (2, 2))
        self.assertTrue(np.all(B > 0))

    def test_no_overlap_gives_zero(self):
        res = [
            [1.0, 1.0],
            [1.0, 1.0]
        ]
        rfn = [0, 1]
        enbf = [0.1, 0.2, 0.3]
        enbr = [1.0, 2.0, 3.0]

        mapper = ResponseMapper(res, rfn, enbf, enbr, m=2, nb=2, nb1=2)
        B = mapper.map_response()

        self.assertTrue(np.allclose(B, 0.0, atol=1e-10))
    
    def test_index_mapping_applies(self):
        res = [
            [10.0, 0.0],
            [5.0, 20.0]
        ]
        rfn = [1, 0]
        enbf = [1.0, 2.0, 3.0]
        enbr = [1.0, 2.0, 3.0]

        mapper = ResponseMapper(res, rfn, enbf, enbr, m=2, nb=2, nb1=2)
        B = mapper.map_response()

        self.assertGreater(B[0, 0], 0)
        self.assertGreater(B[1, 0], 0)
        self.assertNotEqual(B[0, 0], B[1, 0])

    def test_partial_overlap(self):
        res = [
            [1.0, 1.0, 1.0]
        ]
        rfn = [0]
        enbf = [2.0, 3.0, 4.0]
        enbr = [1.0, 2.5, 3.5, 4.5]

        mapper = ResponseMapper(res, rfn, enbf, enbr, m=1, nb=2, nb1=3)
        B = mapper.map_response()

        self.assertEqual(B.shape, (1, 2))
        self.assertTrue(np.any(B > 0))

    def test_output_shape(self):
        res = [[1.0] * 3] * 4
        rfn = [0, 1, 2, 3]
        enbf = [1.0, 2.0, 3.0, 4.0]
        enbr = [1.0, 2.0, 3.0, 4.0]

        mapper  = ResponseMapper(res, rfn, enbf, enbr, m=4, nb=3, nb1=3)
        B = mapper.map_response()

        self.assertEqual(B.shape, (4, 3))

if __name__ == "__main__":
    unittest.main()



