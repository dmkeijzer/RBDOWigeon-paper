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

L_c4 = 0
taper_ratio = 0.4
AR_1_2 = 11.4
AR_3 = 5.701
a = 340
V_s = 30
V_c = 46.01469067334079
V_c_3 = 53.64138948890874
M_s = V_s/a
M_c =V_c/a
beta_s = np.sqrt(1-M_s**2)
beta_c = np.sqrt(1-M_c**2)
Lambda_b = 0
xacfwd = 0.25*1.305
lfus = 4
xacrear = lfus-(1-0.25)*1.305

print("Configuration 1-2 at STALL beta*AR:", beta_s*AR_1_2)
print("Configuration 1-2 at CRUISE beta*AR:", beta_c*AR_1_2)
print("Configuration 3 at STALL beta*AR:", beta_s*AR_3)
print("Configuration 3 at CRUISE beta*AR:", beta_c*AR_3)

def values_conf_1():
    datafile = open(os.path.join(root_path, "inputs_config_1.json"), "r")
    data = json.load(datafile)
    datafile.close()
    ma = data["Structures"]["MTOW"]
    Afwd = data["Aerodynamics"]["AR"]*2
    b_fwd = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_front"])
    b_rear = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_back"])
    S_fwd = data["Aerodynamics"]["S_front"]
    S_rear = data["Aerodynamics"]["S_back"]
    CLa_fwd = data["Aerodynamics"]["CLalpha_back"]
    CLa_rear = CLa_fwd
    Cm_ac_fwd = data["Aerodynamics"]["Cm_ac_front"]
    Cm_ac_rear = data["Aerodynamics"]["Cm_ac_back"]
    CL_max_fwd = data["Aerodynamics"]["CLmax_front"]
    CL_max_rear = data["Aerodynamics"]["CLmax_back"]
    c_fwd = 1.305
    c_rear = 1.305
    #cfwd = data["Aerodynamics"]["MAC1"]
    #crear = data["Aerodynamics"]["MAC2"]
    values = [CL_max_fwd, CL_max_rear, Cm_ac_fwd, Cm_ac_rear, CLa_fwd, CLa_rear, S_fwd, S_rear, Afwd, c_fwd,c_rear,b_fwd,b_rear]
    return values


def values_conf_2():
    datafile = open(os.path.join(root_path, "inputs_config_2.json"), "r")
    data = json.load(datafile)
    datafile.close()
    ma = data["Structures"]["MTOW"]
    Afwd = data["Aerodynamics"]["AR"]*2
    b_fwd = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_front"])
    b_rear = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_back"])
    S_fwd = data["Aerodynamics"]["S_front"]
    S_rear = data["Aerodynamics"]["S_back"]
    CLa_fwd = data["Aerodynamics"]["CLalpha_back"]
    CLa_rear = CLa_fwd
    Cm_ac_fwd = data["Aerodynamics"]["Cm_ac_front"]
    Cm_ac_rear = data["Aerodynamics"]["Cm_ac_back"]
    CL_max_fwd = data["Aerodynamics"]["CLmax_front"]
    CL_max_rear = data["Aerodynamics"]["CLmax_back"]
    c_fwd = 1.305
    c_rear = 1.305
    values = [CL_max_fwd, CL_max_rear, Cm_ac_fwd, Cm_ac_rear, CLa_fwd, CLa_rear, S_fwd, S_rear, Afwd, c_fwd,c_rear,b_fwd,b_rear]
    return values


def values_conf_3():
    datafile = open(os.path.join(root_path, "inputs_config_3.json"), "r")
    data = json.load(datafile)
    datafile.close()
    ma = data["Structures"]["MTOW"]
    CD0 = data["Aerodynamics"]["CD0"]
    e = data["Aerodynamics"]["e"]
    Afwd = data["Aerodynamics"]["AR"]
    b_fwd = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_front"])
    b_rear = np.sqrt(data["Aerodynamics"]["AR"] * data["Aerodynamics"]["S_back"])
    S_fwd = data["Aerodynamics"]["S_front"]
    S_rear = data["Aerodynamics"]["S_back"]
    CLa_fwd = data["Aerodynamics"]["CLalpha_back"]
    CLa_rear = CLa_fwd
    Cm_ac_fwd = data["Aerodynamics"]["Cm_ac_front"]
    Cm_ac_rear = data["Aerodynamics"]["Cm_ac_back"]
    CL_max_fwd = data["Aerodynamics"]["CLmax_front"]
    CL_max_rear = data["Aerodynamics"]["CLmax_back"]
    c = data["Aerodynamics"]["MAC1"]
    values = [CL_max_fwd, CL_max_rear, Cm_ac_fwd, Cm_ac_rear, CLa_fwd, CLa_rear, S_fwd, S_rear, Afwd, c, b_fwd,e,CD0]
    return values


