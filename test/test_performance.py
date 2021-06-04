import unittest
import numpy as np
from Aero_tools import ISA
from Flight_performance.Flight_performance_final import evtol_performance

class testPerformance(unittest.TestCase):
    def test_max_speed(self):

        # !!!! IMPLEMENT WHEN VALUES ARE THERE !!!!
        prop_eff = 0.95
        P_br_max = 600000
        S        = 10
        W        = 2000

        rho     = ISA(300).density()

        # Finding V is iterative
        V = 100
        err = 10

        while err > 0.5:

            V_init  = V
            CL      = 2*W/(rho*V*V*S)
            CD      = 0.05 + 0.05*CL*CL  # CHANGE

            # Compare the maximum speed from the climb rate plot to an analytical solution
            V       = (2*prop_eff*P_br_max/(rho*S*CD))**(1/3)

            err = abs(V - V_init)

        V_max = V

        performance = evtol_performance(300, 60)
        V_max_RC    = performance.climb_performance(testing = True)

        self.assertAlmostEqual(V_max, V_max_RC, delta = 5)

