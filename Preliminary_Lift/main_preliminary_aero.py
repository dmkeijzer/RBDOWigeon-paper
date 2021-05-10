from Preliminary_Lift.Airfoil import *
from Preliminary_Lift.Drag import e_factor, CD0, C_D, LD_ratio, C_L
import constants as c
from Aero_tools import ISA


# A/C
W = c.mTO

# ISA
h = c.hc
atm_flight  = ISA(h)
rho = c.rho
mu = atm_flight.viscosity_dyn()

# Wing Planform Parameter
S =
AR = 9
taper = 0.4
sweepc4 =0
# For double wing configurations
S1 =
S2=
sweepc41= 0
sweepc42=0
taper1= 0.4
taper2= 0.4
#Drag estimation parameters
Cfe = 0.0045
Swet_ratio = 4.5
h_d = 0.2
b_d = 0.2

e_ref = 0.85
#Preliminary Lift-Drag Results
CD_0 = CD0(Cfe, Swet_ratio)

a = 1+2