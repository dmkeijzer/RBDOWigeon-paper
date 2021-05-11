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

# parameters used for sensitivity analyses
# for each parameter: [best estimate, low bound, high bound]
config1_params = {
    "ku": [0.1, 0, 0.5],
    "Jx": [1000, 500, 1E6],
    "Jy": [1000, 500, 1E6],
    "Jz": [1000, 500, 1E6],
    "x_cg_l_fus": [0.5, -0.2, 0.8]
}

config2_params = {
    "ku": [0.1, 0, 0.5],
    "Jx": [1000, 500, 1E6],
    "Jy": [1000, 500, 1E6],
    "Jz": [1000, 500, 1E6],
    "x_cg_l_fus": [0.5, 0.2, 0.8]
}

config3_params = {
    "ku_fus": [0.1, 0, 0.5],
    "ku_w": [0.1, 0, 0.5],
    "Jx": [1000, 500, 1E6],
    "Jy": [1000, 500, 1E6],
    "Jz": [1000, 500, 1E6],
    "x_cg_l_fus": [0.5, 0.2, 0.8],
    "y_fus_b": [0.1, 0.05, 0.3],
    "x_w_l_fus": [0.5, 0.3, 0.7],
    "y_w_b": [0.15, 0.05, 0.35]
}

params = [config1_params, config2_params, config3_params]

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

    b = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_front"])
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


