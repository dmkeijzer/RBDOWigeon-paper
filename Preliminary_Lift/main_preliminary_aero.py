import sys
sys.path.append("../")
from Preliminary_Lift.Airfoil import *
from Preliminary_Lift.Drag import e_factor, CD0, LD_ratio
from constants import *
from Aero_tools import ISA


# A/C
W = mTO * 9.81 #[N]
Vcruise = 70 #[m/s]
# ISA
h = hc # cruise height[m]
atm_flight  = ISA(h)
rho = atm_flight.density() # cte.rho
mu = atm_flight.viscosity_dyn()

# Wing Planform Parameter
S = 15 #[m**2] PLACEHOLDER
AR = 9   #PLACEHOLDER
taper = 0.4
sweepc4 =0
# For double wing configurations
S1 = 7.5 #[m**2]  PLACEHOLDER
S2= 7.5 #[m**2]  PLACEHOLDER
sweepc41= 0
sweepc42=0
taper1= 0.4
taper2= 0.4
#Drag estimation parameters
Cfe = 0.0045
Swet_ratio = 4.5
h_d = 0.2  # preliminary
b_d = 1  # preliminary

e_ref = 0.85
#Preliminary Lift-Drag Results
CD_0 = CD0(Cfe, Swet_ratio)

e_conv = e_factor('normal', h_d, b_d, e_ref)
e_tan = e_factor('tandem', h_d,b_d,e_ref)
e_box = e_factor('box', h_d, b_d, e_ref)

LD_conv = LD_ratio('cruise', CD_0, AR, e_conv), LD_ratio('loiter', CD_0, AR, e_conv)
LD_tan = LD_ratio('cruise', CD_0, AR, e_tan), LD_ratio('loiter', CD_0, AR, e_tan)
LD_box = LD_ratio('cruise', CD_0, AR, e_box), LD_ratio('loiter', CD_0, AR, e_box)

Wing_planform_params_single = wing_planform(AR,S,sweepc4,taper)
Wing_planform_params_double =  wing_planform_double(AR, S1, sweepc41, taper1, S2, sweepc42, taper2)

CL_Design = CL_des(rho,Vcruise,W,S)

Re_Number = Re( rho, Vcruise, Wing_planform_params_single[3], mu), Re( rho, Vcruise, Wing_planform_params_double[0][3], mu), Re( rho, Vcruise, Wing_planform_params_double[1][3], mu)
