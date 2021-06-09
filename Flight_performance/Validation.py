import numpy as np
import matplotlib.pyplot as plt
from Aero_tools import speeds, ISA
from Flight_performance_final import evtol_performance, mission
from constants import g
import scipy.optimize as optimize
from Preliminary_Lift.main_aero import Cl_alpha_curve, CD_a_w, CD_a_f, alpha_lst, Drag

class validation:
    def __init__(self, mass, cruising_alt, cruise_speed, CL_max, wing_surface = 10, A_disk = 3, t_loiter = 30*60,
                 rotational_rate = 5, roc = 5, rod = 5, mission_dist = 300e3):

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
        self.A_disk = A_disk

        # Range over which the values are allowed to vary
        var     = 0.05    # [-] +- percentage variation
        N_pts   = 5       # [-] Number of different variations per parameter

    def monte_carlo_sim(self, var, N_sim, mission_object):

        max_var = 1 + var
        min_var = 1 - var
        E = np.zeros(N_sim)
        t = np.zeros(N_sim)
        mo = mission_object
        for i in range(N_sim):

            print('Progress:', np.round(100*i/N_sim), '%')

            m = mission(mass         = np.random.default_rng().uniform(low = mo.m*min_var, high = mo.m*max_var),
                        cruising_alt = np.random.default_rng().uniform(low = mo.h_cruise*min_var, high = mo.h_cruise*max_var),
                        cruise_speed = np.random.default_rng().uniform(low = mo.v_cruise*min_var, high = mo.v_cruise*max_var),
                        CL_max       = np.random.default_rng().uniform(low = mo.CL_max*min_var, high = mo.CL_max*max_var),
                        wing_surface = np.random.default_rng().uniform(low = mo.S*min_var, high = mo.S*max_var),
                        A_disk       = np.random.default_rng().uniform(low = mo.A_disk*min_var, high = mo.A_disk*max_var),
                        t_loiter     = 30*60,
                        rotational_rate= np.random.default_rng().uniform(low = np.degrees(mo.max_rot)*min_var, high = np.degrees(mo.max_rot)*max_var),
                        roc           = np.random.default_rng().uniform(low = mo.roc*min_var, high = mo.roc*max_var),
                        rod           = np.random.default_rng().uniform(low = mo.rod*min_var, high = mo.rod*max_var),
                        Cl_alpha_curve=Cl_alpha_curve, CD_a_w=CD_a_w, CD_a_f=CD_a_f, alpha_lst=alpha_lst, Drag=Drag)

            _, E[i], t[i] = m.numerical_simulation(0.01, 0, np.pi/2, 305, 67)

        plt.hist(E)
        plt.show()

    def energy_bounds_takeoff(self):

        # Lower bound, based on the optimal take-off trajectory found by Chauhan
        lb = mission(mass = 725, cruising_alt = 305, cruise_speed = 67, CL_max = 1.2, wing_surface = 9, A_disk = 14.14,
                     t_loiter = 30*60, rotational_rate = 1, Cl_alpha_curve=Cl_alpha_curve, CD_a_w=CD_a_w, CD_a_f=CD_a_f,
                     alpha_lst=alpha_lst, Drag=Drag, plotting= True, roc = 15)

        # Get the lower bound of the energy required to climb
        d_lb, E_lb, t_lb = lb.numerical_simulation(0.01, 0, np.pi/2, 305, 67)

        # Energy calculated by Chauhan in Joules
        E_ch = 1871*3600

        print('Comparing the lower bound: ', 100*(E_ch - E_lb)/E_lb, '%', E_ch, E_lb)

        self.monte_carlo_sim(0.15, 50, lb)

        # Upper bound
        ub = mission(mass=3175, cruising_alt=3000, cruise_speed=83, CL_max=1.2, wing_surface=8.464, A_disk=2.052,
                     t_loiter=30 * 60, rotational_rate=1, Cl_alpha_curve=Cl_alpha_curve, CD_a_w=CD_a_w, CD_a_f=CD_a_f,
                     alpha_lst=alpha_lst, Drag=Drag, plotting=True, roc = 7.2)

        d_ub, E_ub, t_ub = ub.numerical_simulation(0.01, 0, np.pi / 2, 3000, 83)

        # Energy from Nathen
        E_nt = 511000*451 + 12*1421000 + 15*224000

        print('Comparing the upper bound: ', 100*(E_nt - E_ub)/E_ub, E_nt, E_ub)


validate = validation(2000, 300, 60, 1.5)
validate.energy_bounds_takeoff()
#validate.monte_carlo_sim(0.10, 100)

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
