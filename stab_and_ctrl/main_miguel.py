import numpy as np
# from stab_and_ctrl.Scissor_Plots import Wing_placement_sizing
from stab_and_ctrl.Vertical_tail_sizing import VT_sizing
from stab_and_ctrl.Aileron_Sizing import Control_surface
from stab_and_ctrl.Elevator_sizing import Elevator_sizing
from stab_and_ctrl.Stability_derivatives import Stab_Derivatives
from structures.Weight import *
from stab_and_ctrl.Model_cruise import Aircraft
import constants as const
from matplotlib import pyplot as plt

# example values based on inputs_config_1.json
W = 2950*9.80665
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
alpha0 = 0
q0 = 0
b0 = 0
phi0 = 0
p0 = 0
r0 = 0
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
S = Srear+Sfwd
Afwd = 9*1
Arear = 9
Gamma = 0
Lambda_c4_fwd = 0.0*np.pi/180
Lambda_c4_rear = 0.0*np.pi/180
cfwd = 1.014129367767935
crear = 1.014129367767935
c = Srear/S*crear+Sfwd/S*cfwd
bfwd = np.sqrt(Sfwd * Afwd)
brear = np.sqrt(Srear * Arear)
b = max(bfwd,brear)
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
# wps = Wing_placement_sizing(W,h, lfus, hfus, wfus, V0, CD0fwd, CLfwd,
#                  CLrear,CLdesfwd,CLdesrear, Clafwd,Clarear,Cmacfwd, Cmacrear, Sfwd, Srear,
#                  Afwd, Arear, Gamma, Lambda_c4_fwd, Lambda_c4_rear, cfwd,
#                  crear, bfwd, brear, efwd, erear, taper, n_rot_f, n_rot_r,
#                  rot_y_range_f, rot_y_range_r, K, ku,Zcg,d,dy,Pbr,1)


aileron = Control_surface(V0,Vstall,CLfwd,CLrear,CLafwd,CLarear,Clafwd,Clarear,Cd0fwd,Cd0rear,
                         Sfwd,Srear,Afwd,Arear,cfwd,crear,bfwd,brear,taper)
elevator_effect = 1.4
dx = 0.1

#### Plotting Vertical Tail ####
nE = 12
Tt0 = 4500
yE = bfwd/2
lv = lfus-xcg
brbv = np.linspace(0.75,1,150)
crcv = np.linspace(0.1,0.4,150)
# for i in range(len(brbv)):
#     for j in crcv:
#         print("For a br/bv = %.3f and cr/cv = %.3f "%(brbv[i],j))
#         vt_br = vt_sizing.final_VT_rudder(nE,Tt0,yE,lv,br_bv=brbv[i],cr_cv=j)
# print("Sv = ",vt_sizing.VT_stability(lv))

ARv = 1.5
sweepTE =25.0*np.pi/180
vt_sizing = VT_sizing(W,h,xcg,lfus,hfus,wfus,V0,Vstall,CD0,CLdesfwd,CLdesrear,CLafwd,CLarear,
                 Sfwd,Srear,Afwd,Arear,Lambda_c4_fwd,Lambda_c4_rear,cfwd,crear,bfwd,brear,taper,ARv,sweepTE)
if isinstance(ARv,(float,int)) and isinstance(sweepTE,(float,int)):
    vt_sizing.plotting(nE,Tt0,yE,br_bv=brbv,cr_cv=crcv,ARv=ARv,sweepTE=sweepTE)
    vt_sizing.plotting(nE, Tt0, yE, br_bv=0.85, cr_cv=0.4,ARv=ARv,sweepTE=sweepTE)
    Sv = vt_sizing.final_VT_rudder(nE,Tt0,yE,br_bv=0.85,cr_cv=0.4,ARv=ARv,sweepTE=sweepTE)[0]
    Svstab = vt_sizing.VT_stability(ARv,sweepTE)
    Svctrl = vt_sizing.VT_controllability(nE,Tt0,yE,br_bv=0.85, cr_cv=0.4,ARv=ARv,sweepTE=sweepTE)
    bv =  vt_sizing.final_VT_rudder(nE,Tt0,yE,br_bv=0.85,cr_cv=0.4,ARv=ARv,sweepTE=sweepTE)[3]
    print("Stability outside: Sv = ",Svstab)
    print("Controllability outside: Sv = ", Svctrl)
    print("Final: Sv, bv=", Sv,bv)
else:
    vt_sizing.plotting(nE,Tt0,yE,br_bv=0.85,cr_cv=0.4,ARv=ARv,sweepTE=sweepTE)

#### Plotting Aileron ####
b1 = 55
b2 =np.linspace(b1,100,150)
Sa_S = np.linspace(0.05,0.20,150)
# elevon.plotting(0.15,b1,b2)
aileron.plotting(Sa_S,b1,b2,True)
aileron.plotting(Sa_S=0.145,b1=b1,b2=99.0,rear=True)

