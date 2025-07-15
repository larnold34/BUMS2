#Simple test cases for prt.py inside of the MAXED directory
import unittest
from io import StringIO
from unittest.mock import patch
from bums2.FORTRAN_METHODS.MAXED.annealing.prt import SAReporter


class TestSAReporter(unittest.TestCase):

    @patch("sys.stdout", new_callable=StringIO)
    def test_prt1_output(self, mock_stdout):
        SAReporter.prt1(i=2, xi=5.5, LB=0.0, UB=5.0)
        output = mock_stdout.getvalue()
        self.assertIn("THE STARTING VALUE", output)
        self.assertIn("2", output)
        self.assertIn("5.5", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_prt2_maximize(self, mock_stdout):
        SAReporter.prt2(maximize=True, x=[1.0, 2.0], f=3.5)
        output = mock_stdout.getvalue()
        self.assertIn("INITIAL X", output)
        self.assertIn("INITIAL F: 3.5", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_prt2_minimize(self, mock_stdout):
        SAReporter.prt2(maximize=False, x=[1.0, 2.0], f=3.5)
        output = mock_stdout.getvalue()
        self.assertIn("INITIAL F: -3.5", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_prt6_acceptance_message(self, mock_stdout):
        SAReporter.prt6(maximize=True)
        self.assertIn("POINT ACCEPTED", mock_stdout.getvalue())

        mock_stdout.seek(0)
        mock_stdout.truncate(0)
        SAReporter.prt6(maximize=False)
        self.assertIn("POINT ACCEPTED", mock_stdout.getvalue())

    @patch("sys.stdout", new_callable=StringIO)
    def test_prt7_rejection_message(self, mock_stdout):
        SAReporter.prt7(maximize=True)
        self.assertIn("REJECTED", mock_stdout.getvalue())

        mock_stdout.seek(0)
        mock_stdout.truncate(0)
        SAReporter.prt7(maximize=False)
        self.assertIn("REJECTED", mock_stdout.getvalue())

    @patch("sys.stdout", new_callable=StringIO)
    def test_prt10_termination(self, mock_stdout):
        SAReporter.prt10()
        output = mock_stdout.getvalue()
        self.assertIn("TERMINATION", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_prt9_maximize_summary(self, mock_stdout):
        SAReporter.prt9(
            maximize=True,
            n=2,
            t=1.5,
            xopt=[1.0, 2.0],
            vm=[0.1, 0.2],
            fopt=4.56,
            nup=3,
            ndown=2,
            nrej=1,
            out_of_bounds=0,
            nnew=1
        )
        output = mock_stdout.getvalue()
        self.assertIn("MAX FUNCTION VALUE", output)
        self.assertIn("UPHILL", output)
        self.assertIn("STEP LENGTH", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_prt9_minimize_summary(self, mock_stdout):
        SAReporter.prt9(
            maximize=False,
            n=2,
            t=0.75,
            xopt=[-1.0, -2.0],
            vm=[0.5, 0.6],
            fopt=-3.21,
            nup=2,
            ndown=1,
            nrej=3,
            out_of_bounds=1,
            nnew=2
        )
        output = mock_stdout.getvalue()
        self.assertIn("MIN FUNCTION VALUE", output)
        self.assertIn("REJECTED UPHILL", output)
        self.assertIn("CURRENT OPTIMAL X", output)


if __name__ == '__main__':
    unittest.main()
