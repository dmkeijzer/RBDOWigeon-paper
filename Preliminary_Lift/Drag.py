import numpy as np

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

