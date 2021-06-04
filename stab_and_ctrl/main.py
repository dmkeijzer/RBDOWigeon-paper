import numpy as np
from stab_and_ctrl.Scissor_Plots import Wing_placement_sizing
from stab_and_ctrl.Vertical_tail_sizing import VT_sizing
from stab_and_ctrl.Aileron_Sizing import Control_surface
from stab_and_ctrl.Elevator_sizing import Elevator_sizing
import constants as const
from matplotlib import pyplot as plt

# example values based on inputs_config_1.json
W = 18315.27
h = 0
lfus = 7.2
hfus = 1.705
wfus = 1.38
xcg = 3.0
V0 = 52
Vstall = 40
M0 = V0 / np.sqrt(const.gamma * const.R * 288.15)
CD0 = 0.03254
theta0 = 0
CLfwd = 1.781
CLrear = 1.737
CLafwd = 5.1685
Clafwd =6.245
Clarear=Clafwd
Cd0fwd = 0.00347
Cd0rear = Cd0fwd
CLarear = CLafwd
Cmacfwd = -0.0645
Cmacrear = -0.0645
S = 10.5
Sfwd = 1/2*S
Srear = S-Sfwd
Afwd = 7*2
Arear = 7*2
Gamma = 0
Lambda_c2_fwd = 0
Lambda_c2_rear = 0
cfwd = 0.65
crear = 0.65
bfwd = np.sqrt(Sfwd * Afwd)
brear = np.sqrt(Srear * Arear)
efwd = 1.1302
erear = 1.1302
taper = 0.4
n_rot_f = 6
n_rot_r = 6
rot_y_range_f = [0.5 * bfwd * 0.1, 0.5 * bfwd * 0.9]
rot_y_range_r = [0.5 * brear * 0.1, 0.5 * brear * 0.9]
K = 4959.86
ku = 0.1
Zcg = 0.7

d = 1.5
wps = Wing_placement_sizing(W,  lfus, hfus, wfus, V0, M0, CD0, CLfwd,
                 CLrear, CLafwd, CLarear, Cmacfwd, Cmacrear, Sfwd, Srear,
                 Afwd, Arear, Gamma, Lambda_c2_fwd, Lambda_c2_rear, cfwd,
                 crear, bfwd, brear, efwd, erear, taper, n_rot_f, n_rot_r,
                 rot_y_range_f, rot_y_range_r, K, ku,Zcg,d)

vt_sizing = VT_sizing(W,h,xcg,lfus,hfus,wfus,V0,Vstall,M0,CD0,theta0,
                      CLfwd,CLrear,CLafwd,CLarear,
                      Cmacfwd,Cmacrear,Sfwd,Srear,Afwd,Arear,0,0,cfwd,crear,bfwd,brear,taper)

elevon = Control_surface(V0,Vstall,CLfwd,CLrear,CLafwd,CLarear,Clafwd,Clarear,Cd0fwd,Cd0rear,
                         Sfwd,Srear,Afwd,Arear,cfwd,crear,bfwd,brear,taper)
elevator_effect = 1.4
dx = 0.1

#### Plotting Vertical Tail ####
nE = 16
Tt0 = 7000
yE = bfwd/2
lv = lfus-xcg
brbv = np.linspace(0.75,1,150)
crcv = np.linspace(0.1,0.4,150)
# for i in range(len(brbv)):
#     for j in crcv:
#         print("For a br/bv = %.3f and cr/cv = %.3f "%(brbv[i],j))
#         vt_br = vt_sizing.final_VT_rudder(nE,Tt0,yE,lv,br_bv=brbv[i],cr_cv=j)
print("Sv = ",vt_sizing.VT_stability(lv))
vt_sizing.plotting(nE,Tt0,yE,lv,br_bv=brbv,cr_cv=crcv)
vt_sizing.plotting(nE,Tt0,yE,lv,br_bv=0.85,cr_cv=0.4)

#### Plotting Aileron ####
b1 = 60
b2 =np.linspace(b1,100,150)
Sa_S = np.linspace(0.05,0.20,150)
# elevon.plotting(0.15,b1,b2)
elevon.plotting(Sa_S,b1,b2,False)

#### Plotting Elevator ####
elevator = Elevator_sizing(W,h,xcg,lfus,hfus,wfus,V0,Vstall,M0,CD0,theta0,CLfwd,CLrear,CLafwd,CLarear,
                           Cmacfwd,Cmacrear,Sfwd,Srear,Afwd,Arear,0,0,cfwd,crear,bfwd,brear,taper,dCLfwd=0.4*CLfwd)
beb = np.linspace(10,100,150)
SeS = np.linspace(0.1,0.4,150)
de_max = 15
elevator.plotting(SeS,beb,de_max)
# xcg_middle = (0.2187 + 3.3439) / 2
# wps.hover_calc.fail_rotors([0, 3, 5, 6])
# xcgs = np.linspace(xcg_middle - 2, xcg_middle + 2, 100)
# acais = []
# for xcg in xcgs:
#     acais.append((wps.hover_calc.acai([xcg, 0])))
# plt.plot(xcgs, acais)
# plt.axvline(xcg_middle)
# plt.axhline(0)
# plt.title("[0, 3, 5, 6]")
# plt.figure()
#
# wps.hover_calc.fail_rotors([1, 2, 4, 7])
# acais = []
# for xcg in xcgs:
#     acais.append((wps.hover_calc.acai([xcg, 0])))
# plt.plot(xcgs, acais)
# plt.axvline(xcg_middle)
# plt.axhline(0)
# plt.title("[1, 2, 4, 7]")
# plt.show()

wps.plotting(0, lfus, dx, elevator_effect, d)
