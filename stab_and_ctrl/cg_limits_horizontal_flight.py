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

taper_ratio = 0.4
a = 340
def Speeds(conf):
    a = 340
    if conf==1:
        datafile = open(os.path.join(root_path, "data/inputs_config_1.json"), "r")
        data = json.load(datafile)
        datafile.close()
        Afwd = data["Aerodynamics"]["AR"] * 2
    if conf==2:
        datafile = open(os.path.join(root_path, "data/inputs_config_2.json"), "r")
        data = json.load(datafile)
        datafile.close()
        Afwd = data["Aerodynamics"]["AR"] * 2
    if conf==3:
        datafile = open(os.path.join(root_path, "data/inputs_config_3.json"), "r")
        data = json.load(datafile)
        datafile.close()
        Afwd = data["Aerodynamics"]["AR"]
    V_c = data["Flight performance"]["V_cruise"]
    V_s = data["Requirements"]["V_stall"]
    M_s = V_s/a
    M_c = V_c/a
    beta_s = np.sqrt(1 - M_s ** 2)
    beta_c = np.sqrt(1 - M_c ** 2)
    print("Configuration %.0f at STALL beta*AR = %.3f"%(conf,beta_s * Afwd))
    print("Configuration %.0f at CRUISE beta*AR = %.3f "%(conf,beta_c * Afwd))
    return V_c, V_s, M_c,M_s

V1 = Speeds(1)
V2 = Speeds(2)
V3 = Speeds(3)

def values_conf_3():
    datafile = open(os.path.join(root_path, "data/inputs_config_3.json"), "r")
    data = json.load(datafile)
    datafile.close()
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


def deps_da(Lambda_quarter_chord, b,lh, h_ht, A, CLaw,conf):
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
    print("Configuration %.0f de/da = %.4f "%(conf,de_da))
    return de_da

def lh(xacfwd,xacrear):
    return abs(xacfwd-xacrear)

def cg_range_conf_1_2(conf):
    conf = conf
    def values_conf_1_2(conf):
        datafile = open(os.path.join(root_path, "data/inputs_config_%.0f.json" % (conf)), "r")
        data = json.load(datafile)
        datafile.close()
        lfus = data["Structures"]["l_fus"]
        hfus = data["Structures"]["h_fus"]
        wfus = data["Structures"]["w_fus"]
        CD0 = data["Aerodynamics"]["CD0"]
        e = data["Aerodynamics"]["e"]
        Afwd = data["Aerodynamics"]["AR"] * 2
        Sweep_c4_fwd = data["Aerodynamics"]["Sweep_front"]
        Sweep_c4_rear = data["Aerodynamics"]["Sweep_back"]
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
        c_fwd = data["Aerodynamics"]["MAC1"]
        c_rear = data["Aerodynamics"]["MAC2"]
        cr =  data["Aerodynamics"]["c_r"]
        xacfwd = 0.25 * c_fwd
        xacrear = lfus - (1 - 0.25) * c_rear
        values = [CL_max_fwd, CL_max_rear, Cm_ac_fwd, Cm_ac_rear, CLa_fwd, CLa_rear, S_fwd, S_rear, Afwd, c_fwd, c_rear,
                  b_fwd, b_rear, xacfwd, xacrear, e, CD0, lfus, hfus, wfus,Sweep_c4_fwd,Sweep_c4_rear,cr]
        return values
    values = values_conf_1_2(conf)
    CLfwd,CLrear,Cmacfwd,Cmacrear,CLafwd, CLarear,Sfwd,Srear,Afwd,cfwd,crear,b_fwd,b_rear,\
    xacfwd,xacrear,e, CD0,lfus,hfus,wfus,Sweep_c4_fwd,Sweep_c4_rear,cr = values
    print("Values: ",values)
    CDafwd = 2*CLafwd*CLfwd/(np.pi*Afwd*e)
    CDarear = 2*CLarear*CLrear/(np.pi*Afwd*e)
    deda = deps_da(Sweep_c4_fwd, b_fwd,lh(xacfwd,xacrear), hfus, Afwd, CLafwd,conf)
    xacfwd_stab = 0.25*cfwd
    xacfwd_control = 0.25 * cfwd
    o = CLafwd*xacfwd_stab+CLarear*(lfus-0.75*cfwd)*Srear/Sfwd*(1-deda)
    p =CLafwd*1+CLarear*1*Srear/Sfwd*(1-deda)
    xcg_max = o/p
    CLrear = 0.8*CLfwd
    oo = CLfwd * xacfwd_control + CLrear * xacrear * Srear / Sfwd -Cmacfwd-Cmacrear*Srear/Sfwd*crear
    pp = CLfwd * 1 + CLrear * 1 * Srear / Sfwd
    xcg_min = oo/pp
    print("Configuration %.0f range: %.4f < x_cg < %.4f"%(conf,xcg_min,xcg_max))
    print("CG Range =%.3f" % (abs(xcg_max - xcg_min)))
    return abs(xcg_max-xcg_min)


