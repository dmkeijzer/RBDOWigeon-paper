import numpy as np
# WING PLANFORM
""""
b =span



"""
def wing_planform(A,S, sweepc4, taper):

    b = np.sqrt(A*S)
    c_r = 2*S/((1+taper)*b)
    c_t = taper * c_r
    c_MAC = (2/3)*c_r*((1+taper+taper**2)/(1+ taper))
    y_MAC = (b/6)*((1 + 2*taper)/(1+taper))
    tan_sweep_LE = 0.25 * (2 * c_r / b) * (1-taper) + np.tan(sweepc4)

    X_LEMAC = y_MAC*tan_sweep_LE

    return b,c_r,c_t,c_MAC, y_MAC, X_LEMAC


# Airfoil Selection