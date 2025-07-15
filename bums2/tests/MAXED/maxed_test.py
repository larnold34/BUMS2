#Simple unittest test cases for the maxed.py in the MAXED directory, not the unfolding code
import unittest
from unittest.mock import patch, MagicMock
from bums2.FORTRAN_METHODS.MAXED.driver.maxed import MaxedDriver

class TestMaxeDriver(unittest.TestCase):
    def setUp(self):
        self.M = 2
        self.NB = 3
        self.MM = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        self.FI = [1.0, 1.0, 1.0]
        self.S = [0.1, 0.1]
        self.D = [5.0, 10.0]
        self.FLUX = 1.0
        self.T = 1.0
        self.RT = 0.9

    @patch("bums2.MAXED.driver.maxed.SimulatedAnnealingRunner")
    def test_driver_runs_successfully(self, mock_runner_class):
        mock_runner = MagicMock()
        mock_runner.run.return_value = [0.1, 0.2]
        mock_runner_class.return_value = mock_runner

        driver = MaxedDriver(
            m=self.M, nb=self.NB, mm=self.MM, fi=self.FI, 
            s=self.S, d=self.D, flux=self.FLUX, t=self.T, rt=self.RT
        )
        lambdas = driver.run()

        self.assertEqual(lambdas, [0.1, 0.2])
        self.assertEqual(len(lambdas), self.M)

    def test_driver_sets_omega_to_m(self):
        driver = MaxedDriver(
            m=self.M, nb=self.NB, mm=self.MM, fi=self.FI, 
            s=self.S, d=self.D, flux=self.FLUX, t=self.T, rt=self.RT
        )
        self.assertEqual(driver.OMEGA, float(self.M))

    @patch("bums2.MAXED.driver.maxed.SimulatedAnnealingRunner")
    def test_driver_invokes_runner_with_expected_params(self, mock_runner_class):
        mock_runner = MagicMock()
        mock_runner.run.return_value = [0.5, 0.6]
        mock_runner_class.retun_value = mock_runner

        driver = MaxedDriver(
            m=self.M, nb=self.NB, mm=self.MM, fi=self.FI, 
            s=self.S, d=self.D, flux=self.FLUX, t=self.T, rt=self.RT
        )
        _ = driver.run()

        args, kwargs = mock_runner_class.call_args
        self.assertEqual(kwargs['N'], self.M)
        self.assertEqual(kwargs['M'], self.M)
        self.assertEqual(kwargs['NB'], self.NB)
        self.assertEqual(kwargs['OMEGA'], float(self.M))

if __name__ == "__main__":
    unittest.main()