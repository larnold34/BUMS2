#The following script is intended to conduct unit testing with detectors.py functions
import os
import tempfile
import unittest
from pathlib import Path
import shutil

from bums2.core.detectors import ResponseCurve, DetectorResponses

class TestDetectors(unittest.TestCase):
    #This function will return a path to a test file, points = list of (energy, value)
    def make_dose_file(self, dirpath, name, units, points):
        path = dirpath / f"{name.replace(' ', '_')}.txt"
        with path.open('w', encoding='utf-8') as f:
            f.write(name + "\n")
            f.write(units + "\n")
            for e, v in points:
                f.write(f"{e:.6e}\t{v:.6e}\n")
        return path
    
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.dose_dir = self.tmpdir / "dose"
        self.response_dir = self.tmpdir / "response"
        self.dose_dir.mkdir()
        self.response_dir.mkdir()

        #A small dose file
        self.dose_pts = [(1.0, 2.0), (2.0, 4.0), (4.0, 8.0)]
        self.dc_file = self.make_dose_file(self.dose_dir, name="LinearDose", units="uDose", points=self.dose_pts)

        #A small response file
        self.res_pts = [(1.0, 1.0), (2.0, 4.0), (4.0, 16.0)]
        self.rc_file = self.make_dose_file(self.response_dir, name="QuadResp", units="uResp", points=self.res_pts)

        #A small example spectrum
        self.ce = [1.0, 2.0, 4.0]
        self.values = [10.0, 100.0, 1000.0]

    def tearDown(self):
        #Apply a clean up
        for p in self.tmpdir.iterdir():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
        self.tmpdir.rmdir()
 

    def test_dose_parsing_and_apply(self):
        rc = ResponseCurve(self.dc_file)
        self.assertEqual(rc.name, "LinearDose")
        self.assertEqual(rc.units, "uDose")

        #Eneries and values are zipped accordingly
        self.assertEqual(rc.energies, tuple(e for e,_ in self.dose_pts))
        self.assertEqual(rc.values, tuple(v for _,v in self.dose_pts))

        # apply: do a log-linear interp of D at each ce, weighted by values
        # but here our points exactly match, so no interpolation:
        # sum_i values[i] * D( ce[i] )
        # = 10*2 + 100*4 + 1000*8 = 20 + 400 + 8000 = 8420
        tot = rc.apply(self.ce, self.values)
        self.assertAlmostEqual(tot, 8420.0, places=6)
    
    def test_detector_response_methods(self):
        dr = DetectorResponses(
            ce = self.ce,
            values = self.values,
            dose_dir = self.dose_dir,
            response_dir = self.response_dir,
        )

        #dose functions should yield one tuple for the single file
        dose_fs = dr.dose_functions()
        self.assertEqual(len(dose_fs), 1)
        name, val, units = dose_fs[0]
        self.assertEqual(name, "LinearDose")
        self.assertEqual(units, "uDose")

        #Sanity double check
        self.assertAlmostEqual(val, 8420.0, places=6)

        #detector response should yield one entry from QuadResp
        resp = dr.detector_response()
        self.assertEqual(len(resp), 1)
        name2, val2, units2, = resp[0]
        self.assertEqual(name2, "QuadResp")
        self.assertEqual(units2, "uResp")

        #Weighted sunm: 10*1 + 100*4 + 1000*16 = 10 + 400 + 16000 = 16410
        self.assertAlmostEqual(val2, 16410.0, places=6)

        #Standard equivalent values listed in correct order, should be 6 entries
        std_eq = dr.standard_equivalent()
        labels = [lbl for lbl,_,_ in std_eq]
        expected_labels = [
            "ICRP-21 Dose Equivalent H",
            "NCRP-38 Dose Equivalent H",
            "ANSI/ANS-6.1.1-1991 Equivalent Dose AP (Ht)",
            "ANSI/ANS-6.1.1-1991 Equivalent Dose PA (Ht)",
            "ANSI/ANS-6.1.1-1991 Equivalent Dose LAT (Ht)",
            "ANSI/ANS-6.1.1-1991 Equivalent Dose ROT (Ht)",
        ]
        self.assertEqual(labels, expected_labels)

        #No need to do exact values, the logic of dfact has already been verified
        #Will test to make sure all the outputs are positive floats
        for _, tval, unit in std_eq:
            self.assertTrue(isinstance(tval, float))
            self.assertGreater(tval, 0.0)
            self.assertEqual(unit, "pSv")

if __name__ == "__main__":
    unittest.main()





