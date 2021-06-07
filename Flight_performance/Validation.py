import numpy as np
import matplotlib.pyplot as plt
from Aero_tools import speeds, ISA
from Flight_performance_final import evtol_performance, mission
from constants import g
import scipy.optimize as optimize

class monte_carlo:
    def __init__(self, mass, cruising_alt, cruise_speed, wing_surface = 10, t_loiter = 30*60, rotational_rate = 5,
                 roc = 5, rod = 5, mission_dist = 300e3):

        # Initial values for all the input parameters
        self.mass = mass
        self.h_cr = cruising_alt
        self.v_cr = cruise_speed
        self.S    = wing_surface
        self.t_lt = t_loiter
        self.rot  = rotational_rate
        self.roc  = roc
        self.rod  = rod
        self.dist = mission_dist

        # Range over which the values are allowed to vary
        var     = 0.05    # [-] +- percentage variation
        N_pts   = 5       # [-] Number of different variations per parameter

        max_var = 1 + var
        min_var = 1 - var

        # Put everything in an array, so it's easier to go over it
        self.params = np.array([np.linspace(self.mass*min_var, self.mass*max_var, N_pts),
                                np.linspace(self.h_cr*min_var, self.h_cr*max_var, N_pts),
                                np.linspace(self.v_cr*min_var, self.v_cr*max_var, N_pts),
                                np.linspace(self.S*min_var,    self.S*max_var, N_pts),
                                np.linspace(self.t_lt*min_var, self.t_lt*max_var, N_pts),
                                np.linspace(self.rot*min_var, self.rot*max_var, N_pts),
                                np.linspace(self.roc*min_var, self.roc*max_var, N_pts),
                                np.linspace(self.rod*min_var, self.rod*max_var, N_pts),
                                np.linspace(self.dist*min_var, self.dist*max_var, N_pts)])

    def monte_carlo_sim(self):


monte_carlo(2000, 300, 60)

# class validation:
#     """
#     Class used to validate the methods used in Flight_performance_final.
#     TODO:
#         - Validate:
#             - Range
#             - Rate-of-climb
#             - Max speed
#             - Power usage
#             - Energy required
#             - ...
#         - Add maximum power
#     """
#     def __init__(self):
#
#         self.h_cruise  = 300
#         self.m  = 2000          # [kg]  Aircraft mass
#         self.W = self.m*g
#         self.V = speeds(altitude=self.h_cruise, m=self.m)
#         self.V_cr = self.V.cruise()    # [m/s] Cruise speed
#
#     def rate_of_climb_vertical(self):
#
#         P_max = 600000 # TODO !!!!! IMPLEMENT !!!!!
#         T_hov = self.W
#         P_hov = 600000    # TODO: ADD FROM PROPULSION
#
#         # Rate of climb from helicopter reader
#         C = 2*(P_max - P_hov)/self.W
#
#         # Rate of climb as done in the model
#         performance = evtol_performance(self.h_cruise, self.V_cr)
#
#         RC = optimize.fsolve(performance.vertical_equilibrium, 5, args=(self.h_cruise, self.m))
#
#         # Compare the 2
#         print("R/C reader:", C)
#         print("R/C model: ", RC)
#
#
# validate = validation()
# validate.rate_of_climb_vertical()
