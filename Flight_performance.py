import numpy as np
import matplotlib.pyplot as plt
from Aero_tools import ISA




class performance:
    def __init__(self, h):

        # Atmospherics
        self.rho = 1.225

        # Set requirements
        self.Vs     = 50
        self.Vmax   = 100
        self.ROC    = 10
        self.nmax   = 2

        # Aerodynamic constants
        self.CLmax  = 1.5
        self.A      = 10
        self.e      = 0.75
        self.CD0    = 0.05

        # Propulsion constants
        self.eff_prop   = 0.8

    def wing_loading(self):
        WS = np.arange(100, 4000, 1)
        # Stall speed
        WS_stall = 0.5*self.rho*(self.Vs**2)*self.CLmax

        # Max speed (Reduction of power with altitude was neglected, as no combustion is involved (revise this for H2))
        WP_speed = self.eff_prop*((self.CD0*0.5*self.rho*(self.Vmax**3)/WS +
                                   WS/(np.pi*self.A*self.e*0.5*self.rho*self.Vmax))**-1)

        # Climb performance
        WP_climb = ((self.ROC + np.sqrt(2*WS)*(self.CD0**0.25)/(1.345*((self.A*self.e)**0.75)))**-1)/self.eff_prop

        # Turning performance
        WP_turn  = self.eff_prop*((self.CD0*0.5*self.rho*(self.Vmax**3)/WS +
                                   WS*self.nmax*self.nmax/(np.pi*self.A*self.e*0.5*self.rho*self.Vmax))**-1)

        plt.plot(WS, WP_speed, label = 'Maximum speed')
        plt.plot(WS, WP_climb, label = 'Rate of climb')
        plt.plot(WS, WP_turn,  label = 'Turn performance')
        plt.vlines(WS_stall, 0, 0.1)
        plt.grid()
        plt.legend()
        plt.show()

# Test run
perf = performance(1000)
perf.wing_loading()
