import sys

import numpy as np

sys.path.append("../")
from Preliminary_Lift.Airfoil import *
from Preliminary_Lift.Drag import *
from Aero_tools import ISA
from Preliminary_Lift.Wing_design import *
from Preliminary_Lift.Airfoil_analysis import airfoil_stats
import os
import json
import matplotlib.pyplot as plt
from Preliminary_Lift.LLTtest2 import LLT1wing , LLT2wings, downwash, downwash_upwash, downwash_fore
from scipy.special import ellipk, ellipe
from scipy.interpolate import interp1d
import numpy as np
root_path = os.path.join(os.getcwd(), os.pardir)

datafile = open(os.path.join(root_path, "data/inputs_config_1.json"), "r")
data = json.load(datafile)
datafile.close()
FP = data["Flight performance"]
STR = data["Structures"]
#AR = 3.75
AR1 = 7.25
AR2=  7.85

W = 3144 #STR["MTOW"] #[N]
Vcruise = 70#FP["V_cruise"] #[m/s]
Wing_loading = FP["WS"]

#Cruise conditions
h = 1000 # cruise height[m]
atm_flight  = ISA(h)
rho = atm_flight.density() # cte.rho
mu = atm_flight.viscosity_dyn()
a = atm_flight.soundspeed()
M = Mach(Vcruise,a)
print("Mach",M)
#Wing planform
S_ref = 26.9148 #W/Wing_loading #[m**2] PLACEHOLDER


# For double wing
s1=0.454545454545

s2=1-s1
b = np.sqrt(0.5*(AR1*s1+s2*AR2)*S_ref) # Due to reqs
#Sweep
sweepc41= 0
sweepc42=0

#Other paramters
b_d = b  # fixed due to span limitations
h_d = 1.4  #  Vertical gap between wings. Based on fuselage size
l_h = 7 # Horizontal gap between wings. Based on fuselgae size
i1 = -0.0

#Fuselage dimensions
l1 = 2.5
l2 = 2.5
l3 = 2.7
w_max = 1.38
h_max = 1.70
d_eq = np.sqrt(h_max*w_max)
#Winglets
h_wl1 =0.5
h_wl2 = 0.5
k_wl = 2.0
#7 9 0.45454545454545453 0 0.5454545454545454 0 0.1961932635918894 18.379085418840855 7.0 1.4 1.38 0.5 0.5 2.0 0
Wing_params =  wing_design(AR1, AR2, s1,sweepc41,s2,sweepc42,M,S_ref, l_h,h_d,w_max,h_wl1,h_wl2, k_wl, i1)
b = Wing_params.wing_planform_double()[1][0]
C_r = Wing_params.wing_planform_double()[1][1]
C_t = Wing_params.wing_planform_double()[1][2]

MAC = Wing_params.wing_planform_double()[1][3]

SweepLE = Wing_params.sweep_atx(0)[0]
deda = 0.25 #downwash(Wing_params.wing_planform_double()[0][0] , Wing_params.AR1,
              #  Wing_params.wing_planform_double()[0][1], Wing_params.wing_planform_double()[0][2], Wing_params.sweepc41, 5, Wing_params.h_ht,
              #  Wing_params.lh, Wing_params.wing_planform_double()[1][0] ,
              #  Wing_params.wing_planform_double()[0][1], Wing_params.wing_planform_double()[0][2], Wing_params.sweepc41,
              #  70)  # deps_da(self.sweepc41, wg[0][0], self.lh, self.h_ht, self.AR_i, slope1)


Slope1 = Wing_params.liftslope(deda)[1]

CLmax = Wing_params.CLmax_s(deda)

#For Drag estimation
k = 0.634 * 10**(-5) # Smooth paint from adsee 2 L2
flamf =0.1  # From ADSEE 2 L2 GA aircraft
IF_f = 1    # From ADSEE 2 L2
IF_w = 1.1   # From ADSEE 2 L2
IF_v = 1.04 #From ADSEE 2 L2
flamw = 0.35 # From ADSEE 2 L2 GA aircraft
u = 8.43 *np.pi/180 # fuselage upsweep
Abase = 0
# Airfoil
airfoil = airfoil_stats()
tc = 0.12 #NACA0012 for winglets and Vtail
tca = 0.17
xcm = 0.3 #NACA0012 for winglets and Vtail
CL_CDmin = airfoil[2]
CL_lst = np.arange(-0.5,1.7,0.100)
#Other parameters
S_v = 0.6
S_t = 0


Drag = componentdrag('tandem',S_ref,l1,l2,l3,d_eq,Vcruise,rho,MAC,AR1,AR2,Mach(Vcruise,a),k,flamf,flamw,mu,tc,xcm,0,SweepLE,u,0,h_d,IF_f,IF_w, IF_v, CL_CDmin,Abase, S_v, s1, s2, h_wl1, h_wl2, k_wl)


CL_design = Drag.CL_des()
Cd_des= Drag.Cd_w(CL_design[0])
Swet_f = Drag.Swet_f()

