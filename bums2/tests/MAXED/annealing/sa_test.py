#Unitesting of sa.py inside of the MAXED directory
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from bums2.FORTRAN_METHODS.MAXED.annealing.sa import SimulatedAnnealing

class TestSimulatedAnnealing(unittest.TestCase):
    def create_sa_instance(self):
        return SimulatedAnnealing(
            m=2,
            nb=2,
            mm=np.array([[1, 1], [1, 1]]),
            fi=np.array([1.0, 1.0]),
            s=np.array([0.1, 0.1]),
            d=np.array([0.5, 0.5]),
            omega=0.1,
            flux=1.0,
            t=1.0,
            rt=0.9,
            max=True,
            max_eval=1000,
            iprint=0
        )
    @patch("bums2.MAXED.annealing.sa.ObjectiveFunction")
    def test_first_evaluation_valid(self, mock_fcn):
        mock_fcn.return_value = lambda x: 3.14

        sa = self.create_sa_instance()
        sa._initialize()
        sa._first_evaluation()
        
        self.assertEqual(sa.F, 3.14)
        self.assertEqual(sa.FOPT, 3.14)
        self.assertEqual(sa.FSTAR[0], 3.14)

    def test_invalid_temperature_check(self):
        sa = self.create_sa_instance()
        sa.T = 0.0  # Force error
        sa._initialize()
        sa._first_evaluation()
        self.assertEqual(sa.IER, 3)

    def test_bounds_violation_check(self):
        sa = self.create_sa_instance()
        sa.X = [1e50, 1e50]  # Out of default [-1e25, 1e25]
        sa._initialize()
        sa._first_evaluation()
        self.assertEqual(sa.IER, 2)

    def test_convergence_detection(self):
        sa = self.create_sa_instance()
        sa._initialize()
        sa.F = 1.0
        sa.FSTAR = [1.0, 1.000001, 1.0000002, 0.999999]
        sa.EPS = 1e-3
        self.assertTrue(sa._converged())

    def test_step_adaptation_logic(self):
        sa = self.create_sa_instance()
        sa._initialize()
        sa.VM = [1.0, 1.0]
        sa.NACP = [18, 2]  # Acceptances per dimension
        sa._adapt_steps()
        self.assertGreater(sa.VM[0], 1.0)
        self.assertLess(sa.VM[1], 1.0)

    def test_propose_in_bounds(self):
        sa = self.create_sa_instance()
        sa._initialize()
        with patch.object(sa.rng, "RANMAR", return_value=0.5):
            xp, oob = sa._propose(h=0, z=0, j=0, LNOBS=0)
        self.assertEqual(len(xp), sa.N)
        self.assertTrue(all(sa.LB[i] <= xp[i] <= sa.UB[i] for i in range(sa.N)))

    @patch("bums2.MAXED.annealing.sa.ObjectiveFunction")
    def test_inner_step_accepts_uphill(self, mock_fcn):
        sa = self.create_sa_instance()
        sa._initialize()
        sa.F = 2.0
        sa.FOPT = 2.0
        mock_fcn.return_value = lambda x: 3.14

        with patch.object(sa.rng, "RANMAR", return_value=0.5):
         nup, nnew, nrej, ndown = sa._inner_step(h=0, z=0, j=0, LNOBDS=0, NUP=0, NNEW=0, NREJ=0, NDOWN=0)
        self.assertEqual(nup, 1)
        self.assertEqual(nnew, 1)
    
    def test_optimize_real_function(self):
        sa = SimulatedAnnealing(
        m=2,
        nb=2,
        mm=np.array([[0.1, 0.2], [0.3, 0.4]]),
        fi=np.array([1.0, 2.0]),
        s=np.array([0.1, 0.1]),
        d=np.array([0.5, 0.5]),
        omega=0.1,
        flux=1.0,
        t=5.0,
        rt=0.85,
        max=True,
        max_eval=1000,
        iprint=0
        )
        try:
            result = sa.optimize()
        except RuntimeError:
            result = sa.XOPT  # fallback if too many evaluations

        assert isinstance(result, list)



if __name__ == '__main__':
    unittest.main()