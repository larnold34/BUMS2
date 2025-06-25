#The following script is intended to conduct unit testing with config.py to make sure variables are assigned properly
import os
import tempfile
import unittest
from pathlib import Path
from bums2.core.config import Bums2Config

class TestBums2Config(unittest.TestCase):

    def make_temp_file(self, contents=""):
        fd, path = tempfile.mkstemp(text=True)
        os.write(fd, contents.encode("utf-8"))
        os.close(fd)
        return Path(path)
    
    def test_basic_from_dict_all_types(self):
        #Prepare a ake input dict, as strings from CLI or CGI
        raw = {
            "input_file": "/foo/bar.in",
            "output_file": "/foo/bar.out",
            "max_energy": "12.5",
            "iter": "250",
            "itertesterror": "10",
            "endtesterror": "0.1",
            "tempij": "1.23",
            "smoothing": "0.05",
            "shape": "0.2",
            "pertubation": "0.03",
            "cal_factor": "99.9",
            # detector mask: three detectors on, two off
            "detector_mask": "true,false,1,0,yes,no",
            # measured counts and errors as comma lists
            "measured_counts": "1.0,2.5,3.5,4.0,5.0,6.0",
            "measured_errors":  "0.1,0.2,0.3,0.4,0.5,0.6",
            # other string fields pass through
            "matrix_name": "UTA4",
            "start_spec": "User Input",
            "alg": "SPUNIT",}
        
        cfg = Bums2Config.from_dict(raw)

        #Paths
        self.assertIsInstance(cfg.input_file, Path)
        self.assertEqual(str(cfg.input_file), "/foo/bar.in")
        self.assertIsInstance(cfg.output_file, Path)
        self.assertEqual(str(cfg.output_file), "/foo/bar.out")

        #Floats
        self.assertEqual(cfg.max_energy, 12.5)
        self.assertEqual(cfg.iter, 250.0)
        self.assertEqual(cfg.itertesterror, 10.0)
        self.assertEqual(cfg.endtesterror, 0.1)
        self.assertEqual(cfg.tempij, 1.23)
        self.assertEqual(cfg.smoothing, 0.05)
        self.assertEqual(cfg.shape, 0.2)
        self.assertEqual(cfg.pertubation, 0.03)
        self.assertEqual(cfg.cal_factor, 99.9)

        #Bool masking
        self.assertEqual(cfg.detector_mask, [True, False, True, False, True, False])

        #Float list parsing
        self.assertEqual(cfg.measured_counts, [1.0, 2.5, 3.5, 4.0, 5.0, 6.0])
        self.assertEqual(cfg.measured_errors, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])

        #Passthrough strings
        self.assertEqual(cfg.matrix_name, "UTA4")
        self.assertEqual(cfg.start_spec, "User Input")
        self.assertEqual(cfg.alg, "SPUNIT")

    def test_missing_optional_fields(self):
        #Build a dict with only the required float variables
        raw = {
            "max_energy": "1.0",
            "iter":   "10",
            "itertesterror": "1",
            "endtesterror":  "2",
            "tempij":      "0.3",
            "smoothing":   "0.4",
            "shape":       "0.5",
            "pertubation": "0.6",
            "cal_factor":  "0.7",
            "matrix_name": "UTA4",
            "start_spec": "User Input",
            "alg": "SPUNIT",
        }

        cfg = Bums2Config.from_dict(raw)

        #Check that everything that was not set is None of empty
        self.assertIsNone(cfg.input_file)
        self.assertIsNone(cfg.output_file)
        self.assertEqual(cfg.detector_mask, [])
        self.assertEqual(cfg.measured_counts, [])
        self.assertEqual(cfg.measured_errors, [])

    def test_bad_type_raises(self):
        raw = {
            "max_energy": "not-a-number",
            "iter":   "10",
            "itertesterror": "0.1",
            "endtesterror":  "0.2",
            "tempij":      "0.3",
            "smoothing":   "0.4",
            "shape":       "0.5",
            "pertubation": "0.6",
            "cal_factor":  "0.7",
            "matrix_name": "UTA4",
            "start_spec": "User Input",
            "alg": "SPUNIT",
        }
        with self.assertRaises(ValueError):
            Bums2Config.from_dict(raw)
    
    def test_ignore_unknown_input(self):
        raw = {
            "max_energy": "2.0",
            "iter":   "20",
            "itertesterror": "0.1",
            "endtesterror":  "0.2",
            "tempij":      "0.3",
            "smoothing":   "0.4",
            "shape":       "0.5",
            "pertubation": "0.6",
            "cal_factor":  "0.7",
            "foo": "bar",          # should be ignored
            "measured_counts": "1,2,3",
            "measured_errors":  "0.1,0.2,0.3",
            "matrix_name": "UTA4",
            "start_spec": "User Input",
            "alg": "SPUNIT",
        }
        cfg = Bums2Config.from_dict(raw)
        self.assertTrue(hasattr(cfg, "foo") is False)
        self.assertEqual(cfg.measured_counts, [1.0, 2.0, 3.0])
        self.assertEqual(cfg.measured_errors, [0.1, 0.2, 0.3])


if __name__ == "__main__":
    unittest.main()
