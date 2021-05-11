import numpy as np
import matplotlib.pyplot as plt
from Aero_tools import ISA
#from constants import*
import json
import scipy.optimize as optim

datafile = open("inputs_config_1.json", "r")

class initial_sizing:
    def __init__(self, h, datafile):

        # Read data from json file
        self.data = json.load(datafile)
        datafile.close()

        # Estimation for ratio between wing area and total area projected from above
        self.StotSw = 1.4

        # Extracting aerodynamic data
        aero        = self.data["Aerodynamics"]
        self.CLmax  = aero["CLmax_front"]
        self.A      = aero["AR"]
        self.e      = aero["e"]
        self.CD0    = aero["CD0"]

        # Atmospherics
        atm_flight  = ISA(h)    # atmospheric conditions during flight
        atm_LTO     = ISA(0)    # atmospheric conditions at landing and take-off (assumed sea-level)
        self.rho_flight = atm_flight.density()
        self.rho_LTO    = atm_LTO.density()

        # Requirements, and others
        reqs        = self.data["Requirements"]
        self.Vs     = reqs["V_stall"]
        self.Vmax   = reqs["V_max"]
        self.ROC    = reqs["ROC"]
        self.nmax   = reqs["n_turn"]
        self.Vcr    = 70

        self.ROC_ho = reqs["ROC_hover"]

        # Propulsion constants
        prop            = self.data["Propulsion"]
        self.eff_prop   = prop["eff_cruise"]    # [-] Propeller efficiency during normal flight
        self.eff_hover  = prop["eff_hover"]     # [-] Propeller efficiency during hover
        self.Ncr        = prop["N_cruise"]      # [-] Number of engines used in cruise
        self.Nho        = prop["N_hover"]       # [-] Number of dedicated hover engines
        self.TA         = prop["TA"]            # [kg/m^2]  Disk loading for ducted fans

        # Structures data
        struc           = self.data["Structures"]
        self.MTOW          = struc["MTOW"]  # [N] Maximum take-off weight in newtons


        # Preparing matplotlib
        fig = plt.figure()
        self.ax1 = fig.add_subplot(111)
        self.ax2 = self.ax1.twiny()

    def stall(self):
        # Stall speed (assuming low altitude)
        return 0.5*self.rho_LTO*(self.Vs**2)*self.CLmax

    def max_speed(self, WS):
        # Max speed (Reduction of power with altitude was neglected, as no combustion is involved (revise this for H2))
        return self.eff_prop*((self.CD0*0.5*self.rho_flight*(self.Vmax**3)/WS +
                                   WS/(np.pi*self.A*self.e*0.5*self.rho_flight*self.Vmax))**-1)

    def climb(self, WS):
        # Climb performance
        return ((self.ROC + np.sqrt(2*WS)*(self.CD0**0.25)/(1.345*((self.A*self.e)**0.75)))**-1)/self.eff_prop

    def turn(self, WS, V):
        # Turning performance (at high altitude and max speed)
        return self.eff_prop*((self.CD0*0.5*self.rho_flight*(V**3)/WS +
                                   WS*self.nmax*self.nmax/(np.pi*self.A*self.e*0.5*self.rho_flight*V))**-1)

    def vertical_flight(self, WS):
        # Most of the equations used here come from:
        # Comprehensive preliminary sizing/resizing method for a fixed wing – VTOL electric UAV

        # Thrust-to-weight required to allow for a sufficient rate of climb, plus a safety factor for acceleration
        TWR = 1.2*(1 + ((self.ROC_ho**2)*self.rho_LTO*self.StotSw/WS))

        # Obtaining Power to weight based on the TWR required
        return (TWR*np.sqrt(self.TA/(2*self.rho_LTO))/self.eff_hover)**-1

    def wing_loading(self):

        # Range of wing loadings to plot the power loadings
        self.WS = np.arange(100, 4000, 1)

        # Produce lines for the WS, WP diagram
        self.WS_stall           = self.stall()
        self.WP_speed           = self.max_speed(self.WS)
        self.WP_climb           = self.climb(self.WS)
        self.WP_turn_max_speed  = self.turn(self.WS, self.Vmax)
        self.WP_turn_cruise     = self.turn(self.WS, self.Vcr)
        self.WP_hov             = self.vertical_flight(self.WS)
        #print(self.WP_hov)

        # Plot wing and thrust loading diagrams
        self.ax1.plot(self.WS, self.WP_speed, label = 'Maximum speed')
        self.ax1.plot(self.WS, self.WP_climb, label = 'Rate of climb')
        self.ax1.plot(self.WS, self.WP_turn_max_speed,  label = 'Turn performance @ $V_{max}$')
        self.ax1.plot(self.WS, self.WP_turn_cruise,     label='Turn performance @ $V_{cr}$')
        self.ax1.plot(self.WS, self.WP_hov, label = 'Vertical flight requirements')
        self.ax1.plot(np.ones(np.size(self.WS))*self.WS_stall, np.linspace(0, 0.1, np.size(self.WS)), label = 'Stall speed')

    def design_point(self):
        """
        Identifies the design space, and finds the optimal design point. Since not all hover engines work during cruise,
        this is done twice, once including hover, and once without. It is assumed that the wing loading at stall will be
        limiting, the most critical power loading corresponding to this is then found. It should be checked in the plot
        whether this indeed corresponds to the most optimal design point.
        """

        # Border of the design space
        crit = np.minimum(np.minimum(np.minimum(np.minimum(self.WP_speed, self.WP_turn_cruise), self.WP_turn_max_speed),
                          self.WP_climb), self.WP_hov)[self.WS < self.WS_stall]

        crit_cruise = np.minimum(np.minimum(np.minimum(self.WP_speed, self.WP_turn_cruise), self.WP_turn_max_speed),
                          self.WP_climb)[self.WS < self.WS_stall]

        # Range of wing loadings in the design space
        ws_crit = self.WS[self.WS < self.WS_stall]

        # Select design point.
        # !!! Check manually in the plot !!!
        self.des_WS         = ws_crit[-1]
        self.des_WP         = crit[-1]          # Design power loading including hover
        self.des_WP_cruise  = crit_cruise[-1]   # Design power loading considering only cruise

        # Write the design point to the data file
        FP = self.data["Flight performance"]

        FP["W/S"]           = float(self.des_WS)
        FP["W/P hover"]     = float(self.des_WP)
        FP["W/P cruise"]    = float(self.des_WP_cruise)

        datfile = open("inputs_config_1.json", "w")
        json.dump(self.data, datfile)
        datfile.close()

        # Plot design space and point
        self.ax1.fill_between(ws_crit, np.zeros(np.size(crit)), crit, facecolor='green', alpha=0.2)
        self.ax1.fill_between(ws_crit, np.zeros(np.size(crit_cruise)), crit_cruise, facecolor='limegreen', alpha=0.2)
        self.ax1.plot(self.des_WS, self.des_WP, 'D', label='Design point')
        self.ax1.legend()
        plt.show()

        # Print results
        print()
        print('====== Design point ====== ')
        print('Wing loading:  ', np.round(self.des_WS, 4), '  N/m^2')
        print('Power loading: ', np.round(self.des_WP, 4), 'N/W')

    def sizing(self):

        # Sizing the wing
        S  = self.MTOW/self.des_WS

        # Total power needed
        P_tot       = self.MTOW/self.des_WP         # Including hover
        P_cruise    = self.MTOW/self.des_WP_cruise  # Cruise only

        # Store results to the data file
        FP = self.data["Flight performance"]
        FP["S"]         = S
        FP["P tot"]     = P_tot
        FP["P cruise"]  = P_cruise
        datfile = open("inputs_config_1.json", "w")
        json.dump(self.data, datfile)
        datfile.close()

        print()
        print('====== Initial sizing ======')
        print('Wing area:                      ', np.round(S, 2), 'm^2')
        print('Total shaft power (incl. hover):', np.round(P_tot, 0), 'W')
        print('Total shaft power (cruise only):', np.round(P_tot, 0), 'W')

        return self.des_WS, self.des_WP



