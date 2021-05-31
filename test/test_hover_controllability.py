import numpy as np
from stab_and_ctrl.hover_controllability import *

def test_hexacopter_example():
    ma = 1.535  # [kg]
    g = 9.8  # [m/s^2]
    Jx, Jy, Jz = 0.0411, 0.0478, 0.0599  # [kg m^2]

    r = 0.275  # [m]
    psi = np.array([0, np.pi/3, 2*np.pi/3, np.pi, 4*np.pi/3, 5*np.pi/3])  # [rad]
    x = r * np.cos(psi)  # [m]
    y = r * np.sin(psi)  # [m]
    ccw = np.array([False, True, False, True, False, True])
    ku = 0.1  # [m]
    eta = 1  # [-]
    K = 6.125  # [N]

    rotors = [Rotor(x[i], y[i], K, ku, eta, ccw[i]) for i in range(6)]
    ac = Aircraft(Jx, Jy, Jz, ma, rotors)

    assert controllable(ac, g=g) and abs(acai(ac, g=g) - 1.4861) < 1E-4
