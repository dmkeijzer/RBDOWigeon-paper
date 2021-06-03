import numpy as np
from stab_and_ctrl.Scissor_Plots import Wing_placement_sizing
from stab_and_ctrl.Vertical_tail_sizing import VT_sizing
import constants as const
from matplotlib import pyplot as plt

# example values based on inputs_config_1.json
W = 18315.27
h = 0
lfus = 4
hfus = 1.6
wfus = 1.3
xcg = 1.680
V0 = 52
Vstall = 40
M0 = V0 / np.sqrt(const.gamma * const.R * 288.15)
CD0 = 0.03254
theta0 = 0
CLfwd = 1.781
CLrear = 1.737
CLafwd = 5.1685
CLarear = CLafwd
Cmacfwd = -0.0645
Cmacrear = -0.0645
Sfwd = 5.25
Srear = 5.25
Afwd = 7
Arear = 7
Gamma = 0
Lambda_c2_fwd = 0
Lambda_c2_rear = 0
cfwd = 0.8748
crear = 0.8748
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


wps = Wing_placement_sizing(W, h, lfus, hfus, wfus, V0, M0, CD0, theta0, CLfwd,
                 CLrear, CLafwd, CLarear, Cmacfwd, Cmacrear, Sfwd, Srear,
                 Afwd, Arear, Gamma, Lambda_c2_fwd, Lambda_c2_rear, cfwd,
                 crear, bfwd, brear, efwd, erear, taper, n_rot_f, n_rot_r,
                 rot_y_range_f, rot_y_range_r, K, ku)

vt_sizing = VT_sizing(W,h,xcg,lfus,hfus,wfus,V0,Vstall,M0,CD0,theta0,
                      CLfwd,CLrear,CLafwd,CLarear,
                      Cmacfwd,Cmacrear,Sfwd,Srear,Afwd,Arear,0,0,cfwd,crear,bfwd,brear,taper)

elevator_effect = 1.4
d = 0
dx = 0.1

nE = 16
Tt0 = 4000
yE = bfwd/2
lv = lfus-xcg
vt_sizing.plotting(nE,Tt0,yE,lv,br_bv=0.87,cr_cv=0.4)
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