class optimization:
    def __init__(self, WS, h_cruise, duct, datafile):

        atm     = ISA(h_cruise)
        atm_TO  = ISA(0)

        # Read data from json file
        data = json.load(datafile)
        datafile.close()

        # Extracting aerodynamic data
        aero        = data["Aerodynamics"]
        self.A      = aero["AR"]
        self.e      = aero["e"]
        self.CD0    = aero["CD0"]

        # Structures data
        struc       = data["Structures"]
        self.MTOW   = struc["MTOW"]  # [N] Maximum take-off weight in newtons



        self.rho_cruise = atm.density()
        self.rho_TO     = atm_TO.density()
        self.S          = self.MTOW/WS

        # Propulsion data
        prop            = data["Propulsion"]
        self.TA         = prop["TA"]
        self.n_cruise   = prop["N_cruise"]
        self.n_hover    = prop["N_hover"]
        self.duct       = duct
        self.hover_eff  = prop["eff_hover"]
        self.cruise_eff = prop["eff_cruise"]
        self.climb_eff  = prop["eff_cruise"]    # Just a simplification, change when more data is available
        self.desc_eff   = prop["eff_cruise"]    # Idem

        prelim      = data["Preliminary estimations"]
        self.t_TO   = prelim["t_TO"]
        self.t_land = prelim["t_land"]

        reqs        = data["Requirements"]
        self.ROC    = reqs["ROC"]

    def cruise_speed(self, W, h):

        rho_cruise = ISA(h).density()

        # Get the optimal lift coefficient for cruise
        CLopt       = np.sqrt(np.pi*self.A*self.e*self.CD0)

        # Drag-to-lift during cruise (optimal conditions)
        self.CDCL_cr    = self.CD0/CLopt + CLopt/(np.pi*self.A*self.e)

        # Get the optimal speed
        self.Vopt    = np.sqrt(2*W/(rho_cruise*self.S*CLopt))
    def hover_power(self):

        if self.duct:
            self.P_h  = 0.5*self.MTOW*np.sqrt(self.TA)/(np.sqrt(self.rho_TO*(self.n_cruise + self.n_hover))*self.hover_eff)

        else:
            self.P_h  = self.MTOW*np.sqrt(self.TA/(2*self.rho_TO*(self.n_cruise + self.n_hover)))

    def cruise_power(self):

        self.P_cr    = self.MTOW*self.Vopt*self.CDCL_cr/self.cruise_eff

    def climb_desc_power(self, h, gamma_descend, ROC_climb):

        rho_cl      = ISA(h).density()

        # Optimal climb velocity
        CL_cl       = np.sqrt(np.pi*self.A*self.e*self.CD0*3)
        self.V_cl   = np.sqrt(2*self.MTOW/(rho_cl*self.S*CL_cl))

        # Climb CLCD
        CD_cl       = self.CD0 + CL_cl*CL_cl/(np.pi*self.A*self.e)
        CLCD_cl     = CL_cl/CD_cl

        # Climb power
        self.P_cl   = (self.MTOW*self.V_cl*(CLCD_cl**-1) + self.MTOW*ROC_climb)/self.climb_eff

        # Optimal power during descent is the same as during climb
        self.P_des   = np.maximum(self.MTOW*self.V_cl*((CLCD_cl**-1) - np.sin(gamma_descend))/self.climb_eff, 0)
        #print(self.P_des)

    def analize_mission(self, h_cruise, gamma_descend, ROC_climb, mission_dist = 300000):

        rho_cl = ISA(h_cruise / 2).density()

        # Optimal climb velocity
        CL_cl = np.sqrt(np.pi * self.A * self.e * self.CD0 * 3)
        V_cl = np.sqrt(2 * self.MTOW / (rho_cl * self.S * CL_cl))

        # Climb angle and distance covered
        gamma_climb = np.arcsin(ROC_climb / V_cl)
        d_climb = h_cruise / np.tan(gamma_climb)

        # Minimum descent angle needed to at least reach the cruising altitude
        d_desc_min = mission_dist - d_climb
        gamma_des_min = np.arctan(h_cruise / d_desc_min)

        # Energy used during climb
        self.climb_desc_power(h_cruise / 2, gamma_descend, ROC_climb)
        t_cl = h_cruise / ROC_climb
        E_climb = self.P_cl * t_cl

        # Energy during descent
        ROD = V_cl * np.sin(gamma_descend)
        t_desc = h_cruise / ROD
        E_desc = self.P_des * t_desc

        # Energy during cruise
        self.cruise_speed(self.MTOW, h_cruise)
        self.cruise_power()
        d_desc = h_cruise / np.tan(gamma_descend)
        d_cruise = mission_dist - d_climb - d_desc
        t_cruise = d_cruise / self.Vopt
        E_cruise = self.P_cr * t_cruise

        E_mission = np.where(d_cruise < 0, np.nan, E_climb + E_desc + E_cruise)
        t_mission = np.where(d_cruise < 0, np.nan, t_cruise + t_cl + t_desc)

        return E_mission, t_mission


    def simulate_missions(self):

        # Range of cruising altitudes and mission ranges
        cruise_alts = np.arange(300, 3000, 1)
        distances   = [50, 100, 200, 300, 400]

        # Go through all mission ranges, and plot the energy consumption vs the flying altitude
        for d in distances:

            E, t_miss = self.analize_mission(cruise_alts, np.radians(5), self.ROC, mission_dist = d*1000)
            label = 'Dist = ' + str(d) + 'km'

            plt.subplot(211)
            plt.plot(cruise_alts, E * 2.77778e-7, label=label)
            plt.xlabel('Cruising altitude [m]')
            plt.ylabel('Energy consumption [kWh]')
            plt.grid()

            plt.subplot(212)
            plt.plot(cruise_alts, t_miss / 3600, label=label)
            plt.xlabel("Cruising altitude [m]")
            plt.ylabel("Mission time [h]")
            plt.grid()


        plt.legend()
        plt.tight_layout()
        plt.show()

        # Optimization of the descent angle (assuming maximum range)
        gamma_descend   = np.array([7, 5, 3, 2, 1])

        for gam in gamma_descend:

            label = 'gamma = ' + str(gam)
            E, t_miss = self.analize_mission(cruise_alts, np.radians(gam), self.ROC,  mission_dist = 300000)
            plt.subplot(211)
            plt.plot(cruise_alts, E * 2.77778e-7, label=label)
            plt.xlabel('Cruising altitude [m]')
            plt.ylabel('Energy consumption [kWh]')
            plt.grid()

            plt.subplot(212)
            plt.plot(cruise_alts, t_miss / 3600, label=label)
            plt.xlabel("Cruising altitude [m]")
            plt.ylabel("Mission time [h]")
            plt.grid()



        plt.legend()
        plt.tight_layout()

        plt.show()




# Run the initial sizing
h_cruise = 500
perf = initial_sizing(h_cruise, datafile)
perf.wing_loading()
perf.design_point()
WS, WP = perf.sizing()

# Estimate the power
datafile = open("inputs_config_1.json", "r")
opt = optimization(WS, 1000, True, datafile)
opt.simulate_missions()
