import numpy as np
from matplotlib import pyplot as plt


class LandingGearCalc:
    """
    Class to calculate optimal landing gear position based on constraints.
    Based on Lecture 9 of AE3211-I Systems Engineering and Aerospace Design
    The coordinate system has its origin at the nose the height of the bottom
    of the fuselage. The x-axis points backwards, the y-axis points towards
    starboard and the z-axis points upwards.

    @author Jakob Schoser
    """
    def __init__(self, max_tw: float, x_ng_min: float, y_max_rotor: float,
                 gamma: float, z_rotor_line_root: float, rotor_rad: float,
                 fus_back_bottom: list, fus_back_top: list):
        """
        Construct a landing gear position calculator object
        :param max_tw: Maximum track width for the main landing gear
        :param x_ng_min: Minimum x-location for the nose gear
        :param y_max_rotor: Maximum y-location of the centre of the most
        outboard rotor on the front wing
        :param gamma: Dihedral of the front wing
        :param z_rotor_line_root: z-location of the point where the straight
        line passing through all rotor centres on the front wing intersects
        with the symmetry plane
        :param rotor_rad: Radius of the most outboard rotor on the front wing
        :param fus_back_bottom: [x, y]-location of the back bottom corner
        of the fuselage
        :param fus_back_top: [x, y]-location of the back top corner
        of the fuselage
        """
        self.max_tw = max_tw
        self.x_ng_min = x_ng_min
        self.y_max_rotor = y_max_rotor
        self.gamma = gamma
        self.z_rotor_line_root = z_rotor_line_root
        self.rotor_rad = rotor_rad
        self.fus_back_bottom = np.array(fus_back_bottom)
        self.fus_back_top = np.array(fus_back_top)

    def optimum_placement(self, x_cg_range: list, x_cg_margin: float,
                          z_cg_max: float, theta: float, phi: float,
                          psi: float, min_ng_load_frac: float) -> tuple:
        # TODO: consider compression of the landing gear
        # TODO: consider y-offset of CG in turnover angle
        """
        Place the landing gear with respect to geometric constraints
        :param x_cg_range: x-range of CG locations
        :param x_cg_margin: margin applied to the aft CG location
        :param z_cg_max: z-location of the highest CG
        :param theta: Pitch angle limit
        :param phi: Lateral ground clearance angle
        :param psi: Turnover angle
        :param min_ng_load_frac: Minimum fraction of the weight to be carried
        by the nose gear
        :return: (x-location of the nose gear, x-location of the main
        landing gear, track width of the main landing gear, height of the
        main landing gear). (None, None, None, None) if the required track
        width exceeds the maximum track width
        """
        # calculate [x, z]-position of MLG due to pitch limit during emergency
        # landing on a regular airfield
        fus_slope = (
                (self.fus_back_top[1] - self.fus_back_bottom[1])
                / (self.fus_back_top[0] - self.fus_back_bottom[0])
        )

        # if the top point on the fuselage back is limiting
        if np.arctan(fus_slope) <= theta:
            fus_lim_pt = self.fus_back_top
        # if the bottom point on the fuselage back is limiting
        else:
            fus_lim_pt = self.fus_back_bottom

        # apply margin to critical CG for tip-back
        cg_rear = (np.array([x_cg_range[1], z_cg_max])
                   + np.array([x_cg_margin, 0]))

        A = np.array([
            [np.tan(theta), -1],
            [-1, -np.tan(theta)]
        ])

        b = fus_lim_pt - cg_rear

        x = np.linalg.solve(A, b)
        mlg_pos = cg_rear + x[0] * np.array([np.tan(theta), -1])

        # calculate [x, z]-position of the nose landing gear based on the
        # minimum load fraction it should have
        d = (mlg_pos - cg_rear)[0] / min_ng_load_frac
        ng_pos = mlg_pos - np.array([d, 0])
        ng_pos[0] = max(ng_pos[0], self.x_ng_min)

        # calculate the minimum track width based on turnover angle
        c = z_cg_max / np.tan(psi)
        alpha = np.arcsin(c / (x_cg_range[0] - ng_pos[0]))
        tw = 2 * np.tan(alpha) * d

        # calculate the minimum track width based on rotor clearance
        z_rotor_centre = (self.z_rotor_line_root
                          + self.y_max_rotor * np.tan(self.gamma))
        z_rotor_bottom = z_rotor_centre - self.rotor_rad
        tw = max(tw, 2 * (self.y_max_rotor
                          - (z_rotor_bottom - mlg_pos[1]) / np.tan(phi)))

        if tw > self.max_tw:
            return None, None, None, None

        return ng_pos[0], mlg_pos[0], tw, abs(mlg_pos[1])

    def plot_lg(self, x_cg_range: list, x_cg_margin: float, z_cg_max: float,
                x_ng: float, x_mlg: float, tw: float, h_mlg: float):
        """
        Create a side and front view plot of the given landing gear
        configuration.
        :param x_cg_range: x-range of CG locations
        :param x_cg_margin: margin applied to the aft CG location
        :param z_cg_max: z-location of the highest CG
        :param x_ng: x-location of the nose gear
        :param x_mlg: x-location of the main landing gear
        :param tw: track width of the main landing gear
        :param h_mlg: height of the main landing gear
        """
        # plot side view
        plt.subplot(211)
        # plot rear CG margin
        plt.plot([x_cg_range[1], x_cg_range[1] + x_cg_margin],
                 [z_cg_max, z_cg_max], color="tab:green", marker="o",
                 label="CG margin")
        # plot CG range
        plt.plot(x_cg_range, [z_cg_max, z_cg_max], color="k", marker="o",
                 label="CG range")
        # plot nose gear
        plt.scatter([x_ng], [-h_mlg], color="tab:blue", label="Nose gear")
        # plot main landing gear
        plt.scatter([x_mlg], [-h_mlg], color="tab:orange",
                    label="Main landing gear")
        plt.legend()
        plt.gca().set_aspect('equal', adjustable='box')

        # plot front view
        plt.subplot(212)
        # plot CG
        plt.scatter([0], [z_cg_max], color="k", label="CG range")
        # plot nose gear
        plt.scatter([0], [-h_mlg], color="tab:blue", label="Nose gear")
        # plot main landing gear
        plt.scatter([tw/2], [-h_mlg], color="tab:orange",
                    label="Main landing gear")
        plt.scatter([-tw/2], [-h_mlg], color="tab:orange")
        plt.legend()
        plt.gca().set_aspect('equal', adjustable='box')

