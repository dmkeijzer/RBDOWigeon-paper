import numpy as np
import matplotlib.pyplot as plt
from Aero_tools import speeds, ISA
from Flight_performance_final import evtol_performance
from constants import g
import scipy.optimize as optimize


class validation:
    """
    Class used to validate the methods used in Flight_performance_final.
    TODO:
        - Validate:
            - Range
            - Rate-of-climb
            - Max speed
            - Power usage
            - Energy required
            - ...
        - Add maximum power
    """
    def __init__(self):

        self.h_cruise  = 300
        self.m  = 2000          # [kg]  Aircraft mass
        self.W = self.m*g
        self.V = speeds(altitude=self.h_cruise, m=self.m)
        self.V_cr = self.V.cruise()    # [m/s] Cruise speed

    def rate_of_climb_vertical(self):

        P_max = 600000 # TODO !!!!! IMPLEMENT !!!!!
        T_hov = self.W
        P_hov = 600000    # TODO: ADD FROM PROPULSION

        # Rate of climb from helicopter reader
        C = 2*(P_max - P_hov)/self.W

        # Rate of climb as done in the model
        performance = evtol_performance(self.h_cruise, self.V_cr)

        RC = optimize.fsolve(performance.vertical_equilibrium, 5, args=(self.h_cruise, self.m))

        # Compare the 2
        print("R/C reader:", C)
        print("R/C model: ", RC)


validate = validation()
validate.rate_of_climb_vertical()
