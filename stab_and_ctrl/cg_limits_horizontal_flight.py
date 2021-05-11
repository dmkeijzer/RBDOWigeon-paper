import numpy as np

b = 10

def deps_da(Lambda_quarter_chord, lh, h_ht, A, CLaw):
    """
    Inputs:
    :param Lambda_quarter_chord: Sweep Angle at c/4 [RAD]
    :param lh: tail arm
    :param h_ht: distance between ac_w with ac_h
    :param A: Aspect Ratio of wing
    :param CLaw: Wing Lift curve slope
    :return: de/dalpha
    """
    r = lh * 2 / b
    mtv = h_ht * 2 / b
    Keps = (0.1124 + 0.1265 * Lambda_quarter_chord + 0.1766 * Lambda_quarter_chord ** 2) / r ** 2 + 0.1024 / r + 2
    Keps0 = 0.1124 / r ** 2 + 0.1024 / r + 2
    v = 1 + (r ** 2 / (r ** 2 + 0.7915 + 5.0734 * mtv ** 2) ** (0.3113))
    de_da = Keps / Keps0 * CLaw / (np.pi * A) * (
            r / (r ** 2 + mtv ** 2) * 0.4876 / (np.sqrt(r ** 2 + 0.6319 + mtv ** 2)) + v * (
            1 - np.sqrt(mtv ** 2 / (1 + mtv ** 2))))
    return de_da