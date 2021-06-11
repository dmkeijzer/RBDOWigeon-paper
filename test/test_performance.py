import unittest
import numpy as np
from Aero_tools import ISA
from Flight_performance.Flight_performance_final import evtol_performance
import scipy.optimize as optimize
from constants import g

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

        performance = evtol_performance(300, 60, S = 10, CL_max = 1.5, mass = 2000, battery_capacity = 500e6,
                                        EOM = 1500, loiter_time = 30*60, CD_vertical = 1)
        V_max_RC    = performance.climb_performance(testing = True)

        self.assertAlmostEqual(V_max, V_max_RC, delta = 5)

    def test_vertical_climb(self):

        performance = evtol_performance(cruising_alt=300, cruise_speed=60, S = 10, CL_max = 1.5, mass = 2000,
                                        battery_capacity = 500e6, EOM = 1500, loiter_time = 30*60, CD_vertical = 1)

        rho    = ISA(0).density()

        # Prediction using terminal velocity
        V_fall  = -np.sqrt(2*performance.W/(performance.CD_vert*rho*performance.S))

        # Prediction using actual model
        V_mod   = performance.vertical_equilibrium(300, testing = True, test_thrust = 0)

        self.assertAlmostEqual(V_fall, V_mod, delta = 2)

    def test_max_thrust(self):
        # Check the numerical inverse of the T vs P relationship

        perf = evtol_performance(cruising_alt = 300, cruise_speed = 60, CL_max=1.5, A_disk=10, S = 14,
                                     battery_capacity=4e6*1.2, mass = 3000, EOM = 3000 - 475, loiter_time = 30*60,
                                     P_max = 3000000)

        T_max = perf.max_thrust(1.225, 50)

        P_m   = perf.thrust_to_power(T_max, 50, 1.225)

        self.assertAlmostEqual(P_m, 0)


