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
b = 10
L_c4 = 0
def values_conf_1():
    datafile = open(os.path.join(root_path, "inputs_config_1.json"), "r")
    data = json.load(datafile)
    datafile.close()
    ma = data["Structures"]["MTOW"]
    b_fwd = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_front"])
    b_rear = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_back"])
    CLa_fwd = data["Aerodynamics"]["CLalpha_back"]
    CLa_rear = CLa_fwd
    Cm_ac_fwd = data["Aerodynamics"]["Cm_ac_front"]
    Cm_ac_rear = data["Aerodynamics"]["Cm_ac_back"]
    CL_max_fwd = data["Aerodynamics"]["CLmax_front"]
    CL_max_rear = data["Aerodynamics"]["CLmax_back"]
    return
def deps_da(Lambda_quarter_chord, lh, h_ht, A, CLaw):
    """
    Inputs:
    :param Lambda_quarter_chord: Sweep Angle at c/4 [RAD]
    :param lh: distance between ac_w1 with ac_w2 (horizontal)
    :param h_ht: distance between ac_w1 with ac_w2 (vertical)
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