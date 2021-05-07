import numpy as np
import matplotlib.pyplot as plt
from Aero_tools import ISA



class performance:
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
        WS = np.arange(100, 4000, 1)

        # Produce lines for the WS, WP diagram
        WS_stall = self.stall()
        WP_speed = self.max_speed(WS)
        WP_climb = self.climb(WS)
        WP_turn_max_speed  = self.turn(WS, self.Vmax)
        WP_turn_cruise     = self.turn(WS, self.Vcr)

        # Border of the design space
        crit    = np.minimum(np.minimum(np.minimum(WP_speed, WP_turn_cruise), WP_turn_max_speed), WP_climb)[WS < WS_stall]

        # Range of wing loadings in the design space
        ws_crit = WS[WS < WS_stall]

        # Select design point, this is assuming a smaller wing is always favored,
        # !!! Check manually in the plot !!!
        self.des_WS     = ws_crit[-1]
        self.des_WP     = crit[-1]

        # Plot design space and point
        self.ax1.fill_between(ws_crit, np.zeros(np.size(crit)), crit, facecolor = 'green', alpha = 0.2)
        self.ax1.plot(self.des_WS, self.des_WP, 'D', label = 'Design point')

        # Plot wing and thrust loading diagrams
        self.ax1.plot(WS, WP_speed, label = 'Maximum speed')
        self.ax1.plot(WS, WP_climb, label = 'Rate of climb')
        self.ax1.plot(WS, WP_turn_max_speed,  label = 'Turn performance @ $V_{max}$')
        self.ax1.plot(WS, WP_turn_cruise,     label='Turn performance @ $V_{cr}$')
        self.ax1.plot(np.ones(np.size(WS))*WS_stall, np.linspace(0, 0.1, np.size(WS)), label = 'Stall speed')
        self.ax1.set_xlabel('Wing loading [N/m^2]')
        self.ax1.set_ylabel('Power loading [N/W]')
        self.ax1.set_ylim(0, 0.15)
        self.ax1.grid()
        self.ax1.legend()

        # Print results
        print()
        print('====== Design point ====== ')
        print('Wing loading:  ', np.round(self.des_WS, 4), '  N/m^2')
        print('Power loading: ', np.round(self.des_WP, 4), 'N/W')

    def disk_loading(self):

        # Range of disk loadings
        TA  = np.arange(1, 1000, 1)

        # Disk loading during hover (T=W)
        WP_hover    = (np.sqrt(TA/2*self.rho_LTO)**-1)*self.eff_hover

        # Find the required disk loading based on the design point found in wing_loading
        self.des_TA  = ((self.des_WP/self.eff_hover)**-2)*2*self.rho_LTO
        print('Disk loading:  ', np.round(self.des_TA, 1), ' N/m^2')

        # Plot disk loading curve
        self.ax2.plot(TA, WP_hover, '--', label = 'Hover')
        self.ax2.set_xlabel('Disk loading ')
        self.ax2.set_ylim(self.ax1.get_ylim())
        self.ax2.legend(loc = 'lower right')
        plt.show()

    def sizing(self):

        # Sizing the wing
        S  = self.MTOW/self.des_WS

        # Power needed in horizontal flight, per engine
        Pcr = self.MTOW/(self.des_WP*self.Ncr)


        print()
        print('====== Initial sizing ======')
        print('Wing area:                      ', np.round(S, 2))
        print('Shaft power per cruise engine:  ', np.round(Pcr))




# Test run
perf = performance(1000, 50000)
perf.wing_loading()
perf.disk_loading()
perf.sizing()
