import sys
sys.path.append("../")
from Preliminary_Lift.Airfoil import *
from Preliminary_Lift.Drag import e_factor, C_D_0, LD_ratio, C_L
from constants import *
from Aero_tools import ISA

# A/C
W = MTOW #[N]
Vcruise = 69.444 #[m/s]

Wing_loading = 551
# ISA
h = h_cruise # cruise height[m]
atm_flight  = ISA(h)
rho = atm_flight.density() # cte.rho
mu = atm_flight.viscosity_dyn()
a = atm_flight.soundspeed()

# Wing Planform Parameter
b = 14 # Due to reqs
S_ref = S #[m**2] PLACEHOLDER
AR = b**2/S_ref   #PLACEHOLDER
taper = 0.4
sweepc4 =0
# For double wing configurations
s1=0.5
s2=1-s1

S1 = S_ref*s1 #[m**2]  PLACEHOLDER
S2= S_ref*s2 #[m**2]  PLACEHOLDER

sweepc41= 0
sweepc42=0
taper1= 0.4
taper2= 0.4

#Lift-Drag estimation parameters
Cfe = 0.0045
Swet_ratio = 4.5
h_d = 2.8  # preliminary: for a 0.2 h/b ratio
b_d = 14  # fixed due to span limitations
e_ref = 0.85
deda = 0.1 # 10%, from Daniel Schitanz, Scholtz
# Airfoil data
NASA_LANGLEY = [6.188, 1.979, -0.065, 0.00445, 0.293] # Lift slope [1/rad], CL_max, C_m cruise, Cd_min, CL for Cdmin.
EPPLER335 = [6.245, 1.61330, 0.0489, 0.00347, 0.241]  # Lift slope [1/rad], CL_max, C_m cruise, Cd_min, CL for Cdmin.

#Preliminary Lift-Drag Results
CD_0 = C_D_0(Cfe, Swet_ratio)

e_conv = e_factor('normal', h_d, b_d, e_ref)
e_tan = e_factor('tandem', h_d,b_d,e_ref)
e_box = e_factor('box', h_d, b_d, e_ref)

LD_conv = LD_ratio('cruise', CD_0, AR, e_conv), LD_ratio('loiter', CD_0, AR, e_conv)
LD_tan = LD_ratio('cruise', CD_0, AR, e_tan), LD_ratio('loiter', CD_0, AR, e_tan)
LD_box = LD_ratio('cruise', CD_0, AR, e_box), LD_ratio('loiter', CD_0, AR, e_box)

Wing_planform_params_single = wing_planform(AR,S,sweepc4,taper)
Wing_planform_params_double =  wing_planform_double(AR, S1, sweepc41, taper1, S2, sweepc42, taper2)
"""
Method 1 to find CLdes
CL_Design_conv = C_L('cruise', CD_0,AR,e_conv)
CL_Design_box =C_L('cruise', CD_0,AR,e_box)
CL_Design_tan = C_L('cruise', CD_0,AR,e_tan)

Cl_des_conv = CL_Design_conv/(np.cos(sweep_atx(0,Wing_planform_params_single[1],14,taper,sweepc4)))**2
Cl_des_box = CL_Design_box/(np.cos(sweep_atx(0,Wing_planform_params_double[0][1],14,taper,sweepc4)))**2
Cl_des_tan = CL_Design_tan/(np.cos(sweep_atx(0,Wing_planform_params_double[0][1],14,taper,sweepc4)))**2

V_cruise_conv = np.sqrt(Wing_loading/(0.5*rho*CL_Design_conv))
V_cruise_box = np.sqrt(Wing_loading/(0.5*rho*CL_Design_box))
V_cruise_tan = np.sqrt(Wing_loading/(0.5*rho*CL_Design_tan))
"""
#Method 2
C_L_des = CL_des(rho,Vcruise,W,S_ref)

Cl_des_conv = C_L_des/(np.cos(sweep_atx(0,Wing_planform_params_single[1],b,taper,sweepc4)))**2
Cl_des_box = C_L_des/(np.cos(sweep_atx(0,Wing_planform_params_double[0][1],b,taper,sweepc4)))**2
Cl_des_tan = C_L_des/(np.cos(sweep_atx(0,Wing_planform_params_double[0][1],b,taper,sweepc4)))**2

Re_Number = Re( rho, Vcruise, Wing_planform_params_single[3], mu), Re( rho, Vcruise, Wing_planform_params_double[0][3], mu), Re( rho, Vcruise, Wing_planform_params_double[1][3], mu)

#Wing performance
sweepc2 = sweep_atx(0.5,Wing_planform_params_single[1],Wing_planform_params_single[0],taper,sweepc4)

Clda_conv = liftslope('normal', AR, sweepc2, Mach(Vcruise,a), EPPLER335[0], s1, s2, deda) # 2pi airfoil slope assumed as placeholder
Clda_double = liftslope('double', AR, sweepc2, Mach(Vcruise,a), NASA_LANGLEY[0], s1, s2, deda) # includes in order: total clda, clda wing1, clda wing 2

C_L_max_conv = 0.9* EPPLER335[1]  # From ADSEE-II L2
C_L_max_double = s1*0.9* NASA_LANGLEY[1]+ s2*0.9*1.930  #Due to downwash Clmax for second wing is lower

print("AR= ", AR)
print(S1)
print("LE sweep=", sweep_atx(0,Wing_planform_params_single[1],b,taper,sweepc4)*180/np.pi)

print("Lift slope conv =", Clda_conv)
print("Lift slope double =", Clda_double)

print("C_L_max_single=", C_L_max_conv)
print("C_L_max_double=", 0.9* NASA_LANGLEY[1],  0.9*1.930)
