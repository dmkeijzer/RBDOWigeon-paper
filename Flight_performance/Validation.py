import numpy as np
import matplotlib.pyplot as plt
from Aero_tools import speeds, ISA
from Flight_performance_final import evtol_performance, mission
from constants import g
import scipy.optimize as optimize

class monte_carlo:
    def __init__(self, mass, cruising_alt, cruise_speed, CL_max, wing_surface = 10, t_loiter = 30*60, rotational_rate = 5,
                 roc = 5, rod = 5, mission_dist = 300e3):

        # Initial values for all the input parameters
        self.mass = mass
        self.h_cr = cruising_alt
        self.v_cr = cruise_speed
        self.S    = wing_surface
        self.CL_max = CL_max
        self.t_lt = t_loiter
        self.rot  = rotational_rate
        self.roc  = roc
        self.rod  = rod
        self.dist = mission_dist

        # Range over which the values are allowed to vary
        var     = 0.05    # [-] +- percentage variation
        N_pts   = 5       # [-] Number of different variations per parameter

    def monte_carlo_sim(self, var, N_sim):

        max_var = 1 + var
        min_var = 1 - var
        E = np.zeros(N_sim)
        t = np.zeros(N_sim)
        for i in range(N_sim):

            print('Progress:', np.round(100*i/N_sim), '%')

            m=mission(mass         = np.random.default_rng().uniform(low = self.mass*min_var, high = self.mass*max_var),
                      cruising_alt = np.random.default_rng().uniform(low = self.h_cr*min_var, high = self.h_cr*max_var),
                      cruise_speed = np.random.default_rng().uniform(low = self.v_cr*min_var, high = self.v_cr*max_var),
                      CL_max       = np.random.default_rng().uniform(low = self.CL_max*min_var, high = self.CL_max*max_var),
                      wing_surface = np.random.default_rng().uniform(low = self.S*min_var, high = self.S*max_var),
                      t_loiter     = 30*60,
                      rotational_rate= np.random.default_rng().uniform(low = self.rot*min_var, high = self.rot*max_var),
                      roc           = np.random.default_rng().uniform(low = self.roc*min_var, high = self.roc*max_var),
                      rod           = np.random.default_rng().uniform(low = self.rod*min_var, high = self.rod*max_var))

            E[i], t[i] = m.total_energy()

        plt.hist(E)
        plt.show()


validation = monte_carlo(2000, 300, 60, 1.5)
validation.monte_carlo_sim(0.10, 100)

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
