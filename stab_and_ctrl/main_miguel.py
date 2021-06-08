import numpy as np
from stab_and_ctrl.Scissor_Plots import Wing_placement_sizing
from stab_and_ctrl.Vertical_tail_sizing import VT_sizing
from stab_and_ctrl.Aileron_Sizing import Control_surface
from stab_and_ctrl.Elevator_sizing import Elevator_sizing
from stab_and_ctrl.Stability_derivatives import Stab_Derivatives
import constants as const
from matplotlib import pyplot as plt

# example values based on inputs_config_1.json
W = 2939.949692*9.80665
h = 1000
lfus = 7.2
hfus = 1.705
wfus = 1.38
xcg = 3.0
V0 = 64.72389428906716
Vstall = 40
Pbr = 110024/1.2 * 0.9 /12
# M0 = V0 / np.sqrt(const.gamma * const.R * 288.15)
CD0 = 0.03254
theta0 = 0
CLfwd = 1.44333
CLrear = 1.44333
CLdesfwd = 0.7382799
CLdesrear = 0.7382799
CLafwd = 5.1685
Clafwd = 6.1879
Clarear=Clafwd
Cd0fwd = 0.00347 # Airfoil drag coefficient [-]
Cd0rear = Cd0fwd
CD0fwd = 0.00822 # Wing drag coefficient [-]
CD0rear = CD0fwd
CLarear = CLafwd
Cmacfwd = -0.0645
Cmacrear = -0.0645
Sfwd = 8.417113787320769
Srear = 8.417113787320769
Afwd = 9*1
Arear = 9
Gamma = 0
Lambda_c4_fwd = 0.0*np.pi/180
Lambda_c4_rear = 0.0*np.pi/180
cfwd = 1.014129367767935
crear = 1.014129367767935
bfwd = np.sqrt(Sfwd * Afwd)
brear = np.sqrt(Srear * Arear)
e = 1.1302
efwd = 0.958
erear = 0.958
taper = 0.45
n_rot_f = 6
n_rot_r = 6
rot_y_range_f = [0.5 * bfwd * 0.1, 0.5 * bfwd * 0.9]
rot_y_range_r = [0.5 * brear * 0.1, 0.5 * brear * 0.9]
K = 4959.86
ku = 0.1
Zcg = 0.70

d = 0
dy = 0.2
wps = Wing_placement_sizing(W,h, lfus, hfus, wfus, V0, CD0fwd, CLfwd,
                 CLrear,CLdesfwd,CLdesrear, Clafwd,Clarear,Cmacfwd, Cmacrear, Sfwd, Srear,
                 Afwd, Arear, Gamma, Lambda_c4_fwd, Lambda_c4_rear, cfwd,
                 crear, bfwd, brear, efwd, erear, taper, n_rot_f, n_rot_r,
                 rot_y_range_f, rot_y_range_r, K, ku,Zcg,d,dy,Pbr,1)


aileron = Control_surface(V0,Vstall,CLfwd,CLrear,CLafwd,CLarear,Clafwd,Clarear,Cd0fwd,Cd0rear,
                         Sfwd,Srear,Afwd,Arear,cfwd,crear,bfwd,brear,taper)
elevator_effect = 1.4
dx = 0.1

#### Plotting Vertical Tail ####
nE = 12
Tt0 = 1000
yE = bfwd/2
lv = lfus-xcg
brbv = np.linspace(0.75,1,150)
crcv = np.linspace(0.1,0.4,150)
# for i in range(len(brbv)):
#     for j in crcv:
#         print("For a br/bv = %.3f and cr/cv = %.3f "%(brbv[i],j))
#         vt_br = vt_sizing.final_VT_rudder(nE,Tt0,yE,lv,br_bv=brbv[i],cr_cv=j)
# print("Sv = ",vt_sizing.VT_stability(lv))

ARv = 1.25
sweepTE = 25
vt_sizing = VT_sizing(W,h,xcg,lfus,hfus,wfus,V0,Vstall,CD0,CLdesfwd,CLdesrear,CLafwd,CLarear,
                 Sfwd,Srear,Afwd,Arear,Lambda_c4_fwd,Lambda_c4_rear,cfwd,crear,bfwd,brear,taper,ARv,sweepTE)
if isinstance(ARv,float):
    vt_sizing.plotting(nE,Tt0,yE,br_bv=brbv,cr_cv=crcv)
    # print(vt_sizing.plotting(nE, Tt0, yE, lv, br_bv=0.85, cr_cv=0.3))
    vt_sizing.plotting(nE, Tt0, yE, br_bv=0.85, cr_cv=0.4)
    Sv = vt_sizing.final_VT_rudder(nE,Tt0,yE,br_bv=0.85,cr_cv=0.4)[0]
    bv =  vt_sizing.final_VT_rudder(nE,Tt0,yE,br_bv=0.85,cr_cv=0.4)[3]
    print("Sv, bv=", Sv,bv)
    # print(Sv)
else:
    vt_sizing.plotting(nE,Tt0,yE,lv,br_bv=0.85,cr_cv=0.3)
# vt_sizing.plotting(nE,Tt0,yE,lv,br_bv=0.65,cr_cv=0.4)
# vt_sizing.plotting(nE,Tt0,yE,lv,br_bv=0.55,cr_cv=0.4)

#### Plotting Aileron ####
b1 = 60
b2 =np.linspace(b1,100,150)
Sa_S = np.linspace(0.05,0.20,150)
# elevon.plotting(0.15,b1,b2)
aileron.plotting(Sa_S,b1,b2,True)
aileron.plotting(Sa_S=0.085,b1=b1,b2=97.5,rear=True)

#### Plotting Elevator ####
elevator = Elevator_sizing(W,h,xcg,lfus,hfus,wfus,V0,Vstall,CD0,theta0,CLfwd,CLrear,CLafwd,CLarear,
                           Cmacfwd,Cmacrear,Sfwd,Srear,Afwd,Arear,0,0,cfwd,crear,bfwd,brear,taper,dCLfwd=0.4*CLfwd)
beb = np.linspace(10,100,150)
SeS = np.linspace(0.1,0.4,150)
de_max = 17.5
elevator.plotting(SeS,beb,de_max)

wps.plotting(0, lfus, dx, elevator_effect, d)

CL0 = 0.82
A = Afwd/2
CD0_a = CD0+CL0**2/(np.pi*A*e)
stability_derivatives = Stab_Derivatives(W,h,lfus,hfus,wfus, d,dy,xcg,Zcg,cfwd,crear,Afwd,Arear,Vstall,
                 V0,Tt0,CLdesfwd,CLdesrear,CD0_a,CL0,2*np.pi/180,0,
                 Clafwd,Clarear, Cd0fwd, Cd0rear, CLafwd,CLarear,Sfwd,Srear,5*np.pi/180/6,0,
                 efwd,erear,Lambda_c4_fwd,Lambda_c4_rear,taper,0.4,
                 bv,Sv,ARv,Pbr,CD0,eta_rear=1,eta_v=1)
print(stability_derivatives.q_derivatives())