Rey = Re(rho, Vcruise,MAC, mu)
print("Re", Rey)
#Stall
stall = Wing_params.CLmax_s(deda)
CLmax = stall[0]
print("CL_des", CL_design)
CDs = Drag.CD(CLmax)
CDs_f = Drag.CD0_f
CDs_w = CDs - CDs_f
#Post stall
Afus = np.pi *d_eq**2/4
post_stall = Wing_params.post_stall_lift_drag(tca, CDs, CDs_f, Afus, deda)

alpha_lst = np.arange(-3,89,0.1)
Cl_alpha_curve = Wing_params.CLa(tca, CDs, CDs_f, Afus, alpha_lst, deda)[0]

CD_a_w = Wing_params.CDa_poststall(tca, CDs_w, CDs_f, Afus, alpha_lst, "wing", Drag.CD, deda)
CD_a_f = Wing_params.CDa_poststall(tca, CDs_w, CDs_f, Afus, alpha_lst, "fus", Drag.CD, deda)

plt.plot(alpha_lst, Cl_alpha_curve)
plt.show()

#x = optimize_wingtips(0,0.2,0.005, 1.5, 'tandem',S_ref,l1,l2,l3,d_eq,Vcruise,rho,MAC,AR,Mach(Vcruise,a),k,flamf,flamw,mu,tc,xcm,0,SweepLE,u,C_t,h_d,IF_f,IF_w, IF_v, CL_CDmin,Abase, S_v, s1, s2)
#                  Drag = componentdrag('tandem',S_ref,l1,l2,l3,d_eq,Vcruise,rho,MAC,AR,Mach(Vcruise,a),k,flamf,flamw,mu,tc,xcm,0,SweepLE,u,C_t,h_d,IF_f,IF_w, IF_v, CL_CDmin,Abase, S_v, s1, s2, h_wl1, h_wl1)
#
#print(x)

#x = LLT2wings(b,2*AR,C_r,C_t,0,5, h_d, 6,b,2*AR,C_r,C_t,0,5, 70, 0, 1.5)
#print(b,C_t, C_r)
#x = LLT1wing
#print(x)
D = 0.965 #m
T = 240.5 #N
ne1 = 6
ne2 = 6

#152.34774175721694 46.21428413797744 1.111617926993772 0.8934300657546558 6 6 0.17 0.17230950765784175 0.004628973850025598 1.8425440913304136 1 0.2723339479180486
alpha_wp = np.arange(-5,18,0.25)
Cl_alpha_curve2 = Wing_params.CLa(tc, CDs, CDs_f, Afus, alpha_wp, deda)
CLwp = Wing_params.CLa_wprop(T, Vcruise,rho,D,ne1,ne2,tc,CDs_w, CDs_f, Afus, alpha_wp, 0.25)
#CLwp = Wing_params.CLa_wprop(200.34774175721694 ,46.21428413797744 ,1.111617926993772, 0.8934300657546558, 6, 6 ,0.17, 0.17230950765784175, 0.004628973850025598, 1.8425440913304136, alpha_wp ,deda)
print("C_T", Wing_params.C_T(ne1,ne2,T, Vcruise, rho))
print("deltaV", Wing_params.deltaV(T, Vcruise, rho, D, ne1, ne2))
print("CLmax", CLwp[1], CLwp[4:6])
print("CLalphanoprop", Wing_params.liftslope(deda)[0], Wing_params.liftslope(deda)[1], Wing_params.liftslope(deda)[4])
print("CLalpha", s1*CLwp[2]+ s2*CLwp[3], CLwp[2:4])
print("Deff", Wing_params.Deff(T,Vcruise, rho, D, ne1, ne2))
plt.plot(alpha_wp, CLwp[6])
plt.plot(alpha_wp, Cl_alpha_curve2[1])
plt.show()

plt.plot(alpha_wp, CLwp[7])
plt.plot(alpha_wp, Cl_alpha_curve2[2])
plt.show()




def plot_stagger_gap(b, CL, S):
    gap = np.linspace(1,1.5,50)
    stagger = np.linspace(1,7,50)

    p = 1 / np.sqrt(1 +  gap ** 2)
    F = ellipk(p)
    E = ellipe(p)
    R = b * np.pi / 4 * ( np.sqrt(1 + gap ** 2) - gap ) / F - E
    k = interp1d( [0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5], [1,1.06,1.1,1.13,1.16,1.21,1.24,1.27], fill_value='extrapolate')
    munk =(1 / (k (gap /stagger) **2) - 0.5) * b / R

    gap, stagger = np.meshgrid(gap,stagger)
    dCL = - 2 * CL * S / (b ** 2) * munk * stagger/ b

    fig = plt.figure(figsize=(6,5))
    left, bottom, width, height = 0.1, 0.1, 0.8, 0.8
    ax = fig.add_axes([left, bottom, width, height])
    ax.set_title(' $ \Delta C_L$  for biplane wings')
    ax.set_xlabel('Stagger [m]')
    ax.set_ylabel('Gap [m]')
    cp = plt.contourf(stagger,gap,dCL)
    plt.colorbar(cp)
    plt.show()
plot_stagger_gap(b, 0.4, S_ref) # plot_stagger_gap(7, 0.4, 16)