#### Plotting Elevator ####
elevator = Elevator_sizing(W,h,xcg,lfus,hfus,wfus,V0,Vstall,CD0,theta0,CLfwd,CLrear,CLafwd,CLarear,
                           Cmacfwd,Cmacrear,Sfwd,Srear,Afwd,Arear,0,0,cfwd,crear,bfwd,brear,taper,dCLfwd=0.4*CLfwd)
beb = np.linspace(10,100,150)
SeS = np.linspace(0.1,0.4,150)
de_max = 17.5
elevator.plotting(SeS,beb,de_max)

# wps.plotting(0, lfus, dx, elevator_effect, d)

CL0 = 0.82
A = Afwd/2
CD0_a = CD0+CL0**2/(np.pi*A*e)


n_ult = 3.2 * 1.5  # 3.2 is the max we found, 1.5 is the safety factor
Pmax = 15.25  # this is defined as maximum perimeter in Roskam, so i took top down view of the fuselage perimeter
lf = 7.2  # length of fuselage
m_pax = 95  # average mass of a passenger according to Google
n_prop = 16  # number of engines
n_pax = 5  # number of passengers (pilot included)
pos_fus = 3.6  # fuselage centre of mass away from the nose
pos_lgear = 3.6  # landing gear position away from the nose
pos_frontwing, pos_backwing = 0.2, 7  # positions of the wings away from the nose
m_prop = [30] * 16  # list of mass of engines (so 30 kg per engine with nacelle and propeller)
pos_prop = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0,
            7.0]  # 8 on front wing and 8 on back wing
wing = Wing(W/9.80665, Sfwd, Srear, n_ult, Afwd, [pos_frontwing, pos_backwing])
fuselage = Fuselage(W/9.80665, Pmax, lfus, n_pax, pos_fus)
lgear = LandingGear(W/9.80665, pos_lgear)
props = Propulsion(n_prop, m_prop, pos_prop)
weight = Weight(m_pax, wing, fuselage, lgear, props, cargo_m=85, cargo_pos=6, battery_m=400, battery_pos=3.6,
                p_pax=[1.5, 3, 3, 4.2, 4.2])

Ixx, Iyy, Izz, Ixz = weight.MMI()

if isinstance(ARv,float) and isinstance(sweepTE,float):
    stability_derivatives = Stab_Derivatives(W,h,lfus,hfus,wfus, d,dy,xcg,Zcg,cfwd,crear,Afwd,Arear,Vstall,
                     V0,Tt0,CLdesfwd,CLdesrear,CD0_a,CL0,theta0,alpha0,
                     Clafwd,Clarear, Cd0fwd, Cd0rear, CLafwd,CLarear,Sfwd,Srear,0,-4*np.pi/180,
                     efwd,erear,Lambda_c4_fwd,Lambda_c4_rear,taper,0.4,
                     bv,Sv,ARv,sweepTE,Pbr,CD0,eta_rear=0.85,eta_v=0.9)
    print("q-derivatives:",stability_derivatives.q_derivatives())
    print("alpha-derivatives:",stability_derivatives.alpha_derivatives())
    print("u-derivatives:",stability_derivatives.u_derivatives())
    print("alpha_dot derivatives:",stability_derivatives.alpha_dot_derivatives())
    print("p-derivatives:",stability_derivatives.p_derivatives())
    print("r-derivatives:", stability_derivatives.r_derivatives())
    print("beta-derivatives:", stability_derivatives.beta_derivatives())
    print("-----Control Derivatives----------")
    print("de-derivatives:", stability_derivatives.de_derivatives(Se_S=0.15,be_b=0.99))
    print("da-derivatives:",stability_derivatives.da_derivatives(Sa_S=0.145,b1=55,b2=99.0))
    print("dr-derivatives:", stability_derivatives.dr_derivatives(cr_cv=0.4,br_bv=0.85))
    print("Kyy2 = %.5f"%(Iyy/(W/9.80665*c**2)))
    print("Iyy = %.5f "%(Iyy))
    stability_derivatives.asym_stability_req(Ixx,Izz,Ixz,0.085,60,97.5,0.4,0.85)
    C_X, C_Z, C_m, C_Y, C_l,C_n = \
        stability_derivatives.return_stab_derivatives(Se_S = 0.15,be_b = 0.99,
                                                      Sa_S=0.145,b1=b1,b2=99.0,cr_cv=0.4,br_bv=0.85)
    aircraft = Aircraft(W, h, S, c, b, V0, theta0, alpha0, q0, b0, phi0, p0, r0, Iyy, Ixx, Izz, Ixz, C_X, C_Z,C_m, CL0,
                        C_Y, C_l, C_n)
    aircraft.plot_results(V0)


