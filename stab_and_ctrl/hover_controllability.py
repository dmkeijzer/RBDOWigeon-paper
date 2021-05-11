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
from dataclasses import dataclass
from itertools import combinations


@dataclass
class Rotor:
    x: float  # x (longitudinal) position w.r.t the centre of mass [m]
    y: float  # y (lateral) position w.r.t the centre of mass [m]
    K: float  # maximum lift [N]
    ku: float  # ratio between reactive torque and lift [m]
    eta: float  # efficiency parameter [-]
    ccw: bool  # rotation direction [-]


@dataclass
class Aircraft:
    Jx: float  # moment of inertia around roll axis [kg m^2]
    Jy: float  # moment of inertia around pitch axis [kg m^2]
    Jz: float  # moment of inertia around yaw axis [kg m^2]
    ma: float  # mass of aircraft
    rotors: list


def acai(Bf, fc, G):
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


def controllable(ac, g=9.81):
    n_states = 8  # x = [h, phi, theta, psi, vh, p, q, r]
    n_ctrl = 4  # u = F - G = [T, L, M, N] - [ma*g, 0, 0, 0]

    # state matrix
    A = np.zeros((n_states, n_states))
    A[:n_states//2, n_states//2:] = np.eye(n_states//2)

    # control matrix
    B = np.zeros((n_states, n_ctrl))
    Jf_inv = np.diag([-1 / ac.ma, 1 / ac.Jx, 1 / ac.Jy, 1 / ac.Jz])
    B[n_states//2:, :] = Jf_inv

    # controllability system
    Cab = np.hstack([np.linalg.matrix_power(A, i) @ B for i in range(8)])
    if np.linalg.matrix_rank(Cab) < n_states:
        return False

    # control effectiveness matrix (equation 5)
    Bf = np.zeros((n_ctrl, len(ac.rotors)))
    Bf[0, :] = [r.eta for r in ac.rotors]  # lift
    Bf[1, :] = [-r.eta * r.y for r in ac.rotors]  # roll torque
    Bf[2, :] = [r.eta * r.x for r in ac.rotors]  # pitch torque
    Bf[3, :] = [(-1 if not r.ccw else 1) * r.eta * r.ku for r in ac.rotors]  # yaw torque

    # ACAI
    if np.linalg.matrix_rank(Bf) == n_ctrl:
        fc = 0.5 * np.array([r.K for r in ac.rotors])
        G = np.zeros(n_ctrl)
        G[0] = ac.ma * g
        rho = acai(Bf, fc, G)

    else:
        rho = -1E6

    if rho <= 0:
        return False

    return rho
