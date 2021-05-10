import numpy as np
import constants as c
# WING PLANFORM
""""
b =span



"""
def wing_planform(AR,S, sweepc4, taper):

    b = np.sqrt(AR*S)
    c_r = 2*S/((1+taper)*b)
    c_t = taper * c_r
    c_MAC = (2/3)*c_r*((1+taper+taper**2)/(1+ taper))
    y_MAC = (b/6)*((1 + 2*taper)/(1+taper))
    tan_sweep_LE = 0.25 * (2 * c_r / b) * (1-taper) + np.tan(sweepc4)

    X_LEMAC = y_MAC*tan_sweep_LE

    return b,c_r,c_t,c_MAC, y_MAC, X_LEMAC

def wing_planform_double(AR, S1, sweepc41, taper1, S2, sweepc42, taper2):
    #Wing 1
    b1 = np.sqrt(2* A * S1)
    c_r1 = 2 * S1 / ((1 + taper1) * b1)
    c_t1 = taper1 * c_r1
    c_MAC1 = (2 / 3) * c_r1 * ((1 + taper1 + taper1 ** 2) / (1 + taper1))
    y_MAC1 = (b1 / 6) * ((1 + 2 * taper1) / (1 + taper1))
    tan_sweep_LE1 = 0.25 * (2 * c_r1 / b1) * (1 - taper1) + np.tan(sweepc41)

    X_LEMAC1 = y_MAC1 * tan_sweep_LE1

    #Wing 2

    b2 = np.sqrt(2* AR * S2)
    c_r2 = 2 * S2 / ((1 + taper2) * b2)
    c_t2 = taper2 * c_r2
    c_MAC2 = (2 / 3) * c_r2 * ((1 + taper2 + taper2 ** 2) / (1 + taper2))
    y_MAC2 = (b2 / 6) * ((1 + 2 * taper2) / (1 + taper2))
    tan_sweep_LE2 = 0.25 * (2 * c_r2 / b2) * (1 - taper2) + np.tan(sweepc42)

    X_LEMAC2 = y_MAC2 * tan_sweep_LE2

    return b1, c_r1, c_t1, c_MAC1, y_MAC1, X_LEMAC1, b2, c_r2, c_t2, c_MAC2, y_MAC2, X_LEMAC2

# Airfoil Selection