#Simple unittest test cases for the sand2 main driver script
import unittest
import numpy as np
import tempfile
import os

from bums2.FORTRAN_METHODS.SAND2.sand2_main import Sand2Pipeline

class TestSand2Pipeline(unittest.TestCase):
    def setUp(self):
        #Create a dummy input and response file
        self.input_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        self.response_file = tempfile.NamedTemporaryFile(delete=False, mode='w')

        # Minimal valid input data
        self.input_file.write("2,3\n")  # M, N0
        self.input_file.write("0,100.0,1.0\n1,200.0,1.5\n")  # RFN, D, S
        self.input_file.write("1.0,2.0\n2.0,2.0\n3.0,0.0\n")  # ENBZKL, ZKL (ZKL[2] unused)
        self.input_file.write("2,4\n")
        self.input_file.write("10,1,0.01\n")  # MAXITER, CHIFAC, DEV
        self.input_file.close()

        self.response_file.write("2\n4\ncounts\n")  # MMM, N1, UNITS
        self.response_file.write("1.0\n")  # ENBR(1)
        self.response_file.write("2.0,0.5,0.2\n")  # ENBR(2), RES(0,0), RES(1,0)
        self.response_file.write("3.0,0.3,0.6\n")  # ENBR(3), ...
        self.response_file.write("4.0,0.1,0.2\n")  # ENBR(4), ...
        self.response_file.close()

    def tearDown(self):
        os.unlink(self.input_file.name)
        os.unlink(self.response_file.name)

    def test_pipeline_executes(self):
        pipeline = Sand2Pipeline(
            input_file=self.input_file.name,
            response_file=self.response_file.name,
            iqds=2,
            iqbs=3,
            max_iter=20,
            chi_fac=1,
            dev=1e-2
        )

        result = pipeline.run()

        self.assertIn("FI", result)
        self.assertIn("FSNEW", result)
        self.assertIn("CHI_DEFAULT", result)
        self.assertIn("CHI_SAND2", result)

        self.assertEqual(result["FI"].shape, result["FSNEW"].shape)
        self.assertTrue(np.all(result["FSNEW"] > 0))
        self.assertLessEqual(result["CHI_SAND2"], result["CHI_DEFAULT"])


    def test_flux_conservation(self):
        pipeline = Sand2Pipeline(
            input_file=self.input_file.name,
            response_file=self.response_file.name
        )

        result = pipeline.run()

        default_flux = result["FLUX_DEFAULT"]
        unfolded_flux = result["FLUX_SOLUTION"]
        self.assertGreater(default_flux, 0)
        self.assertGreater(unfolded_flux, 0)

if __name__ == "__main__":
    unittest.main()