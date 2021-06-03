import sys
sys.path.append("../")
from Preliminary_Lift.Airfoil import *
from Preliminary_Lift.Drag import *
from Aero_tools import ISA
from Preliminary_Lift.Wing_design import *
from Preliminary_Lift.Airfoil_analysis import airfoil_stats
import os
import json
import matplotlib.pyplot as plt
root_path = os.path.join(os.getcwd(), os.pardir)

datafile = open(os.path.join(root_path, "data/inputs_config_1.json"), "r")
data = json.load(datafile)
datafile.close()
FP = data["Flight performance"]
STR = data["Structures"]
AR = 7


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
S_ref = W/Wing_loading #[m**2] PLACEHOLDER
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
l_h = 5 # Horizontal gap between wings. Based on fuselgae size
e_ref = e_OS(AR)
e = e_factor('tandem', h_d,b_d,e_ref)

Wing_params = wing_design(AR,s1,sweepc41,s2,sweepc42,M,S_ref)
MAC = Wing_params.wing_planform_double()[0][3]
SweepLE = Wing_params.sweep_atx(0)[0]
#Fuselage dimensions
l1 = 2.5
l2 = 2
l3 = 2.7
w_max = 1.38
h_max = 1.705
d_eq = np.sqrt(h_max*w_max)
#For Drag estimation
k = 0.634 * 10**(-5) # Smooth paint from adsee 2 L2
flamf =0.1  # From ADSEE 2 L2 GA aircraft
IF_f = 1    # From ADSEE 2 L2
IF_w = 1.1   # From ADSEE 2 L2
flamw = 0.35 # From ADSEE 2 L2 GA aircraft
u = 8.43 *np.pi/180 # fuselage upsweep
Abase = 0
# Airfoil
airfoil = airfoil_stats()
tc = 0.17
xcm = 0.3
CL_CDmin = airfoil[2]
CL_lst = np.arange(-0.5,1.7,0.100)
#Other parameters
S_v = 0.6
S_t = 0


Drag = componentdrag('tandem',S_ref,l1,l2,l3,d_eq,Vcruise,rho,MAC,AR,e,Mach(Vcruise,a),k,flamf,flamw,mu,tc,xcm,0,u,0,h_d,IF_f,IF_w,CL_CDmin,Abase, S_v, S_t)

#Stall
stall = Wing_params.CLmax_s(l_h,h_d,w_max)
CLmax = stall[0]
CDs = Drag.CD(CLmax)
CDs_f = Drag.CD0_f
#Post stall
Afus = np.pi *d_eq/4
post_stall = Wing_params.post_stall_lift_drag(l_h,h_d,w_max,tc, CDs, CDs_f, Afus)
plt.plot(post_stall[0],post_stall[3])

plt.show()









