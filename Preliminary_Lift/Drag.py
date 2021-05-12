import numpy as np
from math import *

#
# From BOX WING FUNDAMENTALS - A DESIGN PERSPECTIVE
# Oswald efficiency factor depending on the wing type
# h = 0.2, b = 1 can be used for a ratio of 0.2 which is a reasonable initial estimation
def e_factor(type,h, b, e_ref):
    """
    h = height difference between wings
    b = span
    """
    if type == 'box':
        ratio = h/b
        return e_ref * (0.44 + ratio* 2.219)/(0.44 + ratio * 0.9594)
    if type == 'tandem':
        ratio = h/b
        factor = 0.5 + (1-0.66 * ratio)/(2.1 + 7.4 * ratio)
        return e_ref * factor ** (-1)
    if type == 'normal':
        return e_ref

# Parasite Drag
"""
Cfe = 0.0045 for light twin wing aircraft ADSEE-I
Swet_ratio = 4 estimation using ADSEE-I

"""
def C_D_0(Swet_ratio, Cf): # ADSEE-I
    return Swet_ratio * Cf


# Parabolic Drag
def C_D(C_L, CD0, AR, e):
    return CD0 + C_L ** 2 / (np.pi * AR * e)

# LD ratio from ADSEE-I
def LD_ratio(phase, CD0, AR, e):
    if phase == 'cruise':
        return np.sqrt((np.pi * AR * e)/(4 * CD0))
    if phase == 'loiter':
        return np.sqrt((3 * np.pi * AR * e)/(16* CD0))

# C_L from ADSEE-I
def C_L(phase, CD0, AR, e):
    if phase == 'cruise':
        return np.sqrt(np.pi * AR * e * CD0)
    if phase == 'loiter':
        return np.sqrt(3 * np.pi * AR * e * CD0)

# CD0 component build up

class componentdrag:
    def __init__(self):


Cf = 1.328 / np.sqrt(Re)
Cf = 0.455 / ( (log10(Re) ** 2.58) * (1 + 0.144 * M * M) ** 0.65 )

Re = min( (rho * V * l / viscosity_dyn), 38.21 * ( l / 0.634E-5) ** 1.053 ) # assuming smooth paint

FFwing = ( 1 + 0.6 / tmax_pos * tc_ratio + 100 * tc_ratio ** 4) * (1.34 * M ** 0.18 * (cos(sweep_tmaxpos)) ** 0.28)
f = (l / sqrt( wfus * hfus)) # wfus = 1.2 hfus = 1.6
FFfus = 1 + 60 / f ** 3 + f / 400
FFnacelle = 1 + 0.35/ f


def CD0():

    #
    return 1