# def cg_range_conf_2(values=values_conf_2(),deda=deps_da(L_c4,values_conf_2()[11],lh(xacfwd,xacrear),h_ht = 1.6,A=values_conf_2()[8],CLaw=values_conf_2()[4])):
#     CLfwd,CLrear,Cmacfwd,Cmacrear,CLafwd, CLarear,Sfwd,Srear,Afwd,cfwd,crear,b_fwd,b_rear = values
#     lfus = 4
#     hfus = 1.6
#     xacfwd_stab = 0.25*cfwd
#     xacfwd_control = 0.25 * cfwd
#     o = CLafwd*xacfwd_stab+CLarear*(lfus-0.75*crear)*Srear/Sfwd*(1-deda)
#     p =CLafwd*1+CLarear*1*Srear/Sfwd*(1-deda)
#     xcg_max = o/p
#     oo = CLfwd * xacfwd_control + CLrear * (lfus-0.75*crear) * Srear / Sfwd -Cmacfwd-Cmacrear*Srear/Sfwd*crear
#     pp = CLfwd * 1 + CLrear * 1 * Srear / Sfwd
#     xcg_min = oo/pp
#     print("Configuration 2 range: %.4f < x_cg < %.4f"%(xcg_min,xcg_max))
#     print("CG Range =%.3f" % (abs(xcg_max - xcg_min)))
#     return abs(xcg_max-xcg_min)

def cg_range_conf_3(values=values_conf_3(),eta=5):
    CLfwd, CLrear, Cmacfwd, Cmacrear, CLafwd, CLarear, Sfwd, Srear, Afwd, cfwd, bfwd,e,CD0 = values
    lfus = 4
    hfus = 1.6
    xacfwd_stab = lfus/2-cfwd/2 + 0.24*cfwd
    xacfwd_control = lfus/2-cfwd/2 +  0.24*cfwd
    CD = CD0 + CLfwd**2/(np.pi*Afwd*e)
    zaccg = eta/100*hfus
    xcg_max = xacfwd_stab
    xcg_min = xacfwd_control-Cmacfwd/CLfwd*cfwd-CD/CLfwd*zaccg
    print("Configuration 3 range: %.4f < x_cg < %.4f"%(xcg_min,xcg_max))
    print("CG Range =%.3f"%(abs(xcg_max-xcg_min)))
    return abs(xcg_max-xcg_min)

cg1 = cg_range_conf_1_2(1)
cg2 = cg_range_conf_1_2(2)
cg3 = cg_range_conf_3()
cg3_1 = cg_range_conf_3(eta=0)

def sensitivity(in1,in2):
    return (in1-in2)/in1*100

print("Initial sensitivity analysis on CG range:", sensitivity(cg3,cg3_1))