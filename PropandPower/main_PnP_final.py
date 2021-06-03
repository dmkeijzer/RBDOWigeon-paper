import numpy as np
import BEM as BEM
import Aero_tools as at
ISA = at.ISA(2500)
a = ISA.soundspeed()
rho = ISA.density()
dyn_visc = ISA.viscosity_dyn()

# B, R, rpm, xi_0, rho, dyn_vis, V_fr, N_stations, a, RN_spacing, T=None, P=None
B = 5
xi_0 = 0.15
A_prop = 0.47
R = np.sqrt(A_prop / (np.pi * (1 - xi_0**2)))

M_t_max = 0.7
rpm = M_t_max*a*60 / (np.pi * 2*R)

V_cruise = 60
N_stations = 30
RN_spacing = 100000

P_cr = 110024
T =  (P_cr*2*np.sqrt(rho*16*A_prop) * 0.65)**(2/3)

propeller = BEM.BEM(B, R, rpm, xi_0, rho, dyn_visc, V_cruise, N_stations, a, RN_spacing, T=T)

# Zeta init
zeta_init = 0
design = propeller.optimise_blade(zeta_init)[1]
# [cs, betas, alpha, E, eff, Tc, self.Pc]
print("Chord per station:", design[0])
print("Pitch per station:", design[1]*180/(2*np.pi))
print("AoA per station:", design[2])
print("D/L ratio per station:", design[3])
print("Propeller efficiency:", design[4])
print("Thrust coefficient:", design[5])
print("Power coefficient:", design[6])

