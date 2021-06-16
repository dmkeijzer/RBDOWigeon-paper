import unittest
import pytest
import pandas as pd

from structures.SolveLoads import Fatigue
from structures.Material import Material

class TestFatigue(unittest.TestCase):
    def setUp(self):
        self.max = 100
        self.fatigue = Fatigue(0, 0, self.max, 4, 2, 0.5, Material.load(file = 'data/materials.csv'))
    def test_Cycle(self):
        t, y = self.fatigue.determineCycle()
        self.assertGreater(y.max(), self.max)
        self.assertEqual(t.max(), 6)
        self.assertEqual(t.min(), 0)

    def test_Miners(self):
        self.fatigue.df = pd.DataFrame({'dS': [400, 140],
                           'count': [0.5 * self.fatigue.mat.BasquinLaw(400), 1.54 * self.fatigue.mat.BasquinLaw(140)]})
        self.assertEqual(1 / self.fatigue.MinersRule(), 2.04)

    def test_Basquins(self):
        self.assertAlmostEqual(self.fatigue.mat.BasquinLaw(140)*1e-6, 0.819970, places=1)
        self.assertAlmostEqual(self.fatigue.mat.BasquinLaw(200)*1e-6, 0.12304, places=0)