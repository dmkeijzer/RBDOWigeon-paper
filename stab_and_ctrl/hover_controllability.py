"""
ACAI hover controllability criterion calculation. Based on:

Controllability Test Procedures for a class of hexacopters
Matlab files for "Controllability Analysis for a Class of Multirotors Subject to Rotor Failure/Wear"

By Guang-Xun Du, Quan Quan, Binxian Yang and Kai-Yuan Cai
Beihang Universty, Beijing, China
05/05/2012
"""

import numpy as np
from scipy.linalg import null_space
from matplotlib import pyplot as plt
from matplotlib import colors as mc
import colorsys
from dataclasses import dataclass
from itertools import combinations
import os
import json

root_path = os.path.join(os.getcwd(), os.pardir)

n_states = 8  # x = [h, phi, theta, psi, vh, p, q, r]
n_ctrl = 4  # u = F - G = [T, L, M, N] - [ma*g, 0, 0, 0]


@dataclass
class Rotor:
    x: float  # x (longitudinal) position w.r.t the centre of mass [m]
    y: float  # y (lateral) position w.r.t the centre of mass [m]
    K: float  # maximum lift [N]
    ku: float  # ratio between reactive torque and lift [m]
    eta: float  # efficiency parameter [-]
    ccw: bool  # rotation direction [-]


class Aircraft:
    def __init__(self, Jx, Jy, Jz, ma, rotors):
        self.Jx = Jx  # moment of inertia around roll axis [kg m^2]
        self.Jy = Jy  # moment of inertia around pitch axis [kg m^2]
        self.Jz = Jz  # moment of inertia around yaw axis [kg m^2]
        self.ma = ma  # mass of aircraft
        self.rotors = rotors

    def plot(self):
        for rotor in self.rotors:
            color = "tab:blue" if rotor.ccw else "tab:orange"
            color = colorsys.rgb_to_hls(*mc.to_rgb(color))
            color = colorsys.hls_to_rgb(color[0], rotor.eta*color[1], color[2])
            plt.scatter(rotor.x, rotor.y, color=color)


def acai(ac, g=9.81):
    # control effectiveness matrix (equation 5)
    Bf = np.zeros((n_ctrl, len(ac.rotors)))
    Bf[0, :] = [r.eta for r in ac.rotors]  # lift
    Bf[1, :] = [-r.eta * r.y for r in ac.rotors]  # roll torque
    Bf[2, :] = [r.eta * r.x for r in ac.rotors]  # pitch torque
    Bf[3, :] = [(-1 if not r.ccw else 1) * r.eta * r.ku for r in ac.rotors]  # yaw torque

    if np.linalg.matrix_rank(Bf) < n_ctrl:
        return -1E6

    fc = 0.5 * np.array([r.K for r in ac.rotors])
    G = np.zeros(n_ctrl)
    G[0] = ac.ma * g

    m = Bf.shape[1]
    M = np.arange(m)
    S1 = np.asarray([s for s in combinations(M, 3)])
    S2 = np.asarray([np.setdiff1d(M, s) for s in S1])
    d = np.zeros(S1.shape[0])

    for j in range(S1.shape[0]):
        # equation 11
        B1 = Bf[:, S1[j, :]]
        B2 = Bf[:, S2[j, :]]

        if np.linalg.matrix_rank(B1) == 3:
            # equation 15
            L = np.diag(2 * fc[S2[j, :]])

            # equation 16
            xi = null_space(B1.transpose())
            xi /= np.linalg.norm(xi)

            # equation 14
            xiB2 = xi.transpose() @ B2
            d[j] = (0.5 * np.sign(xiB2) @ L @ xiB2.transpose()
                    - np.abs(xi.transpose() @ (Bf @ fc - G)))

        else:
            d[j] = 1E6

    # equation 13
    return np.sign(np.min(d)) * np.min(np.abs(d))


