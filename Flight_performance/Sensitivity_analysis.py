import matplotlib.pyplot as plt
import numpy as np
from Flight_performance.Flight_performance_final import mission, evtol_performance
from Aero_tools import ISA, speeds


class sensitivity_analysis:
    """
    This class performs sensitivity analysis for different flight parameters.

    TODO:
        - Add optimum speeds
    """
    def __init__(self, MTOM):

        self.MTOM = MTOM

        self.h_cruise_opt = 305

        plt.rcParams.update({'font.size': 16})
        self.path = '../Flight_performance/Figures/'

    def cruising_altitude(self):

        # Range of cruising altitudes
        altitude = np.arange(300, 3000, 300)

        # Arrays to store values
        dist  = np.zeros(np.size(altitude))
        time  = np.zeros(np.size(altitude))

        for i, h in enumerate(altitude):

            V = speeds(altitude = h, m = self.MTOM)

            performance = evtol_performance(cruising_alt = h, cruise_speed = V.cruise())

            dist[i], time[i] = performance.range(cruising_altitude = h, cruise_speed = V.cruise(), mass = self.MTOM)

        # Plot results
        plt.plot(altitude, dist/1000)
        plt.xlabel('Cruising altitude [m]')
        plt.ylabel('Range [km]')
        plt.grid()
        plt.tight_layout()
        plt.savefig(self.path + 'energy_sensitivity_altitude' +'.pdf')
        plt.show()

        plt.plot(altitude, dist/time)
        plt.xlabel('Cruising altitude [m]')
        plt.ylabel('Block speed [m/s]')
        plt.grid()
        plt.tight_layout()
        plt.savefig(self.path + 'time_sensitivity_altitude' + '.pdf')
        plt.show()

    def cruise_speed(self, plotting = True):

        # Get the stall speed
        V = speeds(self.h_cruise_opt, self.MTOM)
        V_stall = V.stall()

        # Range of cruise speeds
        cruise_speeds = np.linspace(V_stall, 100, 20)

        # Arrays to store values
        dist = np.zeros(np.size(cruise_speeds))
        time = np.zeros(np.size(cruise_speeds))

        for i, V_cr in enumerate(cruise_speeds):

            performance = evtol_performance(cruising_alt = self.h_cruise_opt, cruise_speed = V_cr)

            dist[i], time[i] = performance.range(cruising_altitude=self.h_cruise_opt,
                                                 cruise_speed = V_cr, mass = self.MTOM)

        # Find the optimal speed, for testing purposes
        idx     = np.argmax(dist)
        V_opt   = cruise_speeds[idx]

        if plotting:
            # Plot results
            plt.plot(cruise_speeds, dist / 1000)
            plt.vlines(V.cruise(), 0, 300) # Implement
            plt.xlabel('Cruise speed [m/s]')
            plt.ylabel('Range [km]')
            plt.grid()
            plt.tight_layout()
            plt.savefig(self.path + 'energy_sensitivity_speed' + '.pdf')
            plt.show()

            plt.plot(cruise_speeds, dist / time)
            plt.xlabel('Cruise speed [m/s]')
            plt.ylabel('Block speed [m/s]')
            plt.grid()
            plt.tight_layout()
            plt.savefig(self.path + 'time_sensitivity_speed' + '.pdf')
            plt.show()

        return V_opt

    def wind(self, test_wind = 60, testing = False, plotting = True):

        # Different wind speeds (tail- and headwinds)
        winds = np.arange(-10, 12, 2)

        # Arrays to store values
        dist = np.zeros(np.size(winds))
        time = np.zeros(np.size(winds))
        for i, wind in enumerate(winds):

            # Speed objects
            V = speeds(altitude = self.h_cruise_opt, m = self.MTOM)

            performance = evtol_performance(cruising_alt=self.h_cruise_opt, cruise_speed = V.cruise())

            dist[i], time[i] = performance.range(cruising_altitude=self.h_cruise_opt,
                                                 cruise_speed=V.cruise(), mass=self.MTOM, wind_speed = wind)

        # Range with a headwind as high as the wind speed
        if testing:
            performance = evtol_performance(cruising_alt=self.h_cruise_opt, cruise_speed=60)
            test_dist,_ = performance.range(cruising_altitude=self.h_cruise_opt,
                                          cruise_speed = 60, mass=self.MTOM, wind_speed = test_wind)
            return test_dist

        if plotting:
            # Plot results
            plt.plot(winds, dist / 1000)
            plt.xlabel('Wind [m/s]')
            plt.ylabel('Range [km]')
            plt.grid()
            plt.tight_layout()
            plt.savefig(self.path + 'energy_sensitivity_wind' + '.pdf')
            plt.show()

            plt.plot(winds, dist / time)
            plt.xlabel('Wind [m/s]')
            plt.ylabel('Block speed [m/s]')
            plt.grid()
            plt.tight_layout()
            plt.savefig(self.path + 'time_sensitivity_wind' + '.pdf')
            plt.show()




sensitivity = sensitivity_analysis(2000)
#sensitivity.cruising_altitude()
#sensitivity.cruise_speed()
sensitivity.wind()
