#Unittesting of simann.py within the MAXED directory
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from bums2.FORTRAN_METHODS.MAXED.annealing.simann import SimulatedAnnealingRunner


class TestSimulatedAnnealingRunner(unittest.TestCase):

    def setUp(self):
        self.N = 2
        self.runner_args = {
            "N": self.N,
            "M": 2,
            "NB": 2,
            "MM": [[0.1, 0.2], [0.3, 0.4]],
            "FI": [1.0, 1.0],
            "S": [0.1, 0.1],
            "D": [0.5, 0.5],
            "OMEGA": 0.1,
            "FLUX": 1.0,
        }

    @patch("bums2.MAXED.annealing.simann.SimulatedAnnealing")
    def test_runner_runs_successfully(self, mock_sa_class):
        mock_sa = MagicMock()
        mock_sa.optimize.return_value = [0.1, 0.2]
        mock_sa.XOPT = [0.1, 0.2]
        mock_sa.VM = [0.5, 0.5]
        mock_sa.FOPT = 3.5
        mock_sa.NFCNEV = 100
        mock_sa.NACC = 90
        mock_sa.NOBDS = 5
        mock_sa.T = 0.2
        mock_sa.IER = 0
        mock_sa_class.return_value = mock_sa

        runner = SimulatedAnnealingRunner(**self.runner_args, IPRINT=0)
        result = runner.run()
        self.assertEqual(result, [0.1, 0.2])
        self.assertEqual(len(result), self.N)

    @patch("bums2.MAXED.annealing.simann.SimulatedAnnealing")
    def test_runner_handles_runtimeerror(self, mock_sa_class):
        mock_sa = MagicMock()
        mock_sa.optimize.side_effect = RuntimeError("Max evals exceeded")
        mock_sa.XOPT = [0.0, 0.0]
        mock_sa.VM = [1.0, 1.0]
        mock_sa.FOPT = 0.0
        mock_sa.NFCNEV = 100000
        mock_sa.NACC = 50
        mock_sa.NOBDS = 10
        mock_sa.T = 0.1
        mock_sa.IER = 1
        mock_sa_class.return_value = mock_sa

        runner = SimulatedAnnealingRunner(**self.runner_args, IPRINT=0)
        result = runner.run()
        self.assertEqual(result, [0.0, 0.0])  # Should return XOPT fallback
        self.assertEqual(mock_sa.IER, 1)

    def test_runner_initializes_defaults(self):
        runner = SimulatedAnnealingRunner(**self.runner_args)
        self.assertEqual(runner.EPS, 1e-6)
        self.assertEqual(runner.X, [0.0, 0.0])
        self.assertEqual(runner.VM, [1.0, 1.0])
        self.assertEqual(runner.LB, [-1e25, -1e25])
        self.assertEqual(runner.UB, [1e25, 1e25])
        self.assertEqual(runner.C, [2.0, 2.0])

    def test_runner_returns_expected_length(self):
        runner = SimulatedAnnealingRunner(**self.runner_args, IPRINT=0)
        with patch("bums2.MAXED.annealing.simann.SimulatedAnnealing") as mock_sa_class:
            mock_sa = MagicMock()
            mock_sa.optimize.return_value = [0.1, 0.2]
            mock_sa_class.return_value = mock_sa
            result = runner.run()
            self.assertEqual(len(result), self.N)

    @patch("bums2.MAXED.annealing.simann.SimulatedAnnealing")
    def test_runner_passes_all_parameters(self, mock_sa_class):
        runner = SimulatedAnnealingRunner(**self.runner_args, T=2.5, RT=0.85, IPRINT=0)
        runner.run()

        args, kwargs = mock_sa_class.call_args
        self.assertEqual(kwargs['T'], 2.5)
        self.assertEqual(kwargs['RT'], 0.85)
        self.assertEqual(kwargs['MAX'], True)

    @patch("bums2.MAXED.annealing.simann.VectorPrinter.print_vector")
    @patch("bums2.MAXED.annealing.simann.SimulatedAnnealing")
    def test_runner_prints_vectors(self, mock_sa_class, mock_printer):
        mock_sa = MagicMock()
        mock_sa.optimize.return_value = [0.1, 0.2]
        mock_sa.XOPT = [0.1, 0.2]
        mock_sa.VM = [0.1, 0.1]
        mock_sa.FOPT = 1.0
        mock_sa.NFCNEV = 10
        mock_sa.NACC = 8
        mock_sa.NOBDS = 0
        mock_sa.T = 0.5
        mock_sa.IER = 0
        mock_sa_class.return_value = mock_sa

        runner = SimulatedAnnealingRunner(**self.runner_args, IPRINT=1)
        runner.run()

        self.assertTrue(mock_printer.called)


if __name__ == "__main__":
    unittest.main()
