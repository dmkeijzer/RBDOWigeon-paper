import sys
sys.path.append("../")
from Preliminary_Lift.Airfoil import *
from Preliminary_Lift.Drag import e_factor, C_D_0, LD_ratio, C_L
from constants import *
from Aero_tools import ISA

# A/C
W = mTO*9.81 #[N]
Vcruise = 69.444 #[m/s]

Wing_loading = 551
# ISA
h = h_cruise # cruise height[m]
atm_flight  = ISA(h)
rho = atm_flight.density() # cte.rho
mu = atm_flight.viscosity_dyn()
a = atm_flight.soundspeed()
# Wing Planform Parameter
S = W/Wing_loading #[m**2] PLACEHOLDER
AR = 14**2/S   #PLACEHOLDER
taper = 0.4
sweepc4 =0
# For double wing configurations
s1=0.5
s2=1-s1

S1 = S*s1 #[m**2]  PLACEHOLDER
S2= S*s2 #[m**2]  PLACEHOLDER

sweepc41= 0
sweepc42=0
taper1= 0.4
taper2= 0.4

#Lift-Drag estimation parameters
Cfe = 0.0045
Swet_ratio = 4.5
h_d = 0.2  # preliminary
b_d = 1  # preliminary
e_ref = 0.85
deda = 0.1 # 10%, from Daniel Schitanz, Scholtz



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
C_L_des = CL_des(rho,Vcruise,W,S)

Cl_des_conv = C_L_des/(np.cos(sweep_atx(0,Wing_planform_params_single[1],14,taper,sweepc4)))**2
Cl_des_box = C_L_des/(np.cos(sweep_atx(0,Wing_planform_params_double[0][1],14,taper,sweepc4)))**2
Cl_des_tan = C_L_des/(np.cos(sweep_atx(0,Wing_planform_params_double[0][1],14,taper,sweepc4)))**2

Re_Number = Re( rho, Vcruise, Wing_planform_params_single[3], mu), Re( rho, Vcruise, Wing_planform_params_double[0][3], mu), Re( rho, Vcruise, Wing_planform_params_double[1][3], mu)

#Wing performance
sweepc2 = sweep_atx(0.5,Wing_planform_params_single[1],Wing_planform_params_single[0],taper,sweepc4)

Clda_conv = liftslope('normal', AR, sweepc2, Mach(Vcruise,a), 2*np.pi, s1, s2, deda) # 2pi airfoil slope assumed as placeholder
Clda_double = liftslope('double', AR, sweepc2, Mach(Vcruise,a), 2*np.pi, s1, s2, deda) # includes in order: total clda, clda wing1, clda wing 2

