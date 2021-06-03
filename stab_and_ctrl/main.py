import numpy as np
from stab_and_ctrl.Scissor_Plots import Wing_placement_sizing
from stab_and_ctrl.Vertical_tail_sizing import VT_sizing
from stab_and_ctrl.loading_diagram import CgCalculator
from stab_and_ctrl.landing_gear_placement import LandingGearCalc
import constants as const
from matplotlib import pyplot as plt

# example values based on inputs_config_1.json
W = 28315.27
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

mbat = 400
mwing = 400
mengine = 25
mtom = W / 9.80665
mcargo = 4 * 7
mpax = 88
mpil = 88
mfus = mtom - mbat - 2 * mwing - (n_rot_f + n_rot_r) * mengine - mcargo - 4 * mpax - mpil

x_pil = 1.9
x_pax = [2.9, 4.3]
x_cargo = 5.15
x_bat = 2.9
x_wf = 1.9
x_wr = 5.15
x_fus = 2.6

y_pax = 0.3

z_fus = 0.7
z_bat = 0.4
z_cargo = 0.9
z_pax = 0.9
z_pil = 0.9
z_wf = 0.5
z_wr = 1.4

max_tw = 5
x_ng_min = 0.7
y_max_rotor = bfwd * 0.9
gamma = 0
z_rotor_line_root = z_wf + 0.1
rotor_rad = 0.5
fus_back_bottom = [x_cargo, 0]
fus_back_top = [7.5, 2]
x_cg_margin = 0.1
theta = np.deg2rad(15)
phi = np.deg2rad(7)
psi = np.deg2rad(55)
min_ng_load_frac = 0.08

cgcalc = CgCalculator(mwing + mengine * n_rot_f, mwing + mengine * n_rot_r,
                      mfus, mbat, mcargo, mpax, mpil, [x_fus, 0, 0.5],
                      [x_bat, 0, z_bat], [x_cargo, 0, z_cargo],
                      [[x_pax[0], -y_pax, z_pax], [x_pax[0], y_pax, z_pax],
                       [x_pax[1], -y_pax, z_pax], [x_pax[1], y_pax, z_pax]],
                      [x_pil, 0, z_pil])
x_range, y_range, z_range = cgcalc.calc_cg_range([x_wf, z_wf], [x_wr, z_wr])

lgcalc = LandingGearCalc(max_tw, x_ng_min, y_max_rotor, gamma,
                         z_rotor_line_root, rotor_rad, fus_back_bottom,
                         fus_back_top)
x_ng, x_mlg, tw, h_mlg = lgcalc.optimum_placement(x_range, x_cg_margin,
                                                  z_range[1], theta, phi, psi,
                                                  min_ng_load_frac)
lgcalc.plot_lg(x_range, x_cg_margin, z_range[1], x_ng, x_mlg, tw, h_mlg)
plt.show()


# wps = Wing_placement_sizing(W, h, lfus, hfus, wfus, V0, M0, CD0, theta0, CLfwd,
#                  CLrear, CLafwd, CLarear, Cmacfwd, Cmacrear, Sfwd, Srear,
#                  Afwd, Arear, Gamma, Lambda_c2_fwd, Lambda_c2_rear, cfwd,
#                  crear, bfwd, brear, efwd, erear, taper, n_rot_f, n_rot_r,
#                  rot_y_range_f, rot_y_range_r, K, ku)
#
# vt_sizing = VT_sizing(W,h,xcg,lfus,hfus,wfus,V0,Vstall,M0,CD0,theta0,
#                       CLfwd,CLrear,CLafwd,CLarear,
#                       Cmacfwd,Cmacrear,Sfwd,Srear,Afwd,Arear,0,0,cfwd,crear,bfwd,brear,taper)
#
# elevator_effect = 1.4
# d = 0
# dx = 0.1
#
# nE = 16
# Tt0 = 4000
# yE = bfwd/2
# lv = lfus-xcg
# vt_sizing.plotting(nE,Tt0,yE,lv,br_bv=0.87,cr_cv=0.4)
# # xcg_middle = (0.2187 + 3.3439) / 2
# # wps.hover_calc.fail_rotors([0, 3, 5, 6])
# # xcgs = np.linspace(xcg_middle - 2, xcg_middle + 2, 100)
# # acais = []
# # for xcg in xcgs:
# #     acais.append((wps.hover_calc.acai([xcg, 0])))
# # plt.plot(xcgs, acais)
# # plt.axvline(xcg_middle)
# # plt.axhline(0)
# # plt.title("[0, 3, 5, 6]")
# # plt.figure()
# #
# # wps.hover_calc.fail_rotors([1, 2, 4, 7])
# # acais = []
# # for xcg in xcgs:
# #     acais.append((wps.hover_calc.acai([xcg, 0])))
# # plt.plot(xcgs, acais)
# # plt.axvline(xcg_middle)
# # plt.axhline(0)
# # plt.title("[1, 2, 4, 7]")
# # plt.show()
#
# wps.plotting(0, lfus, dx, elevator_effect, d)
