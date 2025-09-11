#The following script is intended to conduct unit testing with input.py functions
import os
import sys
import tempfile
import unittest
from pathlib import Path
from io import BytesIO
from unittest.mock import patch

from bums2.io.input import InputParser
from bums2.core.config import Bums2Config

class TestInputParser(unittest.TestCase):
    def setUp(self):
        #Create a sample of a CLI input
        self.clitxt = "\n".join([
            "max_energy=10.0",
            "iter=100",
            "itertesterror=5.0",
            "endtesterror=2.5",
            "tempij=1.0",
            "smoothing=0.1",
            "shape=0.2",
            "pertubation=0.3",
            "cal_factor=50.0",
            "matrix_name=UTA4",
            "start_spec=User%20Input",
            "alg=SPUNIT",
            "",
        ])

        #Write out the input
        fd, self.clifile = tempfile.mkstemp(text=True)
        os.write(fd, self.clitxt.encode('utf-8'))
        os.close(fd)

        #Output path, no content needed just the mandatory pathing
        fd2, self.outfile = tempfile.mkstemp(text=True)
        os.close(fd2)

    def tearDown(self):
        os.unlink(self.clifile)
        os.unlink(self.outfile)

    def test_parse_cli_happy_path(self):
        testargs = ["bums2", "-i", self.clifile, "-o", self.outfile]
        with patch.object(sys, "argv", testargs):
            parser = InputParser()
            cfg = parser.parse()

            #Verify some spots in the resulting config
            self.assertEqual(cfg.max_energy, 10.0)
            self.assertEqual(cfg.iter, 100.0)
            self.assertEqual(cfg.alg, "SPUNIT")

            #Paths should be Path instances
            self.assertIsInstance(cfg.input_file, Path)
            self.assertEqual(str(cfg.input_file), self.clifile)
            self.assertIsInstance(cfg.output_file, Path)
            self.assertEqual(str(cfg.output_file), self.outfile)

    @patch.dict(os.environ, {"GATEWAY_INTERFACE": "CGI/1.1"})
    @patch("bums2.io.input.cgi.FieldStorage")
    def test_parse_cgi_happy_path(self, mock_fieldstorage):
        form_data = {
            "max_energy": "20.0",
            "iter": "200",
            "itertesterror": "7.5",
            "endtesterror": "3.5",
            "tempij": "1.2",
            "smoothing": "0.15",
            "shape": "0.25",
            "pertubation": "0.35",
            "cal_factor": "60.0",
            "matrix_name": "LOGNM",
            "start_spec": "Automatic%20Search",
            "alg": "MAXED",
        }

        fake_fs = {}
        for k, v in form_data.items():
            fake_fs[k] = v
        instance = mock_fieldstorage.return_value
        instance.keys.return_value = list(fake_fs)
        instance.getvalue.side_effect = lambda k, default="": fake_fs.get(k, default)

        cfg = InputParser().parse()

        #Now verify that the inputs were decoded and assigned properly
        self.assertEqual(cfg.max_energy, 20.0)
        self.assertEqual(cfg.iter, 200.0)
        self.assertEqual(cfg.alg, "MAXED")
        self.assertEqual(cfg.matrix_name, "LOGNM")
        self.assertEqual(cfg.start_spec, "Automatic Search")

if __name__ == "__main__":
    unittest.main()
