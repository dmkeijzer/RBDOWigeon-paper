import numpy as np
import matplotlib.pyplot as plt
from Aero_tools import ISA



class initial_sizing:
    def __init__(self, h, MTOW):

        # Atmospherics
        atm_flight  = ISA(h)    # atmospheric conditions during flight
        atm_LTO     = ISA(0)    # atmospheric conditions at landing and take-off (assumed sea-level)
        self.rho_flight = atm_flight.density()
        self.rho_LTO    = atm_LTO.density()

        # Requirements, and others
        self.Vs     = 50
        self.Vmax   = 100
        self.ROC    = 10
        self.nmax   = 2
        self.Vcr    = 70
        self.MTOW   = MTOW  # [N] Maximum take-off weight in newtons

        # Aerodynamic constants
        self.CLmax  = 1.5
        self.A      = 10
        self.e      = 0.75
        self.CD0    = 0.05

        # Propulsion constants
        self.eff_prop   = 0.8   # [-] Propeller efficiency during normal flight
        self.eff_hover  = 0.6   # [-] Propeller efficiency during hover
        self.Ncr        = 4     # [-] Number of engines used in cruise
        self.Nho        = 2     # [-] Number of dedicated hover engines
        self.TA_duct    = 1000  # [kg/m^2]  Disk loading for ducted fans
        self.TA_open    = 200   # [kg/m^2]  Disk loading for open props
        self.TA_hybrid  = 80    # [kg/m^2]  Disk loading for hybrid rotating-fixed propellers

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

    def wing_loading(self):

        # Range of wing loadings to plot the power loadings
        self.WS = np.arange(100, 4000, 1)

        # Produce lines for the WS, WP diagram
        self.WS_stall = self.stall()
        self.WP_speed = self.max_speed(self.WS)
        self.WP_climb = self.climb(self.WS)
        self.WP_turn_max_speed  = self.turn(self.WS, self.Vmax)
        self.WP_turn_cruise     = self.turn(self.WS, self.Vcr)


        # Plot wing and thrust loading diagrams
        self.ax1.plot(self.WS, self.WP_speed, label = 'Maximum speed')
        self.ax1.plot(self.WS, self.WP_climb, label = 'Rate of climb')
        self.ax1.plot(self.WS, self.WP_turn_max_speed,  label = 'Turn performance @ $V_{max}$')
        self.ax1.plot(self.WS, self.WP_turn_cruise,     label='Turn performance @ $V_{cr}$')
        self.ax1.plot(np.ones(np.size(self.WS))*self.WS_stall, np.linspace(0, 0.1, np.size(self.WS)), label = 'Stall speed')


    def disk_loading(self):

        # Range of disk loadings
        TA  = np.arange(1, 1000, 1)

        # Disk loading obtained from statistics, converted to N/m^2
        TA_hover    = self.TA_duct*9.81

        # Range of power loadings used for disk loading plot
        self.WP_hover        = (np.sqrt(TA/2*self.rho_LTO)**-1)*self.eff_hover

        # Power loading requirement obtained from assumed disk loading
        WP_hover_duct       = (np.sqrt(self.TA_duct*9.81/(2*self.rho_LTO))**-1)*self.eff_hover
        WP_hover_open       = (np.sqrt(self.TA_open*9.81/(2*self.rho_LTO))**-1)*self.eff_hover
        WP_hover_hybrid     = (np.sqrt(self.TA_hybrid*9.81 / (2*self.rho_LTO)) ** -1) * self.eff_hover

        self.ax1.plot(self.WS, np.ones(np.size(self.WS)) * WP_hover_duct, label = 'hover ducted')
        self.ax1.plot(self.WS, np.ones(np.size(self.WS)) * WP_hover_open, label='hover open')
        self.ax1.plot(self.WS, np.ones(np.size(self.WS)) * WP_hover_hybrid, label='hover hybrid')
        self.ax1.set_xlabel('Wing loading [N/m^2]')
        self.ax1.set_ylabel('Power loading [N/W]')
        self.ax1.set_ylim(0, 0.15)
        self.ax1.grid()
        self.ax1.legend()

        self.WP_hover_crit = np.minimum(np.minimum(WP_hover_duct, WP_hover_open), WP_hover_hybrid)

        """
        # Find the required disk loading based on the design point found in wing_loading
        self.des_TA  = ((self.des_WP/self.eff_hover)**-2)*2*self.rho_LTO
        print('Disk loading:  ', np.round(self.des_TA, 1), ' N/m^2')
        """

        # Plot disk loading curve
        self.ax2.plot(TA, self.WP_hover, '--', label = 'Hover')
        self.ax2.set_xlabel('Disk loading ')
        self.ax2.set_ylim(self.ax1.get_ylim())
        self.ax2.legend(loc = 'lower right')


    def design_point(self):

        # Border of the design space
        crit = np.minimum(np.minimum(np.minimum(np.minimum(self.WP_speed, self.WP_turn_cruise), self.WP_turn_max_speed),
                          self.WP_climb), self.WP_hover_crit)[self.WS < self.WS_stall]

        # Range of wing loadings in the design space
        ws_crit = self.WS[self.WS < self.WS_stall]

        # Select design point, this is assuming a smaller wing is always favored,
        # !!! Check manually in the plot !!!
        self.des_WS = ws_crit[-1]
        self.des_WP = crit[-1]

        # Plot design space and point
        self.ax1.fill_between(ws_crit, np.zeros(np.size(crit)), crit, facecolor='green', alpha=0.2)
        self.ax1.plot(self.des_WS, self.des_WP, 'D', label='Design point')
        plt.show()

        # Print results
        print()
        print('====== Design point ====== ')
        print('Wing loading:  ', np.round(self.des_WS, 4), '  N/m^2')
        print('Power loading: ', np.round(self.des_WP, 4), 'N/W')

    def sizing(self):

        # Sizing the wing
        S  = self.MTOW/self.des_WS

        # Power needed in horizontal flight, per engine
        Pcr = self.MTOW/(self.des_WP*self.Ncr)

        print()
        print('====== Initial sizing ======')
        print('Wing area:                      ', np.round(S, 2))
        print('Shaft power per cruise engine:  ', np.round(Pcr))

        return self.des_WS, self.des_WP