def plot_sensitivities(config, res=20, failed=None, vmin=-0.1, vmax=1.1):
    p = params[config]

    if config == 0:
        ac_generator = config1
    elif config == 1:
        ac_generator = config2
    else:
        ac_generator = config3

    Jx_range = np.linspace(p["Jx"][1], p["Jx"][2], res)
    Jy_range = np.linspace(p["Jy"][1], p["Jy"][2], res)
    Jz_range = np.linspace(p["Jz"][1], p["Jz"][2], res)
    x_cg_l_fus_range = np.linspace(p["x_cg_l_fus"][1], p["x_cg_l_fus"][2], res)

    if config == 0 or config == 1:
        ku_range = np.linspace(p["ku"][1], p["ku"][2], res)

        # vary Jx
        plt.subplot(311)
        rhos = []
        for Jx in Jx_range:
            ac = ac_generator(p["ku"][0], Jx, p["Jy"][0], p["Jz"][0],
                              p["x_cg_l_fus"][0], failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"J$_x$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(Jx_range, rhos)

        # vary Jy
        plt.subplot(312)
        rhos = []
        for Jy in Jy_range:
            ac = ac_generator(p["ku"][0], p["Jx"][0], Jy, p["Jz"][0],
                              p["x_cg_l_fus"][0], failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"J$_y$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(Jy_range, rhos)

        # vary Jz
        plt.subplot(313)
        rhos = []
        for Jz in Jz_range:
            ac = ac_generator(p["ku"][0], p["Jx"][0], p["Jy"][0], Jz,
                              p["x_cg_l_fus"][0], failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"J$_z$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(Jz_range, rhos)

        plt.tight_layout()

        # vary x_cg_l_fus
        plt.figure()
        rhos = []
        for x_cg_l_fus in x_cg_l_fus_range:
            ac = ac_generator(p["ku"][0], p["Jx"][0], p["Jy"][0], p["Jz"][0],
                              x_cg_l_fus, failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"x$_{cg}$/l$_{fus}$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(x_cg_l_fus_range, rhos)

        # vary ku
        plt.figure()
        rhos = []
        for ku in ku_range:
            ac = ac_generator(ku, p["Jx"][0], p["Jy"][0], p["Jz"][0],
                              p["x_cg_l_fus"][0], failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"k$_{\mu}$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(ku_range, rhos)

    else:
        ku_fus_range = np.linspace(p["ku_fus"][1], p["ku_fus"][2], res)
        ku_w_range = np.linspace(p["ku_w"][1], p["ku_w"][2], res)
        y_fus_b_range = np.linspace(p["y_fus_b"][1], p["y_fus_b"][2], res)
        x_w_l_fus_range = np.linspace(p["x_w_l_fus"][1], p["x_w_l_fus"][2], res)
        y_w_b_range = np.linspace(p["y_w_b"][1], p["y_w_b"][2], res)

        # vary Jx
        plt.subplot(311)
        rhos = []
        for Jx in Jx_range:
            ac = ac_generator(p["ku_fus"][0], p["ku_w"][0], Jx, p["Jy"][0],
                              p["Jz"][0], p["x_cg_l_fus"][0], p["y_fus_b"][0],
                              p["x_w_l_fus"][0], p["y_w_b"][0], failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"J$_x$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(Jx_range, rhos)

        # vary Jy
        plt.subplot(312)
        rhos = []
        for Jy in Jy_range:
            ac = ac_generator(p["ku_fus"][0], p["ku_w"][0], p["Jx"][0], Jy,
                              p["Jz"][0], p["x_cg_l_fus"][0], p["y_fus_b"][0],
                              p["x_w_l_fus"][0], p["y_w_b"][0], failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"J$_y$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(Jy_range, rhos)

        # vary Jz
        plt.subplot(313)
        rhos = []
        for Jz in Jz_range:
            ac = ac_generator(p["ku_fus"][0], p["ku_w"][0], p["Jx"][0],
                              p["Jy"][0], Jz, p["x_cg_l_fus"][0],
                              p["y_fus_b"][0], p["x_w_l_fus"][0],
                              p["y_w_b"][0], failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"J$_z$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(Jz_range, rhos)

        plt.tight_layout()

        # vary x_cg_l_fus
        plt.figure()
        rhos = []
        for x_cg_l_fus in x_cg_l_fus_range:
            ac = ac_generator(p["ku_fus"][0], p["ku_w"][0], p["Jx"][0],
                              p["Jy"][0], p["Jz"][0], x_cg_l_fus,
                              p["y_fus_b"][0], p["x_w_l_fus"][0],
                              p["y_w_b"][0], failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"x$_{cg}$/l$_{fus}$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(x_cg_l_fus_range, rhos)

        # vary ku_fus
        plt.figure()
        plt.subplot(211)
        rhos = []
        for ku_fus in ku_fus_range:
            ac = ac_generator(ku_fus, p["ku_w"][0], p["Jx"][0], p["Jy"][0],
                              p["Jz"][0], p["x_cg_l_fus"][0], p["y_fus_b"][0],
                              p["x_w_l_fus"][0], p["y_w_b"][0], failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"k$_{\mu, fus}$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(ku_fus_range, rhos)

        # vary ku_w
        plt.subplot(212)
        rhos = []
        for ku_w in ku_w_range:
            ac = ac_generator(p["ku_fus"][0], ku_w, p["Jx"][0], p["Jy"][0],
                              p["Jz"][0], p["x_cg_l_fus"][0], p["y_fus_b"][0],
                              p["x_w_l_fus"][0], p["y_w_b"][0], failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"k$_{\mu, w}$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(ku_w_range, rhos)

        # vary y_fus_b
        plt.figure()
        plt.subplot(211)
        rhos = []
        for y_fus_b in y_fus_b_range:
            ac = ac_generator(p["ku_fus"][0], p["ku_w"][0], p["Jx"][0],
                              p["Jy"][0], p["Jz"][0], p["x_cg_l_fus"][0],
                              y_fus_b, p["x_w_l_fus"][0], p["y_w_b"][0],
                              failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"y$_{fus}$/b")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(y_fus_b_range, rhos)

        # vary y_w_b
        plt.subplot(212)
        rhos = []
        for y_w_b in y_w_b_range:
            ac = ac_generator(p["ku_fus"][0], p["ku_w"][0], p["Jx"][0],
                              p["Jy"][0], p["Jz"][0], p["x_cg_l_fus"][0],
                              p["y_fus_b"][0], p["x_w_l_fus"][0], y_w_b,
                              failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"y$_{w}$/b")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(y_w_b_range, rhos)

        # vary x_w_l_fus
        plt.figure()
        plt.subplot(211)
        rhos = []
        for x_w_l_fus in x_w_l_fus_range:
            ac = ac_generator(p["ku_fus"][0], p["ku_w"][0], p["Jx"][0],
                              p["Jy"][0], p["Jz"][0], p["x_cg_l_fus"][0],
                              p["y_fus_b"][0], x_w_l_fus, p["y_w_b"][0],
                              failed=failed)
            rhos.append(acai(ac))
        plt.xlabel(r"x$_w$/l$_{fus}$")
        plt.ylabel("ACAI")
        plt.ylim(vmin, vmax)
        plt.plot(x_w_l_fus_range, rhos)


if __name__ == "__main__":
    plot_sensitivities(1)
    plt.show()
