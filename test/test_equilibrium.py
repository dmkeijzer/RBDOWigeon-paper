import unittest
import pytest
import sys
sys.path.append('structures/')

from Equilibrium import PointLoad, Moment, RunningLoad, EquilibriumEquation

class TestEquilibrium(unittest.TestCase):
    def test_PointLoad(self):
        pl = PointLoad([1, 0, 0], [0, 1, 0])
        self.assertEqual(pl.force()[0], 1)
        self.assertEqual(pl.moment()[2], -1)
    
    def test_Moment(self):
        mom = Moment([0, 0, 1])
        self.assertTrue(all(i == 0 for i in mom.force()))
        self.assertListEqual(list(mom.moment()), [0, 0, 1])
    
    def test_RunningLoad(self):
        q = RunningLoad([[1]*5, [2]*5], range(5), 0)
        self.assertListEqual(list(q.force()), [0, 4, 8])
        self.assertListEqual(list(q.moment()), [0, -16, 8])
    
    def test_equilibrium(self):
        load1 = PointLoad([1, 0, 0], [0, 1, 0])
        load2 = PointLoad([1, 0, 0], [-1, 0, 0])
        load3 = PointLoad([0, 1, 0], [0, 1, 0])

        F1 = PointLoad([0, 1, 0], [0, 1, 0])
        F2 = PointLoad([1, 0, 0], [-1, 0, 0])
        F3 = PointLoad([0, -1, 0], [1, 0, 0])

        Eql = EquilibriumEquation(kloads=[load1, load2, load3], ukloads=[F1, F2, F3])
        Eql.SetupEquation()
        self.assertListEqual(list(Eql.SolveEquation()), [-2, -2, -1])
