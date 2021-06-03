import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as sp_int

class PlotBlade:
    def __init__(self, chords, pitchs, radial_coords, R, xi_0, airfoil_name='naca4412', tc_ratio=0.12):
        """
        :param chords: Array with chords, from root to tip [m]
        :param pitchs: Array with pitch angles, from root to tip [rad]
        :param radial_coords: Radial coordinates per station [m]
        :param R: Radius of propeller [m]
        :param xi_0: Hub ratio [-]
        :param airfoil_name: String with ile name of the airfoil to use, by default NACA4412 [-]
        :param tc_ratio: Thickness to chord ratio of the airfoil, by default 12% for NACA4412 [-]
        """
        self.chords = chords
        self.pitchs = pitchs
        self.radial_coords = radial_coords
        self.R = R
        self.xi_0 = xi_0
        self.airfoil_name = airfoil_name
        self.tc_ratio = tc_ratio

    def load_airfoil(self):
        file = open(self.airfoil_name)

        airfoil = file.readlines()

        # Close file
        file.close()

        # List to save formatted coordinates
        airfoil_coord = []

        for line in airfoil:
            # Separate variables inside file
            a = line.split()

            new_line = []
            for value in a:
                new_line.append(float(value))
            airfoil_coord.append(new_line)

        airfoil_coord = np.array(airfoil_coord)
        airfoil_coord = airfoil_coord.T

        return airfoil_coord

    def plot_blade_side(self):
        for i in range(len(self.chords)):
            # Scale the chord length and thickness
            x_coords = self.load_airfoil()[0] * self.chords[i]
            y_coords = self.load_airfoil()[1] * self.chords[i] * self.tc_ratio

            # New coordinates after pitch
            x_coords_n = []
            y_coords_n = []

            # Apply pitch
            for j in range(len(x_coords)):
                # Transform coordinates with angle
                x_coord_n = np.sqrt((x_coords[j]**2 + y_coords[j]**2) /
                                    (1 + (np.tan(np.arctan2(y_coords[j], x_coords[j]) - self.pitchs[i]))**2))
                y_coord_n = x_coord_n * np.tan(np.arctan2(y_coords[j], x_coords[j]) - self.pitchs[i])

                # Save new coordinates
                x_coords_n.append(x_coord_n)
                y_coords_n.append(y_coord_n)

            # Plot the cross section
            # plt.plot(x_coords_n, y_coords_n)
            plt.plot(x_coords, y_coords)

        plt.show()

        return

    def plot_blade_planform(self):
        y_mins = []
        y_maxs = []
        for i in range(len(self.chords)):
            chord_len = self.chords[i]
            # Plot chord at its location, align half chords
            y_maxs.append(chord_len/2)
            y_mins.append(-chord_len/2)

        # Interpolate for smooth distribution
        y_max_fun = sp_int.CubicSpline(self.radial_coords, y_maxs, extrapolate=True)
        y_min_fun = sp_int.CubicSpline(self.radial_coords, y_mins, extrapolate=True)

        # Plot
        radius = np.linspace(self.xi_0, self.R, 200)
        plt.plot(radius, y_min_fun(radius))
        plt.plot(radius, y_max_fun(radius))
        plt.show()