h = 1000
MTOW = 20000

# Test run
perf = initial_sizing(h, MTOW)
perf.wing_loading()
perf.disk_loading()
perf.design_point()
WS, WP = perf.sizing()

class optimization:
    def __init__(self, WS, MTOW, h_cruise, n_cruise, n_hover, duct):

        atm     = ISA(h_cruise)
        atm_TO  = ISA(0)
        self.rho_cruise = atm.density()
        self.rho_TO     = atm_TO.density()
        self.S      = MTOW/WS
        self.A      = 10
        self.e      = 0.75
        self.CD0    = 0.05
        self.TA     = 100
        self.n_cruise = n_cruise
        self.n_hover  = n_hover
        self.duct = duct
        self.ROC  = 10
        self.ROD  = 10

        self.t_TO   = 20
        self.t_land = 30

        self.hover_eff  = 0.6
        self.cruise_eff = 0.95
        self.climb_eff  = 0.8
        self.desc_eff   = 0.8




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
            self.P_h  = 0.5*MTOW*np.sqrt(self.TA)/(np.sqrt(self.rho_TO*(self.n_cruise + self.n_hover))*self.hover_eff)

        else:
            self.P_h  = MTOW*np.sqrt(self.TA/(2*self.rho_TO*(self.n_cruise + self.n_hover)))

    def cruise_power(self):

        self.P_cr    = MTOW*self.Vopt*self.CDCL_cr/self.cruise_eff

    def climb_desc_power(self, h):

        rho_cl      = ISA(h).density()

        # Optimal climb velocity
        CL_cl       = np.sqrt(np.pi*self.A*self.e*self.CD0*3)
        self.V_cl   = np.sqrt(2*MTOW/(rho_cl*self.S*CL_cl))

        # Climb CLCD
        CD_cl       = self.CD0 + CL_cl*CL_cl/(np.pi*self.A*self.e)
        CLCD_cl     = CL_cl/CD_cl

        # Climb power
        self.P_cl    = (MTOW*self.V_cl*(CLCD_cl**-1) + MTOW*self.ROC)/self.climb_eff
        self.P_des   = np.maximum((MTOW*self.V_cl*(CLCD_cl**-1) - MTOW*self.ROD)/self.climb_eff, 0) # has to be changed to more accurate descend model

    def mission_energy(self, h_cruise, mission_dist):

        # Time needed to climb to and descend from cruise altitude
        self.climb_desc_power(h_cruise / 2)
        t_climb = h_cruise/self.ROC
        t_desc  = h_cruise/self.ROD

        # Distance covered during climb and descend (assuming small angles)
        d_climb = self.V_cl*t_climb
        d_desc  = self.V_cl*t_desc

        # Time spent cruising
        self.cruise_speed(MTOW, h_cruise)
        V_cruise = self.Vopt
        t_cruise = (mission_dist - d_climb - d_desc)/V_cruise

        # Total mission energy
        self.hover_power()
        self.cruise_power()
        E_mission = (self.t_TO + self.t_land)*self.P_h + t_cruise*self.P_cr + t_climb*self.P_cl + t_desc*self.P_des
        t_mission = t_cruise + t_climb + t_desc + self.t_TO + self.t_land

        E_ratio   = t_cruise*self.P_cr/(t_climb*self.P_cl + t_desc*self.P_des)
        return E_mission, t_cruise, t_mission, E_ratio

    def simulate_missions(self):

        # Range of cruising altitudes and mission ranges
        cruise_alts = np.arange(300, 3000, 1)
        distances   = [50, 100, 200, 300, 400]

        # Go through all mission ranges, and plot the energy consumption vs the flying altitude
        for d in distances:
            E, t_cruise, t_miss, E_ratio = self.mission_energy(cruise_alts, d*1000)
            label = 'Dist = ' + str(d) + 'km'

            plt.subplot(221)
            plt.plot(cruise_alts, E*2.77778e-7, label = label)
            plt.xlabel('Cruising altitude [m]')
            plt.ylabel('Energy consumption [kWh]')

            plt.subplot(222)
            plt.plot(cruise_alts, t_cruise/3600, label = label)
            plt.xlabel("Cruising altitude [m]")
            plt.ylabel("Time in Cruise [h]")

            plt.subplot(223)
            plt.plot(cruise_alts, t_miss/3600, label = label)
            plt.xlabel("Cruising altitude [m]")
            plt.ylabel("Mission time [h]")


            plt.subplot(224)
            plt.plot(cruise_alts, E_ratio)
            plt.xlabel("Cruising altitude [m]")
            plt.ylabel("$E_{cruise}$/$E_{climb}$")

        #plt.legend()
        plt.tight_layout()
        plt.grid()
        plt.show()



opt = optimization(WS, MTOW, 1000, 4, 2, True)

opt.simulate_missions()
#opt.cruise_speed(MTOW)