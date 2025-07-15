#Simple unittest test cases for the added input parser within the MAXED directory
import unittest
import tempfile
import os

from bums2.FORTRAN_METHODS.MAXED.driver.maxed_input_parser import MaxedInputParser

class TestMaxedInputParser(unittest.TestCase):
    def setUp(self):
        #Minimal dummy input
        self.input_lines = [
            "2,3",
            "1,100.0,1.0",
            "2,200.0,2.0",
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

        self.input_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.input_file.write("\n".join(self.input_lines))
        self.input_file.close()

        self.response_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.response_file.write("\n".join(self.response_lines))
        self.response_file.close()

    def tearDown(self):
        os.remove(self.input_file.name)
        os.remove(self.response_file.name)

    def test_parse_input_fields(self):
        parser = MaxedInputParser(self.input_file.name, self.response_file.name)
        parser.parse()
        data = parser.get_input_data()

        self.assertEqual(data["M"], 2)
        self.assertEqual(data["N0"], 3)
        self.assertEqual(data["RFN"], [1, 2])
        self.assertEqual(data["D"], [100.0, 200.0])
        self.assertEqual(data["S"], [1.0, 2.0])
        self.assertEqual(data["ENBZKL"], [1.0, 2.0, 3.0])
        self.assertEqual(data["ZKL"], [0.1, 0.2, 0.3])
        self.assertEqual(data["MMM"], 2)
        self.assertEqual(data["N1"], 3)

    def test_parse_response_fields(self):
        parser = MaxedInputParser(self.input_file.name, self.response_file.name)
        parser.parse()
        data = parser.get_response_data()

        self.assertEqual(data["MMM"], 2)
        self.assertEqual(data["N1"], 3)
        self.assertEqual(data["UNITS"], "cm^2")
        self.assertEqual(data["ENBR"], [1.0, 2.0, 3.0])

        #RES should be tranposed to [2 x 2]
        self.assertEqual(len(data["RES"]), 2)
        self.assertEqual(len(data["RES"][0]), 2)
        self.assertAlmostEqual(data["RES"][0][0], 1.1)
        self.assertAlmostEqual(data["RES"][1][0], 2.1)

    def test_harder_consistency_assertion(self):
        with open(self.response_file.name, "w") as f:
            f.write("99\n3\ncm^21.0\n2.0,1.1,2.1\n3.0,1.2,2.2")

        parser = MaxedInputParser(self.input_file.name, self.response_file.name)
        with self.assertRaises(AssertionError):
            parser.parse()

if __name__ == "__main__":
    unittest.main()

    