def rank_Cab(ac):
    # state matrix
    A = np.zeros((n_states, n_states))
    A[:n_states // 2, n_states // 2:] = np.eye(n_states // 2)

    # control matrix
    B = np.zeros((n_states, n_ctrl))
    Jf_inv = np.diag([-1 / ac.ma, 1 / ac.Jx, 1 / ac.Jy, 1 / ac.Jz])
    B[n_states // 2:, :] = Jf_inv

    # controllability system
    Cab = np.hstack([np.linalg.matrix_power(A, i) @ B for i in range(8)])
    return np.linalg.matrix_rank(Cab)


def controllable(ac, g=9.81):
    if rank_Cab(ac) < n_states or acai(ac, g=g) <= 0:
        return False

    return True


def double_wing_config(datafile, ku, Jx, Jy, Jz, x_cg_l_fus, failed=None):
    data = json.load(datafile)
    datafile.close()

    ma = data["Structures"]["MTOW"]

    b_front = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_front"])
    b_back = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_back"])
    if b_front != b_back:
        print("Warning: wings are not equal in size")

    l_fus = data["Structures"]["l_fus"]
    K = data["Propulsion"]["Max_T_engine"]

    n_rotors = data["Propulsion"]["N_hover"]
    n_rotor_per_half_wing = n_rotors // 4  # assume equal distribution
    if n_rotors % 4 != 0:
        print("Warning: number of propellers not divisible by 4")

    if failed is not None:
        eta = [(1 if not f else 0) for f in failed]
    else:
        eta = n_rotors * [1]

    # inspired by typical quadcopter configuration. Can change
    ccw = (n_rotor_per_half_wing * [True] + n_rotor_per_half_wing * [False]
           + n_rotor_per_half_wing * [False] + n_rotor_per_half_wing * [True])

    # assumes that the rotors are at the extremities of the fuselage
    x = (2 * n_rotor_per_half_wing * [-x_cg_l_fus * l_fus]
         + 2 * n_rotor_per_half_wing * [l_fus * (1 - x_cg_l_fus)])

    # assumes that the rotors are spaced evenly between the two wingtips
    y = (list(np.linspace(-b_back/2, b_back/2, 2*n_rotor_per_half_wing))
         + list(np.linspace(-b_front/2, b_front/2, 2*n_rotor_per_half_wing)))

    # assumes that K and ku are equal for all engines
    rotors = [Rotor(x[i], y[i], K, ku, eta[i], ccw[i]) for i in range(n_rotors)]

    return Aircraft(Jx, Jy, Jz, ma, rotors)


def config1(ku, Jx, Jy, Jz, x_cg_l_fus, failed=None):
    datafile = open(os.path.join(root_path, "inputs_config_1.json"), "r")
    return double_wing_config(datafile, ku, Jx, Jy, Jz, x_cg_l_fus, failed)


def config2(ku, Jx, Jy, Jz, x_cg_l_fus, failed=None):
    datafile = open(os.path.join(root_path, "inputs_config_2.json"), "r")
    return double_wing_config(datafile, ku, Jx, Jy, Jz, x_cg_l_fus, failed)


def config3(ku_fus, ku_w, Jx, Jy, Jz, x_cg_l_fus, y_fus_b, x_w_l_fus, y_w_b, failed=None):
    datafile = open(os.path.join(root_path, "inputs_config_3.json"), "r")
    data = json.load(datafile)
    datafile.close()

    ma = data["Structures"]["MTOW"]

    b = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S"])
    l_fus = data["Structures"]["l_fus"]
    w_fus = data["Structures"]["w_fus"]
    if y_w_b*b < w_fus/2 or y_fus_b*b < w_fus/2:
        print("Warning: engine intersects with fuselage")
    elif y_w_b*b > b/2:
        print("Warning: engine beyond wingtip")

    # assumes that K is the same for the fuselage rotors in front and back
    K_fus = data["Propulsion"]["Max_T_engine"]
    K_w = K_fus * 1.5  # TODO: get propulsion to specify this
    K = 4 * [K_fus] + 2 * [K_w]

    if data["Propulsion"]["N_hover"] != 6:
        print("Warning: unexpected rotor configuration")

    if failed is not None:
        eta = [(1 if not f else 0) for f in failed]
    else:
        eta = 6 * [1]

    # inspired by example configuration from paper. Can change
    ccw = [True, False, True, False, False, True]

    # assumes that the fuselage rotors are at the extremities of the fuselage
    x = (2 * [-x_cg_l_fus * l_fus] + 2 * [l_fus * (1 - x_cg_l_fus)]
         + 2 * [l_fus * (x_w_l_fus - x_cg_l_fus)])

    # assumes that the fuselage rotors in front and back are at the same y
    y = [-y_fus_b * b, y_fus_b * b, -y_fus_b * b, y_fus_b * b,
         -y_w_b * b, y_w_b * b]

    # assumes that ku is the same for the fuselage rotors in front and back
    ku = 4 * [ku_fus] + 2 * [ku_w]
    rotors = [Rotor(x[i], y[i], K[i], ku[i], eta[i], ccw[i]) for i in range(4)]

    return Aircraft(Jx, Jy, Jz, ma, rotors)


if __name__ == "__main__":
    config1_params = {
        "ku": [0, 0.5],
        "Jx": [500, 1E6],
        "Jy": [500, 1E6],
        "Jz": [500, 1E6],
        "x_cg_l_fus": [0.2, 0.8]
    }

    config2_params = {
        "ku": [0, 0.5],
        "Jx": [500, 1E6],
        "Jy": [500, 1E6],
        "Jz": [500, 1E6],
        "x_cg_l_fus": [0.2, 0.8]
    }

    config3_params = {
        "ku_fus": [0, 0.5],
        "ku_w": [0, 0.5],
        "Jx": [500, 1E6],
        "Jy": [500, 1E6],
        "Jz": [500, 1E6],
        "x_cg_l_fus": [0.2, 0.8],
        "y_fus_b": [0.05, 0.3],
        "x_w_l_fus": [0.3, 0.7],
        "y_w_b": [0.05, 0.35]
    }
