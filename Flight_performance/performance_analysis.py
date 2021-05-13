import numpy as np
import matplotlib.pyplot as plt
from Aero_tools import ISA
import json


class initial_sizing:
    def __init__(self, h, path):

        self.path = path
        datafile = open(self.path, "r")

        # Read data from json file
        self.data = json.load(datafile)
        datafile.close()

        # Extracting aerodynamic data
        aero        = self.data["Aerodynamics"]
        self.CLmax  = aero["CLmax_front"]
        self.A      = aero["AR"]
        self.e      = aero["e"]
        self.CD0    = aero["CD0"]
        self.StotSw = aero["Stot/Sw"]

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
        self.MTOW       = struc["MTOW"]  # [N] Maximum take-off weight in newtons

        # Preparing matplotlib
        fig = plt.figure()
        self.ax1 = fig.add_subplot(111)
        self.ax2 = self.ax1.twiny()

    def stall(self, V_stall):
        # Stall speed (assuming low altitude)
        return 0.5*self.rho_LTO*(V_stall**2)*self.CLmax

    def max_speed(self, WS):
        # Max speed (Reduction of power with altitude was neglected, as no combustion is involved (revise this for H2))
        return self.eff_prop*((self.CD0*0.5*self.rho_flight*(self.Vmax**3)/WS +
                               WS/(np.pi*self.A*self.e*0.5*self.rho_flight*self.Vmax))**-1)

    def climb(self, WS, climb_rate):
        # Climb performance
        return ((climb_rate + np.sqrt(2*WS)*(self.CD0**0.25)/(1.345*((self.A*self.e)**0.75)))**-1)/self.eff_prop

    def turn(self, WS, V, n_turn):
        # Turning performance (at high altitude and max speed)
        return self.eff_prop*((self.CD0*0.5*self.rho_flight*(V**3)/WS +
                               WS*n_turn*n_turn/(np.pi*self.A*self.e*0.5*self.rho_flight*V))**-1)

    def vertical_flight(self, WS, ROC_hover):
        # Most of the equations used here come from:
        # Comprehensive preliminary sizing/resizing method for a fixed wing – VTOL electric UAV

        # Thrust-to-weight required to allow for a sufficient rate of climb, plus a safety factor for acceleration
        TWR = 1.2*(1 + ((ROC_hover**2)*self.rho_LTO*self.StotSw/WS))

        # Obtaining Power to weight based on the TWR required
        return (TWR*np.sqrt(self.TA/(2*self.rho_LTO))/self.eff_hover)**-1

    def wing_loading(self):

        # Range of wing loadings to plot the power loadings
        self.WS = np.arange(100, 4000, 1)

        # Produce lines for the WS, WP diagram
        self.WS_stall           = self.stall(self.Vs)
        self.WP_speed           = self.max_speed(self.WS)
        self.WP_climb           = self.climb(self.WS, self.ROC)
        self.WP_turn_max_speed  = self.turn(self.WS, self.Vmax, self.nmax)
        self.WP_turn_cruise     = self.turn(self.WS, self.Vcr, self.nmax)
        self.WP_hov             = self.vertical_flight(self.WS, self.ROC_ho)

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

        datfile = open(self.path, "w")
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

        # Run wing and power loading
        self.wing_loading()
        self.design_point()

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
        datfile = open(self.path, "w")
        json.dump(self.data, datfile)
        datfile.close()

        print()
        print('====== Initial sizing ======')
        print('Wing area:                      ', np.round(S, 2), 'm^2')
        print('Total shaft power (incl. hover):', np.round(P_tot, 0), 'W')
        print('Total shaft power (cruise only):', np.round(P_cruise, 0), 'W')

        return self.des_WS, self.des_WP

    def testing(self):

        # Just some random inputs for testing
        WS_test     = 500
        V_test      = 100

        # If n = 1, the max speed line should equal that of the turning requirement
        WP_turn  = self.turn(WS_test, V_test, 1)
        WP_speed = self.max_speed(WS_test)

        if abs(WP_turn - WP_speed) > 1e-3:
            print("Turning or speed equations implemented incorrectly")

        # Testing the climb requirement
        descent = self.climb(WS_test, -10)
        climb   = self.climb(WS_test, 10)

        if descent > climb:
            print("Climb equation implemented incorrectly")

        # Hover test
        descent_ho  = self.vertical_flight(WS_test, -10)
        ascent_ho   = self.vertical_flight(WS_test, 10)

        if descent_ho > ascent_ho:
            print("Hover implemented incorrectly")


