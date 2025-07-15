#Simple test cases for prtvec within the MAXED directory
import unittest
from io import StringIO
from unittest.mock import patch
from bums2.FORTRAN_METHODS.MAXED.annealing.prtvec import VectorPrinter

class TestVectorPrinter(unittest.TestCase):
    @patch("sys.stdout", new_callable=StringIO)
    def test_short_vector_output(self, mock_stdout):
        vec = [1.1, 2.2, 3.3]
        VectorPrinter.print_vector("MYVECTOR", vec)
        output = mock_stdout.getvalue()

        self.assertIn("MYVECTOR", output)
        self.assertIn("     1.1", output)
        self.assertEqual(len(output.strip().splitlines()), 2)

    @patch("sys.stdout", new_callable=StringIO)
    def test_multi_line_output(self, mock_stdout):
        vec = list(range(15))
        VectorPrinter.print_vector("LONGVEC", vec)
        output = mock_stdout.getvalue()

        lines = output.strip().splitlines()
        self.assertEqual(len(lines), 3)
        self.assertTrue(all(str(i) in output for i in vec))

    @patch("sys.stdout", new_callable=StringIO)
    def test_exact_line_break(self, mock_stdout):
        vec = list(range(20))
        VectorPrinter.print_vector("TWENTY", vec)
        output = mock_stdout.getvalue()

        lines = output.strip().splitlines()
        self.assertEqual(len(lines), 3)

    @patch("sys.stdout", new_callable=StringIO)
    def test_empty_vector(self, mock_stdout):
        vec = []
        VectorPrinter.print_vector("EMPTY", vec)
        output = mock_stdout.getvalue()

        self.assertIn("EMPTY", output)
        self.assertEqual(len(output.strip().splitlines()), 1)

if __name__ == "__main__":
    unittest.main()

    