#Simple unittest test case for main.py within the MAXED directory
import unittest
import tempfile
import os
from BUMS2.bums2.FORTRAN_METHODS.MAXED.driver.maxed_main import MaxedPipeline
from bums2.FORTRAN_METHODS.MAXED.driver.maxed_input_parser import MaxedInputParser

class TestMaxedOrchestrator(unittest.TestCase):

    def setUp(self):
        # Temporary input file
        self.input_lines = [
            "2,3",
            "0,100.0,1.0",
            "1,200.0,2.0",
            "1.0,0.1",
            "2.0,0.2",
            "3.0,0.3",
            "2,3",
            "1.0"
        ]

        self.response_lines = [
            "2",
            "3",
            "cm^2",
            "1.0",
            "2.0,1.1,2.1",
            "3.0,1.2,2.2"
        ]

        self.input_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.input_file.write("\n".join(self.input_lines))
        self.input_file.close()

        self.response_file = tempfile.NamedTemporaryFile(mode="w+", delete=False)
        self.response_file.write("\n".join(self.response_lines))
        self.response_file.close()

    def tearDown(self):
        os.remove(self.input_file.name)
        os.remove(self.response_file.name)

    def test_pipeline_executes_without_error(self):
        orchestrator = MaxedPipeline(self.input_file.name, self.response_file.name)
        result = orchestrator.run()
        self.assertIsInstance(result, dict)

    def test_result_contains_expected_keys(self):
        orchestrator = MaxedPipeline(self.input_file.name, self.response_file.name)
        result = orchestrator.run()

        expected_keys = ["FI", "FOUT", "FIL", "FL", "LAMBDA",
                         "CHI_DEFAULT", "CHI_MAXENT",
                         "FLUX_DEFAULT", "FLUX_SOLUTION"]
        for key in expected_keys:
            self.assertIn(key, result)

    def test_result_lambda_shape_matches_detector_count(self):
        orchestrator = MaxedPipeline(self.input_file.name, self.response_file.name)
        result = orchestrator.run()

        self.assertEqual(len(result["LAMBDA"]), 2)  # M = 2

    def test_result_flux_consistency(self):
        orchestrator = MaxedPipeline(self.input_file.name, self.response_file.name)
        result = orchestrator.run()

        self.assertAlmostEqual(result["FLUX_DEFAULT"], sum(result["FI"]), places=6)
        self.assertAlmostEqual(result["FLUX_SOLUTION"], sum(result["FOUT"]), places=6)

if __name__ == '__main__':
    unittest.main()