import matplotlib.pyplot as plt
import numpy as np
from Flight_performance_final import mission, evtol_performance
from Aero_tools import ISA, speeds

class sensitivity_analysis:
    """
    This class performs sensitivity analysis for different flight parameters.

    TO DO:
        - Add optimum speeds
        -
    """
    def __init__(self, MTOM):

        self.MTOM = MTOM

        self.h_cruise_opt = 305

        plt.rcParams.update({'font.size': 16})
        self.path = 'C:/Users/Egon Beyne/Desktop/DSE/Final/'

    def cruising_altitude(self):

        # Range of cruising altitudes
        altitude = np.arange(300, 3000, 300)

        # Arrays to store values
        dist  = np.zeros(np.size(altitude))
        time  = np.zeros(np.size(altitude))

        for i, h in enumerate(altitude):

            optimum_speed = 60  # !!!!! IMPLEMENT !!!!!

            performance = evtol_performance(cruising_alt = h, cruise_speed = optimum_speed)

            dist[i], time[i] = performance.range(cruising_altitude = h, cruise_speed = optimum_speed, mass = self.MTOM)

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

    def cruise_speed(self):

        # Get the stall speed
        V = speeds(self.h_cruise_opt, self.MTOM)
        V_stall = V.stall

        # Range of cruise speeds
        cruise_speeds = np.arange(V_stall, 100, 20)

        # Arrays to store values
        dist = np.zeros(np.size(cruise_speeds))
        time = np.zeros(np.size(cruise_speeds))


sensitivity = sensitivity_analysis(2000)

sensitivity.cruising_altitude()