def deps_da(Lambda_quarter_chord, b,lh, h_ht, A, CLaw):
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
def lh(xacfwd,xacrear):
    return abs(xacfwd-xacrear)

def cg_range_conf_1(values=values_conf_1(),deda=deps_da(L_c4,values_conf_1()[11],lh(xacfwd,xacrear),h_ht = 1.6,A=values_conf_1()[8],CLaw=values_conf_1()[4])):
    CLfwd,CLrear,Cmacfwd,Cmacrear,CLafwd, CLarear,Sfwd,Srear,Afwd,cfwd,crear,b_fwd,b_rear = values
    lfus = 4
    hfus = 1.6
    xacfwd_stab = 0.25*cfwd
    xacfwd_control = 0.25 * cfwd
    o = CLafwd*xacfwd_stab+CLarear*lfus*Srear/Sfwd*(1-deda)
    p =CLafwd*1+CLarear*1*Srear/Sfwd*(1-deda)
    xcg_max = o/p
    oo = CLfwd * xacfwd_control + CLrear * (lfus-0.75*crear) * Srear / Sfwd -Cmacfwd-Cmacrear*Srear/Sfwd*crear
    pp = CLfwd * 1 + CLrear * 1 * Srear / Sfwd
    xcg_min = oo/pp
    print("Range: %.4f < x_cg < %.4f"%(xcg_min,xcg_max))
    return abs(xcg_max-xcg_min)


def cg_range_conf_2(values=values_conf_2(),deda=deps_da(L_c4,values_conf_2()[11],lh(xacfwd,xacrear),h_ht = 1.6,A=values_conf_2()[8],CLaw=values_conf_2()[4])):
    CLfwd,CLrear,Cmacfwd,Cmacrear,CLafwd, CLarear,Sfwd,Srear,Afwd,cfwd,crear,b_fwd,b_rear = values
    lfus = 4
    hfus = 1.6
    xacfwd_stab = 0.25*cfwd
    xacfwd_control = 0.25 * cfwd
    o = CLafwd*xacfwd_stab+CLarear*lfus*Srear/Sfwd*(1-deda)
    p =CLafwd*1+CLarear*1*Srear/Sfwd*(1-deda)
    xcg_max = o/p
    oo = CLfwd * xacfwd_control + CLrear * (lfus-0.75*crear) * Srear / Sfwd -Cmacfwd-Cmacrear*Srear/Sfwd*crear
    pp = CLfwd * 1 + CLrear * 1 * Srear / Sfwd
    xcg_min = oo/pp
    print("Range: %.4f < x_cg < %.4f"%(xcg_min,xcg_max))
    return abs(xcg_max-xcg_min)


def cg_range_conf_3(values=values_conf_3(),eta=5):
    CLfwd, CLrear, Cmacfwd, Cmacrear, CLafwd, CLarear, Sfwd, Srear, Afwd, cfwd, bfwd,e,CD0 = values
    lfus = 4
    hfus = 1.6
    xacfwd_stab = 0.24*cfwd
    xacfwd_control = 0.24 * cfwd
    CD = CD0 + CLfwd**2/(np.pi*Afwd*e)
    zaccg = eta/100*hfus
    xcg_max = xacfwd_stab
    xcg_min = xacfwd_control-Cmacfwd/CLfwd*cfwd-CD/CLfwd*zaccg
    print("Range: %.4f < x_cg < %.4f"%(xcg_min,xcg_max))
    return abs(xcg_max-xcg_min)

cg1 = cg_range_conf_1()
cg2 = cg_range_conf_2()
cg3 = cg_range_conf_3()