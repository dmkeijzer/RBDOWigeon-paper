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
from LLTtest2 import LLT1wing , LLT2wings, downwash, downwash_upwash
from scipy.special import ellipk, ellipe
from scipy.interpolate import interp1d
root_path = os.path.join(os.getcwd(), os.pardir)

datafile = open(os.path.join(root_path, "data/inputs_config_1.json"), "r")
data = json.load(datafile)
datafile.close()
FP = data["Flight performance"]
STR = data["Structures"]
AR = 3.75


W = STR["MTOW"] #[N]
Vcruise = 60#FP["V_cruise"] #[m/s]
Wing_loading = FP["WS"]

#Cruise conditions
h = 400 # cruise height[m]
atm_flight  = ISA(h)
rho = atm_flight.density() # cte.rho
mu = atm_flight.viscosity_dyn()
a = atm_flight.soundspeed()
M = Mach(Vcruise,a)

#Wing planform
S_ref = 17.095 #W/Wing_loading #[m**2] PLACEHOLDER
print("S", S_ref)
b = np.sqrt(AR*S_ref) # Due to reqs

# For double wing
s1=0.5
s2=1-s1
#Sweep
sweepc41= 0
sweepc42=0

#Other paramters
b_d = b  # fixed due to span limitations
h_d = 1.4  #  Vertical gap between wings. Based on fuselage size
l_h = 6 # Horizontal gap between wings. Based on fuselgae size

#Fuselage dimensions
l1 = 2.5
l2 = 2
l3 = 2.7
w_max = 1.38
h_max = 1.705
d_eq = np.sqrt(h_max*w_max)
#Winglets
h_wl1 =0
h_wl2 = 0
Wing_params = wing_design(2*AR, 2*AR, s1,sweepc41,s2,sweepc42,M,S_ref, l_h,h_d,w_max,h_wl1,h_wl2)
b = Wing_params.wing_planform_double()[0][0]
C_r = Wing_params.wing_planform_double()[0][1]
C_t = Wing_params.wing_planform_double()[0][2]
print(b,C_r,C_t)
MAC = Wing_params.wing_planform_double()[0][3]
SweepLE = Wing_params.sweep_atx(0)[0]
deda = downwash(Wing_params.wing_planform_double()[0][0] , Wing_params.AR1,
                Wing_params.wing_planform_double()[0][1], Wing_params.wing_planform_double()[0][2], Wing_params.sweepc41, 5, Wing_params.h_ht,
                Wing_params.lh, Wing_params.wing_planform_double()[1][0] ,
                Wing_params.wing_planform_double()[0][1], Wing_params.wing_planform_double()[0][2], Wing_params.sweepc41,
                70)  # deps_da(self.sweepc41, wg[0][0], self.lh, self.h_ht, self.AR_i, slope1)

deda2 = downwash_upwash(Wing_params.wing_planform_double()[0][0] , Wing_params.AR1,
                Wing_params.wing_planform_double()[0][1], Wing_params.wing_planform_double()[0][2], Wing_params.sweepc41, 5, Wing_params.h_ht,
                Wing_params.lh, Wing_params.wing_planform_double()[1][0] , Wing_params.AR2,
                Wing_params.wing_planform_double()[0][1], Wing_params.wing_planform_double()[0][2], Wing_params.sweepc42,
                70)
Slope1 = Wing_params.liftslope(deda)[1]
print("Deps_Da", Wing_params.liftslope(deda)[3], deda2)
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
xcm = 0.3 #NACA0012 for winglets and Vtail
CL_CDmin = airfoil[2]
CL_lst = np.arange(-0.5,1.7,0.100)
#Other parameters
S_v = 0.6
S_t = 0


Drag = componentdrag('tandem',S_ref,l1,l2,l3,d_eq,Vcruise,rho,MAC,AR,Mach(Vcruise,a),k,flamf,flamw,mu,tc,xcm,0,SweepLE,u,0,h_d,IF_f,IF_w, IF_v, CL_CDmin,Abase, S_v, s1, s2, h_wl1, h_wl2)


CL_design = Drag.CL_des()[0]
Cd_des= Drag.Cd_w(CL_design)
Swet_f = Drag.Swet_f()
print("S_f", Swet_f)
print("CLdes", CL_design)

#Stall
stall = Wing_params.CLmax_s(deda)
CLmax = stall[0]

CDs = Drag.CD(CLmax)
CDs_f = Drag.CD0_f
CDs_w = CDs - CDs_f
#Post stall
Afus = np.pi *d_eq**2/4
post_stall = Wing_params.post_stall_lift_drag(tc, CDs, CDs_f, Afus, deda)

alpha_lst = np.arange(-3,89,0.1)
Cl_alpha_curve = Wing_params.CLa(tc, CDs, CDs_f, Afus, alpha_lst, deda)

CD_a_w = Wing_params.CDa_poststall(tc, CDs_w, CDs_f, Afus, alpha_lst, "wing", Drag.CD, deda)
CD_a_f = Wing_params.CDa_poststall(tc, CDs_w, CDs_f, Afus, alpha_lst, "fus", Drag.CD, deda)

plt.plot(alpha_lst, Cl_alpha_curve)
plt.show()

#x = optimize_wingtips(0,0.2,0.005, 1.5, 'tandem',S_ref,l1,l2,l3,d_eq,Vcruise,rho,MAC,AR,Mach(Vcruise,a),k,flamf,flamw,mu,tc,xcm,0,SweepLE,u,C_t,h_d,IF_f,IF_w, IF_v, CL_CDmin,Abase, S_v, s1, s2)
#                  Drag = componentdrag('tandem',S_ref,l1,l2,l3,d_eq,Vcruise,rho,MAC,AR,Mach(Vcruise,a),k,flamf,flamw,mu,tc,xcm,0,SweepLE,u,C_t,h_d,IF_f,IF_w, IF_v, CL_CDmin,Abase, S_v, s1, s2, h_wl1, h_wl1)
#
#print(x)

#x = LLT2wings(b,AR*2,C_r,C_t,0,5, h_d, l_h,b,AR*2,C_r,C_t,0,5, 70)
#print(b,C_t, C_r)
#x = LLT1wing
#print(x)
D = 0.965 #m
T = 146.5 #N
ne1 = 6
ne2 = 6

alpha_wp = np.arange(-3,21,0.25)
Cl_alpha_curve2 = Wing_params.CLa(tc, CDs, CDs_f, Afus, alpha_wp, deda)
CLwp = Wing_params.CLa_wprop(T, Vcruise,rho,D,ne1,ne2,tc,CDs_w, CDs_f, Afus, alpha_wp, deda)
print("DeltaV",Wing_params.deltaV(T, Vcruise,rho,D, ne1, ne2))
plt.plot(alpha_wp, CLwp)
plt.plot(alpha_wp, Cl_alpha_curve2)
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