class mission_analysis:
    def __init__(self, path, h_cruise, m_pl, ac_energy, save_data = False):

        # Import aircraft data
        self.path       = path
        datafile        = open(self.path, "r")
        self.data       = json.load(datafile)
        datafile.close()

        # Structural data
        self.struc  = self.data["Structures"]
        self.EOW    = self.struc["EOW"]
        self.MTOW   = self.struc["MTOW"]

        # Flight performance data
        self.FP             = self.data["Flight performance"]
        self.S              = self.FP["S"]
        self.WS             = self.FP["W/S"]
        self.gamma_descent  = np.radians(self.FP["Gamma descent"])
        self.WP_ho          = self.FP["W/P hover"]
        self.WP_cr          = self.FP["W/P cruise"]
        self.t_to           = self.FP["t_TO"]
        self.t_la           = self.FP["t_land"]

        # Requirements
        self.req    = self.data["Requirements"]
        self.ROC    = self.req["ROC"]
        self.ROC_ho = self.req["ROC_hover"]
        self.ROD_ho = self.req["ROD_hover"]
        self.t_loit = self.req["Loiter time"]
        self.V_st   = self.req["V_stall"]

        # Aerodynamic data
        self.aero   = self.data["Aerodynamics"]
        self.A      = self.aero["AR"]
        self.e      = self.aero["e"]
        self.CD0    = self.aero["CD0"]
        self.StotSw = self.aero["Stot/Sw"]

        # Propulsion data
        self.prop       = self.data["Propulsion"]
        self.TA         = self.prop["TA"]
        self.hover_eff  = self.prop["eff_hover"]
        self.cruise_eff = self.prop["eff_cruise"]

        # Atmospheric properties
        ISA_cr  = ISA(h_cruise)

        # Atmospheric properties at climb, assuming the average height is half the cruise altitude
        h_climb = h_cruise/2
        ISA_cl  = ISA(h_climb)

        # Sea level atmosphere
        ISA_sl  = ISA(0)

        # Densities
        self.rho_cr  = ISA_cr.density()
        self.rho_cl  = ISA_cl.density()
        self.rho_sl  = ISA_sl.density()

        # Other parameters
        self.W              = self.EOW + (m_pl*9.81)    # [N] Aircraft weight
        self.h_cruise       = h_cruise      # [m] Cruising altitude
        self.h_climb        = h_climb       # [m] Average climbing altitude
        self.capacity       = ac_energy     # [J] Aircraft energy
        self.h_tr           = 100           # [m] Transition altitude
        self.save           = save_data     # Boolean to see if data has to be saved or not

        # Warn if the aircraft is overweight
        if np.any(self.W > self.MTOW):
            print()
            print("Aircraft is too heavy, reduce payload weight")
            print()

    def optimal_speeds(self, save = False):

        # Optimal climb speed
        V_climb     = np.sqrt(2*self.W/(self.rho_cl*self.S*np.sqrt(self.A*self.e*np.pi*3*self.CD0)))

        # Optimal cruise speed
        V_cruise    = np.sqrt(2*self.W/(self.rho_cr*self.S*np.sqrt(np.pi * self.A * self.e * self.CD0)))

        # If the input is not an array, store the optimal speed
        if save:

            # Store cruise speed
            FP = self.data["Flight performance"]
            FP["V_cruise"] = V_cruise
            datfile = open(self.path, "w")
            json.dump(self.data, datfile)
            datfile.close()
            print()
            print("Optimal cruise speed (", np.round(V_cruise), "m/s) stored")

        return V_climb, V_cruise

    def hover_power(self, ROC, W):

        TWR = 1.2 * (1 + ((ROC ** 2) * self.rho_sl * self.StotSw / self.WS))

        P_hov = TWR * W * np.sqrt(self.TA / (self.rho_sl * 2)) / self.hover_eff

        if np.any(P_hov < 0):
            print("hover power implemented incorrectly")

        if np.any(P_hov > self.MTOW/self.WP_ho):
            print("More power is needed than is available")

        return P_hov

    def cruise_power(self, W):

        # Get the optimal lift coefficient for cruise
        CLopt = np.sqrt(np.pi * self.A * self.e * self.CD0)

        # Drag-to-lift during cruise (optimal conditions)
        CDCL_cr = self.CD0 / CLopt + CLopt / (np.pi * self.A * self.e)

        _, V_cruise = self.optimal_speeds()

        P_cr    = W*V_cruise*CDCL_cr/self.cruise_eff

        if np.any(P_cr < 0):
            print("Cruise power implemented incorrectly")

        return P_cr

    def climb_power(self, ROC_climb, V_climb, W):

        # Climb CLCD
        CL_cl = np.sqrt(np.pi * self.A * self.e * self.CD0 * 3)
        CD_cl = self.CD0 + CL_cl * CL_cl / (np.pi * self.A * self.e)
        CLCD_cl = CL_cl / CD_cl

        # Climb power, assuming climb efficiency is the same as cruise efficiency
        P_cl   = (W*V_climb*(CLCD_cl**-1) + W*ROC_climb)/self.cruise_eff

        if np.any(P_cl < 0):
            print("Climb power implemented incorrectly")

        if np.any(P_cl > self.MTOW/self.WP_cr):
            print("More power is used than is available")
            print(P_cl, self.MTOW/self.WP_cr)

        return P_cl

    def descent_power(self, gamma_descend, V_desc, W):

        # Climb CLCD
        CL_cl = np.sqrt(np.pi * self.A * self.e * self.CD0 * 3)
        CD_cl = self.CD0 + CL_cl * CL_cl / (np.pi * self.A * self.e)
        CLCD_cl = CL_cl / CD_cl

        P_des   = np.maximum(W*V_desc*((CLCD_cl**-1) - np.sin(gamma_descend))/self.cruise_eff, 0)

        if np.any(P_des < 0):
            print("Descent power implemented incorrectly or descent angle too steep to maintain speed (use brakes/HLD)")

        return P_des

    def climb_energy(self, ROC):

        # Optimal speed
        V_climb, _ = self.optimal_speeds()

        # Climb power
        P_climb    = self.climb_power(self.ROC, V_climb, self.W)

        # Time needed to climb
        t_climb   = (self.h_cruise - self.h_tr)/ROC

        # Energy spent
        E_climb   = P_climb*t_climb

        return E_climb

    def descent_energy(self):

        V_desc, _   = self.optimal_speeds()

        # Power needed
        P_desc      = self.descent_power(self.gamma_descent, V_desc, self.W)

        # Time needed to descent
        t_desc = (self.h_cruise - self.h_tr) / (V_desc*np.sin(self.gamma_descent))

        # Energy spent
        E_desc = P_desc * t_desc

        return E_desc

    def to_hover_energy(self):

        # Get hover power
        P_hover_to  = self.hover_power(self.ROC_ho, self.W)

        E_hover_to  = P_hover_to*self.t_to

        return E_hover_to

    def la_hover_energy(self):

        # Get hover power
        P_hover_la  = self.hover_power(self.ROD_ho, self.W)

        E_hover_la  = P_hover_la*self.t_la

        return E_hover_la

    def loiter_energy(self):

        # Speed for minimum power is the same as maximum climb rate
        V_loit, _ = self.optimal_speeds()

        # Power needed
        P_loit = self.climb_power(0, V_loit, self.W)

        # Energy spent
        E_desc = P_loit * self.t_loit

        return E_desc

    def cruise_energy(self, mission_range):

        # Cruise power
        P_cr    = self.cruise_power(self.W)

        V_cl, V_cr = self.optimal_speeds(save = self.save)

        # Calculate the total distance spent in cruise (Assuming the transition distance is negligible)
        t_climb = (self.h_cruise - self.h_tr)/self.ROC
        d_climb = np.sqrt((V_cl**2) - (self.ROC**2))*t_climb
        d_desc  = (self.h_cruise - self.h_tr)/np.tan(self.gamma_descent)

        d_cruise = mission_range - d_desc - d_climb

        # Check if climb and descent don't take more space than the mission
        if np.any(d_cruise < 0):
            print("Cruise distance needed for climb and descent longer than mission time, reduce cruise altitude")

        # Time spent in cruise (Assuming the aircraft flies at optimal speed)
        t_cruise = d_cruise/V_cr

        E_cruise = P_cr*t_cruise

        return E_cruise

    def range(self):

        E_hover_to  = self.to_hover_energy()
        E_hover_la  = self.la_hover_energy()
        E_climb     = self.climb_energy(self.ROC)
        E_descent   = self.descent_energy()
        E_loiter    = self.loiter_energy()

        # Based on the energy available to the aircraft, estimate the amount left for cruise
        E_cruise    = self.capacity - E_hover_to - E_hover_la - E_climb - E_descent - E_loiter

        # Cruise power
        P_cruise    = self.cruise_power(self.W)

        # Cruising time
        t_cruise    = E_cruise/P_cruise

        # Cruise distance
        _, V_cruise = self.optimal_speeds()
        d_cruise    = V_cruise*t_cruise

        return d_cruise

    def climb_performance(self, h, V, dedicated_hover = False):

        isa = ISA(h)
        rho = isa.density()

        # Required power
        P_r = 0.5 * rho * (V**3) * self.S * (self.CD0 + (2 * self.W / (rho * V * V * self.S)) ** 2) / \
            (np.pi * self.A * self.e)

        # Rate of climb (depending on whether there are dedicated hover engines, power loading is chosen)
        RC  = ((self.WP_cr*dedicated_hover + self.WP_ho * (not dedicated_hover)) ** -1) * self.cruise_eff - P_r / self.W

        return RC

    def climb_perf_chart(self):

        # Range of altitudes
        h = np.arange(300, 3000, 800)

        for alt in h:
            # Calculate the density to reduce the stall speed with altitude
            rho = ISA(alt).density()
            V = np.arange(self.V_st*np.sqrt(self.rho_sl/rho), 400, 0.1)

            RC = self.climb_performance(alt, V)
            label = 'height: ' + str(alt) + ' [m]'
            plt.plot(V, RC, label = label)

        plt.xlabel("Speed [m/s]")
        plt.ylabel("Rate of climb [m/s]")
        plt.grid()
        plt.legend()
        plt.show()

    def total_energy(self, mission_range, pie = False):

        # Energy needed in each flight phase (Ignoring transition for now, as this is juts used for comparison)
        E_hover_to  = self.to_hover_energy()
        E_hover_la  = self.la_hover_energy()
        E_climb     = self.climb_energy(self.ROC)
        E_descent   = self.descent_energy()
        E_loiter    = self.loiter_energy()
        E_cruise    = self.cruise_energy(mission_range)

        # Pie chart with all the energies
        if pie:
            labels    = ['Take-off', 'Climb', 'Cruise', 'Descent', 'Land', 'Loiter']
            fractions = [E_hover_to, E_climb, E_cruise, E_descent, E_hover_la, E_loiter]

            plt.pie(fractions, labels = labels, autopct='%1.1f%%')
            plt.legend(loc = 'lower left')
            plt.show()

        # Total energy needed for the mission
        E_tot   = E_hover_to + E_hover_la + E_climb + E_descent + E_loiter + E_cruise

        return E_tot
