import unittest
import pytest
import sys
sys.path.append('../structures/')

from SolveLoads import *
from MathFunctions.Mechanics import StepFunction

class TestLoads(unittest.TestCase):
    def setUp(self):
        self.L1, self.L2 = SolveACLoads(1.95, 0.5, 3.5)
    def test_ACLoads(self):
        self.assertAlmostEqual(self.L1, 9787.2735, places=4)
        self.assertAlmostEqual(self.L2, 9155.8365, places=4)
    def test_WingLoads(self):
        wingEquation = SolveWingLoads(0.2, 11.2, self.L1, 800, (self.L1 + self.L2) / (8*9.81), 100, 3)
        Fx, Fy, Fz, Mx, My, Mz = WLoads = wingEquation.SolveEquation()
        calced = [-100, -8603.3291, 0, 24089.3216, -560, 830.3329]
        for j in range(len(calced)):
            self.assertAlmostEqual(calced[j], WLoads[j], places=3)